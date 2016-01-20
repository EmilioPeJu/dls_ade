from __future__ import print_function

import unittest
import os
import logging

import dls_ade.module_creator as mc
from pkg_resources import require
require("mock")
from mock import patch, ANY, MagicMock, call

from sys import version_info
if version_info.major == 2:
    import __builtin__ as builtins  # Allows for Python 2/3 compatibility, 'builtins' is namespace for inbuilt functions
else:
    import builtins

logging.basicConfig(level=logging.DEBUG)


def set_up_mock(test_case_object, path):

    patch_obj = patch(path)

    test_case_object.addCleanup(patch_obj.stop)

    mock_obj = patch_obj.start()

    return mock_obj


class ModuleCreatorClassInitTest(unittest.TestCase):

    def setUp(self):

        self.mock_mt = set_up_mock(self, 'dls_ade.module_template.ModuleTemplate')
        self.mock_getlogin = set_up_mock(self, 'os.getlogin')
        self.mock_getlogin.return_value = 'test_login'

    def test_given_reasonable_input_then_initialisation_is_successful(self):

        mc.ModuleCreator("test_module", "test_area", self.mock_mt)

    def test_given_extra_template_args_then_module_template_initialisation_includes_them(self):

        expected_dict = {'module_name': "test_module",
                         'module_path': "test_module",
                         'user_login': "test_login",
                         'additional': "value"}

        base_c = mc.ModuleCreator("test_module", "test_area", self.mock_mt, additional="value")

        self.mock_mt.assert_called_once_with(expected_dict)

    def test_given_no_extra_template_args_then_module_template_initialisation_behaves_as_normal(self):

        expected_dict = {'module_name': "test_module",
                         'module_path': "test_module",
                         'user_login': "test_login"}

        base_c = mc.ModuleCreator("test_module", "test_area", self.mock_mt)

        self.mock_mt.assert_called_once_with(expected_dict)


class ModuleCreatorVerifyRemoteRepoTest(unittest.TestCase):

    def setUp(self):

        self.mock_is_repo_path = set_up_mock(self, 'dls_ade.vcs_git.is_repo_path')

        self.nmc_obj = mc.ModuleCreator("test_module", "test_area", MagicMock())

        self.nmc_obj._remote_repo_valid = False

    def test_given_remote_repo_valid_true_then_function_returns_immediately(self):

        self.nmc_obj._remote_repo_valid = True

        self.nmc_obj.verify_remote_repo()

        self.assertFalse(self.mock_is_repo_path.called)

    def test_given_remote_repo_path_exists_then_exception_raised_with_correct_message(self):

        server_repo_path = self.nmc_obj._server_repo_path

        self.mock_is_repo_path.return_value = True
        comp_message = "The path {dir:s} already exists on gitolite, cannot continue".format(dir=server_repo_path)

        with self.assertRaises(mc.VerificationError) as e:
            self.nmc_obj.verify_remote_repo()

        self.assertEqual(str(e.exception), comp_message)

    def test_given_remote_repo_does_not_exist_then_remote_repo_valid_set_true(self):

        self.mock_is_repo_path.return_value = False

        self.nmc_obj.verify_remote_repo()

        self.assertTrue(self.nmc_obj._remote_repo_valid)


class ModuleCreatorVerifyCanCreateLocalModule(unittest.TestCase):

    def setUp(self):

        self.mock_exists = set_up_mock(self, 'dls_ade.module_creator.os.path.exists')
        self.mock_is_git_dir = set_up_mock(self, 'dls_ade.module_creator.vcs_git.is_git_dir')

        self.nmc_obj = mc.ModuleCreator("test_module", "test_area", MagicMock())

        self.nmc_obj._can_create_local_module = False

    def test_given_remote_repo_valid_true_then_function_returns_immediately(self):

        self.nmc_obj._can_create_local_module = True

        self.nmc_obj.verify_can_create_local_module()

        self.assertFalse(self.mock_exists.called)

    def test_given_module_folder_does_not_exist_and_is_not_in_git_repo_then_flag_set_true(self):

        self.mock_exists.return_value = False
        self.mock_is_git_dir.return_value = False

        self.nmc_obj.verify_can_create_local_module()

        self.assertTrue(self.nmc_obj._can_create_local_module)

    def test_given_module_folder_exists_then_flag_set_false_and_error_returned_is_correct(self):

        self.mock_exists.return_value = True
        self.mock_is_git_dir.return_value = False

        comp_message = "Directory {dir:s} already exists, please move elsewhere and try again.".format(dir=self.nmc_obj._module_path)

        with self.assertRaises(mc.VerificationError) as e:
            self.nmc_obj.verify_can_create_local_module()

        self.assertEqual(str(e.exception), comp_message)

        self.assertFalse(self.nmc_obj._remote_repo_valid)

    def test_given_module_folder_is_in_git_repo_then_flag_set_false_and_error_returned_is_correct(self):

        self.mock_exists.return_value = False
        self.mock_is_git_dir.return_value = True

        comp_message = "Currently in a git repository, please move elsewhere and try again.".format(dir=os.path.join("./", self.nmc_obj.abs_module_path))

        with self.assertRaises(mc.VerificationError) as e:
            self.nmc_obj.verify_can_create_local_module()

        self.assertEqual(str(e.exception), comp_message)

        self.assertFalse(self.nmc_obj._remote_repo_valid)

    def test_given_module_folder_exists_and_is_in_repo_then_flag_set_false_and_error_returned_is_correct(self):

        self.mock_exists.return_value = True
        self.mock_is_git_dir.return_value = True

        comp_message = "Directory {dir:s} already exists, please move elsewhere and try again.\n"
        comp_message += "Currently in a git repository, please move elsewhere and try again."
        comp_message = comp_message.format(dir=self.nmc_obj._module_path)

        with self.assertRaises(mc.VerificationError) as e:
            self.nmc_obj.verify_can_create_local_module()

        self.assertEqual(str(e.exception), comp_message)

        self.assertFalse(self.nmc_obj._remote_repo_valid)


class ModuleCreatorVerifyCanPushLocalRepoToRemoteTest(unittest.TestCase):

    def setUp(self):

        self.mock_exists = set_up_mock(self, 'dls_ade.module_creator.os.path.exists')
        self.mock_is_git_root_dir = set_up_mock(self, 'dls_ade.module_creator.vcs_git.is_git_root_dir')
        self.mock_verify_remote_repo = set_up_mock(self, 'dls_ade.module_creator.ModuleCreator.verify_remote_repo')

        self.nmc_obj = mc.ModuleCreator("test_module", "test_area", MagicMock())

        self.nmc_obj._can_push_repo_to_remote = False

    def test_given_remote_repo_valid_true_then_function_returns_immediately(self):

        self.nmc_obj._can_push_repo_to_remote = True

        self.nmc_obj.verify_can_push_repo_to_remote()

        self.assertFalse(self.mock_exists.called)

    def test_given_module_folder_exists_and_is_repo_and_remote_repo_valid_then_flag_set_true(self):

        self.mock_exists.return_value = True
        self.mock_is_git_root_dir.return_value = True

        self.nmc_obj._remote_repo_valid = True
        self.nmc_obj.verify_can_push_repo_to_remote()

        self.assertTrue(self.nmc_obj._can_push_repo_to_remote)

    def test_given_remote_repo_valid_not_previously_set_but_true_then_flag_set_true(self):

        self.mock_exists.return_value = True
        self.mock_is_git_root_dir.return_value = True

        self.nmc_obj._can_push_repo_to_remote = False

        self.nmc_obj.verify_can_push_repo_to_remote()

        self.assertTrue(self.nmc_obj._can_push_repo_to_remote)

    def test_given_remote_repo_valid_false_then_flag_set_false_and_error_returned_is_correct(self):

        self.nmc_obj._remote_repo_valid = False

        self.mock_verify_remote_repo.side_effect = mc.VerificationError("error")

        self.mock_exists.return_value = True
        self.mock_is_git_root_dir.return_value = True

        with self.assertRaises(mc.VerificationError) as e:
            self.nmc_obj.verify_can_push_repo_to_remote()

        self.assertEqual(str(e.exception), "error")
        self.assertFalse(self.nmc_obj._can_push_repo_to_remote)

    def test_given_module_folder_does_not_exist_then_flag_set_false_and_error_returned_is_correct(self):

        self.mock_exists.return_value = False
        self.mock_is_git_root_dir.return_value = False

        self.nmc_obj._remote_repo_valid = True

        comp_message = "Directory {dir:s} does not exist.".format(dir=self.nmc_obj._module_path)

        with self.assertRaises(mc.VerificationError) as e:
            self.nmc_obj.verify_can_push_repo_to_remote()

        self.assertEqual(str(e.exception), comp_message)
        self.assertFalse(self.nmc_obj._can_push_repo_to_remote)

    def test_given_module_folder_is_not_repo_then_flag_set_false_and_error_returned_is_correct(self):

        self.mock_exists.return_value = True
        self.mock_is_git_root_dir.return_value = False

        self.nmc_obj._remote_repo_valid = True

        comp_message = "Directory {dir:s} is not a git repository. Unable to push to remote repository.".format(dir=self.nmc_obj._module_path)

        with self.assertRaises(mc.VerificationError) as e:
            self.nmc_obj.verify_can_push_repo_to_remote()

        self.assertEqual(str(e.exception), comp_message)
        self.assertFalse(self.nmc_obj._can_push_repo_to_remote)

    def test_given_module_folder_is_not_repo_and_remote_repo_false_then_flag_set_false_and_error_returned_is_correct(self):

        self.mock_verify_remote_repo.side_effect = mc.VerificationError('error')
        self.mock_exists.return_value = True
        self.mock_is_git_root_dir.return_value = False

        comp_message = "Directory {dir:s} is not a git repository. Unable to push to remote repository.\n"
        comp_message = comp_message.format(dir=self.nmc_obj._module_path)
        comp_message += "error"
        comp_message = comp_message.rstrip()

        with self.assertRaises(mc.VerificationError) as e:
            self.nmc_obj.verify_can_push_repo_to_remote()

        self.assertEqual(str(e.exception), comp_message)
        self.assertFalse(self.nmc_obj._can_push_repo_to_remote)


class ModuleCreatorCreateLocalModuleTest(unittest.TestCase):

    def setUp(self):

        self.mock_os = set_up_mock(self, 'dls_ade.module_creator.os')
        self.mock_vcs_git = set_up_mock(self, 'dls_ade.module_creator.vcs_git')
        self.mock_verify_can_create_local_module = set_up_mock(self, 'dls_ade.module_creator.ModuleCreator.verify_can_create_local_module')

        self.mock_module_template_cls = MagicMock()
        self.mock_module_template = MagicMock()
        self.mock_module_template_cls.return_value = self.mock_module_template
        self.mock_create_files = self.mock_module_template.create_files

        self.nmc_obj = mc.ModuleCreator("test_module", "test_area", self.mock_module_template_cls)

    def test_given_verify_can_create_local_module_passes_then_can_create_local_module_set_false(self):

        self.nmc_obj.create_local_module()

        self.assertFalse(self.nmc_obj._can_create_local_module)

    def test_given_verify_can_create_local_module_fails_then_exception_raised_with_correct_message(self):

        self.mock_verify_can_create_local_module.side_effect = mc.VerificationError("error")

        with self.assertRaises(Exception) as e:
            self.nmc_obj.create_local_module()

        self.assertFalse(self.mock_os.path.isdir.called)
        self.assertEqual(str(e.exception), "error")

    def test_given_can_create_local_module_true_then_rest_of_function_is_run(self):

        self.nmc_obj.create_local_module()

        call_list = [call(self.nmc_obj.abs_module_path), call(self.nmc_obj._cwd)]

        self.mock_os.chdir.assert_has_calls(call_list)
        self.assertTrue(self.mock_create_files.called)
        self.mock_vcs_git.init_repo.assert_called_once_with(self.nmc_obj.abs_module_path)
        self.mock_vcs_git.stage_all_files_and_commit.assert_called_once_with(self.nmc_obj.abs_module_path)


class ModuleCreatorPrintMessageTest(unittest.TestCase):

    def setUp(self):

        self.mock_module_template = MagicMock()
        self.nmc_obj = mc.ModuleCreator("test_module", "test_area", self.mock_module_template)

    def test_given_function_called_then_module_template_print_message_called(self):

        self.nmc_obj.print_message()

        self.mock_module_template.print_message_assert_called_once_with()


class ModuleCreatorPushRepoToRemoteTest(unittest.TestCase):

    def setUp(self):

        self.mock_verify_can_push_repo_to_remote = set_up_mock(self, 'dls_ade.module_creator.ModuleCreator.verify_can_push_repo_to_remote')
        self.mock_add_new_remote_and_push = set_up_mock(self, 'dls_ade.module_creator.vcs_git.add_new_remote_and_push')

        self.nmc_obj = mc.ModuleCreator("test_module", "test_area", MagicMock())

    def test_given_verify_can_push_repo_to_remote_passes_then_flag_set_false_and_add_new_remote_and_push_called(self):

        self.nmc_obj.push_repo_to_remote()

        self.assertFalse(self.nmc_obj._can_push_repo_to_remote)

        self.mock_add_new_remote_and_push.assert_called_with(self.nmc_obj._server_repo_path, self.nmc_obj.abs_module_path)

    def test_given_verify_can_push_repo_to_remote_fails_then_exception_raised_with_correct_message(self):

        self.nmc_obj._can_push_repo_to_remote = False
        self.mock_verify_can_push_repo_to_remote.side_effect = mc.VerificationError("error")

        with self.assertRaises(mc.VerificationError) as e:
            self.nmc_obj.push_repo_to_remote()

        self.assertFalse(self.mock_add_new_remote_and_push.called)
        self.assertEqual(str(e.exception), "error")


class ModuleCreatorWithAppsClassInitTest(unittest.TestCase):

    def setUp(self):

        self.mock_mt = set_up_mock(self, 'dls_ade.module_template.ModuleTemplate')
        self.mock_getlogin = set_up_mock(self, 'os.getlogin')
        self.mock_getlogin.return_value = 'test_login'

    def test_given_reasonable_input_then_initialisation_is_successful(self):

        mc.ModuleCreatorWithApps("test_module", "test_area", self.mock_mt, app_name="test_app")

    def test_given_extra_template_args_then_module_template_initialisation_includes_them(self):

        expected_dict = {'module_name': "test_module",
                         'module_path': "test_module",
                         'user_login': "test_login",
                         'app_name': "test_app",
                         'additional': "value"}

        base_c = mc.ModuleCreatorWithApps("test_module", "test_area", self.mock_mt, app_name="test_app", additional="value")

        self.mock_mt.assert_called_once_with(expected_dict)

    def test_given_no_app_name_then_exception_raised_with_correct_message(self):

        comp_message = "'app_name' must be provided as keyword argument."

        with self.assertRaises(mc.mt.ArgumentError) as e:
            base_c = mc.ModuleCreatorWithApps("test_module", "test_area", self.mock_mt, additional="value")

        self.assertEqual(str(e.exception), comp_message)


class ModuleCreatorAddAppToModuleVerifyRemoteRepoTest(unittest.TestCase):

    def setUp(self):

        self.mock_check_if_remote_repo_has_app = set_up_mock(self, 'dls_ade.module_creator.ModuleCreatorAddAppToModule._check_if_remote_repo_has_app')
        self.mock_is_repo_path = set_up_mock(self, 'dls_ade.module_creator.vcs_git.is_repo_path')

        self.nmc_obj = mc.ModuleCreatorAddAppToModule("test_module", "test_area", MagicMock(), app_name="test_app")

        self.nmc_obj._remote_repo_valid = False

    def test_given_remote_repo_valid_true_then_function_returns_immediately(self):

        self.nmc_obj._remote_repo_valid = True

        self.nmc_obj.verify_remote_repo()

        self.assertFalse(self.mock_is_repo_path.called)

    def test_given_server_repo_path_does_not_exist_then_exception_raised_with_correct_message(self):

        self.mock_is_repo_path.return_value = False
        self.nmc_obj._server_repo_path = "notinrepo"

        comp_message = "The path {path:s} does not exist on gitolite, so cannot clone from it".format(path="notinrepo")

        with self.assertRaises(mc.VerificationError) as e:
            self.nmc_obj.verify_remote_repo()

        self.assertEqual(str(e.exception), comp_message)

    def test_given_app_exists_in_server_repo_then_exception_raised_with_correct_error_message(self):

        self.mock_is_repo_path.return_value = True
        self.nmc_obj._server_repo_path = "inrepo1"
        self.mock_check_if_remote_repo_has_app.return_value = True

        comp_message = "The repository {path:s} has an app that conflicts with app name: {app_name:s}".format(path="inrepo1", app_name="test_app")

        with self.assertRaises(mc.VerificationError) as e:
            self.nmc_obj.verify_remote_repo()

        self.assertEqual(str(e.exception), comp_message)

    def test_given_all_checks_passed_then_remote_repo_valid_set_true(self):

        self.mock_is_repo_path.return_value = True
        self.mock_check_if_remote_repo_has_app.return_value = False

        self.nmc_obj.verify_remote_repo()

        self.assertTrue(self.nmc_obj._remote_repo_valid)


class ModuleCreatorAddAppToModuleCheckIfRemoteRepoHasApp(unittest.TestCase):

    def setUp(self):

        self.mock_vcs_git = set_up_mock(self, 'dls_ade.module_creator.vcs_git')
        self.mock_exists = set_up_mock(self, 'dls_ade.module_creator.os.path.exists')
        self.mock_rmtree = set_up_mock(self, 'dls_ade.module_creator.shutil.rmtree')

        self.mock_repo = MagicMock()
        self.mock_vcs_git.temp_clone.return_value = self.mock_repo

        self.mock_repo.working_tree_dir = "tempdir"

        self.nmc_obj = mc.ModuleCreatorAddAppToModule("test_module", "test_area", MagicMock(), app_name="test_app")

    def test_given_remote_repo_path_is_not_on_server_then_exception_raised_with_correct_message(self):

        self.mock_vcs_git.is_repo_path.return_value = False

        comp_message = ("Remote repo {repo:s} does not exist. Cannot "
                        "clone to determine if there is an app_name "
                        "conflict with {app_name:s}".format(repo="test_repo_path", app_name="test_app"))

        with self.assertRaises(mc.RemoteRepoError) as e:
            self.nmc_obj._check_if_remote_repo_has_app("test_repo_path")

        self.assertEqual(str(e.exception), comp_message)

    def test_given_remote_repo_exists_on_server_then_temp_clone_called_correctly(self):

        self.mock_vcs_git.is_repo_path.return_value = True

        try:
            self.nmc_obj._check_if_remote_repo_has_app("test_repo_path")
        except:
            pass

        self.mock_vcs_git.temp_clone.assert_called_once_with("test_repo_path")

    def test_given_app_exists_then_return_value_is_true(self):

        self.mock_vcs_git.is_repo_path.return_value = True
        self.mock_exists.return_value = True

        exists = self.nmc_obj._check_if_remote_repo_has_app("test_repo_path")

        self.assertTrue(exists)
        self.mock_exists.assert_called_once_with("tempdir/test_appApp")

    def test_given_app_does_not_exist_then_return_value_is_false(self):

        self.mock_vcs_git.is_repo_path.return_value = True
        self.mock_exists.return_value = False

        exists = self.nmc_obj._check_if_remote_repo_has_app("test_repo_path")

        self.assertFalse(exists)
        self.mock_exists.assert_called_once_with("tempdir/test_appApp")

    def test_given_exception_raised_in_temp_clone_then_rmtree_not_called(self):

        self.mock_vcs_git.temp_clone.side_effect = Exception("test_exception")
        self.mock_vcs_git.is_repo_path.return_value = True

        with self.assertRaises(Exception) as e:
            self.nmc_obj._check_if_remote_repo_has_app("test_repo_path")

        self.assertEqual(str(e.exception), "test_exception")
        self.assertFalse(self.mock_rmtree.called)

    def test_given_exception_raised_after_mkdtemp_then_rmtree_called(self):

        self.mock_exists.side_effect = Exception("test_exception")
        self.mock_vcs_git.is_repo_path.return_value = True

        with self.assertRaises(Exception) as e:
            self.nmc_obj._check_if_remote_repo_has_app("test_repo_path")

        self.assertEqual(str(e.exception), "test_exception")
        self.mock_rmtree.assert_called_once_with("tempdir")

    def test_given_app_exists_then_true_returned(self):

        self.mock_exists.return_value = True
        self.mock_vcs_git.is_repo_path.return_value = True

        exists = self.nmc_obj._check_if_remote_repo_has_app("test_repo_path")

        self.assertTrue(exists)

    def test_given_app_does_not_exist_then_false_returned(self):

        self.mock_exists.return_value = False
        self.mock_vcs_git.is_repo_path.return_value = True

        exists = self.nmc_obj._check_if_remote_repo_has_app("test_repo_path")

        self.assertFalse(exists)


class ModuleCreatorAddAppToModulePushRepoToRemoteTest(unittest.TestCase):

    def setUp(self):

        self.mock_verify_can_push_repo_to_remote = set_up_mock(self, 'dls_ade.module_creator.ModuleCreatorAddAppToModule.verify_can_push_repo_to_remote')
        self.mock_push_to_remote = set_up_mock(self, 'dls_ade.module_creator.vcs_git.push_to_remote')

        self.nmc_obj = mc.ModuleCreatorAddAppToModule("test_module", "test_area", MagicMock(), app_name="test_app")

    def test_given_verify_can_push_repo_to_remote_passes_then_flag_set_false_and_add_new_remote_and_push_called(self):

        self.nmc_obj.push_repo_to_remote()

        self.assertFalse(self.nmc_obj._can_push_repo_to_remote)

        self.mock_push_to_remote.assert_called_with(self.nmc_obj.abs_module_path)

    def test_given_verify_can_push_repo_to_remote_fails_then_exception_raised_with_correct_message(self):

        self.nmc_obj._can_push_repo_to_remote = False
        self.mock_verify_can_push_repo_to_remote.side_effect = mc.VerificationError("error")

        with self.assertRaises(Exception) as e:
            self.nmc_obj.push_repo_to_remote()

        self.assertFalse(self.mock_push_to_remote.called)
        self.assertEqual(str(e.exception), "error")


class ModuleCreatorAddAppToModuleCreateLocalModuleTest(unittest.TestCase):

    def setUp(self):

            self.mock_chdir = set_up_mock(self, 'dls_ade.module_creator.os.chdir')
            self.mock_vcs_git = set_up_mock(self, 'dls_ade.module_creator.vcs_git')
            self.mock_verify_can_create_local_module = set_up_mock(self, 'dls_ade.module_creator.ModuleCreator.verify_can_create_local_module')

            self.mock_module_template_cls = MagicMock()
            self.mock_module_template = MagicMock()
            self.mock_module_template_cls.return_value = self.mock_module_template
            self.mock_create_files = self.mock_module_template.create_files

            self.nmc_obj = mc.ModuleCreatorAddAppToModule("test_module", "test_area", self.mock_module_template_cls, app_name="test_app")

    def test_given_verify_can_create_local_module_passes_then_flag_set_false_and_clone_and_create_files_called(self):

        self.nmc_obj.create_local_module()

        self.assertFalse(self.nmc_obj._can_create_local_module)

        call_list = [call(self.nmc_obj.abs_module_path), call(self.nmc_obj._cwd)]

        self.mock_vcs_git.clone.assert_called_once_with(self.nmc_obj._server_repo_path, self.nmc_obj.abs_module_path)
        self.mock_chdir.assert_has_calls(call_list)
        self.assertTrue(self.mock_create_files.called)
        self.mock_vcs_git.stage_all_files_and_commit.assert_called_once_with(self.nmc_obj.abs_module_path)

    def test_given_verify_can_create_local_module_fails_then_exception_raised_with_correct_message(self):

        self.mock_verify_can_create_local_module.side_effect = mc.VerificationError("error")

        with self.assertRaises(mc.VerificationError) as e:
            self.nmc_obj.create_local_module()

        self.assertFalse(self.mock_vcs_git.clone.called)
        self.assertEqual(str(e.exception), "error")
