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
from unittest import TestCase

from ruamel.yaml import YAML

from exhibition.main import Config


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
        settings = Config(YAML_DATA, parent=parent)

        self.assertEqual(settings["sitename"], "bob")
        self.assertEqual(settings["thingy"], ["one", "two", "three"])
        self.assertEqual(settings["test"], True)

        self.assertEqual(settings.get("sitename"), "bob")
        self.assertEqual(settings.get("test"), True)
        self.assertEqual(settings.get("sitetitle"), None)
        self.assertEqual(parent.get("sitename"), None)

        with self.assertRaises(KeyError):
            settings["sitetitle"]

    def test_keys(self):
        settings = Config(YAML_DATA)

        self.assertCountEqual(list(settings.keys()), ["sitename", "thingy"])

    def test_keys_with_parent(self):
        parent = Config({"test": True})
        settings = Config(YAML_DATA, parent=parent)

        self.assertCountEqual(list(settings.keys()), ["sitename", "thingy", "test"])
        self.assertCountEqual(list(parent.keys()), ["test"])

    def test_values(self):
        settings = Config(YAML_DATA)

        self.assertCountEqual(list(settings.values()), ["bob", ["one", "two", "three"]])

    def test_values_with_parent(self):
        parent = Config({"test": True})
        settings = Config(YAML_DATA, parent=parent)

        self.assertCountEqual(list(settings.values()), ["bob", ["one", "two", "three"], True])
        self.assertCountEqual(list(parent.values()), [True])

    def test_items(self):
        settings = Config(YAML_DATA)

        self.assertCountEqual(list(settings.items()),
                              [("sitename", "bob"), ("thingy", ["one", "two", "three"])])

    def test_items_with_parent(self):
        parent = Config({"test": True})
        settings = Config(YAML_DATA, parent=parent)

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
        settings = Config(YAML_DATA, parent=parent)

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
        settings = Config(YAML_DATA, parent=parent)

        self.assertEqual(len(settings), 3)
        self.assertEqual(len(parent), 1)
