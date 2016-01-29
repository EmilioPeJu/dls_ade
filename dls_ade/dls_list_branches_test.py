#!/bin/env dls-python

import unittest

from pkg_resources import require

from dls_ade import dls_list_branches

require("mock")
from mock import patch, MagicMock
from argparse import _StoreAction
from argparse import _StoreTrueAction


class MakeParserTest(unittest.TestCase):

    @patch('dls_ade.dls_changes_since_release.ArgParser.add_module_name_arg')
    def test_module_name_set(self, module_mock):

        dls_list_branches.make_parser()

        module_mock.assert_called_once_with()
