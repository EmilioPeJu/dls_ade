#!/bin/env dls-python

import unittest
import dls_ade.dls_start_new_module
from argparse import _StoreTrueAction
from mock import patch
from dls_ade.exceptions import VerificationError


class MakeParserTest(unittest.TestCase):

    def setUp(self):
        self.parser = dls_ade.dls_start_new_module.make_parser()

    @patch('dls_ade.dls_changes_since_release.ArgParser.add_module_name_arg')
    def test_module_name_set(self, parser_mock):

        dls_ade.dls_start_new_module.make_parser()

        parser_mock.assert_called_once_with()

    def test_no_import_argument_has_correct_attributes(self):
        option = self.parser._option_string_actions['-n']
        self.assertIsInstance(option, _StoreTrueAction)
        self.assertEqual(option.dest, "no_import")
        self.assertIn("--no-import", option.option_strings)

    def test_fullname_argument_has_correct_attributes(self):
        option = self.parser._option_string_actions['-f']
        self.assertIsInstance(option, _StoreTrueAction)
        self.assertEqual(option.dest, "fullname")
        self.assertIn("--fullname", option.option_strings)

    @patch("dls_ade.dls_start_new_module.Server.create_remote_repo")
    @patch("dls_ade.dls_start_new_module.Server.is_server_repo")
    def test_create_empty_project_name_taken(self,
                                             mock_is_server_repo,
                                             mock_create_remote_repo):

        # Repo already exists
        mock_is_server_repo.return_value = True

        # Raise exception and do not try to create the repo
        with self.assertRaises(VerificationError):
            dls_ade.dls_start_new_module.create_empty_remote("ioc",
                                                             "BL99P-TS-IOC-03")
        mock_create_remote_repo.assert_not_called()

    @patch("dls_ade.dls_start_new_module.Server.create_remote_repo")
    @patch("dls_ade.dls_start_new_module.Server.is_server_repo")
    def test_create_empty_project_name_avalable(self,
                                                mock_is_server_repo,
                                                mock_create_remote_repo):
        # Repo does not already exist
        mock_is_server_repo.return_value = False

        dls_ade.dls_start_new_module.create_empty_remote("ioc",
                                                         "BL99P-TS-IOC-03")
        mock_create_remote_repo.assert_called_once()


    def test_create_empty_project_quiet(self):
        pass


if __name__ == '__main__':

    # buffer option suppresses stdout generated from tested code
    unittest.main(buffer=True)
