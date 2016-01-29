#!/bin/env dls-python

import unittest

from pkg_resources import require

from dls_ade import dls_checkout_module

require("mock")
from mock import patch, MagicMock
from argparse import _StoreAction
from argparse import _StoreTrueAction


class MakeParserTest(unittest.TestCase):

    def setUp(self):
        self.parser = dls_checkout_module.make_parser()

    def test_module_name_has_correct_attributes(self):
        arguments = self.parser._positionals._actions[4]
        self.assertEqual(arguments.type, str)
        self.assertEqual(arguments.dest, 'module_name')

    def test_branch_argument_has_correct_attributes(self):
        option = self.parser._option_string_actions['-b']
        self.assertIsInstance(option, _StoreAction)
        self.assertEqual(option.type, str)
        self.assertEqual(option.dest, "branch")
        self.assertIn("--branch", option.option_strings)

    def test_force_argument_has_correct_attributes(self):
        option = self.parser._option_string_actions['-f']
        self.assertIsInstance(option, _StoreTrueAction)
        self.assertEqual(option.dest, "force")
        self.assertIn("--force", option.option_strings)


class CheckTechnicalAreaTest(unittest.TestCase):

    def test_given_area_not_ioc_then_no_error_raised(self):
        area = "support"
        module = "test_module"

        dls_checkout_module.check_technical_area(area, module)

    def test_given_area_ioc_module_everything_then_no_error_raised(self):
        area = "ioc"
        module = "everything"

        dls_checkout_module.check_technical_area(area, module)

    def test_given_area_ioc_module_split_two_then_no_error_raised(self):
        area = "ioc"
        module = "modules/test_module"

        dls_checkout_module.check_technical_area(area, module)

    def test_given_area_ioc_module_split_less_than_two_then_error_raised(self):
        area = "ioc"
        module = "test_module"
        expected_error_msg = "Missing Technical Area under Beamline"
        try:
            dls_checkout_module.check_technical_area(area, module)
        except Exception as error:
            self.assertEqual(error.message, expected_error_msg)


class CheckSourceFilePathValidTest(unittest.TestCase):

    @patch('dls_ade.dls_checkout_module.vcs_git.is_server_repo', return_value=True)
    def test_given_valid_source_then_no_error_raised(self, _1):
        source = "controls/python/dls_release"

        dls_checkout_module.check_source_file_path_valid(source)

    @patch('dls_ade.dls_checkout_module.vcs_git.is_server_repo', return_value=False)
    def test_given_invalid_source_then_error_raised(self, _1):
        source = "controls/python/doesnotexist"
        expected_error_msg = "Repository does not contain " + source

        try:
            dls_checkout_module.check_source_file_path_valid(source)
        except Exception as error:
            self.assertEqual(error.message, expected_error_msg)


class CheckModuleFilePathValidTest(unittest.TestCase):

    @patch('dls_ade.dls_checkout_module.os.path.isdir', return_value=False)
    def test_given_valid_module_then_no_error_raised(self, _1):
        module = "doesnotexistyet"

        dls_checkout_module.check_module_file_path_valid(module)

    @patch('dls_ade.dls_checkout_module.os.path.isdir', return_value=True)
    def test_given_existing_module_then_error_raised(self, _1):
        module = "test_module"
        expected_error_msg = "Path already exists: " + module

        try:
            dls_checkout_module.check_module_file_path_valid(module)
        except Exception as error:
            self.assertEqual(error.message, expected_error_msg)


if __name__ == '__main__':
    # buffer option suppresses stdout generated from tested code
    unittest.main(buffer=True)
