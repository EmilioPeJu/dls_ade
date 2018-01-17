#!/bin/env dls-python

import unittest
from dls_ade import dls_changes_since_release
from mock import ANY, patch


class MakeParserTest(unittest.TestCase):

    @patch('dls_ade.dls_changes_since_release.ArgParser.add_module_name_arg')
    def test_module_name_set(self, parser_mock):

        dls_changes_since_release.make_parser()

        parser_mock.assert_called_once_with()
