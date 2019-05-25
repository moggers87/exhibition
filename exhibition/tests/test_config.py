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

from io import StringIO
from tempfile import NamedTemporaryFile
from unittest import TestCase, mock

from ruamel.yaml import YAML

from exhibition.config import SITE_YAML_PATH, Config

YAML_DATA = """
sitename: bob
thingy:
    - one
    - two
    - three
"""


class ConfigTestCase(TestCase):
    def test_load_str(self):
        settings = Config(YAML_DATA)

        self.assertEqual(len(settings), 2)
        self.assertEqual(settings["sitename"], "bob")
        self.assertEqual(settings["thingy"], ["one", "two", "three"])

    def test_load_file(self):
        yaml_file = StringIO(YAML_DATA)
        settings = Config(yaml_file)

        self.assertEqual(len(settings), 2)
        self.assertEqual(settings["sitename"], "bob")
        self.assertEqual(settings["thingy"], ["one", "two", "three"])

    def test_load_dict(self):
        yaml_dict = dict(YAML(typ="safe").load(YAML_DATA))
        settings = Config(yaml_dict)

        self.assertEqual(len(settings), 2)
        self.assertEqual(settings["sitename"], "bob")
        self.assertEqual(settings["thingy"], ["one", "two", "three"])

    def test_load_AssertionError(self):
        # raise an AssertionError if it's not a dict or file-like object
        with self.assertRaises(AssertionError):
            Config(12)

    def test_no_load(self):
        settings = Config()
        self.assertEqual(len(settings), 0)

    def test_from_path(self):
        with NamedTemporaryFile() as yaml_file:
            yaml_file.write(YAML_DATA.encode())
            yaml_file.file.flush()  # just to be sure

            settings = Config.from_path(yaml_file.name)

            self.assertEqual(len(settings), 2)
            self.assertEqual(settings["sitename"], "bob")
            self.assertEqual(settings["thingy"], ["one", "two", "three"])

    def test_getitem(self):
        settings = Config(YAML_DATA)

        self.assertEqual(settings["sitename"], "bob")
        self.assertEqual(settings["thingy"], ["one", "two", "three"])

        self.assertEqual(settings.get("sitename"), "bob")
        self.assertEqual(settings.get("sitetitle"), None)

        with self.assertRaises(KeyError):
            settings["sitetitle"]

    def test_getitem_with_parent(self):
        parent = Config({"test": True})
        settings = Config(YAML_DATA, parent=parent, node=mock.Mock())

        self.assertEqual(settings["sitename"], "bob")
        self.assertEqual(settings["thingy"], ["one", "two", "three"])
        self.assertEqual(settings["test"], True)

        self.assertEqual(settings.get("sitename"), "bob")
        self.assertEqual(settings.get("test"), True)
        self.assertEqual(settings.get("sitetitle"), None)
        self.assertEqual(parent.get("sitename"), None)

        with self.assertRaises(KeyError):
            settings["sitetitle"]

    def test_setitem(self):
        settings = Config(YAML_DATA)

        settings["sitename"] = "mysite"

        self.assertEqual(settings["sitename"], "mysite")
        self.assertEqual(settings["thingy"], ["one", "two", "three"])

    def test_setitem_with_parent(self):
        parent = Config({"test": True})
        settings = Config(YAML_DATA, parent=parent, node=mock.Mock())

        settings["sitename"] = "mysite"
        settings["test"] = False

        self.assertEqual(settings["sitename"], "mysite")
        self.assertEqual(settings["thingy"], ["one", "two", "three"])
        self.assertEqual(settings["test"], False)
        self.assertEqual(parent["test"], True)

        with self.assertRaises(KeyError):
            parent["sitename"]

    def test_keys(self):
        settings = Config(YAML_DATA)

        self.assertCountEqual(list(settings.keys()), ["sitename", "thingy"])

    def test_keys_with_parent(self):
        parent = Config({"test": True, "sitename": "me"})
        settings = Config(YAML_DATA, parent=parent, node=mock.Mock())

        self.assertCountEqual(list(settings.keys()), ["sitename", "thingy", "test"])
        self.assertCountEqual(list(parent.keys()), ["test", "sitename"])

    def test_iter(self):
        settings = Config(YAML_DATA)

        self.assertCountEqual(list(settings), ["sitename", "thingy"])

    def test_iter_with_parent(self):
        parent = Config({"test": True, "sitename": "me"})
        settings = Config(YAML_DATA, parent=parent, node=mock.Mock())

        self.assertCountEqual(list(settings.keys()), ["sitename", "thingy", "test"])
        self.assertCountEqual(list(parent.keys()), ["test", "sitename"])

    def test_values(self):
        settings = Config(YAML_DATA)

        self.assertCountEqual(list(settings.values()), ["bob", ["one", "two", "three"]])

    def test_values_with_parent(self):
        parent = Config({"test": True})
        settings = Config(YAML_DATA, parent=parent, node=mock.Mock())

        self.assertCountEqual(list(settings.values()), ["bob", ["one", "two", "three"], True])
        self.assertCountEqual(list(parent.values()), [True])

    def test_items(self):
        settings = Config(YAML_DATA)

        self.assertCountEqual(list(settings.items()),
                              [("sitename", "bob"), ("thingy", ["one", "two", "three"])])

    def test_items_with_parent(self):
        parent = Config({"test": True})
        settings = Config(YAML_DATA, parent=parent, node=mock.Mock())

        self.assertCountEqual(list(settings.items()),
                              [("sitename", "bob"), ("thingy", ["one", "two", "three"]),
                               ("test", True)])
        self.assertCountEqual(list(parent.items()), [("test", True)])

    def test_contains(self):
        settings = Config(YAML_DATA)

        self.assertIn("sitename", settings)
        self.assertIn("thingy", settings)
        self.assertNotIn("test", settings)

    def test_contains_with_parent(self):
        parent = Config({"test": True})
        settings = Config(YAML_DATA, parent=parent, node=mock.Mock())

        self.assertIn("test", settings)
        self.assertIn("sitename", settings)
        self.assertIn("thingy", settings)

        self.assertIn("test", parent)
        self.assertNotIn("sitename", parent)
        self.assertNotIn("thingy", parent)

    def test_len(self):
        settings = Config(YAML_DATA)

        self.assertEqual(len(settings), 2)

    def test_len_with_parent(self):
        parent = Config({"test": True})
        settings = Config(YAML_DATA, parent=parent, node=mock.Mock())

        self.assertEqual(len(settings), 3)
        self.assertEqual(len(parent), 1)

    def test_parent_and_node(self):
        with self.assertRaises(AssertionError):
            Config({}, parent=Config({}))

        with self.assertRaises(AssertionError):
            Config({}, node=mock.Mock())

        # these should be fine
        Config({})
        Config({}, parent=Config({}), node=mock.Mock())

    def test_get_name_for_root_config(self):
        config = Config({})
        self.assertEqual(config.get_name(), SITE_YAML_PATH)

    def test_get_name_for_node_config(self):
        node = mock.Mock()
        node.full_path = "this-file.html"
        config = Config({}, parent=mock.Mock(), node=node)
        self.assertEqual(config.get_name(), node.full_path)

    def test_KeyError_contains_name_of_child(self):
        node = mock.Mock()
        node.full_path = "this-file.html"
        config = Config({}, parent=Config({}), node=node)

        with self.assertRaises(KeyError) as exp:
            config["some key"]

        self.assertIn("this-file.html", str(exp.exception))

    def test_KeyError_contains_name_of_site_yaml(self):
        config = Config({})

        with self.assertRaises(KeyError) as exp:
            config["some key"]

        self.assertIn(SITE_YAML_PATH, str(exp.exception))

    def test_copy(self):
        parent = Config({})
        settings = Config(YAML_DATA, parent=parent, node=mock.Mock())
        copied = settings.copy()

        self.assertNotEqual(settings, copied)
        self.assertEqual([i for i in settings.keys()], [i for i in copied.keys()])
        self.assertEqual(settings.parent, copied.parent)

        settings["bob"] = "hello"
        self.assertNotEqual([i for i in settings.keys()], [i for i in copied.keys()])

    def test_repr(self):
        settings = Config({})
        # just a smoke test to make sure it doesn't blow up
        self.assertTrue(isinstance(repr(settings), str))
        self.assertTrue(repr(settings))
