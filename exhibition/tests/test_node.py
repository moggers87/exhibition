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
import hashlib
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

LONG_META = """---
%s
---
Some text
""" % "\n".join(["thing%s: 1" % i for i in range(100)])

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

EMPTY_DIGEST = hashlib.md5().hexdigest()[:8]
BINARY_DIGEST = hashlib.md5(BINARY_FILE).hexdigest()[:8]
JSON_DIGEST = hashlib.md5(JSON_FILE.encode()).hexdigest()[:8]


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

    def test_full_url_base_url(self):
        path = pathlib.Path(self.content_path.name, "page.html")
        path.touch()

        for base in ["/base/", "/base", "base/"]:
            self.default_settings["base_url"] = base
            node = Node(path, None, meta=self.default_settings)
            self.assertEqual(node.full_url, "/base/")

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

    def test_process_long_meta(self):
        path = pathlib.Path(self.content_path.name, "blog")
        with path.open("w") as f:
            f.write(LONG_META)

        node = Node(path, None)
        self.assertEqual(list(node._meta.keys()), [])
        self.assertEqual(node._content_start, None)

        self.assertCountEqual(list(node.meta.keys()), ["thing%s" % i for i in range(100)])
        self.assertEqual(node._content_start, 1098)

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

    def test_cached_data(self):
        path = pathlib.Path(self.content_path.name, "blog.yaml")
        with path.open("w") as f:
            f.write(YAML_FILE)

        node = Node(path, None)

        self.assertEqual(node.data, {"thingy": 3, "bob": [1, 2]})

        with path.open("w") as f:
            f.write("test: 1")

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
        child3_path = pathlib.Path(self.content_path.name, "picture.jpg")
        child3_path.touch()

        parent_node = Node.from_path(parent_path, meta={"ignore": "*.html"})
        self.assertCountEqual(list(parent_node.children.keys()), ["picture.jpg"])

    def test_from_path_and_ignore_list(self):
        parent_path = pathlib.Path(self.content_path.name)
        child1_path = pathlib.Path(self.content_path.name, "page1.html")
        child1_path.touch()
        child2_path = pathlib.Path(self.content_path.name, "page2.html")
        child2_path.touch()
        child3_path = pathlib.Path(self.content_path.name, "picture.jpg")
        child3_path.touch()
        child4_path = pathlib.Path(self.content_path.name, "picture.gif")
        child4_path.touch()

        parent_node = Node.from_path(parent_path, meta={"ignore": ["*.html", "*.gif"]})
        self.assertCountEqual(list(parent_node.children.keys()), ["picture.jpg"])

    def test_from_path_with_meta(self):
        parent_path = pathlib.Path(self.content_path.name)
        child1_path = pathlib.Path(self.content_path.name, "page1.html")
        child1_path.touch()
        child2_path = pathlib.Path(self.content_path.name, "page2.html")
        child2_path.touch()

        meta_path = pathlib.Path(self.content_path.name, "meta.yaml")
        with meta_path.open("w") as f:
            f.write("test: bob")

        parent_node = Node.from_path(parent_path)
        self.assertCountEqual(list(parent_node.children.keys()), ["page1.html", "page2.html"])
        self.assertEqual(parent_node.meta["test"], "bob")

    def test_cache_bust_one_glob(self):
        parent_path = pathlib.Path(self.content_path.name)
        child1_path = pathlib.Path(self.content_path.name, "bust-me.jpg")
        child1_path.touch()
        child2_path = pathlib.Path(self.content_path.name, "page.html")
        child2_path.touch()

        meta_path = pathlib.Path(self.content_path.name, "meta.yaml")
        with meta_path.open("w") as f:
            f.write("cache_bust_glob: \"*.jpg\"")

        parent_node = Node.from_path(parent_path)
        parent_node.meta.update(**self.default_settings)
        self.assertCountEqual(parent_node.children.keys(), ["bust-me.jpg", "page.html"])

        child1_node = parent_node.children["bust-me.jpg"]
        child2_node = parent_node.children["page.html"]

        self.assertEqual(child1_node.full_path,
                         str(pathlib.Path(self.deploy_path.name,
                                          "bust-me.{}.jpg".format(EMPTY_DIGEST))))
        self.assertEqual(child2_node.full_path,
                         str(pathlib.Path(self.deploy_path.name, "page.html")))

        self.assertEqual(child1_node.full_url, "/bust-me.{}.jpg".format(EMPTY_DIGEST))
        self.assertEqual(child2_node.full_url, "/page")

    def test_cache_bust_multi_glob(self):
        parent_path = pathlib.Path(self.content_path.name)
        child1_path = pathlib.Path(self.content_path.name, "bust-me.jpg")
        child1_path.touch()
        child2_path = pathlib.Path(self.content_path.name, "page.html")
        child2_path.touch()

        meta_path = pathlib.Path(self.content_path.name, "meta.yaml")
        with meta_path.open("w") as f:
            f.write("cache_bust_glob:\n  - \"*.jpeg\"\n  - \"*.jpg\"")

        parent_node = Node.from_path(parent_path)
        parent_node.meta.update(**self.default_settings)
        self.assertCountEqual(parent_node.children.keys(), ["bust-me.jpg", "page.html"])

        child1_node = parent_node.children["bust-me.jpg"]
        child2_node = parent_node.children["page.html"]

        self.assertEqual(child1_node.full_path,
                         str(pathlib.Path(self.deploy_path.name,
                                          "bust-me.{}.jpg".format(EMPTY_DIGEST))))
        self.assertEqual(child2_node.full_path,
                         str(pathlib.Path(self.deploy_path.name, "page.html")))

        self.assertEqual(child1_node.full_url, "/bust-me.{}.jpg".format(EMPTY_DIGEST))
        self.assertEqual(child2_node.full_url, "/page")

    def test_cache_bust_binary_file(self):
        parent_path = pathlib.Path(self.content_path.name)
        child_path = pathlib.Path(self.content_path.name, "bust-me.jpg")
        with child_path.open("wb") as f:
            f.write(BINARY_FILE)

        parent_node = Node.from_path(parent_path)
        parent_node.meta.update(**self.default_settings)
        parent_node.meta["cache_bust_glob"] = "*"
        self.assertCountEqual(parent_node.children.keys(), ["bust-me.jpg"])

        child_node = parent_node.children["bust-me.jpg"]

        self.assertEqual(child_node.full_path,
                         str(pathlib.Path(self.deploy_path.name,
                                          "bust-me.{}.jpg".format(BINARY_DIGEST))))

        self.assertEqual(child_node.full_url, "/bust-me.{}.jpg".format(BINARY_DIGEST))

    def test_cache_bust_text_file(self):
        parent_path = pathlib.Path(self.content_path.name)
        child_path = pathlib.Path(self.content_path.name, "bust-me.jpg")
        with child_path.open("w") as f:
            f.write(JSON_FILE)

        parent_node = Node.from_path(parent_path)
        parent_node.meta.update(**self.default_settings)
        parent_node.meta["cache_bust_glob"] = "*"
        self.assertCountEqual(parent_node.children.keys(), ["bust-me.jpg"])

        child_node = parent_node.children["bust-me.jpg"]

        self.assertEqual(child_node.full_path,
                         str(pathlib.Path(self.deploy_path.name,
                                          "bust-me.{}.jpg".format(JSON_DIGEST))))

        self.assertEqual(child_node.full_url, "/bust-me.{}.jpg".format(JSON_DIGEST))

    def test_get_from_path_relative_str_on_leaf(self):
        parent_path = pathlib.Path(self.content_path.name)
        pathlib.Path(self.content_path.name, "images").mkdir()
        child1_path = pathlib.Path(self.content_path.name, "images", "bust-me.jpg")
        child1_path.touch()
        pathlib.Path(self.content_path.name, "pages").mkdir()
        child2_path = pathlib.Path(self.content_path.name, "pages", "page.html")
        child2_path.touch()

        parent_node = Node.from_path(parent_path)

        child_node = parent_node.children["images"].children["bust-me.jpg"]
        target_node = parent_node.children["pages"].children["page.html"]

        self.assertEqual(child_node.get_from_path("../pages/page.html"), target_node)

    def test_get_from_path_relative_pathlib_on_leaf(self):
        parent_path = pathlib.Path(self.content_path.name)
        pathlib.Path(self.content_path.name, "images").mkdir()
        child1_path = pathlib.Path(self.content_path.name, "images", "bust-me.jpg")
        child1_path.touch()
        pathlib.Path(self.content_path.name, "pages").mkdir()
        child2_path = pathlib.Path(self.content_path.name, "pages", "page.html")
        child2_path.touch()

        parent_node = Node.from_path(parent_path)

        child_node = parent_node.children["images"].children["bust-me.jpg"]
        target_node = parent_node.children["pages"].children["page.html"]

        self.assertEqual(child_node.get_from_path(pathlib.Path("..", "pages", "page.html")),
                         target_node)

    def test_get_from_path_relative_str_on_dir(self):
        parent_path = pathlib.Path(self.content_path.name)
        pathlib.Path(self.content_path.name, "images").mkdir()
        child1_path = pathlib.Path(self.content_path.name, "images", "bust-me.jpg")
        child1_path.touch()
        pathlib.Path(self.content_path.name, "pages").mkdir()
        child2_path = pathlib.Path(self.content_path.name, "pages", "page.html")
        child2_path.touch()

        parent_node = Node.from_path(parent_path)

        child_node = parent_node.children["images"]
        target_node = parent_node.children["pages"].children["page.html"]

        self.assertEqual(child_node.get_from_path("../pages/page.html"), target_node)

    def test_get_from_path_relative_pathlib_on_dir(self):
        parent_path = pathlib.Path(self.content_path.name)
        pathlib.Path(self.content_path.name, "images").mkdir()
        child1_path = pathlib.Path(self.content_path.name, "images", "bust-me.jpg")
        child1_path.touch()
        pathlib.Path(self.content_path.name, "pages").mkdir()
        child2_path = pathlib.Path(self.content_path.name, "pages", "page.html")
        child2_path.touch()

        parent_node = Node.from_path(parent_path)

        child_node = parent_node.children["images"]
        target_node = parent_node.children["pages"].children["page.html"]

        self.assertEqual(child_node.get_from_path(pathlib.Path("..", "pages", "page.html")),
                         target_node)

    def test_get_from_path_relative_str_with_dot(self):
        parent_path = pathlib.Path(self.content_path.name)
        pathlib.Path(self.content_path.name, "images").mkdir()
        child1_path = pathlib.Path(self.content_path.name, "images", "bust-me.jpg")
        child1_path.touch()
        pathlib.Path(self.content_path.name, "pages").mkdir()
        child2_path = pathlib.Path(self.content_path.name, "pages", "page.html")
        child2_path.touch()

        parent_node = Node.from_path(parent_path)

        child_node = parent_node.children["pages"]
        target_node = parent_node.children["pages"].children["page.html"]

        self.assertEqual(child_node.get_from_path("./page.html"), target_node)

    def test_get_from_path_relative_pathlib_with_dot(self):
        parent_path = pathlib.Path(self.content_path.name)
        pathlib.Path(self.content_path.name, "images").mkdir()
        child1_path = pathlib.Path(self.content_path.name, "images", "bust-me.jpg")
        child1_path.touch()
        pathlib.Path(self.content_path.name, "pages").mkdir()
        child2_path = pathlib.Path(self.content_path.name, "pages", "page.html")
        child2_path.touch()

        parent_node = Node.from_path(parent_path)

        child_node = parent_node.children["pages"]
        target_node = parent_node.children["pages"].children["page.html"]

        self.assertEqual(child_node.get_from_path(pathlib.Path(".", "page.html")),
                         target_node)

    def test_get_from_path_absolute_str(self):
        parent_path = pathlib.Path(self.content_path.name)
        pathlib.Path(self.content_path.name, "images").mkdir()
        child1_path = pathlib.Path(self.content_path.name, "images", "bust-me.jpg")
        child1_path.touch()
        pathlib.Path(self.content_path.name, "pages").mkdir()
        child2_path = pathlib.Path(self.content_path.name, "pages", "page.html")
        child2_path.touch()

        parent_node = Node.from_path(parent_path)

        child_node = parent_node.children["images"].children["bust-me.jpg"]
        target_node = parent_node.children["pages"].children["page.html"]

        self.assertEqual(child_node.get_from_path("/pages/page.html"), target_node)

    def test_get_from_path_absolute_pathlib(self):
        parent_path = pathlib.Path(self.content_path.name)
        pathlib.Path(self.content_path.name, "images").mkdir()
        child1_path = pathlib.Path(self.content_path.name, "images", "bust-me.jpg")
        child1_path.touch()
        pathlib.Path(self.content_path.name, "pages").mkdir()
        child2_path = pathlib.Path(self.content_path.name, "pages", "page.html")
        child2_path.touch()

        parent_node = Node.from_path(parent_path)

        child_node = parent_node.children["images"].children["bust-me.jpg"]
        target_node = parent_node.children["pages"].children["page.html"]

        self.assertEqual(child_node.get_from_path(pathlib.Path("/pages/page.html")), target_node)

    def test_get_from_path_not_existing_from_str(self):
        parent_path = pathlib.Path(self.content_path.name)
        pathlib.Path(self.content_path.name, "images").mkdir()
        child1_path = pathlib.Path(self.content_path.name, "images", "bust-me.jpg")
        child1_path.touch()
        pathlib.Path(self.content_path.name, "pages").mkdir()
        child2_path = pathlib.Path(self.content_path.name, "pages", "page.html")
        child2_path.touch()

        parent_node = Node.from_path(parent_path)

        child_node = parent_node.children["images"].children["bust-me.jpg"]

        with self.assertRaises(OSError):
            child_node.get_from_path("../not-a-page.html")

    def test_get_from_path_not_existing_from_pathlib(self):
        parent_path = pathlib.Path(self.content_path.name)
        pathlib.Path(self.content_path.name, "images").mkdir()
        child1_path = pathlib.Path(self.content_path.name, "images", "bust-me.jpg")
        child1_path.touch()
        pathlib.Path(self.content_path.name, "pages").mkdir()
        child2_path = pathlib.Path(self.content_path.name, "pages", "page.html")
        child2_path.touch()

        parent_node = Node.from_path(parent_path)

        child_node = parent_node.children["images"].children["bust-me.jpg"]

        with self.assertRaises(OSError):
            child_node.get_from_path(pathlib.Path("..", "not-a-page.html"))

    def test_root_node_is_kept(self):
        parent_path = pathlib.Path(self.content_path.name)
        pathlib.Path(self.content_path.name, "images").mkdir()
        pathlib.Path(self.content_path.name, "pages").mkdir()
        child_path = pathlib.Path(self.content_path.name, "pages", "page.html")
        child_path.touch()

        parent_node = Node.from_path(parent_path)

        self.assertEqual(parent_node.root_node, parent_node)
        self.assertEqual(parent_node.children["pages"].root_node, parent_node)
        self.assertEqual(parent_node.children["pages"].children["page.html"].root_node, parent_node)
        self.assertEqual(parent_node.children["pages"].children["page.html"].parent.root_node,
                         parent_node)
        self.assertEqual(
            parent_node.children["pages"].children["page.html"].parent.parent.root_node,
            parent_node
        )
        self.assertEqual(
            parent_node.children["pages"].children["page.html"].parent.parent.root_node,
            parent_node
        )
