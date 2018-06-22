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
import os

INDEX_CONTENTS = """<html>
    <head>
        <title>Hello</title>
    </head>
    <body>
        Hello world!
    </body>
</html>
"""

CSS_CONTENTS = """// CSS file
html, body {
    color: black;
    background-color: white;
}
"""

class ServeTestCase(TestCase):
    def setUp(self):
        self.tmp_dir = TemporaryDirectory()

        with open(os.path.join(self.tmp_dir.name, "index.html"), "w") as index:
            index.write(INDEX_CONTENTS)

        with open(os.path.join(self.tmp_dir.name, "style.css"), "w") as css:
            css.write(CSS_CONTENTS)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_fetch_file(self):
        paqwertysqwerty 

    def test_fetch_file_with_prefix(self):
        pass

    def test_index(self):
        pass

    def test_404(self):
        pass
