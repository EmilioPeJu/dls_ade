#!/bin/env dls-python


from __future__ import print_function
from sys import version_info
if version_info.major == 2:
    import __builtin__ as builtins  # Allows for Python 2/3 compatibility, 'builtins' is namespace for inbuilt functions
else:
    import builtins
import unittest
from argparse import _StoreAction
from pkg_resources import require
import dls_list_modules
require("mock")
from mock import patch, ANY, MagicMock


class ParserTest(unittest.TestCase):

    def setUp(self):
        self.parser = dls_list_modules.make_parser()

    def test_domain_argument_has_correct_attributes(self):
        option = self.parser._option_string_actions['-d']
        self.assertIsInstance(option, _StoreAction)
        self.assertEqual(option.type, str)
        self.assertEqual(option.dest, "domain_name")
        self.assertIn("--domain", option.option_strings)


class PrintModuleListTest(unittest.TestCase):

    @patch('vcs_git.subprocess.check_output')
    def test_subprocess_called_with_correct_list(self, mock_sub):
        source = "/test/source"
        list_cmd = "ssh " + dls_list_modules.vcs_git.GIT_ROOT + " expand controls"

        dls_list_modules.print_module_list(source)

        mock_sub.assert_called_once_with(list_cmd.split())

    @patch('vcs_git.subprocess.check_output', return_value="/test/source/module")
    def test_print_called(self, mock_sub):
        source = "/test/source"
        mock_print = MagicMock()

        with patch.object(builtins, 'print', mock_print):
            dls_list_modules.print_module_list(source)

        mock_print.assert_called_once_with(ANY)
