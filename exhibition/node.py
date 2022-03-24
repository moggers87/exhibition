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

from collections import OrderedDict
from functools import cached_property
from importlib import import_module
import hashlib
import pathlib

from ruamel.yaml import YAML
from ruamel.yaml.error import FileMark, MarkedYAMLError

from .config import Config

yaml_parser = YAML(typ="safe")

DATA_EXTRACTORS = {
    ".yaml": yaml_parser.load,
    ".json": yaml_parser.load,
}

DEFAULT_STRIP_EXTS = [".html"]
DEFAULT_INDEX_FILE = "index.html"
DEFAULT_DIR_MODE = 0o755
DEFAULT_FILE_MODE = 0o644


class FrontMatterNotFound(Exception):
    pass


class Node:
    """
    A node represents a file or directory
    """
    _meta_names = ["meta.yaml", "meta.yml"]

    _meta_header = "---\n"
    _meta_footer = "---\n"

    def __init__(self, path, parent, meta=None):
        """
        :param path:
            A :class:`pathlib.Path` that is either the ``content_path`` or a
            child of it.
        :param parent:
            Either another :class:`Node` or ``None``
        :param meta:
            A dict-like object that will be passed to a :class:`Config`
            instance
        """
        self.path_obj = path
        self.parent = parent
        self.children = OrderedDict()

        self.is_leaf = self.path_obj.is_file()

        try:
            parent_meta = self.parent.meta
        except AttributeError:
            parent_meta = None

        self.__meta = Config({}, parent=parent_meta, node=self.parent)
        if meta:
            self.__meta.update(meta)

        if self.parent:
            self.parent.add_child(self)
            self.root_node = self.parent.root_node
        else:
            self.root_node = self

    @classmethod
    def from_path(cls, path, parent=None, meta=None):
        """
        Given a :class:`pathlib.Path`, create a Node from that path as well as
        any children. Children are loaded in Unicode codepoint order - this
        order is preserved in ``Node.children`` if you're unsure what that
        means.

        If the path is not a file or a dir, an :class:`AssertionError` is
        raised

        :param path:
            A :class:`pathlib.Path` that is either the ``content_path`` or a
            child of it.
        :param parent:
            Either another :class:`Node` or ``None``
        :param meta:
            A dict-like object that will be passed to a :class:`Config`
            instance
        """
        # path should be a pathlib object
        assert path.is_file() or path.is_dir()

        node = cls(path, parent=parent, meta=meta)

        if path.is_dir():
            children = []

            dir_files = sorted(path.iterdir(), key=lambda p: p.name)
            for child in dir_files:
                if child.name in cls._meta_names and child.is_file():
                    with child.open() as co:
                        node.meta.load(co)
                else:
                    children.append(child)

            for child in children:
                ignored = False
                globs = node.meta.get("ignore", [])

                if not isinstance(globs, (list, tuple)):
                    globs = [globs]

                for glob in globs:
                    if child in path.glob(glob):
                        ignored = True
                        break
                if not ignored:
                    cls.from_path(child, node)

        return node

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.path_obj.name)

    def get_from_path(self, path):
        """
        Given a relative or absolute path, return the :class:`Node` that
        represents that path.

        :param path:
            A :class:`str` or :class:`pathlib.Path`
        """
        if not isinstance(path, pathlib.PurePath):
            path = pathlib.PurePath(path)

        if path.is_absolute():
            found_node = self.root_node
            parts = path.parts[1:]
        else:
            if self.is_leaf:
                found_node = self.parent
            else:
                found_node = self
            parts = path.parts

        try:
            for part in parts:
                if part == "..":
                    found_node = found_node.parent
                else:
                    found_node = found_node.children[part]
        except KeyError as exp:
            raise OSError("{} could not find {}".format(self, exp.args)) from exp

        return found_node

    @property
    def full_path(self):
        """
        Full path of node when deployed
        """
        if self.parent is None:
            return self.meta["deploy_path"]
        else:
            if self.cache_bust:
                suffixes = "".join(self.path_obj.suffixes)
                pth = self.path_obj.with_suffix(".{}{}".format(self.cache_bust, suffixes))
                name = pth.name
            else:
                name = self.path_obj.name
            return str(pathlib.Path(self.parent.full_path, name))

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
            if self.path_obj.name == self.index_file:
                name = ""
            elif self.path_obj.suffix in self.strip_exts:
                name = self.path_obj.stem
            elif self.cache_bust:
                suffixes = "".join(self.path_obj.suffixes)
                pth = self.path_obj.with_suffix(".{}{}".format(self.cache_bust, suffixes))
                name = pth.name
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
        Process node and either create the directory or write contents of file
        to ``deploy_path``
        """
        if not self.is_leaf:
            dir_mode = self.meta.get("dir_mode", DEFAULT_DIR_MODE)
            dir_obj = pathlib.Path(self.full_path)
            dir_obj.mkdir()
            dir_obj.chmod(dir_mode)
            return

        file_mode = self.meta.get("file_mode", DEFAULT_FILE_MODE)
        file_obj = pathlib.Path(self.full_path)

        with file_obj.open("w" if type(self.content) is str else "wb") as fo:
            fo.write(self.content)
        file_obj.chmod(file_mode)

    @cached_property
    def content(self):
        """
        Get the actual content of the Node

        If ``filter`` has been specified in :attr:`meta`, that filter will be
        used to further process the content.
        """
        self.meta  # fetch meta and set __content_start
        with self.path_obj.open("rb") as file_obj:
            file_obj.seek(self.__content_start)
            content = file_obj.read()
        try:
            content = content.decode("utf-8")
        except UnicodeDecodeError:
            return content
        for fltr, globs in self.content_filters():
            for filter_glob in globs:
                if self.path_obj in self.path_obj.parent.glob(filter_glob):
                    content = fltr(self, content)
                    break
        return content

    def content_filters(self):
        """Yields tuples in the form (filter_funct, glob pattern)"""
        content_filter = self.meta.get("filter")
        if content_filter is None:
            content_filter = []
        elif not isinstance(content_filter, (list, tuple)):
            content_filter = [(content_filter, self.meta.get("filter_glob", None))]

        for item in content_filter:
            if isinstance(item, (list, tuple)):
                fltr, globs = item
            else:
                fltr = item
                globs = None
            filter_module = import_module(fltr)
            if globs is None:
                globs = filter_module.DEFAULT_GLOB
            if not isinstance(globs, (list, tuple)):
                globs = [globs]
            yield (filter_module.content_filter, globs)

    def __read_frontmatter(self):
        found_header = False
        with self.path_obj.open("rb") as file_obj:
            while True:
                data = file_obj.read(100)
                try:
                    data = data.decode("utf-8")
                except UnicodeDecodeError:
                    raise FrontMatterNotFound

                if data == '':
                    # we've run out of file, either we didn't find a header or
                    # we're missing a footer
                    raise FrontMatterNotFound
                elif not found_header:
                    if data.startswith(self._meta_header):
                        found_header = True
                        found_meta = data[len(self._meta_header):]
                    else:
                        # if our token is not the first thing in the file, then
                        # it's not for us
                        raise FrontMatterNotFound
                else:
                    found_meta += data

                if self._meta_footer in found_meta:
                    idx = found_meta.index(self._meta_footer)
                    found_meta = found_meta[:idx]
                    break
        return found_meta

    @cached_property
    def meta(self):
        """
        Configuration object

        Finds and processes the YAML front matter at the top of a file

        If the file does not start with ``---\\n``, then it's assumed the file
        does not contain any meta YAML for us to process
        """
        self.__content_start = 0
        if not self.is_leaf:
            return self.__meta

        try:
            frontmatter = self.__read_frontmatter()
        except FrontMatterNotFound:
            return self.__meta

        try:
            self.__meta.load(frontmatter)
        except MarkedYAMLError as exp:
            exp.context_mark = FileMark(
                name=str(self.path_obj),
                index=exp.context_mark.index + len(self._meta_header),
                line=exp.context_mark.line + 1,
                column=exp.context_mark.column,
            )
            exp.problem_mark = FileMark(
                name=str(self.path_obj),
                index=exp.problem_mark.index + len(self._meta_header),
                line=exp.problem_mark.line + 1,
                column=exp.problem_mark.column,
            )
            raise exp

        self.__content_start = len(self._meta_header) + len(frontmatter) + len(self._meta_footer)

        return self.__meta

    @property
    def marks(self):
        """
        Marked sections from content
        """
        if not hasattr(self, "_marks"):
            self._marks = {}
            # make sure that _marks gets populated
            self.content

        return self._marks

    @cached_property
    def data(self):
        """Extracts data from contents of file

        For example, a YAML file
        """
        if self.path_obj.is_dir():
            return

        func = DATA_EXTRACTORS[self.path_obj.suffix]
        data = func(self.content)

        return data

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

    @cached_property
    def cache_bust(self):
        cache_bust_version = None
        globs = self.meta.get("cache_bust_glob", [])
        if not isinstance(globs, (list, tuple)):
            globs = [globs]
        for cache_bust_glob in globs:
            if self.path_obj in self.path_obj.parent.glob(cache_bust_glob):
                hasher = hashlib.md5()
                content = self.content
                if isinstance(content, str):
                    # content needs to be bytes just for this bit
                    content = content.encode("utf-8")
                hasher.update(content)

                cache_bust_version = hasher.hexdigest()[:8]
                break

        return cache_bust_version

    @property
    def strip_exts(self):
        strip_exts = self.meta.get("strip_exts", DEFAULT_STRIP_EXTS)
        if not isinstance(strip_exts, (list, tuple)):
            strip_exts = [strip_exts]

        return strip_exts

    @property
    def index_file(self):
        index_file = self.meta.get("index_file", DEFAULT_INDEX_FILE)

        return index_file
