#!/bin/env dls-python

import unittest
import dls_ade.dls_start_new_module
from argparse import _StoreTrueAction


class MakeParserTest(unittest.TestCase):

    def setUp(self):
        self.parser = dls_ade.dls_start_new_module.make_parser()

    def test_module_name_has_correct_attributes(self):
        arguments = self.parser._positionals._actions[4]
        self.assertEqual(arguments.type, str)
        self.assertEqual(arguments.dest, 'module_name')

    def test_branch_argument_has_correct_attributes(self):
        option = self.parser._option_string_actions['-n']
        self.assertIsInstance(option, _StoreTrueAction)
        self.assertEqual(option.dest, "no_import")
        self.assertIn("--no-import", option.option_strings)

    def test_force_argument_has_correct_attributes(self):
        option = self.parser._option_string_actions['-f']
        self.assertIsInstance(option, _StoreTrueAction)
        self.assertEqual(option.dest, "fullname")
        self.assertIn("--fullname", option.option_strings)


if __name__ == '__main__':

    # buffer option suppresses stdout generated from tested code
    unittest.main(buffer=True)
