#!/bin/env dls-python

import unittest

from pkg_resources import require

from dls_ade import dls_checkout_module

require("mock")
from mock import patch
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


class CheckParsedArgumentsValidTest(unittest.TestCase):

    def setUp(self):
        self.parser = dls_checkout_module.make_parser()
        parse_error_patch = patch('dls_checkout_module.ArgParser.error')
        self.addCleanup(parse_error_patch.stop)
        self.mock_error = parse_error_patch.start()

    def test_given_empty_module_name_then_error_raised(self):
        args = {}
        expected_error_msg = "Module name required"

        dls_checkout_module.check_parsed_arguments_valid(args, self.parser)

        self.mock_error.assert_called_once_with(expected_error_msg)

    def test_given_module_name_then_no_error_raised(self):
        args = {'module_name': ""}

        dls_checkout_module.check_parsed_arguments_valid(args, self.parser)

        self.assertFalse(self.mock_error.call_count)


class CheckTechnicalAreaTest(unittest.TestCase):

    def setUp(self):
        self.parser = dls_checkout_module.make_parser()
        parse_error_patch = patch('dls_checkout_module.ArgParser.error')
        self.addCleanup(parse_error_patch.stop)
        self.mock_error = parse_error_patch.start()

    def test_given_area_not_ioc_then_no_error_raised(self):
        args = {'module_name': "test_module", 'area': "support"}

        dls_checkout_module.check_technical_area(args, self.parser)

        self.assertFalse(self.mock_error.call_count)

    def test_given_area_ioc_module_everything_then_no_error_raised(self):
        args = {'module_name': "everything", 'area': "ioc"}

        dls_checkout_module.check_technical_area(args, self.parser)

        self.assertFalse(self.mock_error.call_count)

    def test_given_area_ioc_module_split_more_than_one_then_no_error_raised(self):
        args = {'module_name': "modules/test_module", 'area': "ioc"}

        dls_checkout_module.check_technical_area(args, self.parser)

        self.assertFalse(self.mock_error.call_count)

    def test_given_area_ioc_module_split_less_than_one_then_no_error_raised(self):
        args = {'module_name': "test_module", 'area': "ioc"}
        expected_error_msg = "Missing Technical Area under Beamline"

        dls_checkout_module.check_technical_area(args, self.parser)

        self.mock_error.assert_called_once_with(expected_error_msg)


class CheckSourceFilePathValidTest(unittest.TestCase):

    def setUp(self):
        self.parser = dls_checkout_module.make_parser()
        parse_error_patch = patch('dls_checkout_module.ArgParser.error')
        self.addCleanup(parse_error_patch.stop)
        self.mock_error = parse_error_patch.start()

    @patch('dls_checkout_module.vcs_git.is_repo_path', return_value=True)
    def test_given_valid_source_then_no_error_raised(self, mock_in_repo):
        source = "controls/python/dls_release"

        dls_checkout_module.check_source_file_path_valid(source, self.parser)

        self.assertFalse(self.mock_error.call_count)

    @patch('dls_checkout_module.vcs_git.is_repo_path', return_value=False)
    def test_given_invalid_source_then_error_raised(self, mock_in_repo):
        source = "controls/python/doesnotexist"
        expected_error_msg = \
            "Repository does not contain " + source

        dls_checkout_module.check_source_file_path_valid(source, self.parser)

        self.mock_error.assert_called_once_with(expected_error_msg)


class CheckModuleFilePathValidTest(unittest.TestCase):

    def setUp(self):
        self.parser = dls_checkout_module.make_parser()
        parse_error_patch = patch('dls_checkout_module.ArgParser.error')
        self.addCleanup(parse_error_patch.stop)
        self.mock_error = parse_error_patch.start()

    @patch('dls_checkout_module.os.path.isdir', return_value=False)
    def test_given_valid_module_then_no_error_raised(self, mock_isdir):
        module = "doesnotexistyet"

        dls_checkout_module.check_module_file_path_valid(module, self.parser)

        self.assertFalse(self.mock_error.call_count)

    @patch('dls_checkout_module.os.path.isdir', return_value=True)
    def test_given_existing_module_then_error_raised(self, mock_isdir):
        module = "dls_checkout_module_test.py"
        expected_error_msg = "Path already exists: " + module

        dls_checkout_module.check_module_file_path_valid(module, self.parser)

        self.mock_error.assert_called_once_with(expected_error_msg)


if __name__ == '__main__':

    # buffer option suppresses stdout generated from tested code
    unittest.main(buffer=True)