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
from unittest import TestCase, mock
import pathlib

from jinja2.exceptions import TemplateRuntimeError
from jinja2 import Markup

from exhibition.filters.jinja2 import content_filter as jinja_filter
from exhibition.main import Node


PLAIN_TEMPLATE = """
{% for i in range(3) -%}
    <p>{{ i }}</p>
{%- endfor %}
""".strip()

CONTENT_BLOCK = "".join(["{% block content %}", PLAIN_TEMPLATE, "{% endblock %}"])

BASE_TEMPLATE = """
<p>Title</p>
{% block content %}{% endblock %}
""".strip()

ERROR_TEMPLATE = """
{% raise "This is an error" %}
""".strip()

MARK_TEMPLATE = """
{% mark thingy %}
Hello
{% endmark %}
Bye
""".strip()

MD_TEMPLATE = """
{% filter markdown %}
## Hello

This is *text*
{% endfilter %}
""".strip()

TYPOG_TEMPLATE = """
{% filter typogrify %}
Hello -- how are you?
{% endfilter %}
""".strip()

METASORT_TEMPLATE = """
{% for child in node.children.values()|metasort("bob") -%}
{{ child.meta.bob }}
{%- endfor %}
""".strip()

METASELECT_TEMPLATE = """
{% for child in node.children.values()|metaselect("bob") -%}
{{ child.meta.bob }}
{%- endfor %}
""".strip()

METAREJECT_TEMPLATE = """
{% for child in node.children.values()|metareject("bob") -%}
{{ child.meta.bob }}
{%- endfor %}
""".strip()


class Jinja2TestCase(TestCase):
    def test_template(self):
        node = Node(mock.Mock(), None, meta={"templates": []})
        node.is_leaf = False
        result = jinja_filter(node, PLAIN_TEMPLATE)
        self.assertEqual(result, "<p>0</p><p>1</p><p>2</p>")

    def test_extends(self):
        template_name = "bob.j2"
        with TemporaryDirectory() as tmp_dir:
            with pathlib.Path(tmp_dir, template_name).open("w") as tmpl:
                tmpl.write(BASE_TEMPLATE)

            node = Node(mock.Mock(), None, meta={"templates": [tmp_dir], "extends": "bob.j2"})
            node.is_leaf = False
            result = jinja_filter(node, CONTENT_BLOCK)
            self.assertEqual(result, "<p>Title</p>\n<p>0</p><p>1</p><p>2</p>")

    def test_extends_with_multiple_template_dirs(self):
        template_name = "bob.j2"
        with TemporaryDirectory() as tmp1_dir, TemporaryDirectory() as tmp2_dir:
            with pathlib.Path(tmp1_dir, template_name).open("w") as tmpl:
                tmpl.write(BASE_TEMPLATE)

            with pathlib.Path(tmp2_dir, template_name).open("w") as tmpl:
                tmpl.write("empty")

            node = Node(mock.Mock(), None,
                        meta={"templates": [tmp1_dir, tmp2_dir], "extends": "bob.j2"})
            node.is_leaf = False
            result = jinja_filter(node, CONTENT_BLOCK)
            self.assertEqual(result, "<p>Title</p>\n<p>0</p><p>1</p><p>2</p>")

            # switch order of template dirs,
            node = Node(mock.Mock(), None,
                        meta={"templates": [tmp2_dir, tmp1_dir], "extends": "bob.j2"})
            node.is_leaf = False
            result = jinja_filter(node, CONTENT_BLOCK)
            self.assertEqual(result, "empty")

    def test_default_block(self):
        template_name = "bob.j2"
        with TemporaryDirectory() as tmp_dir:
            with pathlib.Path(tmp_dir, template_name).open("w") as tmpl:
                tmpl.write(BASE_TEMPLATE)

            node = Node(mock.Mock(), None, meta={"templates": [tmp_dir], "extends": "bob.j2"})
            node.is_leaf = False
            result = jinja_filter(node, PLAIN_TEMPLATE)
            self.assertEqual(result, "<p>Title</p>\n")

            node = Node(mock.Mock(), None, meta={"templates": [tmp_dir],
                                                 "extends": "bob.j2", "default-block": "content"})
            node.is_leaf = False
            result = jinja_filter(node, PLAIN_TEMPLATE)
            self.assertEqual(result, "<p>Title</p>\n\n<p>0</p><p>1</p><p>2</p>")

    def test_context(self):
        path = mock.Mock()
        path.name = "thisfile.html"
        node = Node(path, None, meta={"templates": []})
        node.is_leaf = False
        result = jinja_filter(node, "{{ node }}")
        self.assertEqual(result, "&lt;Node: thisfile.html&gt;")

        result = jinja_filter(node, "{{ undef_value }}")
        self.assertEqual(result, "")

    def test_raise_extension(self):
        node = Node(mock.Mock(), None, meta={"templates": []})
        node.is_leaf = False
        with self.assertRaises(TemplateRuntimeError) as excp:
            jinja_filter(node, ERROR_TEMPLATE)

        self.assertEqual(excp.exception.message, "This is an error")

    def test_mark_extension(self):
        with TemporaryDirectory() as content_path, TemporaryDirectory() as deploy_path:
            path = pathlib.Path(content_path, "blog.html")
            with path.open("w") as f:
                f.write(MARK_TEMPLATE)

            node = Node(path, Node(path.parent, None, {"content_path": content_path,
                                                       "deploy_path": deploy_path,
                                                       "filter": "exhibition.filters.jinja2",
                                                       "templates": []}))
            self.assertEqual(node.marks, {"thingy": Markup("\nHello\n")})

            node.render()
            with pathlib.Path(deploy_path, "blog.html").open("r") as f:
                content = f.read()

            self.assertEqual(content, "\nHello\n\nBye")

    def test_markdown_filter(self):
        node = Node(mock.Mock(), None, meta={"templates": []})
        node.is_leaf = False
        result = jinja_filter(node, MD_TEMPLATE)
        self.assertEqual(result, "<h2>Hello</h2>\n<p>This is <em>text</em></p>")

    def test_typogrify_filter(self):
        node = Node(mock.Mock(), None, meta={"templates": []})
        node.is_leaf = False
        result = jinja_filter(node, TYPOG_TEMPLATE)
        self.assertEqual(result, "\nHello &#8212; how are&nbsp;you?\n")

    def test_metasort(self):
        node = Node(mock.Mock(), None, meta={"templates": []})
        node._content_start = 0
        for i in [3, 5, 27, 2, 1]:
            new_node = Node(mock.Mock(), node, meta={"bob": i})
            new_node._content_start = 0
        result = jinja_filter(node, METASORT_TEMPLATE)

        self.assertEqual(result, "123527")

    def test_metaselect(self):
        node = Node(mock.Mock(),  None, meta={"templates": []})
        node._content_start = 0
        for i in [True, True, False, True, None]:
            new_node = Node(mock.Mock(), node, meta={"bob": i})
            new_node._content_start = 0
        result = jinja_filter(node, METASELECT_TEMPLATE)

        self.assertEqual(result, "TrueTrueTrue")

    def test_metareject(self):
        node = Node(mock.Mock(),  None, meta={"templates": []})
        node._content_start = 0
        for i in [True, True, False, True, None]:
            new_node = Node(mock.Mock(), node, meta={"bob": i})
            new_node._content_start = 0
        result = jinja_filter(node, METAREJECT_TEMPLATE)

        # dict key order isn't stable, but it'll be one of these
        self.assertIn(result, ["FalseNone", "NoneFalse"])
