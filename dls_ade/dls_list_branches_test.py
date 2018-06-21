#!/bin/env dls-python

import unittest
from dls_ade import dls_list_branches
from mock import patch, MagicMock


class MakeParserTest(unittest.TestCase):

    @patch('dls_ade.dls_changes_since_release.ArgParser.add_module_name_arg')
    def test_module_name_set(self, parser_mock):

        dls_list_branches.make_parser()

        parser_mock.assert_called_once_with()
