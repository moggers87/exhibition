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

from tempfile import TemporaryDirectory
from unittest import TestCase
import pathlib

from exhibition.main import Node


GOOD_META = """---
thingy: 3
---
Some text
"""

BAD_END_META = """---
thingy: 3

Some text
"""

BAD_START_META = """
---
thingy: 3
---
Some text
"""

NO_META = """
Some text
"""

YAML_FILE = """
thingy: 3
bob:
    - 1
    - 2
"""

JSON_FILE = """
{
    "thingy": 3,
    "bob": [
        1,
        2
    ]
}
"""

BINARY_FILE = (
    b"\x00\x00\x01\x00\x02\x00\x10\x10\x10\x00\x01\x00\x04\x00(\x01\x00\x00&"
    b"\x00\x00\x00  \x10\x00\x01\x00\x04\x00\xe8\x02\x00\x00N\x01\x00\x00("
    b"\x00\x00\x00\x10\x00\x00\x00 \x00\x00\x00\x01\x00\x04\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x01\x00\x00\x08\x0c\n\x00\x16\x18\x17\x00:<;\x00"
    b"@BA\x00TV"
)


class NodeTestCase(TestCase):
    def setUp(self):
        self.content_path = TemporaryDirectory()
        self.deploy_path = TemporaryDirectory()

        self.default_settings = {"content_path": self.content_path.name,
                                 "deploy_path": self.deploy_path.name}

    def tearDown(self):
        self.content_path.cleanup()
        self.deploy_path.cleanup()

    def test_repr(self):
        path = pathlib.Path(self.content_path.name, "page.html")
        path.touch()
        node = Node(path, None, meta=self.default_settings)

        self.assertEqual(repr(node), "<Node: page.html>")

    def test_full_path(self):
        path = pathlib.Path(self.content_path.name, "page.html")
        path.touch()
        node = Node(path, None, meta=self.default_settings)

        self.assertEqual(node.full_path, self.deploy_path.name)

    def test_full_path_with_parent(self):
        parent_path = pathlib.Path(self.content_path.name)
        child_path = pathlib.Path(self.content_path.name, "page.html")
        child_path.touch()

        parent_node = Node(parent_path, None, meta=self.default_settings)
        child_node = Node(child_path, parent_node)

        self.assertEqual(child_node.full_path, self.deploy_path.name + "/page.html")

    def test_full_url(self):
        path = pathlib.Path(self.content_path.name, "page.html")
        path.touch()
        node = Node(path, None, meta=self.default_settings)

        self.assertEqual(node.full_url, "/")

    def test_full_url_with_parent(self):
        parent_path = pathlib.Path(self.content_path.name)
        child_path = pathlib.Path(self.content_path.name, "page.jpg")
        child_path.touch()

        parent_node = Node(parent_path, None, meta=self.default_settings)
        child_node = Node(child_path, parent_node)

        self.assertEqual(child_node.full_url, "/page.jpg")

    def test_full_url_with_strip_ext(self):
        parent_path = pathlib.Path(self.content_path.name)
        child_path = pathlib.Path(self.content_path.name, "page.html")
        child_path.touch()

        parent_node = Node(parent_path, None, meta=self.default_settings)
        child_node = Node(child_path, parent_node)

        self.assertEqual(child_node.full_url, "/page")

    def test_full_url_with_index(self):
        parent_path = pathlib.Path(self.content_path.name)
        child_path = pathlib.Path(self.content_path.name, "index.html")
        child_path.touch()

        parent_node = Node(parent_path, None, meta=self.default_settings)
        child_node = Node(child_path, parent_node)

        self.assertEqual(child_node.full_url, "/")

    def test_walk(self):
        parent_path = pathlib.Path(self.content_path.name)
        child_path = pathlib.Path(self.content_path.name, "index.html")
        child_path.touch()

        parent_node = Node(parent_path, None, meta=self.default_settings)
        child_node = Node(child_path, parent_node)

        self.assertEqual(list(parent_node.walk(include_self=True)), [parent_node, child_node])
        self.assertEqual(list(parent_node.walk()), [child_node])

        self.assertEqual(list(child_node.walk(include_self=True)), [child_node])
        self.assertEqual(list(child_node.walk()), [])

    def test_render_dir(self):
        parent_path = pathlib.Path(self.content_path.name)
        child_path = pathlib.Path(self.content_path.name, "blog")
        child_path.mkdir()

        parent_node = Node(parent_path, None, meta=self.default_settings)
        child_node = Node(child_path, parent_node)

        self.assertFalse(pathlib.Path(child_node.full_path).exists())
        child_node.render()
        self.assertTrue(pathlib.Path(child_node.full_path).exists())
        self.assertTrue(pathlib.Path(child_node.full_path).is_dir())

    def test_render_file(self):
        parent_path = pathlib.Path(self.content_path.name)
        child_path = pathlib.Path(self.content_path.name, "blog")
        child_path.touch()

        parent_node = Node(parent_path, None, meta=self.default_settings)
        child_node = Node(child_path, parent_node)

        self.assertFalse(pathlib.Path(child_node.full_path).exists())
        child_node.render()
        self.assertTrue(pathlib.Path(child_node.full_path).exists())
        self.assertTrue(pathlib.Path(child_node.full_path).is_file())

    def test_render_binary_file(self):
        parent_path = pathlib.Path(self.content_path.name)
        child_path = pathlib.Path(self.content_path.name, "blog")
        with child_path.open("wb") as cf:
            cf.write(BINARY_FILE)

        parent_node = Node(parent_path, None, meta=self.default_settings)
        child_node = Node(child_path, parent_node)

        self.assertFalse(pathlib.Path(child_node.full_path).exists())
        child_node.render()
        self.assertTrue(pathlib.Path(child_node.full_path).exists())
        self.assertTrue(pathlib.Path(child_node.full_path).is_file())

        with pathlib.Path(child_node.full_path).open("rb") as df:
            content = df.read()
            self.assertEqual(content, BINARY_FILE)

    def test_process_good_meta(self):
        path = pathlib.Path(self.content_path.name, "blog")
        with path.open("w") as f:
            f.write(GOOD_META)

        node = Node(path, None)
        self.assertEqual(list(node._meta.keys()), [])
        self.assertEqual(node._content_start, None)

        self.assertEqual(list(node.meta.keys()), ["thingy"])
        self.assertEqual(node._content_start, 18)

    def test_process_bad_start_meta(self):
        path = pathlib.Path(self.content_path.name, "blog")
        with path.open("w") as f:
            f.write(BAD_START_META)

        node = Node(path, None)
        self.assertEqual(list(node._meta.keys()), [])
        self.assertEqual(node._content_start, None)

        self.assertEqual(list(node.meta.keys()), [])
        self.assertEqual(node._content_start, 0)

    def test_process_bad_end__meta(self):
        path = pathlib.Path(self.content_path.name, "blog")
        with path.open("w") as f:
            f.write(BAD_END_META)

        node = Node(path, None)
        self.assertEqual(list(node._meta.keys()), [])
        self.assertEqual(node._content_start, None)

        self.assertEqual(list(node.meta.keys()), [])
        self.assertEqual(node._content_start, 0)

    def test_process_no_meta(self):
        path = pathlib.Path(self.content_path.name, "blog")
        with path.open("w") as f:
            f.write(NO_META)

        node = Node(path, None)
        self.assertEqual(list(node._meta.keys()), [])
        self.assertEqual(node._content_start, None)

        self.assertEqual(list(node.meta.keys()), [])
        self.assertEqual(node._content_start, 0)

    def test_get_content(self):
        path = pathlib.Path(self.content_path.name, "blog")
        with path.open("w") as f:
            f.write("a" * 10)

        node = Node(path, None)
        self.assertEqual(node.get_content(), "a" * 10)
        self.assertEqual(node._content_start, 0)

        node._content = None
        node._content_start = 5
        node.get_content()
        self.assertEqual(node.get_content(), "a" * 5)
        self.assertEqual(node._content_start, 5)

    def test_yaml_data(self):
        path = pathlib.Path(self.content_path.name, "blog.yaml")
        with path.open("w") as f:
            f.write(YAML_FILE)

        node = Node(path, None)

        self.assertEqual(node.data, {"thingy": 3, "bob": [1, 2]})

    def test_json_data(self):
        path = pathlib.Path(self.content_path.name, "blog.json")
        with path.open("w") as f:
            f.write(JSON_FILE)

        node = Node(path, None)

        self.assertEqual(node.data, {"thingy": 3, "bob": [1, 2]})

    def test_dir_data(self):
        path = pathlib.Path(self.content_path.name, "blog.json")
        path.mkdir()

        node = Node(path, None)

        self.assertEqual(node.data, None)

    def test_data_unsupported(self):
        path = pathlib.Path(self.content_path.name, "blog.xml")
        path.touch()

        node = Node(path, None)

        with self.assertRaises(KeyError):
            node.data

    def test_add_child(self):
        parent_path = pathlib.Path(self.content_path.name)
        child_path = pathlib.Path(self.content_path.name, "page.html")

        parent_node = Node(parent_path, None, meta=self.default_settings)
        child_node = Node(child_path, parent_node)

        self.assertEqual(parent_node.children, {"page.html": child_node})

        with self.assertRaises(AssertionError):
            parent_node.add_child(Node(pathlib.Path(self.content_path.name, "page2.html"), None))

    def test_siblings(self):
        parent_path = pathlib.Path(self.content_path.name)
        child1_path = pathlib.Path(self.content_path.name, "page1.html")
        child2_path = pathlib.Path(self.content_path.name, "page2.html")

        parent_node = Node(parent_path, None, meta=self.default_settings)
        child1_node = Node(child1_path, parent_node)
        child2_node = Node(child2_path, parent_node)

        self.assertEqual(child1_node.siblings, {"page2.html": child2_node})
        self.assertEqual(child2_node.siblings, {"page1.html": child1_node})

    def test_from_path(self):
        parent_path = pathlib.Path(self.content_path.name)
        child1_path = pathlib.Path(self.content_path.name, "page1.html")
        child1_path.touch()
        child2_path = pathlib.Path(self.content_path.name, "page2.html")
        child2_path.touch()

        parent_node = Node.from_path(parent_path)
        self.assertCountEqual(list(parent_node.children.keys()), ["page1.html", "page2.html"])

    def test_from_path_and_ignore(self):
        parent_path = pathlib.Path(self.content_path.name)
        child1_path = pathlib.Path(self.content_path.name, "page1.html")
        child1_path.touch()
        child2_path = pathlib.Path(self.content_path.name, "page2.html")
        child2_path.touch()

        parent_node = Node.from_path(parent_path, meta={"ignore": "*.html"})
        self.assertCountEqual(list(parent_node.children.keys()), [])
