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

from http.server import HTTPServer, SimpleHTTPRequestHandler
import logging
import pathlib
import shutil
import threading

from .node import Node

logger = logging.getLogger("exhibition")


def gen(settings):
    """
    Generate site

    Deletes ``deploy_path`` first.
    """
    shutil.rmtree(settings["deploy_path"], True)
    root_node = Node.from_path(pathlib.Path(settings["content_path"]), meta=settings)

    for item in root_node.walk(True):
        logger.info("Rendering %s", item.full_url)
        item.render()


class ExhibitionBaseHTTPRequestHandler(SimpleHTTPRequestHandler):
    def _sanitise_path(self, path):
        """ Strip leading and trailing / as well as base_url, if preset """
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        path = path.strip("/")
        if self._settings.get("base_url"):
            base = self._settings["base_url"].strip("/")
            if not path.startswith(base):
                return
            path = path.lstrip(base).strip("/")

        return path

    def translate_path(self, path):
        path = self._sanitise_path(path)
        root_node = Node.from_path(pathlib.Path(self._settings["content_path"]),
                                   meta=self._settings)

        try:
            node = root_node.get_from_path(pathlib.PurePath(path).parent or path)
        except (OSError, TypeError):
            return ""

        path = pathlib.Path(self._settings["deploy_path"], path)

        if not (path.exists() or path.suffix):
            for ext in node.strip_exts:
                new_path = path.with_suffix(ext)
                if new_path.exists():
                    return str(new_path)
        elif path.is_dir():
            new_path = pathlib.Path(path, node.index_file)
            if new_path.exists():
                return str(new_path)

        return str(path)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        return super().end_headers()


def serve(settings, server_address):
    """
    Serves the generated site from ``deploy_path``

    Respects settings like ``base_url`` if present.
    """
    logger = logging.getLogger("exhibition.server")

    # this is quite ewwww, but whatever.
    class ExhibitionHTTPRequestHandler(ExhibitionBaseHTTPRequestHandler):
        _settings = settings

    httpd = HTTPServer(server_address, ExhibitionHTTPRequestHandler)

    logger.warning("Listening on http://%s:%s", *server_address)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()

    return (httpd, t)
