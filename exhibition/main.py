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
import logging
import os
import pathlib
import shutil
import threading

from ruamel.yaml import YAML

logger = logging.getLogger("exhibition")

SITE_YAML_PATH = "site.yaml"

yaml_parser = YAML(typ="safe")

DATA_EXTRACTORS = {
    ".yaml": yaml_parser.load,
    ".json": yaml_parser.load,
}


class Config:
    """
    Configuration object that implements a dict-like interface

    If a key cannot be found in this instance, the parent :class:`Config` will
    be searched (and its parent, etc.)
    """
    def __init__(self, data=None, parent=None):
        """
        :param data:
            Can be one of a string, a file-like object, a dict-like object, or
            ``None``. The first two will be assumed as YAML
        :param parent:
            Parent :class:`Config` or ``None`` if this is the root configuration object
        """
        self.parent = parent
        self._base_config = {}

        if data:
            self.load(data)

    def load(self, data):
        """
        Load data into configutation object

        :param data:
            If a string or file-like object, ``data`` is parsed as if it were
            YAML data. If a dict-like object, ``data`` is added to the internal
            dictionary.

            Otherwise an :class:`AssertionError` exception is raised
        """
        if isinstance(data, (str, io.IOBase)):
            self._base_config.update(yaml_parser.load(data))
        elif isinstance(data, dict):
            self._base_config.update(data)
        else:
            raise AssertionError("data needs to be a string, file-like, or dict-like object")

    @classmethod
    def from_path(cls, path):
        """Load YAML data from a file"""
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
                if k not in _keys_set:
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

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self._base_config.keys())


class Node:
    """
    A node represents a file or directory
    """
    _meta_names = ["meta.yaml", "meta.yml"]
    _index_file = "index.html"
    _strip_exts = [".html"]

    _meta_header = "---\n"
    _meta_footer = "---\n"

    _dir_mode = 0o755
    _file_mode = 0o644

    _content_start = None
    _content = None
    _data = None
    _marks = None

    def __init__(self, path, parent, meta=None):
        """
        :param path:
            A :class:`pathlib.Path` that is either the ``content_path`` or a child of it.
        :param parent:
            Either another :class:`Node` or ``None``
        :param meta:
            A dict-like object that will be passed to a :class:`Config` instance
        """
        self.path_obj = path
        self.parent = parent
        self.children = {}

        self.is_leaf = self.path_obj.is_file()

        self._meta = Config({}, getattr(self.parent, "meta", None))
        if meta:
            self._meta.update(meta)

        if self.parent:
            self.parent.add_child(self)

    @classmethod
    def from_path(cls, path, parent=None, meta=None):
        """
        Given a :class:`pathlib.Path`, create a Node from that path as well as
        any children

        If the path is not a file or a dir, an :class:`AssertionError` is raised

        :param path:
            A :class:`pathlib.Path` that is either the ``content_path`` or a child of it.
        :param parent:
            Either another :class:`Node` or ``None``
        :param meta:
            A dict-like object that will be passed to a :class:`Config` instance
        """
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
                    with child.open() as co:
                        node.meta.load(co)
                else:
                    cls.from_path(child, node)

        return node

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.path_obj.name)

    @property
    def full_path(self):
        """
        Full path of node when deployed
        """
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
        """
        Process node and either create the directory or write contents of file to ``deploy_path``
        """
        if not self.is_leaf:
            pathlib.Path(self.full_path).mkdir(self._dir_mode)
            return

        file_obj = pathlib.Path(self.full_path)
        file_obj.touch(self._file_mode)

        content = self.get_content()

        with file_obj.open("w" if type(content) is str else "wb") as fo:
            fo.write(content)

    def process_meta(self):
        """
        Finds and processes the YAML fonrt matter at the top of a file

        If the file does not start with ``---\\n``, then it's assumed the file
        does not contain any meta YAML for us to process
        """
        if self._content_start is not None:
            # we've done this already
            return
        if not self.is_leaf:
            self._content_start = 0
            return

        found_header = False
        with self.path_obj.open("rb") as file_obj:
            while True:
                data = file_obj.read(100)
                try:
                    data = data.decode("utf-8")
                except UnicodeDecodeError:
                    self._content_start = 0
                    return

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

        self._meta.load(found_meta)
        self._content_start = len(self._meta_header) + len(found_meta) + len(self._meta_footer)

    def get_content(self):
        """
        Get the actual content of the Node

        First calls :meth:`process_meta` to find the end any front matter that
        might be present and then returns the rest of the file

        If ``filter`` has been specified in :attr:`meta`, that filter will be
        used to further process the content.
        """
        if self._content is not None:
            return self._content

        self.process_meta()
        content_filter = self.meta.get("filter")
        with self.path_obj.open("rb") as file_obj:
            file_obj.seek(self._content_start)
            self._content = file_obj.read()
            try:
                self._content = self._content.decode("utf-8")
            except UnicodeDecodeError:
                return self._content

            if content_filter is not None:
                filter_module = import_module(content_filter)
                filter_glob = self.meta.get("filter-glob", filter_module.DEFAULT_GLOB)
                if self.path_obj in self.path_obj.parent.glob(filter_glob):
                    self._content = filter_module.content_filter(self, self._content)

        return self._content

    @property
    def meta(self):
        """
        Configuration object

        Automatically loads front-matter if applicable
        """
        self.process_meta()
        return self._meta

    @property
    def marks(self):
        """
        Marked sections from content

        Calls :meth:`get_content` to process content if that hasn't been done
        already
        """
        if self._marks is not None:
            return self._marks

        self._marks = {}
        # make sure that _marks gets populated
        self.get_content()

        return self._marks

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
        """
        Add a child to the current Node

        If the child doesn't already have its :attr:`parent` set to this Node,
        then an :class:`AssertionError` is raised.
        """
        assert child.parent == self
        self.children[child.path_obj.name] = child

    @property
    def siblings(self):
        """Returns all children of the parent Node, except for itself"""
        return {k: v for k, v in self.parent.children.items() if v is not self}


def gen(settings):
    """
    Generate site

    Deletes ``deploy_path`` first.
    """
    shutil.rmtree(settings["deploy_path"], True)
    root_node = Node.from_path(pathlib.Path(settings["content_path"]), meta=settings)

    for item in root_node.walk(True):
        logger.info("Rendering %s", item.full_url)
        item.render()


def serve(settings):
    """
    Serves the generated site from ``deploy_path``

    Respects settings like ``base_url`` if present.
    """
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
