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

from exhibition import main


logger = logging.getLogger("exhibition")


@click.group()
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
    settings = main.Config.from_path(main.SITE_YAML_PATH)
    main.gen(settings)


@exhibition.command(short_help="Serve site locally")
def serve():
    """
    Serve files from deploy_path as a webserver would
    """
    settings = main.Config.from_path(main.SITE_YAML_PATH)
    httpd, thread = main.serve(settings)

    try:
        thread.join()
    except (KeyboardInterrupt, SystemExit):
        httpd.shutdown()
