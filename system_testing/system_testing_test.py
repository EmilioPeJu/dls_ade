import unittest
import subprocess
from pkg_resources import require
require("mock")
from mock import patch, ANY, MagicMock, PropertyMock  # @UnresolvedImport

import system_testing as st


def setup_module(self):
    st.ENVIRONMENT_CORRECT = True


def set_up_mock(test_case_obj, mock_path):
    patch_obj = patch(mock_path)
    test_case_obj.addCleanup(patch_obj.stop)
    mock_obj = patch_obj.start()

    return mock_obj


class GetLocalTempCloneTest(unittest.TestCase):

    @patch('system_testing.Server')
    def test_given_server_repo_path_then_repo_cloned_correctly(self,
                                                               server_mock):
        mock_repo = MagicMock(working_tree_dir="test_working_tree_dir")
        mock_vcs = MagicMock(repo=mock_repo)
        server_mock.return_value.temp_clone.return_value = mock_vcs

        return_value = st.get_local_temp_clone("test_repo_path")

        server_mock.return_value.temp_clone.assert_called_once_with(
            "test_repo_path")
        self.assertEqual(return_value, "test_working_tree_dir")


class DeleteTempRepoTest(unittest.TestCase):

    def setUp(self):

        self.patch_gettempdir = patch('system_testing.tempfile.gettempdir')
        self.patch_is_local_repo_root = patch('system_testing.vcs_git.is_local_repo_root')
        self.patch_rmtree = patch('system_testing.shutil.rmtree')

        self.addCleanup(self.patch_gettempdir.stop)
        self.addCleanup(self.patch_is_local_repo_root.stop)
        self.addCleanup(self.patch_rmtree.stop)

        self.mock_gettempdir = self.patch_gettempdir.start()
        self.mock_is_local_repo_root = self.patch_is_local_repo_root.start()
        self.mock_rmtree = self.patch_rmtree.start()

        self.mock_gettempdir.return_value = "/tmp"

    def test_given_repo_not_in_temp_dir_then_exception_raised_with_correct_message(self):

        comp_message = "/usr/bin/not_in_tempdir is not a temporary folder, cannot delete."

        with self.assertRaises(st.SystemTestingError) as e:
            st.delete_temp_repo("/usr/bin/not_in_tempdir")

        self.assertEqual(str(e.exception), comp_message)

    def test_given_repo_not_git_root_dir_then_exception_raised_with_correct_message(self):

        self.mock_is_local_repo_root.return_value = False

        comp_message = "/tmp/not_git_root_dir is not a git root directory, cannot delete."

        with self.assertRaises(st.SystemTestingError) as e:
            st.delete_temp_repo("/tmp/not_git_root_dir")

        self.assertEqual(str(e.exception), comp_message)

    def test_given_both_tests_pass_then_shutil_rmtree_called_on_given_file_path(self):

        self.mock_is_local_repo_root.return_value = True

        st.delete_temp_repo("/tmp/git_root_dir")

        self.mock_rmtree.assert_called_once_with("/tmp/git_root_dir")


class SystemTestCheckIfReposEqualTest(unittest.TestCase):

    def setUp(self):

        self.st_obj = st.SystemTest("test_script", "test_name")

    @patch('system_testing.subprocess.check_output')
    def test_given_a_path_is_empty_then_exception_raised_with_correct_message(self, mock_check_output):

        comp_message = "Two paths must be given to compare folders.\npath 1: , path 2: path_two."

        with self.assertRaises(st.SystemTestingError) as e:
            st.check_if_repos_equal("", "path_two")

        self.assertEqual(str(e.exception), comp_message)

    @patch('system_testing.subprocess.check_output')
    def test_subprocess_check_output_given_correct_input(self, mock_check_output):

        st.check_if_repos_equal("local_path_one", "local_path_two")

        mock_check_output.assert_called_once_with(['diff', '-rq', '--exclude=.git', '--exclude=.gitattributes', '--exclude=.keep', 'local_path_one', 'local_path_two'])

    @patch('system_testing.subprocess.check_output')
    def test_given_subprocess_return_code_1_then_function_returns_false(self, mock_check_output):
        mock_check_output.side_effect = subprocess.CalledProcessError(1, "This just makes the return code 1")

        return_value = st.check_if_repos_equal("path1", "path2")

        self.assertFalse(return_value)

    @patch('system_testing.subprocess.check_output')
    def test_given_subprocess_return_code_0_then_function_returns_true(self, mock_check_output):
        mock_check_output.return_value = ""

        return_value = st.check_if_repos_equal("path1", "path2")

        self.assertTrue(return_value)


class SystemTestLoadSettingsTest(unittest.TestCase):

    def test_given_dictionary_contains_only_items_in_settings_list_then_dict_updated_with_all(self):

        settings = {
            'arguments': "--area python test_module_name",
            'std_out_compare_string': "test_output"
        }

        st_obj = st.SystemTest("test_script.py", "test_name")

        st_obj.load_settings(settings)

        self.assertEqual(st_obj._arguments, "--area python test_module_name")
        self.assertEqual(st_obj._std_out_compare_string, "test_output")

    def test_given_dictionary_contains_items_that_do_not_exist_in_settings_list_then_dict_only_updated_with_those_that_are(self):

        settings = {
            'arguments': "--area python test_module_name",
            'std_out_compare_string': "test_output",
            'std_out': "this should not get updated"
        }

        st_obj = st.SystemTest("test_script.py", "test_name")

        st_obj.load_settings(settings)

        self.assertEqual(st_obj._arguments, "--area python test_module_name")
        self.assertEqual(st_obj._std_out_compare_string, "test_output")
        self.assertNotEqual(st_obj._std_out, "this should not get updated")


class SystemTestSetServerRepoToDefaultTest(unittest.TestCase):

    def setUp(self):

        self.mock_vcs_git = set_up_mock(self, 'system_testing.vcs_git')
        self.mock_is_server_repo = set_up_mock(self, 'dls_ade.Server.is_server_repo')
        self.mock_clone = set_up_mock(self, 'dls_ade.Server.temp_clone')
        st.Server.url = "ssh://GIT_SSH_ROOT"

        self.st_obj = st.SystemTest("test_script", "test_name")

    def test_given_no_default_server_repo_path_then_function_returns_immediately(self):

        self.st_obj.load_settings({})

        self.st_obj.set_server_repo_to_default()

        self.assertFalse(self.mock_clone.called)

    def test_given_default_server_repo_path_but_no_server_repo_path_then_function_raises_exception_with_correct_message(self):

        self.st_obj.load_settings({
            'default_server_repo_path': "path/to/default",
        })

        with self.assertRaises(st.SettingsError) as e:
            self.st_obj.set_server_repo_to_default()

        self.assertTrue(all(x in str(e.exception) for x in ["default_server_repo_path"]))

        self.assertFalse(self.mock_clone.called)

    def test_given_both_paths_and_server_repo_does_not_already_exist_then_vcs_git_functions_called_correctly(self):

        mock_temp_repo = MagicMock(working_tree_dir="tempdir")
        self.mock_clone.return_value = mock_temp_repo
        self.mock_is_server_repo.return_value = False

        self.st_obj.load_settings({
            'default_server_repo_path': "path/to/default",
            'server_repo_path': "path/to/new",
        })

        self.st_obj.set_server_repo_to_default()

        self.mock_clone.assert_called_once_with("path/to/default")
        self.mock_vcs_git.delete_remote.assert_called_once_with(
            mock_temp_repo.repo, "origin")
        mock_temp_repo.add_new_remote_and_push.assert_called_once_with("path/to/new")

    def test_given_both_paths_and_server_repo_already_exists_then_vcs_git_functions_called_correctly(self):

        mock_temp_repo = MagicMock(working_tree_dir="tempdir",
                                   active_branch="test_branch")
        self.mock_clone.return_value.repo = mock_temp_repo
        self.mock_is_server_repo.return_value = True

        self.st_obj.load_settings({
            'default_server_repo_path': "path/to/default",
            'server_repo_path': "path/to/altered",
        })
        self.st_obj.server.url = "ssh://GIT_SSH_ROOT/"

        self.st_obj.set_server_repo_to_default()

        self.mock_clone.assert_called_once_with("path/to/default")
        self.mock_vcs_git.delete_remote.assert_called_once_with(mock_temp_repo,
                                                                "origin")

        mock_temp_repo.create_remote.assert_called_once_with(
            "origin", "ssh://GIT_SSH_ROOT/path/to/altered")
        mock_temp_repo.git.push.assert_called_once_with("origin",
                                                        "test_branch", "-f")


class SystemTestCallScriptTest(unittest.TestCase):

    def setUp(self):
        self.mock_popen = set_up_mock(self, 'system_testing.subprocess.Popen')

    def test_given_no_input_then_popen_has_no_standard_input_set_and_communicate_called_without_input(self):
        mock_process = MagicMock(returncode=1)
        mock_process.communicate.return_value = ("test_out", "test_err")
        self.mock_popen.return_value = mock_process

        st_obj = st.SystemTest("test_script", "test_name")
        st_obj.load_settings(
                {
                    'arguments': "--area python test_server_repo_path",
                }
        )

        st_obj.call_script()

        self.mock_popen.assert_called_once_with(["test_script", "--area", "python", "test_server_repo_path"],
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE,
                                                stdin=None)

        mock_process.communicate.assert_called_once_with(None)

        self.assertEqual(st_obj._std_out, "test_out")
        self.assertEqual(st_obj._std_err, "test_err")
        self.assertEqual(st_obj._return_code, 1)

    def test_given_input_then_popen_has_standard_input_set_to_pipe_and_communicate_called_with_input(self):
        mock_process = MagicMock(returncode=1)
        mock_process.communicate.return_value = ("test_out", "test_err")
        self.mock_popen.return_value = mock_process

        st_obj = st.SystemTest("test_script", "test_name")
        st_obj.load_settings(
                {
                    'arguments': "--area python test_server_repo_path",
                    'input': "I am input",
                }
        )

        st_obj.call_script()

        self.mock_popen.assert_called_once_with(["test_script", "--area", "python", "test_server_repo_path"],
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE,
                                                stdin=subprocess.PIPE)

        mock_process.communicate.assert_called_once_with("I am input")

        self.assertEqual(st_obj._std_out, "test_out")
        self.assertEqual(st_obj._std_err, "test_err")
        self.assertEqual(st_obj._return_code, 1)

    def test_given_input_is_blank_string_then_popen_has_standard_input_set_to_pipe_and_communicate_called_with_input(self):
        mock_process = MagicMock(returncode=1)
        mock_process.communicate.return_value = ("test_out", "test_err")
        self.mock_popen.return_value = mock_process

        st_obj = st.SystemTest("test_script", "test_name")
        st_obj.load_settings(
                {
                    'arguments': "--area python test_server_repo_path",
                    'input': "",
                }
        )

        st_obj.call_script()

        self.mock_popen.assert_called_once_with(["test_script", "--area", "python", "test_server_repo_path"],
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE,
                                                stdin=subprocess.PIPE)

        mock_process.communicate.assert_called_once_with("")

        self.assertEqual(st_obj._std_out, "test_out")
        self.assertEqual(st_obj._std_err, "test_err")
        self.assertEqual(st_obj._return_code, 1)

class SystemTestCheckStdErrForExceptionTest(unittest.TestCase):

    def test_given_neither_exception_type_nor_message_then_test_passes(self):

        st_obj = st.SystemTest("test_script", "test_name")

        st_obj.check_std_out_for_exception_string()

    def test_given_type_provided_but_no_message_then_exception_raised_with_correct_message(self):

        comp_message = ("Both exception_type and exception_string must be provided.")

        st_obj = st.SystemTest("test_script", "test_name")

        st_obj.load_settings({
            'exception_type': "test_exception_type"
        })

        with self.assertRaises(st.SystemTestingError) as e:
            st_obj.check_std_out_for_exception_string()

        self.assertEqual(str(e.exception), comp_message)

    def test_given_message_provided_but_no_type_then_exception_raised_with_correct_message(self):

        comp_message = ("Both exception_type and exception_string must be provided.")

        st_obj = st.SystemTest("test_script", "test_name")

        st_obj.load_settings({
            'exception_string': "test exception string"
        })

        with self.assertRaises(st.SystemTestingError) as e:
            st_obj.check_std_out_for_exception_string()

        self.assertEqual(str(e.exception), comp_message)

    def test_given_return_code_0_then_assertion_failed(self):

        st_obj = st.SystemTest("test_script", "test_name")
        st_obj._return_code = 0

        st_obj.load_settings({
            'exception_type': "test_exception_type",
            'exception_string': "test exception string"
        })

        with self.assertRaises(AssertionError):
            st_obj.check_std_out_for_exception_string()

    def test_given_exception_not_raised_in_script_then_test_fails(self):

        st_obj = st.SystemTest("test_script", "test_name")
        st_obj._return_code = 1
        st_obj._std_err = "\nother_exception_type: other exception string\n"

        st_obj.load_settings({
            'exception_type': "test_exception_type",
            'exception_string': "test exception string"
        })

        with self.assertRaises(AssertionError):
            st_obj.check_std_out_for_exception_string()

    def test_given_exception_raised_in_script_then_test_passes(self):

        st_obj = st.SystemTest("test_script", "test_name")
        st_obj._return_code = 1
        st_obj._std_err = "\ntest_exception_type: test exception string\n"

        st_obj.load_settings({
            'exception_type': "test_exception_type",
            'exception_string': "test exception string"
        })

        st_obj.check_std_out_for_exception_string()


class SystemTestCompareStdOutToStringTest(unittest.TestCase):

    def test_given_comparison_string_is_none_then_function_returns(self):

        st_obj = st.SystemTest("test_script", "test_name")

        st_obj._std_out_compare_string = None
        st_obj._std_out = "I definitely exist."

        st_obj.compare_std_out_to_string()

    def test_given_std_out_equal_to_comparison_string_then_test_passes(self):

        st_obj = st.SystemTest("test_script", "test_name")
        st_obj._std_out = "String to test for."

        st_obj.load_settings({
            'std_out_compare_string': "String to test for."
        })

        st_obj.compare_std_out_to_string()

    def test_given_std_out_not_equal_to_comparison_string_then_test_fails(self):

        st_obj = st.SystemTest("test_script", "test_name")
        st_obj._std_out = "String to test for."

        st_obj.load_settings({
            'std_out_compare_string': "A different string."
        })

        with self.assertRaises(AssertionError):
            st_obj.compare_std_out_to_string()


class SystemTestCheckStdOutStartsWithStringTest(unittest.TestCase):

    def test_given_starts_with_string_is_none_then_function_returns(self):

        st_obj = st.SystemTest("test_script", "test_name")

        st_obj._std_out_starts_with_string = None
        st_obj._std_out = "I definitely exist."

        st_obj.check_std_out_starts_with_string()

    def test_given_std_out_starts_with_string_then_test_passes(self):

        st_obj = st.SystemTest("test_script", "test_name")
        st_obj._std_out = "String to test for."

        st_obj.load_settings({
            'std_out_starts_with_string': "String to test",
        })

        st_obj.check_std_out_starts_with_string()

    def test_given_std_out_does_not_start_with_comparison_string_then_test_fails(self):

        st_obj = st.SystemTest("test_script", "test_name")
        st_obj._std_out = "String to test for."

        st_obj.load_settings({
            'std_out_starts_with_string': "String_",
        })

        with self.assertRaises(AssertionError):
            st_obj.check_std_out_starts_with_string()


class SystemTestCheckStdOutEndsWithStringTest(unittest.TestCase):

    def test_given_ends_with_string_is_none_then_function_returns(self):

        st_obj = st.SystemTest("test_script", "test_name")

        st_obj._std_out_ends_with_string = None
        st_obj._std_out = "I definitely exist."

        st_obj.check_std_out_ends_with_string()

    def test_given_std_out_ends_with_comparison_string_then_test_passes(self):

        st_obj = st.SystemTest("test_script", "test_name")
        st_obj._std_out = "String to test for."

        st_obj.load_settings({
            'std_out_ends_with_string': "to test for.",
        })

        st_obj.check_std_out_ends_with_string()

    def test_given_std_out_does_not_end_with_comparison_string_then_test_fails(self):

        st_obj = st.SystemTest("test_script", "test_name")
        st_obj._std_out = "String to test for."

        st_obj.load_settings({
            'std_out_ends_with_string': "test_for.",
        })

        with self.assertRaises(AssertionError):
            st_obj.check_std_out_ends_with_string()


class SystemTestCheckForAndCloneRemoteRepoTest(unittest.TestCase):

    def setUp(self):

        self.st_obj = st.SystemTest("test_script", "test_name")
        self.mock_check_remote_repo_exists = set_up_mock(
                self,
                "system_testing.SystemTest.check_remote_repo_exists"
        )

        self.mock_clone_server_repo = set_up_mock(
            self,
            "system_testing.SystemTest.clone_server_repo"
        )

    def test_given_no_server_repo_path_then_function_returns(self):

        self.st_obj.check_for_and_clone_remote_repo()

        self.assertFalse(self.mock_check_remote_repo_exists.called)

    def test_given_server_repo_path_then_remote_repo_exists_and_clone_called(self):

        self.st_obj._server_repo_path = "test/server/repo/path"

        self.st_obj.check_for_and_clone_remote_repo()

        self.mock_check_remote_repo_exists.assert_called_once_with()

        self.mock_clone_server_repo.assert_called_once_with()


class SystemTestCheckRemoteRepoExists(unittest.TestCase):

    def setUp(self):

        self.st_obj = st.SystemTest("test_script", "test_name")
        self.st_obj._server_repo_path = "test_repo_path"

    @patch('dls_ade.Server.is_server_repo', return_value=False)
    def test_given_is_server_repo_false_then_assert_failed(self, mock_is_server_repo):

        with self.assertRaises(AssertionError):
            self.st_obj.check_remote_repo_exists()

        mock_is_server_repo.assert_called_once_with("test_repo_path")

    @patch('dls_ade.Server.is_server_repo', return_value=True)
    def test_given_is_server_repo_true_then_no_assertion_failed(self, mock_is_server_repo):

        self.st_obj.check_remote_repo_exists()

        mock_is_server_repo.assert_called_once_with("test_repo_path")


class SystemTestCloneServerRepoTest(unittest.TestCase):

    def setUp(self):
        self.repo_mock = MagicMock(working_tree_dir='root/dir/of/repo')
        self.server_mock = MagicMock()
        self.server_mock.temp_clone.return_value.repo = self.repo_mock

        self.st_obj = st.SystemTest("test_script", "test_name")
        self.st_obj.server = self.server_mock
        self.mock_checkout_remote_branch = set_up_mock(self, 'system_testing.vcs_git.checkout_remote_branch')

    def test_given_function_called_then_server_clone_path_set_to_working_tree_dir_of_repo(self):

        self.st_obj._server_repo_path = "test_repo_path"

        self.st_obj.clone_server_repo()

        self.st_obj.server.temp_clone.assert_called_once_with("test_repo_path")
        self.assertEqual(self.st_obj._server_repo_clone_path, "root/dir/of/repo")

    def test_given_function_called_with_no_branch_set_then_checkout_remote_branch_not_called(self):

        self.st_obj._server_repo_path = "test_repo_path"

        self.st_obj._branch_name = ""

        self.st_obj.clone_server_repo()

        self.st_obj.server.temp_clone.assert_called_once_with("test_repo_path")
        self.assertEqual(self.st_obj._server_repo_clone_path, "root/dir/of/repo")
        self.assertFalse(self.mock_checkout_remote_branch.called)

    def test_given_function_called_with_branch_set_then_checkout_remote_branch_called(self):

        self.st_obj._server_repo_path = "test_repo_path"

        self.st_obj._branch_name = "test_branch_name"

        self.st_obj.clone_server_repo()

        self.st_obj.server.temp_clone.assert_called_once_with("test_repo_path")
        self.assertEqual(self.st_obj._server_repo_clone_path, "root/dir/of/repo")
        self.mock_checkout_remote_branch.assert_called_once_with("test_branch_name", self.repo_mock)


class SystemTestCheckLocalRepoActiveBranchTest(unittest.TestCase):

    def setUp(self):
        self.mock_get_active_branch = set_up_mock(self, 'system_testing.vcs_git.get_active_branch')

        self.st_obj = st.SystemTest("test_script", "test_name")

    def test_given_no_branch_name_then_function_returns_immediately(self):

        self.st_obj._branch_name = ""
        self.st_obj._local_repo_path = "test_lrp"

        self.st_obj.check_local_repo_active_branch()

        self.assertFalse(self.mock_get_active_branch.called)

    def test_given_no_local_repo_path_then_function_returns_immediately(self):

        self.st_obj._branch_name = "test_branch"
        self.st_obj._local_repo_path = ""

        self.st_obj.check_local_repo_active_branch()

        self.assertFalse(self.mock_get_active_branch.called)

    @patch('dls_ade.vcs_git.init_repo')
    def test_given_repository_branch_is_different_than_expected_then_assertion_error_raised(self, mock_init):

        self.st_obj._branch_name = "test_branch"
        self.mock_get_active_branch.return_value = "other_branch"
        self.st_obj._local_repo_path = "test_lrp"

        with self.assertRaises(AssertionError):
            self.st_obj.check_local_repo_active_branch()

        self.mock_get_active_branch.assert_called_once_with(
            mock_init.return_value)

    @patch('dls_ade.vcs_git.init_repo')
    def test_given_repository_branch_is_the_same_as_expected_then_test_passes(self, mock_init):

        self.st_obj._branch_name = "test_branch"
        self.mock_get_active_branch.return_value = "test_branch"
        self.st_obj._local_repo_path = "test_lrp"

        self.st_obj.check_local_repo_active_branch()

        self.mock_get_active_branch.assert_called_once_with(
            mock_init.return_value)


class SystemTestRunGitAttributesTest(unittest.TestCase):

    def setUp(self):
        self.mock_check_git_attributes = set_up_mock(self, 'system_testing.vcs_git.check_git_attributes')

        self.st_obj = st.SystemTest("test_script", "test_name")

    def test_given_no_attributes_dict_then_function_returns(self):

        self.st_obj._attributes_dict = {}
        self.st_obj._server_repo_path = "test_srcp"
        self.st_obj._local_repo_path = "test_lrp"

        self.st_obj.run_git_attributes_tests()

        self.assertFalse(self.mock_check_git_attributes.called)


    def test_given_neither_path_is_defined_but_attributes_dict_is_defined_then_exception_raised_with_correct_message(self):

        self.st_obj._attributes_dict = {'test': "attribute"}

        comp_message = "As an attributes dict has been provided, either the local_repo_path or server_repo_clone_path must be provided."

        with self.assertRaises(st.SystemTestingError) as e:
            self.st_obj.run_git_attributes_tests()

        self.assertEqual(str(e.exception), comp_message)

    @patch('dls_ade.vcs_git.init_repo')
    def test_given_server_repo_clone_path_has_attributes_then_assertion_passed(self, mock_init):

        self.st_obj._attributes_dict = {'test': "attribute"}
        self.st_obj._server_repo_clone_path = "test_srcp"
        self.mock_check_git_attributes.return_value = True

        self.st_obj.run_git_attributes_tests()

        self.mock_check_git_attributes.assert_called_once_with(
            mock_init.return_value, {'test': "attribute"})

    @patch('dls_ade.vcs_git.init_repo')
    def test_given_server_repo_clone_path_has_no_attributes_then_assertion_failed(self, mock_init):

        self.st_obj._attributes_dict = {'test': "attribute"}
        self.st_obj._server_repo_clone_path = "test_srcp"
        self.mock_check_git_attributes.return_value = False

        with self.assertRaises(AssertionError):
            self.st_obj.run_git_attributes_tests()

        self.mock_check_git_attributes.assert_called_once_with(
            mock_init.return_value, {'test': "attribute"})

    @patch('dls_ade.vcs_git.init_repo')
    def test_given_local_repo_clone_path_has_attributes_then_assertion_passed(self, mock_init):

        self.st_obj._attributes_dict = {'test': "attribute"}
        self.st_obj._local_repo_path = "test_lrp"
        self.mock_check_git_attributes.return_value = True

        self.st_obj.run_git_attributes_tests()

        self.mock_check_git_attributes.assert_called_once_with(
            mock_init.return_value, {'test': "attribute"})

    @patch('dls_ade.vcs_git.init_repo')
    def test_given_local_repo_clone_path_has_no_attributes_then_assertion_failed(self, mock_init):

        self.st_obj._attributes_dict = {'test': "attribute"}
        self.st_obj._local_repo_path = "test_lrp"
        self.mock_check_git_attributes.return_value = False

        with self.assertRaises(AssertionError):
            self.st_obj.run_git_attributes_tests()

        self.mock_check_git_attributes.assert_called_once_with(
        mock_init.return_value, {'test': "attribute"})

    @patch('dls_ade.vcs_git.init_repo')
    def test_given_both_paths_have_attributes_then_assertion_passed(self, _):

        self.st_obj._attributes_dict = {'test': "attribute"}
        self.st_obj._local_repo_path = "test_lrp"
        self.st_obj._server_repo_clone_path = "test_lcrp"
        self.mock_check_git_attributes.return_value = True

        self.st_obj.run_git_attributes_tests()

        self.assertEqual(self.mock_check_git_attributes.call_count, 2)

    @patch('dls_ade.vcs_git.init_repo')
    def test_given_both_paths_do_not_have_attributes_then_assertion_failed(self, _):

        self.st_obj._attributes_dict = {'test': "attribute"}
        self.st_obj._local_repo_path = "test_lrp"
        self.st_obj._server_repo_clone_path = "test_lcrp"
        self.mock_check_git_attributes.return_value = False

        with self.assertRaises(AssertionError):
            self.st_obj.run_git_attributes_tests()

        self.assertEqual(self.mock_check_git_attributes.call_count, 1)


class SystemTestRunComparisonTests(unittest.TestCase):

    def setUp(self):
        self.mock_check_folders_equal = set_up_mock(self, 'system_testing.check_if_repos_equal')

        self.st_obj = st.SystemTest("test_script", "test_name")

    def test_given_no_repo_comp_method_then_function_returns(self):

        self.st_obj._repo_comp_method = ""

        self.st_obj.run_comparison_tests()

        self.assertFalse(self.mock_check_folders_equal.called)

    def test_given_repo_comp_method_is_local_comp_then_check_folders_equal_called_on_local_paths(self):

        self.st_obj._repo_comp_method = "local_comp"
        self.st_obj._local_comp_path_one = "local_comp_path_one"
        self.st_obj._local_comp_path_two = "local_comp_path_two"

        self.st_obj.run_comparison_tests()

        self.mock_check_folders_equal.assert_called_once_with("local_comp_path_one", "local_comp_path_two")

    def test_given_repo_comp_method_is_server_comp_then_check_folders_equal_called_on_local_path_one_and_server_repo_clone_path(self):

        self.st_obj._repo_comp_method = "server_comp"
        self.st_obj._local_comp_path_one = "local_comp_path_one"
        self.st_obj._server_repo_clone_path = "server_clone_path"

        self.st_obj.run_comparison_tests()

        self.mock_check_folders_equal.assert_called_once_with("local_comp_path_one", "server_clone_path")

    def test_given_repo_comp_method_is_all_comp_then_check_folders_equal_called_on_all_paths(self):

        self.st_obj._repo_comp_method = "all_comp"
        self.st_obj._local_comp_path_one = "local_comp_path_one"
        self.st_obj._local_comp_path_two = "local_comp_path_two"
        self.st_obj._server_repo_clone_path = "server_clone_path"

        self.st_obj.run_comparison_tests()

        self.mock_check_folders_equal.assert_any_call("local_comp_path_one", "local_comp_path_two")
        self.mock_check_folders_equal.assert_any_call("local_comp_path_one", "server_clone_path")

    def test_given_comp_method_not_shown_then_error_raised_with_correct_message(self):

        self.st_obj._repo_comp_method = "not_comp"

        comp_message = ("The repo_comp_method must be called using one of "
                        "the following:"
                        "\nlocal_comp, server_comp, all_comp."
                        "\nGot: not_comp")

        with self.assertRaises(st.SystemTestingError) as e:
            self.st_obj.run_comparison_tests()

        self.assertEqual(str(e.exception), comp_message)


class SystemTestDeleteClonedServerRepo(unittest.TestCase):

    def setUp(self):

        self.st_obj = st.SystemTest("test_script", "test_name")

        self.mock_delete_temp_repo = set_up_mock(self, "system_testing.delete_temp_repo")

    def test_given_server_repo_clone_does_not_exist_then_function_returns(self):

        self.st_obj._server_repo_clone_path = ""

        self.st_obj.delete_cloned_server_repo()

        self.assertFalse(self.mock_delete_temp_repo.called)

    def test_given_server_repo_clone_exists_then_delete_temp_repo_called_and_clone_path_set_blank(self):

        self.st_obj._server_repo_clone_path = "test/repo/clone/path"

        self.st_obj.delete_cloned_server_repo()

        self.mock_delete_temp_repo.assert_called_once_with("test/repo/clone/path")

        self.assertEqual(self.st_obj._server_repo_clone_path, "")


def teardown_module():
    st.ENVIRONMENT_CORRECT = False