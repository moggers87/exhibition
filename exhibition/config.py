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

import io

from ruamel.yaml import YAML

SITE_YAML_PATH = "site.yaml"

yaml_parser = YAML(typ="safe")


class Config:
    """
    Configuration object that implements a dict-like interface

    If a key cannot be found in this instance, the parent :class:`Config` will
    be searched (and its parent, etc.)
    """
    def __init__(self, data=None, parent=None, node=None):
        """
        :param data:
            Can be one of a string, a file-like object, a dict-like object, or
            ``None``. The first two will be assumed as YAML
        :param parent:
            Parent :class:`Config` or ``None`` if this is the root
            configuration object
        :param node:
            The node that this object to bound to, or ``None`` if it is the
            root configuration object
        """
        assert (parent is None) == (node is None), \
            "Either both parent and node are defined or they are both None"

        self.parent = parent
        self.node = node
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

    def get_name(self):
        if self.node is None:
            return SITE_YAML_PATH
        else:
            return self.node.full_path

    def __getitem__(self, key):
        try:
            return self._base_config[key]
        except KeyError as exp:
            exp_str = "Could not find %s in %s" % (key, self.get_name())
            if self.parent is None:
                raise KeyError(exp_str) from exp
            else:
                try:
                    return self.parent[key]
                except KeyError as exp_parent:
                    raise KeyError(exp_str) from exp_parent

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
        return klass(self._base_config.copy(), parent=self.parent, node=self.node)

    def __repr__(self):
        return "<%s: %s: %s>" % (self.__class__.__name__,
                                 self.get_name(),
                                 self._base_config.keys())
