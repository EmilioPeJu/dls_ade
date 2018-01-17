#!/bin/env dls-python

from dls_ade import dls_tar_module
import unittest

from mock import patch, ANY, MagicMock
from argparse import _StoreAction
from argparse import _StoreTrueAction


class MakeParserTest(unittest.TestCase):

    def setUp(self):
        self.parser = dls_tar_module.make_parser()

    @patch('dls_ade.dls_changes_since_release.ArgParser.add_module_name_arg')
    def test_module_name_set(self, parser_mock):

        dls_tar_module.make_parser()

        parser_mock.assert_called_once_with()

    @patch('dls_ade.dls_changes_since_release.ArgParser.add_release_arg')
    def test_release_set(self, parser_mock):

        dls_tar_module.make_parser()

        parser_mock.assert_called_once_with()

    def test_untar_argument_has_correct_attributes(self):
        option = self.parser._option_string_actions['-u']
        self.assertIsInstance(option, _StoreTrueAction)
        self.assertEqual(option.dest, "untar")
        self.assertIn("--untar", option.option_strings)

    def test_epics_version_argument_has_correct_attributes(self):
        option = self.parser._option_string_actions['-e']
        self.assertIsInstance(option, _StoreAction)
        self.assertEqual(option.dest, "epics_version")
        self.assertIn("--epics_version", option.option_strings)


class CheckAreaArchivableTest(unittest.TestCase):

    def test_given_invalid_area_then_error_raised(self):
        area = "not_an_area"
        try:
            dls_tar_module.check_area_archivable(area)
        except Exception as error:
            self.assertEqual(str(error), "Modules in area " + area + " cannot be archived")

    def test_given_support_area_then_no_error_raised(self):
        area = 'support'

        dls_tar_module.check_area_archivable(area)

    def test_given_ioc_area_then_no_error_raised(self):
        area = 'ioc'

        dls_tar_module.check_area_archivable(area)

    def test_given_python_area_then_error_raised(self):
        area = 'python'

        dls_tar_module.check_area_archivable(area)

    def test_given_matlab_area_then_error_raised(self):
        area = 'matlab'

        dls_tar_module.check_area_archivable(area)


class CheckFilePaths(unittest.TestCase):

    @patch('dls_ade.dls_tar_module.os.path.isfile', return_value=False)
    @patch('dls_ade.dls_tar_module.os.path.isdir', return_value=True)
    def test_given_not_untar_and_paths_valid_then_no_error_raised(self, _1, _2):
        untar = False
        release_dir = "valid_release"
        archive = "valid_release.tar.gz"

        dls_tar_module.check_file_paths(release_dir, archive, untar)

    @patch('dls_ade.dls_tar_module.os.path.isfile', return_value=True)
    @patch('dls_ade.dls_tar_module.os.path.isdir', return_value=True)
    def test_given_not_untar_and_archive_exists_then_error_raised(self, _1, _2):
        untar = False
        release_dir = "valid_release"
        archive = "already_exists"
        expected_error_message = "Archive '" + archive + "' already exists"

        try:
            dls_tar_module.check_file_paths(release_dir, archive, untar)
        except Exception as error:
            self.assertEqual(str(error), expected_error_message)

    @patch('dls_ade.dls_tar_module.os.path.isfile', return_value=False)
    @patch('dls_ade.dls_tar_module.os.path.isdir', return_value=False)
    def test_given_not_untar_and_release_dir_doesnt_exist_then_error_raised(self, _1, _2):
        untar = False
        release_dir = "doesnt_exist"
        archive = "valid_release.tar.gz"
        expected_error_message = "Path '" + release_dir + "' doesn't exist"

        try:
            dls_tar_module.check_file_paths(release_dir, archive, untar)
        except Exception as error:
            self.assertEqual(str(error), expected_error_message)

    @patch('dls_ade.dls_tar_module.os.path.isfile', return_value=True)
    @patch('dls_ade.dls_tar_module.os.path.isdir', return_value=False)
    def test_given_untar_and_paths_valid_then_no_error_raised(self, _1, _2):
        untar = True
        release_dir = "valid_release"
        archive = "valid_release.tar.gz"

        dls_tar_module.check_file_paths(release_dir, archive, untar)

    @patch('dls_ade.dls_tar_module.os.path.isfile', return_value=False)
    @patch('dls_ade.dls_tar_module.os.path.isdir', return_value=False)
    def test_given_untar_and_archive_doesnt_exist_then_error_raised(self, _1, _2):
        untar = True
        release_dir = "valid_release"
        archive = "doesnt_exist"
        expected_error_message = "Archive '" + archive + "' doesn't exist"

        try:
            dls_tar_module.check_file_paths(release_dir, archive, untar)
        except Exception as error:
            self.assertEqual(str(error), expected_error_message)

    @patch('dls_ade.dls_tar_module.os.path.isfile', return_value=True)
    @patch('dls_ade.dls_tar_module.os.path.isdir', return_value=True)
    def test_given_untar_and_release_dir_exist_then_no_error_raised(self, _1, _2):
        untar = True
        release_dir = "already_exists"
        archive = "valid_release.tar.gz"
        expected_error_message = "Path '" + release_dir + "' already exists"

        try:
            dls_tar_module.check_file_paths(release_dir, archive, untar)
        except Exception as error:
            self.assertEqual(str(error), expected_error_message)
