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
Pandoc filter

To use, add the following to your configuration file:

.. code-block:: yaml

   filter: exhibition.filters.pandoc
   pandoc_config:
     format: org

``format`` can be any format that Pandoc supports
"""

from pypandoc import convert_text

DEFAULT_GLOB = "*.html"

PANDOC_META_CONFIG = "pandoc_config"

DEFAULT_PANDOC_KWARGS = {
    "to": "html",
}


class PandocMissingFormatError(TypeError):
    pass


def content_filter(node, content):
    """
    This is the actual content filter called by :class:`exhibition.main.Node`
    on appropriate nodes.

    :param node:
        The node being rendered
    :param content:
        The content of the node, stripped of any YAML frontmatter
    """
    kwargs = DEFAULT_PANDOC_KWARGS.copy()
    kwargs.update(node.meta.get(PANDOC_META_CONFIG, {}))
    if kwargs.get("format") is None:
        raise PandocMissingFormatError("You must specify a format, see documentation")
    return convert_text(content, **kwargs)
