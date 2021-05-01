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

from filecmp import dircmp
from tempfile import TemporaryDirectory
from unittest import TestCase, mock
import logging
import pathlib

from click.testing import CliRunner

from exhibition import command, config
import exhibition


class CommandTestCase(TestCase):
    @mock.patch("exhibition.command.utils.gen")
    @mock.patch("exhibition.command.config.Config.from_path", return_value=config.Config())
    def test_gen(self, config_mock, gen_mock):
        runner = CliRunner()
        result = runner.invoke(command.exhibition, ["gen"])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(gen_mock.call_count, 1)
        self.assertEqual(gen_mock.call_args, ((config_mock.return_value,), {}))

        self.assertEqual(config_mock.call_args, ((config.SITE_YAML_PATH,), {}))

    @mock.patch("exhibition.command.utils.serve", return_value=(mock.Mock(), mock.Mock()))
    @mock.patch("exhibition.command.config.Config.from_path", return_value=config.Config())
    def test_serve(self, config_mock, serve_mock):
        runner = CliRunner()
        result = runner.invoke(command.exhibition, ["serve"])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(serve_mock.call_count, 1)
        expected_args = ((config_mock.return_value, ("localhost", 8000)), {})
        self.assertEqual(serve_mock.call_args, expected_args)

        self.assertEqual(config_mock.call_args, ((config.SITE_YAML_PATH,), {}))
        self.assertEqual(serve_mock.return_value[0].shutdown.call_count, 0)
        self.assertEqual(serve_mock.return_value[1].join.call_count, 1)

        serve_mock.return_value[1].join.side_effect = KeyboardInterrupt
        # this time with a simulated keyboard interrupt
        result = runner.invoke(command.exhibition, ["serve"])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(serve_mock.call_count, 2)
        expected_args = ((config_mock.return_value, ("localhost", 8000)), {})
        self.assertEqual(serve_mock.call_args, expected_args)

        self.assertEqual(config_mock.call_args, ((config.SITE_YAML_PATH,), {}))
        self.assertEqual(serve_mock.return_value[0].shutdown.call_count, 1)
        self.assertEqual(serve_mock.return_value[1].join.call_count, 2)

        # Undoing the KeyboardInterrupt
        serve_mock.return_value[1].join.side_effect = None
        # Now testing w args
        config_mock.reset_mock()
        serve_mock.reset_mock()
        serve_mock.return_value[0].reset_mock()
        serve_mock.return_value[1].reset_mock()
        addr_options = ["serve", "--server", "localhost", "--port", "8001"]
        result = runner.invoke(command.exhibition, addr_options)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(serve_mock.call_count, 1)
        expected_args = ((config_mock.return_value, ("localhost", 8001)), {})
        self.assertEqual(serve_mock.call_args, expected_args)

        self.assertEqual(serve_mock.return_value[0].shutdown.call_count, 0)
        self.assertEqual(serve_mock.return_value[1].join.call_count, 1)

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


class CreateTestCase(TestCase):
    def _dir_cmp(self, pathA, pathB):
        dir_diff = dircmp(pathA, pathB)
        return dir_diff.left_only + dir_diff.right_only + dir_diff.funny_files + dir_diff.diff_files

    def test_create(self):
        with TemporaryDirectory() as tmpDir:
            path = pathlib.Path(tmpDir, "site")
            runner = CliRunner()
            result = runner.invoke(command.exhibition, ["create", str(path)])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(path.exists(), True)
            self.assertEqual(
                self._dir_cmp(path, pathlib.Path(exhibition.__path__[0], "data", "starter")),
                [],
            )

    def test_existing_dir(self):
        with TemporaryDirectory() as tmpDir:
            path = pathlib.Path(tmpDir, "site")
            path.mkdir()
            runner = CliRunner()
            result = runner.invoke(command.exhibition, ["create", str(path)])
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(path.exists(), True)

    def test_force_with_existing_dir(self):
        with TemporaryDirectory() as tmpDir:
            path = pathlib.Path(tmpDir, "site")
            path.mkdir()
            runner = CliRunner()
            result = runner.invoke(command.exhibition, ["create", "--force", str(path)])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(path.exists(), True)
            self.assertEqual(
                self._dir_cmp(path, pathlib.Path(exhibition.__path__[0], "data", "starter")),
                [],
            )

    def test_force_without_existing_dir(self):
        with TemporaryDirectory() as tmpDir:
            path = pathlib.Path(tmpDir, "site")
            runner = CliRunner()
            result = runner.invoke(command.exhibition, ["create", "--force", str(path)])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(path.exists(), True)
            self.assertEqual(
                self._dir_cmp(path, pathlib.Path(exhibition.__path__[0], "data", "starter")),
                [],
            )
