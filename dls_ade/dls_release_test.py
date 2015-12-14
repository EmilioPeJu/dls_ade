#!/bin/env dls-python

import unittest
import logging
from dls_ade import dls_release
from pkg_resources import require
require("mock")
from mock import patch, ANY, MagicMock
from argparse import _StoreAction
from argparse import _StoreTrueAction

logging.basicConfig(level=logging.DEBUG)


class ParserTest(unittest.TestCase):

    def setUp(self):
        self.parser = dls_release.make_parser()

    def test_module_name_has_correct_attributes(self):
        pass

    def test_release_has_correct_attributes(self):
        pass

    def test_branch_option_has_correct_attributes(self):
        option = self.parser._option_string_actions['-b']
        self.assertIsInstance(option, _StoreAction)
        self.assertEqual(option.type, str)
        self.assertEqual(option.dest, "branch")
        self.assertIn("--branch", option.option_strings)

    def test_force_option_has_correct_attributes(self):
        option = self.parser._option_string_actions['-f']
        self.assertIsInstance(option, _StoreTrueAction)
        self.assertEqual(option.dest, "force")
        self.assertIn("--force", option.option_strings)

    def test_no_test_build_option_has_correct_attributes(self):
        option = self.parser._option_string_actions['-t']
        self.assertIsInstance(option, _StoreTrueAction)
        self.assertEqual(option.dest, "skip_test")
        self.assertIn("--no-test-build", option.option_strings)

    def test_local_build_option_has_correct_attributes(self):
        option = self.parser._option_string_actions['-l']
        self.assertIsInstance(option, _StoreTrueAction)
        self.assertEqual(option.dest, "local_build")
        self.assertIn("--local-build-only", option.option_strings)

    def test_test_build_only_option_has_correct_attributes(self):
        option = self.parser._option_string_actions['-T']
        self.assertIsInstance(option, _StoreTrueAction)
        self.assertEqual(option.dest, "test_only")
        self.assertIn("--test_build-only", option.option_strings)

    def test_epics_version_option_has_correct_attributes(self):
        option = self.parser._option_string_actions['-e']
        self.assertIsInstance(option, _StoreAction)
        self.assertEqual(option.type, str)
        self.assertEqual(option.dest, "epics_version")
        self.assertIn("--epics_version", option.option_strings)

    def test_message_option_has_correct_attributes(self):
        option = self.parser._option_string_actions['-m']
        self.assertIsInstance(option, _StoreAction)
        self.assertEqual(option.type, str)
        self.assertEqual(option.default, "")
        self.assertEqual(option.dest, "message")
        self.assertIn("--message", option.option_strings)

    def test_next_version_option_has_correct_attributes(self):
        option = self.parser._option_string_actions['-n']
        self.assertIsInstance(option, _StoreTrueAction)
        self.assertEqual(option.dest, "next_version")
        self.assertIn("--next_version", option.option_strings)

    def test_git_option_has_correct_attributes(self):
        option = self.parser._option_string_actions['-g']
        self.assertIsInstance(option, _StoreTrueAction)
        self.assertEqual(option.dest, "git")
        self.assertIn("--git", option.option_strings)

    def test_rhel_version_option_has_correct_attributes(self):
        option = self.parser._option_string_actions['-r']
        self.assertIsInstance(option, _StoreAction)
        self.assertEqual(option.type, str)
        self.assertEqual(option.dest, "rhel_version")
        self.assertIn("--rhel_version", option.option_strings)

    def test_windows_option_has_correct_attributes(self):
        option = self.parser._option_string_actions['-w']
        self.assertIsInstance(option, _StoreAction)
        self.assertEqual(option.type, str)
        self.assertEqual(option.dest, "windows")
        
    def test_has_windows_option_with_short_name_w_long_name_windows(self):
        option = self.parser._option_string_actions['-w']
        self.assertIsNotNone(option)
        self.assertIn("--windows", option.option_strings)


class TestCreateBuildObject(unittest.TestCase):

    @patch('dls_ade.dls_release.dlsbuild.default_build')
    def test_given_empty_options_then_default_build_called_with_None(self, mock_default):

        options = FakeOptions()
        dls_release.create_build_object(options)

        self.assertTrue(mock_default.called)
        mock_default.assert_called_once_with(None)

    @patch('dls_ade.dls_release.dlsbuild.default_build')
    def test_given_epicsversion_then_default_build_called_with_epics_version(self, mock_default):
        version = "R3.14.12.3"

        options = FakeOptions(epics_version=version)

        dls_release.create_build_object(options)

        mock_default.assert_called_once_with(version)

    @patch('dls_ade.dls_release.dlsbuild.RedhatBuild')
    def test_given_rhel_version_then_RedhatBuild_called_with_rhel_and_epics_version(self, mock_default):
        rhel_version = "25"

        options = FakeOptions(rhel_version=rhel_version)

        dls_release.create_build_object(options)

        mock_default.assert_called_once_with(rhel_version, None)

    @patch('dls_ade.dls_release.dlsbuild.RedhatBuild')
    def test_given_rhel_version_then_RedhatBuild_called_with_rhel_and_epics_version(self, mock_build):
        rhel_version = "25"
        epics_version = "R3.14.12.3"

        options = FakeOptions(
            rhel_version=rhel_version,
            epics_version=epics_version)

        dls_release.create_build_object(options)

        mock_build.assert_called_once_with(rhel_version,epics_version)

    @patch('dls_ade.dls_release.dlsbuild.WindowsBuild')
    def test_given_windows_option_without_rhel_then_WindowsBuild_called_with_windows_and_epics_version(self, mock_build):
        windows = 'xp'

        options = FakeOptions(windows=windows)

        dls_release.create_build_object(options)

        mock_build.assert_called_once_with(windows, None)

    @patch('dls_ade.dls_release.dlsbuild.Builder.set_area')
    def test_given_any_option_then_set_area_called_with_default_area_option(
        self, mock_set):
        options = FakeOptions()

        dls_release.create_build_object(options)

        mock_set.assert_called_once_with(options.area)

    @patch('dls_ade.dls_release.dlsbuild.Builder.set_area')
    def test_given_area_option_then_set_area_called_with_given_area_option(self, mock_set):
        area = 'python'

        options = FakeOptions(area=area)

        dls_release.create_build_object(options)

        mock_set.assert_called_once_with(options.area)

    @patch('dls_ade.dls_release.dlsbuild.Builder.set_force')
    def test_given_any_option_then_set_force_called_with_default_force_option(self, mock_set):
        options = FakeOptions()

        dls_release.create_build_object(options)

        mock_set.assert_called_once_with(None)

    @patch('dls_ade.dls_release.dlsbuild.Builder.set_force')
    def test_given_force_option_then_set_force_called_with_given_force_option(self, mock_set):
        force = True
        options = FakeOptions(force=force)

        dls_release.create_build_object(options)

        mock_set.assert_called_once_with(True)


class TestCheckParsedOptionsValid(unittest.TestCase):

    def setUp(self):
        self.parser = dls_release.make_parser()
        parse_error_patch = patch('dls_ade.dls_release.ArgParser.error')
        self.addCleanup(parse_error_patch.stop)
        self.mock_error = parse_error_patch.start()
        self.args = MagicMock()
        self.args.module_name = ""
        self.args.release = ""
        self.args.next_version = False

    def test_given_no_module_name_then_parser_error_specifying_no_module_name(self):
        expected_error_msg = 'Module name not specified'

        dls_release.check_parsed_arguments_valid(self.args, self.parser)

        self.mock_error.assert_called_once_with(expected_error_msg)

    def test_given_no_release_then_parser_error_called_specifying_no_module_version(self):
        self.args.module_name = "build"
        expected_error_msg = 'Module version not specified'

        dls_release.check_parsed_arguments_valid(self.args, self.parser)

        self.mock_error.assert_called_once_with(expected_error_msg)

    def test_given_area_option_of_etc_and_module_equals_build_then_parser_error_specifying_this(self):

        self.args.module_name = "build"
        self.args.release = "12"
        self.args.area = "etc"

        expected_error_msg = 'Cannot release etc/build or etc/redirector as'
        expected_error_msg += ' modules - use configure system instead'

        dls_release.check_parsed_arguments_valid(self.args, self.parser)

        self.mock_error.assert_called_once_with(expected_error_msg)

    def test_given_area_option_of_etc_and_module_equals_redirector_then_parser_error_specifying_this(self):
        self.args.module_name = "redirector"
        self.args.release = "12"
        self.args.area = "etc"

        expected_error_msg = 'Cannot release etc/build or etc/redirector as'
        expected_error_msg += ' modules - use configure system instead'

        dls_release.check_parsed_arguments_valid(self.args, self.parser)

        self.mock_error.assert_called_once_with(expected_error_msg)

    def test_given_area_option_of_etc_and_module_not_build_then_parser_error_not_called(self):

        self.args.module_name = "not build"
        self.args.release = "12"
        self.args.area = "etc"
        self.args.git = False

        dls_release.check_parsed_arguments_valid(self.args, self.parser)

        self.assertFalse(self.mock_error.call_count)

    def test_given_default_area_and_module_of_redirector_then_parser_error_not_called(self):

        self.args.module_name = "redirector"
        self.args.release = "12"
        self.args.area = "support"
        self.args.git = False

        dls_release.check_parsed_arguments_valid(self.args, self.parser)

        self.assertFalse(self.mock_error.call_count)

    def test_given_next_version_and_git_flag_then_parser_error_called(self):

        self.args.module_name = "module_name"
        self.args.release = "12"
        self.args.area = "support"
        self.args.next_version = True
        self.args.git = True

        expected_error_message = "When git is specified, version number must be provided"

        dls_release.check_parsed_arguments_valid(self.args, self.parser)

        self.mock_error.assert_called_once_with(expected_error_message)

    def test_given_args_list_length_1_and_next_version_flag_then_parser_error_not_called(self):

        self.args.module_name = "redirector"
        self.args.release = ""
        self.args.area = "support"
        self.args.next_version = True
        self.args.git = False

        dls_release.check_parsed_arguments_valid(self.args, self.parser)

        self.assertFalse(self.mock_error.call_count)

    def test_given_git_and_archive_area_else_good_options_then_raise_error(self):

        self.args.module_name = "module"
        self.args.release = "version"
        self.args.area = "archive"
        self.args.git = True

        expected_error_message = self.args.area + " area not supported by git"

        dls_release.check_parsed_arguments_valid(self.args, self.parser)

        self.mock_error.assert_called_once_with(expected_error_message)

    def test_given_git_and_epics_area_else_good_options_then_raise_error(self):

        self.args.module_name = "module"
        self.args.release = "version"
        self.args.area = "epics"
        self.args.git = True

        expected_error_message = self.args.area + " area not supported by git"

        dls_release.check_parsed_arguments_valid(self.args, self.parser)

        self.mock_error.assert_called_once_with(expected_error_message)

    def test_given_git_and_matlab_area_else_good_options_then_raise_error(self):

        self.args.module_name = "module"
        self.args.release = "version"
        self.args.area = "matlab"
        self.args.git = True

        expected_error_message = self.args.area + " area not supported by git"

        dls_release.check_parsed_arguments_valid(self.args, self.parser)

        self.mock_error.assert_called_once_with(expected_error_message)

    def test_given_git_and_etc_area_else_good_options_then_raise_error(self):

        self.args.module_name = "module"
        self.args.release = "version"
        self.args.area = "etc"
        self.args.git = True

        expected_error_message = self.args.area + " area not supported by git"

        dls_release.check_parsed_arguments_valid(self.args, self.parser)

        self.mock_error.assert_called_once_with(expected_error_message)

    def test_given_git_and_tools_area_else_good_options_then_error_not_raised(self):

        self.args.module_name = "module"
        self.args.release = "version"
        self.args.area = "tools"
        self.args.git = True

        dls_release.check_parsed_arguments_valid(self.args, self.parser)

        self.assertFalse(self.mock_error.call_count)


class TestCreateVCSObject(unittest.TestCase):

    @patch('dls_ade.dls_release.vcs_svn.Svn')
    @patch('dls_ade.dls_release.vcs_git.Git')
    def test_given_git_option_then_git_vcs_object_created(self, mock_git, mock_svn):

        module = 'dummy'
        options = FakeOptions(git=True)

        vcs = dls_release.create_vcs_object(module, options)

        mock_git.assert_called_once_with(module, options)
        self.assertFalse(mock_svn.called)

    @patch('dls_ade.dls_release.vcs_svn.Svn')
    @patch('dls_ade.dls_release.vcs_git.Git')
    def test_not_given_git_option_then_svn_vcs_object_created(self, mock_git, mock_svn):

        module = 'dummy'
        options = FakeOptions()

        vcs = dls_release.create_vcs_object(module, options)

        mock_svn.assert_called_once_with(module, options)
        self.assertFalse(mock_git.called)


class TestNextVersionNumber(unittest.TestCase):

    def test_given_empty_list_of_releases_then_return_first_version_number(self):

        releases = []
        expected_version = "0-1"

        version = dls_release.next_version_number(releases)

        self.assertEqual(version, expected_version)

    def test_given_list_of_one_release_then_return_incremented_latest_version_number(self):
        
        releases = ['5-5']
        expected_version = '5-6'

        version = dls_release.next_version_number(releases)

        self.assertEqual(version, expected_version)

    def test_given_list_of_complex_releases_then_return_incremented_latest_version_number(self):

        releases = ['1-3-5dls7','2-3-5dls7','2-3-4dls8','2-3-5dls8']
        expected_version = '2-3-5dls9'

        version = dls_release.next_version_number(releases)

        self.assertEqual(version, expected_version)


class TestGetLastRelease(unittest.TestCase):

    def test_given_list_of_one_release_number_then_return_that_number(self):

        releases = ['1-5-3-4']
        expected_version = releases[0]

        version = dls_release.get_last_release(releases)

        self.assertEqual(version, expected_version)

    def test_given_list_of_releases_with_diff_major_number_then_return_latest_version(self):

        releases = ['1-0', '3-0', '2-0']
        expected_version = releases[1]

        version = dls_release.get_last_release(releases)

        self.assertEqual(version, expected_version)

    def test_given_list_of_complex_releases_then_return_latest_version(self):

        releases = ['1-3-5dls7', '2-3-5dls7', '2-3-4dls8', '2-3-5dls8']
        expected_version = releases[-1]

        version = dls_release.get_last_release(releases)

        self.assertEqual(version, expected_version)


class TestFormatArgumentVersion(unittest.TestCase):

    def test_given_string_arg_with_periods_then_return_same_string_with_dashes(self):

        arg_version = '1.4.3dls5'

        version = dls_release.format_argument_version(arg_version)

        self.assertEqual(len(version), len(arg_version))
        self.assertFalse('.' in version)
        self.assertEqual(arg_version.split('.'), version.split('-'))

    def test_given_empty_string_arg_then_return_empty_string(self):

        arg_version = ''

        self.assertEqual(arg_version, dls_release.format_argument_version(arg_version))

    def test_given_string_arg_with_no_dots_return_same_string(self):

        arg_version = '1-4'

        self.assertEqual(arg_version, dls_release.format_argument_version(arg_version))


class TestIncrementVersionNumber(unittest.TestCase):

    def test_given_single_digit_then_return_incremented_digit(self):

        release_number = '4'
        expected_number = '5'

        incremented_number = dls_release.increment_version_number(release_number)

        self.assertEqual(incremented_number, expected_number)

    def test_given_two_digit_then_return_number_with_most_minor_digit_incremented(self):

        release_number = '4-5'
        expected_number = '4-6'

        incremented_number = dls_release.increment_version_number(release_number)

        self.assertEqual(incremented_number, expected_number)

    def test_given_dls_release_number_then_return_with_incremented_most_minor_number(self):

        release_number = '4-5dls12'
        expected_number = '4-5dls13'

        incremented_number = dls_release.increment_version_number(release_number)

        self.assertEqual(incremented_number, expected_number)


class TestConstructInfoMessage(unittest.TestCase):

    def test_given_default_args_then_construct_specific_string(self):
        
        module = 'dummy'
        version = '1-0'
        options = FakeOptions()
        build = dls_release.create_build_object(options)

        expected_message = 'Releasing %s %s from trunk,' % (module, version)
        expected_message += ' using %s build server' % build.get_server()
        expected_message += ' and epics %s' % build.epics()

        returned_message = dls_release.construct_info_message(
            module, options, version, build)

        self.assertEqual(expected_message, returned_message)

    def test_given_default_args_and_branch_then_construct_specific_string_referencing_branch(self):

        module = 'dummy'
        version = '3-5'
        options = FakeOptions(branch='new_feature')
        build = dls_release.create_build_object(options)

        expected_message = 'Releasing %s %s from branch %s,' % (
            module, version, options.branch)
        expected_message += ' using %s build server' % build.get_server()
        expected_message += ' and epics %s' % build.epics()

        returned_message = dls_release.construct_info_message(
            module, options, version, build)

        self.assertEqual(expected_message, returned_message)

    def test_given_default_args_and_ioc_area_then_construct_specific_string(self):

        module = 'dummy'
        version = '1-0'
        options = FakeOptions(area='ioc')
        build = dls_release.create_build_object(options)

        expected_message = 'Releasing %s %s from trunk,' % (module, version)
        expected_message += ' using %s build server' % build.get_server()
        expected_message += ' and epics %s' % build.epics()

        returned_message = dls_release.construct_info_message(
            module, options, version, build)

        self.assertEqual(expected_message, returned_message)

    def test_if_area_not_support_or_ioc_then_return_string_without_epics_specified(self):

        module = 'dummy'
        version = '1-0'
        options = FakeOptions(area='python')
        build = dls_release.create_build_object(options)

        returned_message = dls_release.construct_info_message(
            module, options, version, build)

        self.assertFalse('epics' in returned_message)
        self.assertFalse(build.epics() in returned_message)


class TestCheckEpicsVersion(unittest.TestCase):

    def test_given_epics_option_then_return_true(self):

        e_module = 'some_epics_version'
        e_option = 'specified_epics_version'
        e_build = 'some_other_epics_version'

        sure = dls_release.check_epics_version_consistent(
            e_module, e_option, e_build)

        self.assertTrue(sure)

    @patch('dls_ade.dls_release.ask_user_input', return_value='n')
    def test_given_no_epics_option_and_mismatched_module_and_build_epics_then_ask_user_for_input(self, mock_ask):

        e_option = None
        e_module = 'specified_epics_version'
        e_build = 'some_other_epics_version'

        sure = dls_release.check_epics_version_consistent(
            e_module, e_option, e_build)

        mock_ask.assert_called_once_with(ANY)

    def test_given_no_epics_option_and_matching_module_and_build_epics_then_return_true(self):

        e_option = None
        e_module = 'specified_epics_version'
        e_build = 'specified_epics_version'

        sure = dls_release.check_epics_version_consistent(
            e_module, e_option, e_build)

        self.assertTrue(sure)

    @patch('dls_ade.dls_release.ask_user_input', return_value='n')
    def test_given_no_epics_option_and_matching_module_and_build_epics_except_build_spcificies_64bit_then_return_true(self, mock_ask):

        e_option = None
        e_module = 'R3.14.11'
        e_build = 'R3.14.11_64'

        sure = dls_release.check_epics_version_consistent(
            e_module, e_option, e_build)

        self.assertFalse(mock_ask.call_count, "shouldn't have called ask_user_input()")
        self.assertTrue(sure)


class TestGetModuleEpicsVersion(unittest.TestCase):

    def test_given_vcs_object_can_return_filecontents_with_epics_version_mentioned_then_return_epics_version(self):
        
        expected_epics = 'R3.14.12.3'

        module_epics = dls_release.get_module_epics_version(FakeVcs())

        self.assertEqual(module_epics, expected_epics)

    def test_given_vcs_object_can_return_filecontents_without_epics_version_mentioned_then_return_empty_list(self):

        FakeVcs = MagicMock()
        FakeVcs.cat.return_value = 'BLGUI = $(SUPPORT)/BLGui/3-5'
        module_epics = dls_release.get_module_epics_version(FakeVcs)

        self.assertFalse(len(module_epics))


class TestPerformTestBuild(unittest.TestCase):

    def setUp(self):

        self.fake_build = MagicMock()

    def test_given_any_option_when_called_then_return_string_and_test_failure_bool(self):

        test_message, test_fail = dls_release.perform_test_build(
            self.fake_build, FakeOptions(), FakeVcs())

        self.assertIsInstance(test_message, str)
        self.assertIsInstance(test_fail, bool)

    def test_given_local_test_build_not_possible_when_Called_then_return_specific_string(self):

        options = FakeOptions()
        self.fake_build.local_test_possible = MagicMock(return_value=False)
        expected_message = "Local test build not possible since local system "
        expected_message += "not the same OS as build server"

        test_message, test_fail = dls_release.perform_test_build(
            self.fake_build, FakeOptions(), FakeVcs())

        self.assertEqual(test_message, expected_message)

    def test_given_local_test_build_possible_then_returned_string_begins_with_specific_string(self):

        options = FakeOptions()
        expected_message = "Performing test build on local system"

        test_message, test_fail = dls_release.perform_test_build(
            self.fake_build, FakeOptions(), FakeVcs())

        self.assertTrue(
            test_message.startswith(expected_message),
            "returned message does not start with expected string")

    def test_given_local_test_possible_and_build_fails_then_return_test_failed(self):

        options = FakeOptions()
        self.fake_build.test.return_value = 1

        test_message, test_fail = dls_release.perform_test_build(
            self.fake_build, FakeOptions(), FakeVcs())

        self.assertTrue(test_fail)

    def test_given_local_test_possible_then_test_build_performed_once_with_vcs_and_version_as_args(self):

        options = FakeOptions()
        version = '0-1'
        vcs = FakeVcs(version=version)
        self.fake_build.test.return_value = 1

        test_message, test_fail = dls_release.perform_test_build(
            self.fake_build, FakeOptions(), vcs)

        self.fake_build.test.assert_called_once_with(vcs)

    def test_given_test_possible_and_build_works_then_return_test_not_failed_and_message_ends_with_specific_string(self):

        options = FakeOptions()
        self.fake_build.test.return_value = 0
        expected_message_end = "Test build successful. Continuing with build"
        expected_message_end += " server submission"

        test_message, test_fail = dls_release.perform_test_build(
            self.fake_build, FakeOptions(), FakeVcs())

        self.assertFalse(test_fail)
        self.assertTrue(
            test_message.endswith(expected_message_end),
            "returned message does not end with expected string")

    def test_given_test_possible_and_build_works_and_local_build_option_then_message_ends_without_continuation_info(self):

        options = FakeOptions(local_build=True)
        self.fake_build.test.return_value = 0
        expected_message = "Performing test build on local system"
        expected_message += '\nTest build successful.'

        test_message, test_fail = dls_release.perform_test_build(
            self.fake_build, options, FakeVcs())

        self.assertEqual(test_message, expected_message)


class TestMain(unittest.TestCase):

    def setUp(self):

        methods_to_patch = [
            'create_build_object',
            'create_vcs_object',
            'check_parsed_arguments_valid',
            'format_argument_version',
            'next_version_number',
            'get_last_release',
            'increment_version_number',
            'construct_info_message',
            'check_epics_version_consistent',
            'ask_user_input',
            'perform_test_build',
            'ArgParser.parse_args',
        ]

        self.patch = {}
        self.mocks = {}
        for method in methods_to_patch:
            self.patch[method] = patch('dls_ade.dls_release.' + method)
            self.addCleanup(self.patch[method].stop)
            self.mocks[method] = self.patch[method].start()

        self.mocks['ArgParser.parse_args'].return_value = ['', '']

        self.manager = MagicMock()

    def test_nothing(self):

        self.assertEqual(0, self.mocks['create_build_object'].call_count)

    def test_god_function_does_things_in_the_right_order(self):

        pass


class FakeOptions(object):
    def __init__(self,**kwargs):
        self.rhel_version = kwargs.get('rhel_version', None)
        self.epics_version = kwargs.get('epics_version', None)
        self.windows = kwargs.get('windows', None)
        self.area = kwargs.get('area', 'support')
        self.force = kwargs.get('force', None)
        self.git = kwargs.get('git', False)
        self.branch = kwargs.get('branch', None)
        self.next_version = kwargs.get('next_version', None)
        self.skip_test = kwargs.get('skip_test', False)
        self.local_build = kwargs.get('local_build', False)


class FakeVcs(object):
    def __init__(self, **kwargs):
        self.version = kwargs.get('version', None)

    def cat(self,filename, version=None):
        file_contents = '''
            CALC            = $(SUPPORT)/calc/3-1
            BLGUI           = $(SUPPORT)/BLGui/3-5


            # If using the sequencer, point SNCSEQ at its top directory:
            #SNCSEQ=$(EPICS_BASE)/../modules/soft/seq


            # EPICS_BASE usually appears last so other apps can override stuff:
            EPICS_BASE=/dls_sw/epics/R3.14.12.3/base


            # Set RULES here if you want to take build rules from somewhere
            # other than EPICS_BASE:
            #RULES=/path/to/epics/support/module/rules/x-y
        '''
        return file_contents

if __name__ == '__main__':

    # buffer option suppresses stdout generated from tested code
    unittest.main(buffer=True)
