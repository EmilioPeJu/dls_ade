#!/bin/env dls-python

from dls_ade import dls_tar_module
import unittest
from pkg_resources import require
require("mock")
import mock
from mock import patch, ANY, MagicMock
from argparse import _StoreAction
from argparse import _StoreTrueAction


class MakeParserTest(unittest.TestCase):

    def setUp(self):
        self.parser = dls_tar_module.make_parser()

    def test_module_name_has_correct_attributes(self):
        arguments = self.parser._positionals._actions[4]
        self.assertEqual(arguments.type, str)
        self.assertEqual(arguments.dest, 'module_name')

    def test_release_has_correct_attributes(self):
        arguments = self.parser._positionals._actions[5]
        self.assertEqual(arguments.type, str)
        self.assertEqual(arguments.dest, 'release')

    def test_branch_argument_has_correct_attributes(self):
        option = self.parser._option_string_actions['-u']
        self.assertIsInstance(option, _StoreTrueAction)
        self.assertEqual(option.dest, "untar")
        self.assertIn("--untar", option.option_strings)

    def test_force_argument_has_correct_attributes(self):
        option = self.parser._option_string_actions['-e']
        self.assertIsInstance(option, _StoreAction)
        self.assertEqual(option.dest, "epics_version")
        self.assertIn("--epics_version", option.option_strings)


class CheckAreaTest(unittest.TestCase):

    def setUp(self):
        self.parser = dls_tar_module.make_parser()
        parse_error_patch = patch('dls_ade.dls_tar_module.ArgParser.error')
        self.addCleanup(parse_error_patch.stop)
        self.mock_error = parse_error_patch.start()

    def test_given_invalid_area_then_error_raised(self):
        args = MagicMock()
        args.area = "not_an_area"
        dls_tar_module.check_area(args, self.parser)

        self.mock_error.assert_called_once_with("Modules in area " + args.area + " cannot be archived")

    def test_given_support_area_then_error_raised(self):
        args = MagicMock()
        args.area = 'support'
        dls_tar_module.check_area(args, self.parser)

        self.assertFalse(self.mock_error.call_count)

    def test_given_ioc_area_then_error_raised(self):
        args = MagicMock()
        args.area = 'ioc'
        dls_tar_module.check_area(args, self.parser)

        self.assertFalse(self.mock_error.call_count)

    def test_given_python_area_then_error_raised(self):
        args = MagicMock()
        args.area = 'python'
        dls_tar_module.check_area(args, self.parser)

        self.assertFalse(self.mock_error.call_count)

    def test_given_matlab_area_then_error_raised(self):
        args = MagicMock()
        args.area = 'matlab'
        dls_tar_module.check_area(args, self.parser)

        self.assertFalse(self.mock_error.call_count)


class SetUpEpicsEnvironmentTest(unittest.TestCase):

    def setUp(self):
        self.parser = dls_tar_module.make_parser()
        parse_error_patch = patch('dls_ade.dls_tar_module.ArgParser.error')
        self.addCleanup(parse_error_patch.stop)
        self.mock_error = parse_error_patch.start()

    def test_given_invalid_epics_version_then_error_raised(self):
        args = MagicMock()
        args.epics_version = "not_an_epics_version"

        dls_tar_module.set_up_epics_environment(args, self.parser)

        self.mock_error.assert_called_once_with("Expected epics version like R3.14.8.2, got: " +
                                                args.epics_version)

    def test_given_valid_epics_version_then_no_error_raised(self):
        args = MagicMock()
        args.epics_version = 'R3.14.8.2.1.1'

        dls_tar_module.set_up_epics_environment(args, self.parser)

        self.assertFalse(self.mock_error.call_count)

    def test_given_valid_epics_version_without_R_then_no_error_raised(self):
        args = MagicMock()
        args.epics_version = '3.14.8.2.1.1'

        dls_tar_module.set_up_epics_environment(args, self.parser)

        self.assertFalse(self.mock_error.call_count)


class CheckTechnicalAreaTest(unittest.TestCase):

    def setUp(self):
        self.parser = dls_tar_module.make_parser()
        parse_error_patch = patch('dls_ade.dls_tar_module.ArgParser.error')
        self.addCleanup(parse_error_patch.stop)
        self.mock_error = parse_error_patch.start()

    def test_given_not_ioc_then_no_error_raised(self):
        args = MagicMock()
        args.area = 'not_ioc'

        dls_tar_module.check_technical_area(args, self.parser)

        self.assertFalse(self.mock_error.call_count)

    def test_given_area_ioc_and_length_module_two_then_no_error_raised(self):
        args = MagicMock()
        args.area = 'ioc'
        args.module_name = 'test/module'

        dls_tar_module.check_technical_area(args, self.parser)

        self.assertFalse(self.mock_error.call_count)

    def test_given_area_ioc_and_length_module_less_than_two_then_error_raised(self):
        args = MagicMock()
        args.area = 'ioc'
        args.module_name = 'test'
        expected_error_message = "Missing Technical Area under Beamline"

        dls_tar_module.check_technical_area(args, self.parser)

        self.mock_error.assert_called_once_with(expected_error_message)


class CheckFilePaths(unittest.TestCase):

    def setUp(self):
        self.parser = dls_tar_module.make_parser()
        parse_error_patch = patch('dls_ade.dls_tar_module.ArgParser.error')
        self.addCleanup(parse_error_patch.stop)
        self.mock_error = parse_error_patch.start()

    @patch('dls_ade.dls_tar_module.os.path.isfile', return_value=False)
    @patch('dls_ade.dls_tar_module.os.path.isdir', return_value=True)
    def test_given_not_untar_and_paths_valid_then_no_error_raised(self, _1, _2):
        args = MagicMock()
        args.untar = False

        release_dir = "valid_release"
        archive = "valid_release.tar.gz"

        dls_tar_module.check_file_paths(release_dir, archive, args, self.parser)

        self.assertFalse(self.mock_error.call_count)

    @patch('dls_ade.dls_tar_module.os.path.isfile', return_value=True)
    @patch('dls_ade.dls_tar_module.os.path.isdir', return_value=True)
    def test_given_not_untar_and_archive_exists_then_error_raised(self, _1, _2):
        args = MagicMock()
        args.untar = False

        release_dir = "valid_release"
        archive = "already_exists"
        expected_error_message = "Archive '" + archive + "' already exists"

        dls_tar_module.check_file_paths(release_dir, archive, args, self.parser)

        self.mock_error.assert_called_once_with(expected_error_message)

    @patch('dls_ade.dls_tar_module.os.path.isfile', return_value=False)
    @patch('dls_ade.dls_tar_module.os.path.isdir', return_value=False)
    def test_given_not_untar_and_release_dir_doesnt_exist_then_error_raised(self, _1, _2):
        args = MagicMock()
        args.untar = False

        release_dir = "doesnt_exist"
        archive = "valid_release.tar.gz"
        expected_error_message = "Path '" + release_dir + "' doesn't exist"

        dls_tar_module.check_file_paths(release_dir, archive, args, self.parser)

        self.mock_error.assert_called_once_with(expected_error_message)

    @patch('dls_ade.dls_tar_module.os.path.isfile', return_value=True)
    @patch('dls_ade.dls_tar_module.os.path.isdir', return_value=False)
    def test_given_untar_and_paths_valid_then_no_error_raised(self, _1, _2):
        args = MagicMock()
        args.untar = True

        release_dir = "valid_release"
        archive = "valid_release.tar.gz"

        dls_tar_module.check_file_paths(release_dir, archive, args, self.parser)

        self.assertFalse(self.mock_error.call_count)

    @patch('dls_ade.dls_tar_module.os.path.isfile', return_value=False)
    @patch('dls_ade.dls_tar_module.os.path.isdir', return_value=False)
    def test_given_untar_and_archive_doesnt_exist_then_no_error_raised(self, _1, _2):
        args = MagicMock()
        args.untar = True

        release_dir = "valid_release"
        archive = "doesnt_exist"
        expected_error_message = "Archive '" + archive + "' doesn't exist"

        dls_tar_module.check_file_paths(release_dir, archive, args, self.parser)

        self.mock_error.assert_called_once_with(expected_error_message)

    @patch('dls_ade.dls_tar_module.os.path.isfile', return_value=True)
    @patch('dls_ade.dls_tar_module.os.path.isdir', return_value=True)
    def test_given_untar_and_release_dir_exist_then_no_error_raised(self, _1, _2):
        args = MagicMock()
        args.untar = True

        release_dir = "already_exists"
        archive = "valid_release.tar.gz"
        expected_error_message = "Path '" + release_dir + "' already exists"

        dls_tar_module.check_file_paths(release_dir, archive, args, self.parser)

        self.mock_error.assert_called_once_with(expected_error_message)
