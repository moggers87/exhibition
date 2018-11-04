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


def serve(settings):
    """
    Serves the generated site from ``deploy_path``

    Respects settings like ``base_url`` if present.
    """
    logger = logging.getLogger("exhibition.server")

    class ExhibitionHTTPRequestHandler(SimpleHTTPRequestHandler):
        def translate_path(self, path):
            path = path.strip("/")
            if settings.get("base_url"):
                base = settings["base_url"].strip("/")
                if not path.startswith(base):
                    return ""
                path = path.lstrip(base).strip("/")

            path = pathlib.Path(settings["deploy_path"], path)

            if not (path.exists() or path.suffix):
                for ext in Node._strip_exts:
                    new_path = path.with_suffix(ext)
                    if new_path.exists():
                        return str(new_path)
            elif path.is_dir():
                new_path = pathlib.Path(path, Node._index_file)
                if new_path.exists():
                    return str(new_path)

            return str(path)

    server_address = ('localhost', 8000)

    httpd = HTTPServer(server_address, ExhibitionHTTPRequestHandler)

    logger.warning("Listening on http://%s:%s", *server_address)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()

    return (httpd, t)
