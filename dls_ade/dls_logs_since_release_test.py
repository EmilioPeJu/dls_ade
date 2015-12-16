#!/bin/env dls-python

import unittest
from dls_ade import dls_logs_since_release
import logging

from pkg_resources import require
require("mock")
from mock import patch, MagicMock, ANY
from argparse import _StoreAction
from argparse import _StoreTrueAction


class MakeParserTest(unittest.TestCase):

    def setUp(self):
        self.parser = dls_logs_since_release.make_parser()

    def test_module_name_has_correct_attributes(self):
        arguments = self.parser._positionals._actions[4]
        self.assertEqual(arguments.type, str)
        self.assertEqual(arguments.dest, 'module_name')

    def test_earlier_argument_has_correct_attributes(self):
        option = self.parser._option_string_actions['-e']
        self.assertIsInstance(option, _StoreAction)
        self.assertEqual(option.type, int)
        self.assertEqual(option.dest, "earlier_release")
        self.assertIn("--earlier_release", option.option_strings)

    def test_later_argument_has_correct_attributes(self):
        option = self.parser._option_string_actions['-l']
        self.assertIsInstance(option, _StoreAction)
        self.assertEqual(option.dest, "later_release")
        self.assertIn("--later_release", option.option_strings)

    def test_verbose_argument_has_correct_attributes(self):
        option = self.parser._option_string_actions['-v']
        self.assertIsInstance(option, _StoreTrueAction)
        self.assertEqual(option.dest, "verbose")
        self.assertIn("--verbose", option.option_strings)

    def test_raw_argument_has_correct_attributes(self):
        option = self.parser._option_string_actions['-r']
        self.assertIsInstance(option, _StoreTrueAction)
        self.assertEqual(option.dest, "raw")
        self.assertIn("--raw", option.option_strings)


class CheckTechnicalAreaTest(unittest.TestCase):
    # >>> Get MagicMock version from other checkout module branch
    pass


class ColourTest(unittest.TestCase):

    def test_given_word_and_raw_then_return_word(self):
        word = "test_word"
        col = "test_col"

        args = MagicMock()
        args.raw = True

        return_value = dls_logs_since_release.colour(word, col, args)

        self.assertEqual(return_value, word)

    def test_given_word_and_not_raw_then_return_formatted_word(self):
        word = "test_word"
        col = 5
        expected_return_value = "\x1b[" + str(col) + "m" + str(word) + "\x1b[0m"

        args = MagicMock()
        args.raw = False

        return_value = dls_logs_since_release.colour(word, col, args)

        self.assertEqual(return_value, expected_return_value)
