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

from stat import S_IFDIR, S_IFREG
from tempfile import TemporaryDirectory
from unittest import TestCase
import hashlib
import pathlib

from ruamel.yaml.error import MarkedYAMLError

from exhibition.node import DEFAULT_DIR_MODE, DEFAULT_FILE_MODE, Node

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

INVALID_YAML = """
make: an
wish: [it's
3: am
""".strip()

INVALID_YAML_META = """---
%s
---
Some text
""" % INVALID_YAML

YAML_FILE = """
thingy: 3
bob:
    - 1
    - 2
"""

YAML_WITH_IGNORE = """
ignore: "*"
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
        rendered_child = pathlib.Path(child_node.full_path)
        self.assertTrue(rendered_child.exists())
        self.assertTrue(rendered_child.is_dir())
        self.assertEqual(rendered_child.stat().st_mode, S_IFDIR + DEFAULT_DIR_MODE)

    def test_render_file(self):
        parent_path = pathlib.Path(self.content_path.name)
        child_path = pathlib.Path(self.content_path.name, "blog")
        child_path.touch()

        parent_node = Node(parent_path, None, meta=self.default_settings)
        child_node = Node(child_path, parent_node)

        self.assertFalse(pathlib.Path(child_node.full_path).exists())
        child_node.render()
        rendered_child = pathlib.Path(child_node.full_path)
        self.assertTrue(rendered_child.exists())
        self.assertTrue(rendered_child.is_file())
        self.assertEqual(rendered_child.stat().st_mode, S_IFREG + DEFAULT_FILE_MODE)

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
        self.assertEqual(list(node.meta.keys()), ["thingy"])
        self.assertEqual(node.content, GOOD_META[18:])

    def test_process_long_meta(self):
        path = pathlib.Path(self.content_path.name, "blog")
        with path.open("w") as f:
            f.write(LONG_META)

        node = Node(path, None)
        self.assertCountEqual(list(node.meta.keys()), ["thing%s" % i for i in range(100)])
        self.assertEqual(node.content, LONG_META[1098:])

    def test_process_bad_start_meta(self):
        path = pathlib.Path(self.content_path.name, "blog")
        with path.open("w") as f:
            f.write(BAD_START_META)

        node = Node(path, None)
        self.assertEqual(list(node.meta.keys()), [])
        self.assertEqual(node.content, BAD_START_META)

    def test_process_bad_end__meta(self):
        path = pathlib.Path(self.content_path.name, "blog")
        with path.open("w") as f:
            f.write(BAD_END_META)

        node = Node(path, None)
        self.assertEqual(list(node.meta.keys()), [])
        self.assertEqual(node.content, BAD_END_META)

    def test_process_no_meta(self):
        path = pathlib.Path(self.content_path.name, "blog")
        with path.open("w") as f:
            f.write(NO_META)

        node = Node(path, None)
        self.assertEqual(list(node.meta.keys()), [])
        self.assertEqual(node.content, NO_META)

    def test_get_content(self):
        path = pathlib.Path(self.content_path.name, "blog")
        with path.open("w") as f:
            f.write("a" * 10)

        node = Node(path, None)
        self.assertEqual(node.content, "a" * 10)

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
        self.assertEqual(list(parent_node.children.keys()), ["page1.html", "page2.html"])

    def test_from_path_and_ignore(self):
        parent_path = pathlib.Path(self.content_path.name)
        child1_path = pathlib.Path(self.content_path.name, "page1.html")
        child1_path.touch()
        child2_path = pathlib.Path(self.content_path.name, "page2.html")
        child2_path.touch()
        child3_path = pathlib.Path(self.content_path.name, "picture.jpg")
        child3_path.touch()

        parent_node = Node.from_path(parent_path, meta={"ignore": "*.html"})
        self.assertEqual(list(parent_node.children.keys()), ["picture.jpg"])

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
        self.assertEqual(list(parent_node.children.keys()), ["picture.jpg"])

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
        self.assertEqual(list(parent_node.children.keys()), ["page1.html", "page2.html"])
        self.assertEqual(parent_node.meta["test"], "bob")

    def test_from_path_meta_comes_first(self):
        parent_path = pathlib.Path(self.content_path.name)

        # not sure if default ordering for files is by creation time or by
        # name, so let's write one file here, and another after the meta.yaml
        child1_path = pathlib.Path(self.content_path.name, "1page.html")
        child1_path.touch()

        path = pathlib.Path(self.content_path.name, "meta.yaml")
        with path.open("w") as f:
            f.write(YAML_WITH_IGNORE)

        child2_path = pathlib.Path(self.content_path.name, "page2.html")
        child2_path.touch()

        parent_node = Node.from_path(parent_path, meta={})
        self.assertEqual(list(parent_node.children.keys()), [])

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
        self.assertEqual(list(parent_node.children.keys()), ["bust-me.jpg", "page.html"])

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
        self.assertEqual(list(parent_node.children.keys()), ["bust-me.jpg", "page.html"])

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
        self.assertEqual(list(parent_node.children.keys()), ["bust-me.jpg"])

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
        self.assertEqual(list(parent_node.children.keys()), ["bust-me.jpg"])

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

    def test_strip_exts_default(self):
        parent_path = pathlib.Path(self.content_path.name)
        child_path = pathlib.Path(self.content_path.name, "blog.html")
        child_path.touch()

        parent_node = Node(parent_path, None, meta=self.default_settings)
        child_node = Node(child_path, parent_node)

        self.assertEqual(child_node.strip_exts, [".html"])
        self.assertEqual(child_node.full_url, "/blog")

    def test_strip_exts_custom(self):
        parent_path = pathlib.Path(self.content_path.name)
        child_path = pathlib.Path(self.content_path.name, "blog.tw2")
        child_path.touch()

        settings = {"strip_exts": [".tw2"]}
        settings.update(self.default_settings)
        parent_node = Node(parent_path, None, meta=settings)
        child_node = Node(child_path, parent_node)

        self.assertEqual(child_node.strip_exts, [".tw2"])
        self.assertEqual(child_node.full_url, "/blog")

    def test_strip_exts_multiple(self):
        parent_path = pathlib.Path(self.content_path.name)
        child1_path = pathlib.Path(self.content_path.name, "blog.bluh")
        child1_path.touch()
        child2_path = pathlib.Path(self.content_path.name, "story.tw2")
        child2_path.touch()

        settings = {"strip_exts": [".tw2", ".bluh"]}
        settings.update(self.default_settings)
        parent_node = Node(parent_path, None, meta=settings)
        child1_node = Node(child1_path, parent_node)
        child2_node = Node(child2_path, parent_node)

        self.assertEqual(child1_node.strip_exts, [".tw2", ".bluh"])
        self.assertEqual(child1_node.full_url, "/blog")

        self.assertEqual(child2_node.strip_exts, [".tw2", ".bluh"])
        self.assertEqual(child2_node.full_url, "/story")

    def test_strip_exts_not_a_list(self):
        parent_path = pathlib.Path(self.content_path.name)
        child_path = pathlib.Path(self.content_path.name, "blog.html")
        child_path.touch()

        settings = {"strip_exts": ".html"}
        settings.update(self.default_settings)
        parent_node = Node(parent_path, None, meta=settings)
        child_node = Node(child_path, parent_node)

        self.assertEqual(child_node.strip_exts, [".html"])
        self.assertEqual(child_node.full_url, "/blog")

    def test_strip_exts_disabled(self):
        parent_path = pathlib.Path(self.content_path.name)
        child_path = pathlib.Path(self.content_path.name, "blog.html")
        child_path.touch()

        settings = {"strip_exts": []}
        settings.update(self.default_settings)
        parent_node = Node(parent_path, None, meta=settings)
        child_node = Node(child_path, parent_node)

        self.assertEqual(child_node.strip_exts, [])
        self.assertEqual(child_node.full_url, "/blog.html")

    def test_index_file_default(self):
        parent_path = pathlib.Path(self.content_path.name)
        child1_path = pathlib.Path(self.content_path.name, "index.html")
        child1_path.touch()
        child2_path = pathlib.Path(self.content_path.name, "blog.html")
        child2_path.touch()

        parent_node = Node(parent_path, None, meta=self.default_settings)
        child1_node = Node(child1_path, parent_node)
        child2_node = Node(child2_path, parent_node)

        self.assertEqual(child1_node.index_file, "index.html")
        self.assertEqual(child1_node.full_url, "/")
        self.assertEqual(child2_node.index_file, "index.html")
        self.assertEqual(child2_node.full_url, "/blog")

    def test_index_file_custom(self):
        parent_path = pathlib.Path(self.content_path.name)
        child1_path = pathlib.Path(self.content_path.name, "index.html")
        child1_path.touch()
        child2_path = pathlib.Path(self.content_path.name, "blog.html")
        child2_path.touch()

        settings = {"index_file": "blog.html"}
        settings.update(self.default_settings)
        parent_node = Node(parent_path, None, meta=settings)
        child1_node = Node(child1_path, parent_node)
        child2_node = Node(child2_path, parent_node)

        self.assertEqual(child1_node.index_file, "blog.html")
        self.assertEqual(child1_node.full_url, "/index")
        self.assertEqual(child2_node.index_file, "blog.html")
        self.assertEqual(child2_node.full_url, "/")

    def test_invalid_yaml(self):
        path_meta = pathlib.Path(self.content_path.name, "meta.yaml")
        with path_meta.open("w") as f:
            f.write(INVALID_YAML)
        path = pathlib.Path(self.content_path.name, "index.html")
        with path.open("w") as f:
            f.write(GOOD_META)

        with self.assertRaises(MarkedYAMLError) as context:
            Node.from_path(pathlib.Path(self.content_path.name))
        self.assertEqual(context.exception.context_mark.line, 1)
        self.assertEqual(context.exception.context_mark.column, 6)
        self.assertEqual(context.exception.context_mark.name, str(path_meta))
        self.assertEqual(context.exception.problem_mark.line, 2)
        self.assertEqual(context.exception.problem_mark.column, 1)
        self.assertEqual(context.exception.problem_mark.name, str(path_meta))

    def test_invalid_yaml_meta(self):
        path = pathlib.Path(self.content_path.name, "blog")
        with path.open("w") as f:
            f.write(INVALID_YAML_META)

        node = Node(path, None)
        with self.assertRaises(MarkedYAMLError) as context:
            node.meta.keys()
        self.assertEqual(context.exception.context_mark.line, 2)
        self.assertEqual(context.exception.context_mark.column, 6)
        self.assertEqual(context.exception.context_mark.name, str(path))
        self.assertEqual(context.exception.problem_mark.line, 3)
        self.assertEqual(context.exception.problem_mark.column, 1)
        self.assertEqual(context.exception.problem_mark.name, str(path))

    def test_dir_mode(self):
        settings = {
            "dir_mode": 0o765,
            "file_mode": 0o764,
        }
        settings.update(self.default_settings)
        parent_path = pathlib.Path(self.content_path.name)
        child_path = pathlib.Path(self.content_path.name, "blog")
        child_path.mkdir()

        parent_node = Node(parent_path, None, meta=settings)
        child_node = Node(child_path, parent_node)

        self.assertFalse(pathlib.Path(child_node.full_path).exists())
        child_node.render()
        rendered_child = pathlib.Path(child_node.full_path)
        self.assertTrue(rendered_child.exists())
        self.assertTrue(rendered_child.is_dir())
        self.assertEqual(rendered_child.stat().st_mode, S_IFDIR + settings["dir_mode"])

    def test_mode_file(self):
        settings = {
            "dir_mode": 0o765,
            "file_mode": 0o764,
        }
        settings.update(self.default_settings)
        parent_path = pathlib.Path(self.content_path.name)
        child_path = pathlib.Path(self.content_path.name, "blog")
        child_path.touch()

        parent_node = Node(parent_path, None, meta=settings)
        child_node = Node(child_path, parent_node)

        self.assertFalse(pathlib.Path(child_node.full_path).exists())
        child_node.render()
        rendered_child = pathlib.Path(child_node.full_path)
        self.assertTrue(rendered_child.exists())
        self.assertTrue(rendered_child.is_file())
        self.assertEqual(rendered_child.stat().st_mode, S_IFREG + settings["file_mode"])
