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

from jinja2 import Environment, FileSystemLoader, nodes
from jinja2.exceptions import TemplateRuntimeError
from jinja2.ext import Extension
from jinja2.nodes import CallBlock


EXTENDS_TEMPLATE_TEMPLATE = """{%% extends "%s" %%}
"""
START_BLOCK_TEMPLATE = """{%% block "%s" %%}
"""
END_BLOCK_TEMPLATE = """{%% endblock %%}
"""

DEFAULT_GLOB = "*.html"


class RaiseError(Extension):
    tags = set(["raise"])

    def _raise_error(self, message, caller):
        raise TemplateRuntimeError(message)

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        message = parser.parse_expression()

        return CallBlock(
            self.call_method('_raise_error', [message], lineno=lineno),
            [], [], []).set_lineno(lineno)



def content_filter(node, content):
    env = Environment(
        loader=FileSystemLoader(node.meta["templates"]),
        extensions=[RaiseError],
        autoescape=True,
    )
    parts = []

    if node.meta.get("extends"):
        parts.append(EXTENDS_TEMPLATE_TEMPLATE % node.meta["extends"])

    if node.meta.get("default-block"):
        parts.extend(
            START_BLOCK_TEMPLATE % node.meta["default-block"],
            content,
            END_BLOCK_TEMPLATE,
        )
    else:
        parts.append(content)

    content = "".join(parts)

    template = env.from_string(content)

    return template.render({"node": node})
