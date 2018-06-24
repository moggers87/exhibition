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
from unittest import TestCase
import os
import pathlib

from exhibition.main import gen, Config


class GenTestCase(TestCase):
    def test_clean_deploy_dir(self):
        with TemporaryDirectory() as deploy, TemporaryDirectory() as content:
            settings = Config({"deploy_path": deploy, "content_path": content})
            old_file = os.path.join(deploy, "someoldfile")
            with open(old_file, "w") as of:
                of.write("content!")

            # file exists and then is deleted during site generation
            self.assertTrue(os.path.exists(old_file))
            gen(settings)
            self.assertFalse(os.path.exists(old_file))

    def test_walk_nodes(self):
        files = [
            "blog/index.html",
            "blog/post.html",
            "index.html",
            "style.css",
        ]
        dirs = ["blog"]
        with TemporaryDirectory() as deploy, TemporaryDirectory() as content:
            settings = Config({"deploy_path": deploy, "content_path": content})
            for d in dirs:
                pathlib.Path(content, d).mkdir()

            for f in files:
                pathlib.Path(content, f).touch()

            gen(settings)

            for item in files + dirs:
                with self.subTest("%s exists in %s" % (item, deploy)):
                    self.assertTrue(pathlib.Path(deploy, item).exists())
