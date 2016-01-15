#!/bin/env dls-python

import unittest

from pkg_resources import require

from dls_ade import dls_list_branches

require("mock")
from mock import patch, MagicMock
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

    def test_given_area_not_ioc_then_no_error_raised(self):
        area = "support"
        module = "test_module"

        dls_list_branches.check_technical_area(area, module)

    def test_given_area_ioc_module_split_two_then_no_error_raised(self):
        area = "ioc"
        module = "modules/test_module"

        dls_list_branches.check_technical_area(area, module)

    def test_given_area_ioc_module_split_less_than_two_then_no_error_raised(self):
        area = "ioc"
        module = "test_module"
        expected_error_msg = "Missing Technical Area under Beamline"

        try:
            dls_list_branches.check_technical_area(area, module)
        except Exception as error:
            self.assertEqual(error.message, expected_error_msg)
