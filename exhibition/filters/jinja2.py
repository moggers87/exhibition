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

"""
Jinja2 template filter

To use, add the following to your configuration file:

.. code-block:: yaml

   filter: exhibition.filters.jinja2
"""

from datetime import datetime, timezone

from jinja2 import Environment, FileSystemLoader, contextfilter
from jinja2.exceptions import TemplateRuntimeError
from jinja2.ext import Extension
from jinja2.nodes import CallBlock, ContextReference, Const
from markdown import markdown as md_func
from typogrify.templatetags import jinja_filters as typogrify_filters


EXTENDS_TEMPLATE_TEMPLATE = """{%% extends "%s" %%}
"""
START_BLOCK_TEMPLATE = """{%% block %s %%}
"""
END_BLOCK_TEMPLATE = """{% endblock %}
"""

DEFAULT_GLOB = "*.html"

NODE_TMPL_VAR = "node"

DEFAULT_MD_KWARGS = {
    "output_format": "html5",
}


def metasort(nodes, key=None, reverse=False):
    """
    Sorts a list of nodes based on keys found in their meta objects
    """
    def key_func(node):
        return node.meta[key]

    return sorted(nodes, key=key_func, reverse=reverse)


def metaselect(nodes, key):
    for n in nodes:
        if n.meta.get(key):
            yield n


def metareject(nodes, key):
    for n in nodes:
        if not n.meta.get(key):
            yield n


@contextfilter
def markdown(ctx, text):
    kwargs = DEFAULT_MD_KWARGS.copy()
    node = ctx[NODE_TMPL_VAR]

    kwargs.update(node.meta.get("markdown_config", {}))

    return md_func(text, **kwargs)


class RaiseError(Extension):
    """
    Raise an exception during template rendering:

    .. code-block:: jinja

       {% raise "This is an error" %}
    """
    tags = set(["raise"])

    def _raise_error(self, message, caller):
        raise TemplateRuntimeError(message)

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        message = parser.parse_expression()

        return CallBlock(
            self.call_method('_raise_error', [message], lineno=lineno),
            [], [], []).set_lineno(lineno)


class Mark(Extension):
    """
    Marks a section for use later:

    .. code-block:: html+jinja

       {% mark intro %}
       <p>My Intro</p>
       {% endmark %}

       <p>Some more text</p>

    This can then be referenced via :attr:`Node.marks`.
    """
    tags = set(['mark'])

    def parse(self, parser):
        token = next(parser.stream)
        lineno = token.lineno
        tag = token.value
        name = next(parser.stream).value
        body = parser.parse_statements(["name:end%s" % tag], drop_needle=True)
        return CallBlock(self.call_method('_render_output', args=[ContextReference(), Const(name)]),
                         [], [], body).set_lineno(lineno)

    def _render_output(self, ctx, name, caller=None):
        """
        Assign the marked content to :attr:`Node.marks`
        """
        if not caller:
            return ""
        out = caller()
        ctx[NODE_TMPL_VAR].marks[name] = out
        return out


def content_filter(node, content):
    """
    This is the actual content filter called by :class:`exhibition.main.Node`
    on appropiate nodes.

    :param node:
        The node being rendered
    :param content:
        The content of the node, stripped of any YAML front matter
    """
    env = Environment(
        loader=FileSystemLoader(node.meta["templates"]),
        extensions=[RaiseError, Mark],
        autoescape=True,
    )
    env.filters["markdown"] = markdown
    env.filters["metasort"] = metasort
    env.filters["metaselect"] = metaselect
    env.filters["metareject"] = metareject
    typogrify_filters.register(env)

    parts = []

    if node.meta.get("extends"):
        parts.append(EXTENDS_TEMPLATE_TEMPLATE % node.meta["extends"])

    if node.meta.get("default-block"):
        parts.extend([
            START_BLOCK_TEMPLATE % node.meta["default-block"],
            content,
            END_BLOCK_TEMPLATE,
        ])
    else:
        parts.append(content)

    content = "".join(parts)

    template = env.from_string(content)

    return template.render({
        NODE_TMPL_VAR: node,
        "time_now": datetime.now(timezone.utc),
    })
