# -*- coding: utf-8 -*-
#
# Copyright Kevin Deldycke <kevin@deldycke.com> and contributors.
# All Rights Reserved.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

import textwrap

import pytest

from .conftest import MANAGER_IDS
from .test_cli import CLISubCommandTests


class TestRestore(CLISubCommandTests):


    subcmd = 'restore', 'dummy.toml'


    def __init__(self):
        """ Seed common subcommand tests with a dummy file and content to
        allow the CLI to not fail on required file input. """
        self.create_toml('dummy.toml', """
            [dummy_manager]
            fancy_package = "0.0.1"
            """)


    @staticmethod
    def create_toml(filename, content):
        """ Utility to produce TOML files. """
        with open(filename, 'w') as doc:
            doc.write(textwrap.dedent(content.strip()))


    def test_default_all_manager(self, invoke):
        self.create_toml('all-managers.toml', ''.join(["""
            [{}]
            blah = 123
            """.format(m) for m in MANAGER_IDS]))

        result = invoke('restore', 'all-managers.toml')
        assert result.exit_code == 0
        assert 'all-managers.toml' in result.output
        self.check_manager_selection(result.output)


    @pytest.mark.parametrize('mid', MANAGER_IDS)
    def test_single_manager(self, invoke, mid):
        self.create_toml('all-managers.toml', ''.join(["""
            [{}]
            blah = 123
            """.format(m) for m in MANAGER_IDS]))

        result = invoke('--manager', mid, 'restore', 'all-managers.toml')
        assert result.exit_code == 0
        self.check_manager_selection(result.output, {mid})


    def test_ignore_unrecognized_manager(self, invoke):
        self.create_toml('unrecognized.toml', """
            [random_section]
            blah = 123
            """)

        result = invoke('restore', 'unrecognized.toml')
        assert result.exit_code == 0
        assert 'unrecognized.toml' in result.output
        assert 'warning: Ignore [random_section] section.' in result.output


    def test_restore_single_manager(self, invoke):
        self.create_toml('pip-npm-dummy.toml', """
            [pip3]
            fancy_package = "0.0.1"

            [npm]
            dummy_package = "2.2.2"
            """)

        result = invoke('--manager', 'npm', 'restore', 'pip-npm-dummy.toml')
        assert result.exit_code == 0
        assert 'pip-npm-dummy.toml' in result.output
        assert 'Restore pip3' not in result.output
        assert 'Restore npm' in result.output


    def test_restore_excluded_manager(self, invoke):
        self.create_toml('pip-npm-dummy.toml', """
            [pip3]
            fancy_package = "0.0.1"

            [npm]
            dummy_package = "2.2.2"
            """)

        result = invoke('--exclude', 'npm', 'restore', 'pip-npm-dummy.toml')
        assert result.exit_code == 0
        assert 'pip-npm-dummy.toml' in result.output
        assert 'Restore pip3' in result.output
        assert 'Restore npm' not in result.output


    def test_empty_manager(self, invoke):
        self.create_toml('pip-empty.toml', """
            [pip3]
            """)

        result = invoke('restore', 'pip-empty.toml')
        assert result.exit_code == 0
        assert 'pip-empty.toml' in result.output
        assert 'Restore pip3' in result.output
