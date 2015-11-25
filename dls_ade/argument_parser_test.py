#!/bin/env dls-python

import unittest
from argument_parser import ArgParser
from argparse import _StoreAction
from argparse import _StoreTrueAction


class ArgParserInitTest(unittest.TestCase):

    def setUp(self):
        self.parser = ArgParser("")

    def test_area_argument_has_correct_attributes(self):
        option = self.parser._option_string_actions['-a']
        self.assertIsInstance(option, _StoreAction)
        self.assertEqual(option.type, str)
        self.assertEqual(option.dest, "area")
        self.assertIn("--area", option.option_strings)

    def test_python_argument_has_correct_attributes(self):
        option = self.parser._option_string_actions['-p']
        self.assertIsInstance(option, _StoreTrueAction)
        self.assertEqual(option.dest, "python")
        self.assertIn("--python", option.option_strings)

    def test_ioc_argument_has_correct_attributes(self):
        option = self.parser._option_string_actions['-i']
        self.assertIsInstance(option, _StoreTrueAction)
        self.assertEqual(option.dest, "ioc")
        self.assertIn("--ioc", option.option_strings)


class ArgParserParseArgsTest(unittest.TestCase):

    def setUp(self):
        self.parser = ArgParser("")

    def test_given_dash_i_in_args_then_area_is_ioc(self):
        args = self.parser.parse_args("-i".split())

        self.assertEqual(args.area, "ioc")

    def test_given_double_dash_ioc_in_args_then_area_is_ioc(self):
        args = self.parser.parse_args("--ioc".split())

        self.assertEqual(args.area, "ioc")

    def test_given_dash_p_in_args_then_area_is_python(self):
        args = self.parser.parse_args("-p".split())

        self.assertEqual(args.area, "python")

    def test_given_double_dash_python_in_args_then_area_is_python(self):
        args = self.parser.parse_args("--python".split())

        self.assertEqual(args.area, "python")

if __name__ == '__main__':

    # buffer option suppresses stdout generated from tested code
    unittest.main(buffer=True)
