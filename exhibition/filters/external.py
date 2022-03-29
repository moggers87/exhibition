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
External command filter

Use an external command to process a file, like so:

.. code-block:: yaml

   filter: exhibition.filters.external
   external_cmd: sed 's/this/that/g' {INPUT} > {OUTPUT}
"""

from tempfile import TemporaryDirectory
import pathlib
import subprocess

DEFAULT_GLOB = "*.*"

INPUT_NAME = "input"
OUTPUT_NAME = "output"

INPUT_KEY = "INPUT"
OUTPUT_KEY = "OUTPUT"


def content_filter(node, content):
    """
    This is the actual content filter called by :class:`exhibition.main.Node`
    on appropriate nodes.

    :param node:
        The node being rendered
    :param content:
        The content of the node, stripped of any YAML frontmatter
    """
    tmp_dir = TemporaryDirectory()
    input_file = pathlib.Path(tmp_dir.name, INPUT_NAME)
    output_file = pathlib.Path(tmp_dir.name, OUTPUT_NAME)

    cmd = node.meta["external_cmd"]
    cmd = cmd.format(**{
        INPUT_KEY: input_file,
        OUTPUT_KEY: output_file,
    })

    with input_file.open("w") as f:
        f.write(content)

    subprocess.run(cmd, shell=True)

    with output_file.open("r") as f:
        output = f.read()

    return output
