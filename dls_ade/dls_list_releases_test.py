#!/bin/env dls-python

from dls_ade import dls_list_releases
import unittest
from argparse import _StoreAction
from argparse import _StoreTrueAction

from pkg_resources import require
require("mock")
from mock import patch, ANY, MagicMock


class GetRhelVersionTest(unittest.TestCase):

    @patch('dls_ade.dls_list_releases.platform.system', return_value='Linux')
    @patch('dls_ade.dls_list_releases.platform.dist', return_value=['redhat', 'test_release_str.test', 'test_name'])
    def test_given_Linux_Redhat_then_return_release(self, _1, _2):
        release = dls_list_releases.get_rhel_version()

        self.assertEqual(release, 'test_release_str')

    @patch('dls_ade.dls_list_releases.platform.system', return_value='Linux')
    @patch('dls_ade.dls_list_releases.platform.dist', return_value=['not_redhat', 'test_release_str.test', 'test_name'])
    def test_given_Linux_not_Redhat_then_return_default(self, _1, _2):
        release = dls_list_releases.get_rhel_version()

        self.assertEqual(release, '6')

    @patch('dls_ade.dls_list_releases.platform.system', return_value='not_Linux')
    @patch('dls_ade.dls_list_releases.platform.dist', return_value=['redhat', 'test_release_str.test', 'test_name'])
    def test_given_not_Linux_then_return_default(self, _1, _2):
        release = dls_list_releases.get_rhel_version()

        self.assertEqual(release, '6')


class MakeParserTest(unittest.TestCase):

    def setUp(self):
        self.parser = dls_list_releases.make_parser()

    @patch('dls_ade.dls_changes_since_release.ArgParser.add_module_name_arg')
    def test_module_name_set(self, parser_mock):

        dls_list_releases.make_parser()

        parser_mock.assert_called_once_with()

    @patch('dls_ade.dls_changes_since_release.ArgParser.add_git_flag')
    def test_git_flag_set(self, parser_mock):

        dls_list_releases.make_parser()

        parser_mock.assert_called_once_with(
            help_msg="Print releases available in git")

    @patch('dls_ade.dls_changes_since_release.ArgParser.add_epics_version_flag')
    def test_epics_version_flag_set(self, parser_mock):

        dls_list_releases.make_parser()

        parser_mock.assert_called_once_with()

    def test_latest_argument_has_correct_attributes(self):
        option = self.parser._option_string_actions['-l']
        self.assertIsInstance(option, _StoreTrueAction)
        self.assertEqual(option.dest, "latest")
        self.assertIn("--latest", option.option_strings)

    def test_rhel_version_argument_has_correct_attributes(self):
        option = self.parser._option_string_actions['-r']
        self.assertIsInstance(option, _StoreAction)
        self.assertEqual(option.dest, "rhel_version")
        self.assertIn("--rhel_version", option.option_strings)
