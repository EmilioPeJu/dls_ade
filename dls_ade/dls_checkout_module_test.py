#!/bin/env dls-python

import unittest
from dls_ade import dls_checkout_module
from mock import patch, MagicMock


class MakeParserTest(unittest.TestCase):

    def setUp(self):
        self.parser = dls_checkout_module.make_parser()

    @patch('dls_ade.dls_changes_since_release.ArgParser.add_branch_flag')
    def test_branch_set(self, parser_mock):

        dls_checkout_module.make_parser()

        parser_mock.assert_called_once_with(
            help_msg="Checkout a specific named branch rather than the default (master)")

    def test_parser_has_correct_attributes(self):
        args = self.parser.parse_args("-p module1".split())
        self.assertEqual(args.module_name, "module1")
        self.assertEqual(args.area, "python")

    def test_parser_does_not_accept_version(self):
        try:
            self.parser.parse_args("-p module1 0-1".split())
            self.fail("dls-checkout-module should not accept a version")
        except SystemExit:
            pass


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
