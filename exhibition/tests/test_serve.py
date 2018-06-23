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

from http.client import HTTPConnection
from tempfile import TemporaryDirectory
from unittest import TestCase
import os

from exhibition.main import Config, serve


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

        self.client = HTTPConnection("localhost", "8000")

    def tearDown(self):
        self.tmp_dir.cleanup()
        self.client.close()
        self.server.shutdown()
        self.server.server_close()

    def get_server(self, settings):
        httpd, thread = serve(settings)
        self.server = httpd

    def test_fetch_file(self):
        settings = Config({"deploy_path": self.tmp_dir.name})
        self.get_server(settings)

        self.client.request("GET", "/style.css")
        response = self.client.getresponse()
        self.assertEqual(response.status, 200)
        content = response.read()
        self.assertEqual(content, CSS_CONTENTS.encode())

    def test_fetch_file_with_prefix(self):
        settings = Config({"deploy_path": self.tmp_dir.name, "base_url": "/bob/"})
        self.get_server(settings)

        self.client.request("GET", "/bob/style.css")
        response = self.client.getresponse()
        self.assertEqual(response.status, 200)
        content = response.read()
        self.assertEqual(content, CSS_CONTENTS.encode())

        self.client.request("GET", "/style.css")
        response = self.client.getresponse()
        self.assertEqual(response.status, 404)

    def test_index(self):
        settings = Config({"deploy_path": self.tmp_dir.name})
        self.get_server(settings)

        self.client.request("GET", "/")
        response = self.client.getresponse()
        self.assertEqual(response.status, 200)
        content = response.read()
        self.assertEqual(content, INDEX_CONTENTS.encode())

    def test_404(self):
        settings = Config({"deploy_path": self.tmp_dir.name})
        self.get_server(settings)

        self.client.request("GET", "/not-existing.html")
        response = self.client.getresponse()
        self.assertEqual(response.status, 404)
