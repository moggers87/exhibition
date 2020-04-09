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
import pathlib

from exhibition.config import Config
from exhibition.utils import serve

INDEX_CONTENTS = """<html>
    <head>
        <title>Hello</title>
    </head>
    <body>
        Hello world!
    </body>
</html>
"""

BLOG_INDEX_CONTENTS = """<html>
    <head>
        <title>Blog</title>
    </head>
    <body>
        Goodbye world!
    </body>
</html>
"""

PAGE_CONTENTS = """<html>
    <head>
        <title>Page 1</title>
    </head>
    <body>
        This is a page
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

        with pathlib.Path(self.tmp_dir.name, "index.html").open("w") as index:
            index.write(INDEX_CONTENTS)

        with pathlib.Path(self.tmp_dir.name, "page.html").open("w") as page:
            page.write(PAGE_CONTENTS)

        with pathlib.Path(self.tmp_dir.name, "style.css").open("w") as css:
            css.write(CSS_CONTENTS)

        self.blog_dir = pathlib.Path(self.tmp_dir.name, "blog")
        self.blog_dir.mkdir()

        with pathlib.Path(self.blog_dir, "index.html").open("w") as index:
            index.write(BLOG_INDEX_CONTENTS)

        self.client = HTTPConnection("localhost", "8000")

    def tearDown(self):
        self.tmp_dir.cleanup()
        self.client.close()
        self.server.shutdown()
        self.server.server_close()

    def get_server(self, settings):
        server_address = ("localhost", 8000)
        httpd, thread = serve(settings, server_address)
        self.server = httpd

    def test_fetch_file(self):
        settings = Config({"deploy_path": self.tmp_dir.name, "content_path": self.tmp_dir.name})
        self.get_server(settings)

        self.client.request("GET", "/style.css")
        response = self.client.getresponse()
        self.assertEqual(response.status, 200)
        content = response.read()
        self.assertEqual(content, CSS_CONTENTS.encode())
        headers = dict(response.getheaders())
        self.assertEqual(headers["Cache-Control"], "no-store")

    def test_fetch_file_with_get_params(self):
        settings = Config({"deploy_path": self.tmp_dir.name, "content_path": self.tmp_dir.name})
        self.get_server(settings)

        self.client.request("GET", "/style.css?something=1")
        response = self.client.getresponse()
        self.assertEqual(response.status, 200)
        content = response.read()
        self.assertEqual(content, CSS_CONTENTS.encode())
        headers = dict(response.getheaders())
        self.assertEqual(headers["Cache-Control"], "no-store")

    def test_fetch_file_with_fragment(self):
        settings = Config({"deploy_path": self.tmp_dir.name, "content_path": self.tmp_dir.name})
        self.get_server(settings)

        self.client.request("GET", "/style.css#something")
        response = self.client.getresponse()
        self.assertEqual(response.status, 200)
        content = response.read()
        self.assertEqual(content, CSS_CONTENTS.encode())
        headers = dict(response.getheaders())
        self.assertEqual(headers["Cache-Control"], "no-store")

    def test_fetch_file_with_prefix(self):
        settings = Config({"deploy_path": self.tmp_dir.name, "content_path": self.tmp_dir.name,
                           "base_url": "/bob/"})
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
        settings = Config({"deploy_path": self.tmp_dir.name, "content_path": self.tmp_dir.name})
        self.get_server(settings)

        self.client.request("GET", "/")
        response = self.client.getresponse()
        self.assertEqual(response.status, 200)
        content = response.read()
        self.assertEqual(content, INDEX_CONTENTS.encode())
        headers = dict(response.getheaders())
        self.assertEqual(headers["Cache-Control"], "no-store")

    def test_404(self):
        settings = Config({"deploy_path": self.tmp_dir.name, "content_path": self.tmp_dir.name})
        self.get_server(settings)

        self.client.request("GET", "/not-existing.html")
        response = self.client.getresponse()
        self.assertEqual(response.status, 404)
        headers = dict(response.getheaders())
        self.assertEqual(headers["Cache-Control"], "no-store")

    def test_stripped_extension(self):
        settings = Config({"deploy_path": self.tmp_dir.name, "content_path": self.tmp_dir.name})
        self.get_server(settings)

        self.client.request("GET", "/page")
        response = self.client.getresponse()
        self.assertEqual(response.status, 200)
        content = response.read()
        self.assertEqual(content, PAGE_CONTENTS.encode())

    def test_custom_stripped_extension(self):
        settings = Config({"deploy_path": self.tmp_dir.name, "content_path": self.tmp_dir.name,
                           "strip_exts": ".css"})
        self.get_server(settings)

        self.client.request("GET", "/style")
        response = self.client.getresponse()
        self.assertEqual(response.status, 200)
        content = response.read()
        self.assertEqual(content, CSS_CONTENTS.encode())

        self.client.request("GET", "/page")
        response = self.client.getresponse()
        self.assertEqual(response.status, 404)

    def test_stripped_extension_and_trailing_slash(self):
        settings = Config({"deploy_path": self.tmp_dir.name, "content_path": self.tmp_dir.name})
        self.get_server(settings)

        self.client.request("GET", "/page/")
        response = self.client.getresponse()
        self.assertEqual(response.status, 200)
        content = response.read()
        self.assertEqual(content, PAGE_CONTENTS.encode())

    def test_stripped_extension_with_extension(self):
        settings = Config({"deploy_path": self.tmp_dir.name, "content_path": self.tmp_dir.name})
        self.get_server(settings)

        self.client.request("GET", "/page.html")
        response = self.client.getresponse()
        self.assertEqual(response.status, 200)
        content = response.read()
        self.assertEqual(content, PAGE_CONTENTS.encode())

    def test_stripped_extension_not_exists(self):
        settings = Config({"deploy_path": self.tmp_dir.name, "content_path": self.tmp_dir.name})
        self.get_server(settings)

        self.client.request("GET", "/unknown")
        response = self.client.getresponse()
        self.assertEqual(response.status, 404)

    def test_dir_index(self):
        settings = Config({"deploy_path": self.tmp_dir.name, "content_path": self.tmp_dir.name})
        self.get_server(settings)

        self.client.request("GET", "/blog/")
        response = self.client.getresponse()
        self.assertEqual(response.status, 200)
        content = response.read()
        self.assertEqual(content, BLOG_INDEX_CONTENTS.encode())

    def test_dir_without_index(self):
        settings = Config({"deploy_path": self.tmp_dir.name, "content_path": self.tmp_dir.name})
        index = pathlib.Path(self.blog_dir, "index.html")
        index.unlink()
        self.assertFalse(index.exists())
        self.get_server(settings)

        self.client.request("GET", "/blog/")
        response = self.client.getresponse()
        self.assertEqual(response.status, 200)
