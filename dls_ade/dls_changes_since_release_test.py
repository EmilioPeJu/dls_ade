#!/bin/env dls-python

import unittest

from pkg_resources import require

from dls_ade import dls_changes_since_release

require("mock")
from mock import patch


class MakeParserTest(unittest.TestCase):

    def setUp(self):
        self.parser = dls_changes_since_release.make_parser()

    def test_module_name_has_correct_attributes(self):
        arguments = self.parser._positionals._actions[4]
        self.assertEqual(arguments.type, str)
        self.assertEqual(arguments.dest, 'module_name')


class CheckParsedArgumentsValidTest(unittest.TestCase):

    def setUp(self):
        self.parser = dls_changes_since_release.make_parser()
        parse_error_patch = patch('dls_ade.dls_changes_since_release.ArgParser.error')
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


class CheckTechnicalAreaTest(unittest.TestCase):

    def setUp(self):
        self.parser = dls_changes_since_release.make_parser()
        parse_error_patch = patch('dls_ade.dls_changes_since_release.ArgParser.error')
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


class MainTest(unittest.TestCase):
    pass
