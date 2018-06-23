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

from unittest import TestCase, mock
import logging

from click.testing import CliRunner

from exhibition import command, main


class CommandTestCase(TestCase):
    @mock.patch("exhibition.command.main.gen")
    @mock.patch("exhibition.command.main.Config.from_path", return_value=main.Config())
    def test_gen(self, config_mock, gen_mock):
        runner = CliRunner()
        result = runner.invoke(command.exhibition, ["gen"])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(gen_mock.call_count, 1)
        self.assertEqual(gen_mock.call_args, ((config_mock.return_value,), {}))

        self.assertEqual(config_mock.call_args, ((main.SITE_YAML_PATH,), {}))

    @mock.patch("exhibition.command.main.serve", return_value=(mock.Mock(), mock.Mock()))
    @mock.patch("exhibition.command.main.Config.from_path", return_value=main.Config())
    def test_serve(self, config_mock, serve_mock):
        runner = CliRunner()
        result = runner.invoke(command.exhibition, ["serve"])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(serve_mock.call_count, 1)
        self.assertEqual(serve_mock.call_args, ((config_mock.return_value,), {}))

        self.assertEqual(config_mock.call_args, ((main.SITE_YAML_PATH,), {}))
        self.assertEqual(serve_mock.return_value[0].shutdown.call_count, 0)
        self.assertEqual(serve_mock.return_value[1].join.call_count, 1)

        serve_mock.return_value[1].join.side_effect = KeyboardInterrupt
        # this time with a simulated keyboard interrupt
        result = runner.invoke(command.exhibition, ["serve"])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(serve_mock.call_count, 2)
        self.assertEqual(serve_mock.call_args, ((config_mock.return_value,), {}))

        self.assertEqual(config_mock.call_args, ((main.SITE_YAML_PATH,), {}))
        self.assertEqual(serve_mock.return_value[0].shutdown.call_count, 1)
        self.assertEqual(serve_mock.return_value[1].join.call_count, 2)

    @mock.patch.object(command, "logger")
    def test_exhibition(self, log_mock):
        @command.exhibition.command()
        def test():
            pass

        # logging defaults to warn
        runner = CliRunner()
        result = runner.invoke(command.exhibition, ["test"])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(log_mock.addHandler.call_count, 1)
        self.assertEqual(log_mock.setLevel.call_count, 1)
        self.assertEqual(log_mock.setLevel.call_args, ((logging.WARN,), {}))

        # one verbose is info
        log_mock.reset_mock()
        result = runner.invoke(command.exhibition, ["-v", "test"])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(log_mock.addHandler.call_count, 1)
        self.assertEqual(log_mock.setLevel.call_count, 1)
        self.assertEqual(log_mock.setLevel.call_args, ((logging.INFO,), {}))

        # two or more verbose is debug
        log_mock.reset_mock()
        result = runner.invoke(command.exhibition, ["-vv", "test"])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(log_mock.addHandler.call_count, 1)
        self.assertEqual(log_mock.setLevel.call_count, 1)
        self.assertEqual(log_mock.setLevel.call_args, ((logging.DEBUG,), {}))

        result = runner.invoke(command.exhibition, ["-vvv", "test"])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(log_mock.addHandler.call_count, 2)
        self.assertEqual(log_mock.setLevel.call_count, 2)
        self.assertEqual(log_mock.setLevel.call_args, ((logging.DEBUG,), {}))
