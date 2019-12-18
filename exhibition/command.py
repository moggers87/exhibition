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
Documentation for this module can be found in :doc:`commandline`
"""

import logging

import click

from . import __version__, config, utils

logger = logging.getLogger("exhibition")


@click.group()
@click.version_option(version=__version__)
@click.option("-v", "--verbose", count=True,
              help="Verbose output, can be used multiple times to increase logging level")
def exhibition(verbose):
    logger.addHandler(logging.StreamHandler())
    if verbose > 1:
        logger.setLevel(logging.DEBUG)
    elif verbose == 1:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.WARN)


@exhibition.command(short_help="Generate site")
def gen():
    """
    Generate site from content_path
    """
    settings = config.Config.from_path(config.SITE_YAML_PATH)
    utils.gen(settings)


@exhibition.command(short_help="Serve site locally")
@click.option("-s", "--server", default="localhost", help="Hostname to serve the site at.")
@click.option("-p", "--port", default=8000, type=int, help="Port to serve the site at.")
def serve(server, port):
    """
    Serve files from deploy_path as a webserver would
    """
    settings = config.Config.from_path(config.SITE_YAML_PATH)
    server_address = (server, port)
    httpd, thread = utils.serve(settings, server_address)

    try:
        thread.join()
    except (KeyboardInterrupt, SystemExit):
        httpd.shutdown()
