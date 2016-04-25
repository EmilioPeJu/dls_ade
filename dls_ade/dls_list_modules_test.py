#!/bin/env dls-python

from __future__ import print_function
from sys import version_info
if version_info.major == 2:
    import __builtin__ as builtins  # Allows for Python 2/3 compatibility, 'builtins' is namespace for inbuilt functions
else:
    import builtins

import unittest
from pkg_resources import require
from dls_ade import dls_list_modules
require("mock")
from mock import patch, ANY, MagicMock


class ParserTest(unittest.TestCase):

    def setUp(self):
        self.parser = dls_list_modules.make_parser()

    def test_domain_name_has_correct_attributes(self):
        arguments = self.parser._positionals._actions[4]
        self.assertEqual(arguments.type, str)
        self.assertEqual(arguments.dest, 'domain_name')


class PrintModuleListTest(unittest.TestCase):

    @patch('dls_ade.vcs_git.subprocess.check_output')
    def test_subprocess_called_with_correct_list(self, mock_sub):
        source = "test/source"
        list_cmd = "ssh " + dls_list_modules.vcs_git.GIT_ROOT + " expand controls"

        dls_list_modules.print_module_list(source)

        mock_sub.assert_called_once_with(list_cmd.split())

    @patch('dls_ade.vcs_git.get_server_repo_list', return_value=["test/source/module", "test/source2/module2"])
    def test_given_valid_source_then_print_called(self, _1):
        source = "test/source"

        with patch.object(builtins, 'print') as mock_print:
            dls_list_modules.print_module_list(source)

        call_args = mock_print.call_args_list
        self.assertEqual(call_args[0][0][0], 'module')
        # Check that module2 from source2 is not printed
        self.assertEqual(len(call_args), 1)

    @patch('dls_ade.vcs_git.get_server_repo_list', return_value=["test/source/module"])
    def test_given_invalid_source_then_print_not_called(self, _1):
        source = "test/not_source"

        with patch.object(builtins, 'print') as mock_print:
            dls_list_modules.print_module_list(source)

        # Check that only called once (twice if source valid)
        self.assertFalse(mock_print.call_count)
