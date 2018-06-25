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


class Jinja2TestCase(TestCase):
    def test_template(self):
        node = Node(mock.Mock(), None, meta={"templates": []})
        result = jinja_filter(node, PLAIN_TEMPLATE)
        self.assertEqual(result, "<p>0</p><p>1</p><p>2</p>")

    def test_extends(self):
        template_name = "bob.j2"
        with TemporaryDirectory() as tmp_dir:
            with pathlib.Path(tmp_dir, template_name).open("w") as tmpl:
                tmpl.write(BASE_TEMPLATE)

            node = Node(mock.Mock(), None, meta={"templates": [tmp_dir], "extends": "bob.j2"})
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
            result = jinja_filter(node, CONTENT_BLOCK)
            self.assertEqual(result, "<p>Title</p>\n<p>0</p><p>1</p><p>2</p>")

            # switch order of template dirs,
            node = Node(mock.Mock(), None,
                        meta={"templates": [tmp2_dir, tmp1_dir], "extends": "bob.j2"})
            result = jinja_filter(node, CONTENT_BLOCK)
            self.assertEqual(result, "empty")

    def test_default_block(self):
        template_name = "bob.j2"
        with TemporaryDirectory() as tmp_dir:
            with pathlib.Path(tmp_dir, template_name).open("w") as tmpl:
                tmpl.write(BASE_TEMPLATE)

            node = Node(mock.Mock(), None, meta={"templates": [tmp_dir], "extends": "bob.j2"})
            result = jinja_filter(node, PLAIN_TEMPLATE)
            self.assertEqual(result, "<p>Title</p>\n")

            node = Node(mock.Mock(), None, meta={"templates": [tmp_dir],
                                                 "extends": "bob.j2", "default-block": "content"})
            result = jinja_filter(node, PLAIN_TEMPLATE)
            self.assertEqual(result, "<p>Title</p>\n\n<p>0</p><p>1</p><p>2</p>")

    def test_context(self):
        path = mock.Mock()
        path.name = "thisfile.html"
        node = Node(path, None, meta={"templates": []})
        result = jinja_filter(node, "{{ node }}")
        self.assertEqual(result, "&lt;Node: thisfile.html&gt;")

        result = jinja_filter(node, "{{ undef_value }}")
        self.assertEqual(result, "")

    def test_raise_extension(self):
        node = Node(mock.Mock(), None, meta={"templates": []})
        with self.assertRaises(TemplateRuntimeError) as excp:
            jinja_filter(node, ERROR_TEMPLATE)

        self.assertEqual(excp.exception.message, "This is an error")