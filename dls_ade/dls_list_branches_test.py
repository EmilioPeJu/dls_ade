#!/bin/env dls-python

import unittest

from pkg_resources import require

from dls_ade import dls_list_branches

require("mock")
from mock import patch
from argparse import _StoreAction
from argparse import _StoreTrueAction


class MakeParserTest(unittest.TestCase):

    def setUp(self):
        self.parser = dls_list_branches.make_parser()

    def test_module_name_has_correct_attributes(self):
        arguments = self.parser._positionals._actions[4]
        self.assertEqual(arguments.type, str)
        self.assertEqual(arguments.dest, 'module_name')


class CheckTechnicalAreaTest(unittest.TestCase):

    def setUp(self):
        self.parser = dls_list_branches.make_parser()
        parse_error_patch = patch('dls_ade.dls_list_branches.ArgParser.error')
        self.addCleanup(parse_error_patch.stop)
        self.mock_error = parse_error_patch.start()

    def test_given_area_not_ioc_then_no_error_raised(self):
        args = {'module_name': "test_module", 'area': "support"}

        dls_list_branches.check_technical_area(args, self.parser)

        self.assertFalse(self.mock_error.call_count)

    def test_given_area_ioc_module_split_two_then_no_error_raised(self):
        args = {'module_name': "modules/test_module", 'area': "ioc"}

        dls_list_branches.check_technical_area(args, self.parser)

        self.assertFalse(self.mock_error.call_count)

    def test_given_area_ioc_module_split_less_than_two_then_no_error_raised(self):
        args = {'module_name': "test_module", 'area': "ioc"}
        expected_error_msg = "Missing Technical Area under Beamline"

        dls_list_branches.check_technical_area(args, self.parser)

        self.mock_error.assert_called_once_with(expected_error_msg)