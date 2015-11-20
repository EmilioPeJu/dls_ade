#!/bin/env dls-python

import unittest
import dls_changes_since_release
from pkg_resources import require
require("mock")
from mock import patch, ANY, MagicMock
from dls_ade import vcs_git
from argparse import _StoreAction
from argparse import _StoreTrueAction


class ParserTest(unittest.TestCase):

    def setUp(self):
        self.parser = dls_changes_since_release.make_parser()

    def test_area_option_has_correct_attributes(self):
        option = self.parser._option_string_actions['-a']
        self.assertIsInstance(option, _StoreAction)
        self.assertEqual(option.type, str)
        self.assertEqual(option.dest, "area")
        self.assertIn("--area", option.option_strings)


class CheckParsedOptionsValid(unittest.TestCase):

    def setUp(self):
        self.parser = dls_changes_since_release.make_parser()
        parse_error_patch = patch('dls_changes_since_release.ArgumentParser.error')
        self.addCleanup(parse_error_patch.stop)
        self.mock_error = parse_error_patch.start()

    def test_given_empty_module_name_then_error_raised(self):
        args = {}
        expected_error_msg = "Module name required"

        dls_changes_since_release.check_parsed_arguments_valid(args, self.parser)

        self.mock_error.assert_called_once_with(expected_error_msg)

    def test_given_module_name_then_no_error_raised(self):
        args = {'module_name': ""}

        dls_changes_since_release.check_parsed_arguments_valid(args, self.parser)

        self.assertFalse(self.mock_error.call_count)


class TestTechnicalAreaCheck(unittest.TestCase):

    def setUp(self):
        self.parser = dls_changes_since_release.make_parser()
        parse_error_patch = patch('dls_changes_since_release.ArgumentParser.error')
        self.addCleanup(parse_error_patch.stop)
        self.mock_error = parse_error_patch.start()

    def test_given_ioc_and_module_path_greater_than_1_then_no_error_raised(self):
        args = {'module': "testing/test", 'area': "ioc"}

        dls_changes_since_release.check_technical_area_valid(args, self.parser)

        self.assertFalse(self.mock_error.call_count)

    def test_given_ioc_and_module_path_one_or_less_then_error_raised(self):
        args = {'module': "test", 'area': "ioc"}
        expected_error_msg = "Missing Technical Area Under Beamline"

        dls_changes_since_release.check_technical_area_valid(args, self.parser)

        self.mock_error.assert_called_once_with(expected_error_msg)


class TestMain(unittest.TestCase):
    pass