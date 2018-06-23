##
#
# Copyright (C) 2018 Matt Molyneaux
# 
# This file is part of Exhibition.
# 
# Exhibition is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Exhibition is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Exhibition.  If not, see <https://www.gnu.org/licenses/>.
#
##

from http.server import HTTPServer, SimpleHTTPRequestHandler
from importlib import import_module
import io
import json
import logging
import os
import pathlib
import re
import shutil
import threading

from ruamel.yaml import YAML

logger = logging.getLogger("exhibition")

SITE_YAML_PATH = "site.yaml"

yaml_parser = YAML(typ="safe")

DATA_EXTRACTORS = {
    ".yaml": yaml_parser.load,
    ".json": json.loads,
}


class Config:
    def __init__(self, data=None, parent=None):
        self.parent = parent
        self._base_config = {}

        if data:
            self.load(data)

    def load(self, data):
        if isinstance(data, (str, io.IOBase)):
            self._base_config.update(yaml_parser.load(data))
        elif isinstance(data, dict):
            self._base_config.update(data)
        else:
            raise AssertionError("data needs to be a string, file-like, or dict-like object")

    @classmethod
    def from_path(cls, path):
        with open(path) as f:
            obj = cls(f)

        return obj

    def __getitem__(self, key):
        try:
            return self._base_config[key]
        except KeyError:
            if self.parent is None:
                raise
            else:
                return self.parent[key]

    def __setitem__(self, key, value):
        self._base_config[key] = value

    def __contains__(self, key):
        return key in self.keys()

    def __len__(self):
        return len(list(self.keys()))

    def __iter__(self):
        return self.keys()

    def keys(self):
        _keys_set = set()
        for k in self._base_config.keys():
            _keys_set.add(k)
            yield k

        if self.parent is not None:
            for k in self.parent.keys():
                if k in _keys_set:
                    _keys_set.add(k)
                    yield k

    def values(self):
        for k in self.keys():
            yield self[k]

    def items(self):
        for k in self.keys():
            yield (k, self[k])

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def update(self, *args, **kwargs):
        self._base_config.update(*args, **kwargs)

    def copy(self):
        klass = type(self)
        return klass(self._base_config.copy(), self.parent)


class Node:
    _meta_names = ["meta.yaml", "meta.yml"]
    _index_file = "index.html"
    _strip_exts = ["html"]

    _meta_header = "---\n"
    _meta_footer = "---\n"

    _dir_mode = 0o755
    _file_mode = 0o644

    _content_start = None
    _data = None

    def __init__(self, path, parent, meta=None):
        self.path_obj = path
        self.parent = parent
        self.children = {}

        self.is_leaf = self.path_obj.is_file()

        self.meta = Config({}, getattr(self.parent, "meta", None))
        if meta:
            self.meta.update(meta)

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.path_obj.name)

    @property
    def full_path(self):
        if self.parent is None:
            return self.meta["deploy_path"]
        else:
            return str(pathlib.Path(self.parent.full_path, self.path_obj.name))

    @property
    def full_url(self):
        """Get full URL for node, including trailing slash"""
        if self.parent is None:
            base_url = self.meta.get("base_url", "/")
            if not base_url.startswith("/"):
                base_url = "/" + base_url
            if not base_url.endswith("/"):
                base_url = base_url + "/"

            return base_url
        elif self.is_leaf:
            if self.path_obj.name == self._index_file:
                name = ""
            elif self.path_obj.suffix in self._strip_exts:
                name = self.path_obj.stem
            else:
                name = self.path_obj.name

            return "".join([self.parent.full_url, name])
        else:
            return "".join([self.parent.full_url, self.path_obj.name, "/"])

    def walk(self, include_self=False):
        """Walk through Node tree"""
        if include_self:
            yield self

        for child in self.children.values():
            yield child
            for grandchild in child.walk():
                yield grandchild

    def render(self):
        if not self.is_leaf:
            pathlib.Path(self.full_path).mkdir(self._dir_mode)
            return

        file_obj = pathlib.Path(self.full_path)
        file_obj.touch(self._file_mode)


        content = self.get_content()
        content_filter = self.meta.get("filter")

        if content_filter is not None:
            filter_module = import_module(content_filter)
            filter_glob = self.meta.get("filter-glob", filter_module.DEFAULT_GLOB)
            if file_obj in file_obj.parent.glob(filter_glob):
                content = filter_module.content_filter(self, content)

        file_obj.open("w").write(content)

    def process_meta(self):
        """
        Finds and processes the meta YAML from the top of a file

        If the file does not start with ---\n, then it's assumed the file does
        not contain any meta YAML for us to process
        """
        if self._content_start is not None:
            # we've done with already
            return

        found_header = False
        file_obj = self.path_obj.open("r")
        while True:
            data = file_obj.read(100)

            if data == '':
                # we've run out of file, either we didn't find a header or
                # we're missing a footer
                self._content_start = 0
                return
            elif not found_header:
                if data.startswith(self._meta_header):
                    found_header = True
                    found_meta = data[len(self._meta_header):]
                else:
                    # if our token is not the first thing in the file, then
                    # it's not for us
                    self._content_start = 0
                    return
            else:
                found_meta += data

            if self._meta_footer in found_meta:
                idx = found_meta.index(self._meta_footer)
                found_meta = found_meta[:idx]
                break

        self.meta.load(found_meta)
        self._content_start = len(self._meta_header) + len(found_meta) + len(self._meta_footer)    
                 
    def get_content(self):
        self.process_meta()
        file_obj = self.path_obj.open("r")
        file_obj.seek(self._content_start)
        return file_obj.read()

    @property
    def data(self):
        """Extracts data from contents of file

        For example, a YAML file
        """
        if self.path_obj.is_dir():
            return

        if self._data is None:
            data = self.get_content()

            func = DATA_EXTRACTORS[self.path_obj.suffix]

            self._data = func(data)

        return self._data

    def add_child(self, child):
        self.children[child.path_obj.name] = child

    @property
    def siblings(self):
        return {k: v for k, v in self.parent.children.items() if v is not self}

    @classmethod
    def from_path(cls, path, parent=None, meta=None):
        # path should be a pathlib object
        assert path.is_file() or path.is_dir()


        node = cls(path, parent=parent, meta=meta)

        if path.is_dir():
            for child in path.iterdir():
                ignored = False
                for glob in node.meta.get("ignore", []):
                    if child in path.glob(glob):
                        ignored = True
                        break
                if ignored:
                    continue

                if child.name in cls._meta_names and child.is_file():
                    node.meta.load(child.open())
                else:
                    node.add_child(cls.from_path(child, node))

        return node


def gen(settings):
    shutil.rmtree(settings["deploy_path"], True)
    root_node = Node.from_path(pathlib.Path(settings["content_path"]), meta=settings)

    for item in root_node.walk(True):
        logger.info("Rendering %s", item.full_url)
        item.render()


def serve(settings):
    logger = logging.getLogger("exhibition.server")

    class ExhibitionHTTPRequestHandler(SimpleHTTPRequestHandler):
        def translate_path(self, path):
            path = path.strip("/")
            if settings.get("base_url"):
                base = settings["base_url"].strip("/")
                if not path.startswith(base):
                    return ""
                path = path.lstrip(base).strip("/")

            path = os.path.join(settings["deploy_path"], path)

            return path

    server_address = ('localhost', 8000)

    httpd = HTTPServer(server_address, ExhibitionHTTPRequestHandler)

    logger.warning("Listening on http://%s:%s", *server_address)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()

    return (httpd, t)
