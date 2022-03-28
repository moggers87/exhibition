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
from jinja2.nodes import CallBlock, Const, ContextReference
from markdown import markdown as md_func
from pypandoc import convert_text as pandoc_func
from typogrify.templatetags import jinja_filters as typogrify_filters

from exhibition.filters.base import BaseFilter
from exhibition.filters.markdown import DEFAULT_MD_KWARGS, MARKDOWN_META_CONFIG
from exhibition.filters.pandoc import (DEFAULT_PANDOC_KWARGS, PANDOC_META_CONFIG,
                                       PandocMissingFormatError)

EXTENDS_TEMPLATE_TEMPLATE = """{%% extends "%s" %%}
"""
START_BLOCK_TEMPLATE = """{%% block %s %%}
"""
END_BLOCK_TEMPLATE = """{% endblock %}
"""

DEFAULT_GLOB = "*.html"

NODE_TMPL_VAR = "node"


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

    kwargs.update(node.meta.get(MARKDOWN_META_CONFIG, {}))

    return md_func(text, **kwargs)


@contextfilter
def pandoc(ctx, text, fmt=None):
    """Use Pandoc to convert from one format to another. Takes source format as
    an optional argument.

    Uses the same ``pandoc_config`` meta key as :mod:`exhibition.filters.pandoc`
    """
    kwargs = DEFAULT_PANDOC_KWARGS.copy()
    node = ctx[NODE_TMPL_VAR]

    kwargs.update(node.meta.get(PANDOC_META_CONFIG, {}))

    if fmt is not None:
        kwargs["format"] = fmt
    elif kwargs.get("format") is None:
        raise PandocMissingFormatError("You must specify a format, see documentation")

    return pandoc_func(text, **kwargs)


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

    def _render_output(self, ctx, name, caller):
        """
        Assign the marked content to :attr:`Node.marks`
        """
        out = caller()
        ctx[NODE_TMPL_VAR].marks[name] = out
        return out


class JinjaFilter(BaseFilter):
    """
    This is the actual content filter called by :class:`exhibition.main.Node`
    on appropriate nodes.

    :param node:
        The node being rendered
    :param content:
        The content of the node, stripped of any YAML frontmatter
    """
    template_loader_class = FileSystemLoader
    extensions = (RaiseError, Mark)

    def __init__(self, extra_filters=None):
        """``extra_filters`` should be a dict. The keys are the name of the
        filter and the values are the template filters"""
        if extra_filters is None:
            self.extra_filters = {}
        else:
            self.extra_filters = extra_filters

    def get_environment(self):
        """Get Jinja environment

        Sets up template loader and extensions
        """
        return Environment(
            loader=self.template_loader_class(self.node.meta["templates"]),
            extensions=self.extensions,
            autoescape=True,
        )

    def add_template_filters(self, env):
        """Add template filters to current Environment"""
        env.filters["pandoc"] = pandoc
        env.filters["markdown"] = markdown
        env.filters["metasort"] = metasort
        env.filters["metaselect"] = metaselect
        env.filters["metareject"] = metareject
        typogrify_filters.register(env)

        for name, flt in self.extra_filters.items():
            env.filters[name] = flt

    def get_context_data(self):
        """Returns context data that is used for rendering the template"""
        return {
            NODE_TMPL_VAR: self.node,
            "time_now": datetime.now(timezone.utc),
        }

    def prepare_content(self):
        """Prepares content by adding ``{% extends %}`` and a default block, if
        either are specified"""
        parts = []

        if self.node.meta.get("extends"):
            parts.append(EXTENDS_TEMPLATE_TEMPLATE % self.node.meta["extends"])

        if self.node.meta.get("default_block"):
            parts.extend([
                START_BLOCK_TEMPLATE % self.node.meta["default_block"],
                self.content,
                END_BLOCK_TEMPLATE,
            ])
        else:
            parts.append(self.content)

        return "".join(parts)

    def content_filter(self):
        """Bring everything together and render the template"""
        env = self.get_environment()
        self.add_template_filters(env)

        template = env.from_string(self.prepare_content())

        return template.render(self.get_context_data())


content_filter = JinjaFilter()
