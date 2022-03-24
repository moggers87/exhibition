##
#
# Copyright (C) 2022 Matt Molyneaux
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
Markdown filter

To use, add the following to your configuration file:

.. code-block:: yaml

   filter: exhibition.filters.markdown
"""

from markdown import markdown

DEFAULT_GLOB = "*.html"

DEFAULT_MD_KWARGS = {
    "output_format": "html5",
}

MARKDOWN_META_CONFIG = "markdown_config"


def content_filter(node, content):
    """
    This is the actual content filter called by :class:`exhibition.main.Node`
    on appropiate nodes.

    :param node:
        The node being rendered
    :param content:
        The content of the node, stripped of any YAML frontmatter
    """
    kwargs = DEFAULT_MD_KWARGS.copy()
    kwargs.update(node.meta.get(MARKDOWN_META_CONFIG, {}))
    return markdown(content, **kwargs)
