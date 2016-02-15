#!/bin/env dls-python

import unittest
from pkg_resources import require
from dls_ade import dls_checkout_module

require("mock")
from mock import patch, MagicMock


class MakeParserTest(unittest.TestCase):

    def setUp(self):
        self.parser = dls_checkout_module.make_parser()

    @patch('dls_ade.dls_changes_since_release.ArgParser.add_branch_flag')
    def test_branch_set(self, parser_mock):

        dls_checkout_module.make_parser()

        parser_mock.assert_called_once_with(
            help_msg="Checkout a specific named branch rather than the default (master)")

    def test_module_name_has_correct_attributes(self):
        arguments = self.parser._positionals._actions[5]
        self.assertEqual(arguments.type, str)
        self.assertEqual(arguments.nargs, '?')
        self.assertEqual(arguments.dest, 'module_name')


class CheckTechnicalAreaTest(unittest.TestCase):

    def test_given_area_not_ioc_then_no_error_raised(self):
        area = "support"
        module = "test_module"

        dls_checkout_module.check_technical_area(area, module)

    def test_given_area_ioc_module_all_then_no_error_raised(self):
        area = "ioc"
        module = ""

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
            self.assertEqual(str(error), expected_error_msg)


if __name__ == '__main__':
    # buffer option suppresses stdout generated from tested code
    unittest.main(buffer=True)
