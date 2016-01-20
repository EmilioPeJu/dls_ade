from __future__ import print_function

import unittest
import os
import logging

import dls_ade.new_module_creator as new_c
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


class GetNewModuleCreatorTest(unittest.TestCase):

    def setUp(self):

        nmc_classes_to_patch = [
            'Creator',
            'CreatorWithApps',
        ]

        self.nmc_mocks = {}
        for cls in nmc_classes_to_patch:
            self.nmc_mocks[cls] = set_up_mock(self, 'dls_ade.new_module_creator.NewModule' + cls)

        self.mock_nmc_base = self.nmc_mocks['Creator']
        self.mock_nmc_with_apps = self.nmc_mocks['CreatorWithApps']

        mt_classes_to_patch = [
            'Python',
            'Support',
            'Tools'
        ]

        self.mt_mocks = {}
        for cls in mt_classes_to_patch:
            self.mt_mocks[cls] = set_up_mock(self, 'dls_ade.module_template.ModuleTemplate' + cls)

        self.mock_get_new_ioc = set_up_mock(self, 'dls_ade.new_module_creator.get_new_module_creator_ioc')

        # self.mocks['CreatorTools'].return_value = "Example"

    def test_given_unsupported_area_then_exception_raised(self):

        with self.assertRaises(Exception):
            new_c.get_new_module_creator("test_module", "fake_area")

    def test_given_area_is_ioc_then_get_new_module_creator_ioc_called(self):

        new_ioc_creator = new_c.get_new_module_creator("test_module", "ioc", fullname=True)

        self.mock_get_new_ioc.assert_called_once_with("test_module", True)

    def test_given_area_is_python_with_invalid_name_then_new_module_creator_python_not_returned(self):

        with self.assertRaises(Exception):
            new_py_creator = new_c.get_new_module_creator("test_module", "python")

        self.assertFalse(self.mock_nmc_base.called)

        with self.assertRaises(Exception):
            new_py_creator = new_c.get_new_module_creator("dls_test-module", "python")

        self.assertFalse(self.mock_nmc_base.called)

        with self.assertRaises(Exception):
            new_py_creator = new_c.get_new_module_creator("dls_test.module", "python")

        self.assertFalse(self.mock_nmc_base.called)

    def test_given_area_is_python_with_valid_name_then_new_module_creator_returned_with_correct_args(self):

        new_py_creator = new_c.get_new_module_creator("dls_test_module", "python")

        self.mock_nmc_base.assert_called_once_with("dls_test_module", "python", self.mt_mocks['Python'])

    def test_given_area_is_support_then_new_module_creator_returned_with_correct_args(self):

        new_sup_creator = new_c.get_new_module_creator("test_module")  # Area automatically support

        self.mock_nmc_with_apps.assert_called_once_with("test_module", "support", self.mt_mocks['Support'], app_name="test_module")

    def test_given_area_is_tools_then_new_module_creator_returned_with_correct_args(self):

        new_tools_creator = new_c.get_new_module_creator("test_module", "tools")

        self.mock_nmc_base.assert_called_once_with("test_module", "tools", self.mt_mocks['Tools'])


class GetNewModuleCreatorIOCTest(unittest.TestCase):

    def setUp(self):

        self.git_root_dir = new_c.vcs_git.GIT_ROOT_DIR

        nmc_classes_to_patch = [
            'CreatorWithApps',
            'CreatorAddAppToModule'
        ]

        self.nmc_mocks = {}
        for cls in nmc_classes_to_patch:
            self.nmc_mocks[cls] = set_up_mock(self, 'dls_ade.new_module_creator.NewModule' + cls)

        self.mock_nmc_with_apps = self.nmc_mocks['CreatorWithApps']
        self.mock_nmc_add_app = self.nmc_mocks['CreatorAddAppToModule']

        mt_classes_to_patch = [
            'IOC',
            'IOCBL'
        ]

        self.mt_mocks = {}
        for cls in mt_classes_to_patch:
            self.mt_mocks[cls] = set_up_mock(self, 'dls_ade.module_template.ModuleTemplate' + cls)

        self.mock_is_repo_path = set_up_mock(self, 'dls_ade.new_module_creator.vcs_git.is_repo_path')

        # self.mocks['CreatorTools'].return_value = "Example"

    def test_given_module_name_with_no_slash_or_dash_then_exception_raised_with_correct_message(self):

        comp_message = "Need a name with dashes or hyphens in it, got test_module"

        with self.assertRaises(new_c.ParsingError) as e:
            new_ioc_creator = new_c.get_new_module_creator_ioc("test_module")

        self.assertEqual(str(e.exception), comp_message)

    def test_given_not_BL_and_dash_separated_then_new_module_creator_with_apps_returned_with_correct_args(self):

        new_ioc_creator = new_c.get_new_module_creator_ioc("test-module-IOC-01")

        self.mock_nmc_with_apps.assert_called_once_with("test/test-module-IOC-01", "ioc", self.mt_mocks['IOC'], app_name="test-module-IOC-01")

    def test_given_area_is_ioc_and_not_BL_and_slash_separated_with_fullname_true_then_new_module_creator_with_apps_returned_with_correct_args(self):

        new_ioc_creator = new_c.get_new_module_creator_ioc("test/module/02", fullname=True)

        self.mock_nmc_with_apps.assert_called_once_with("test/test-module-IOC-02", "ioc", self.mt_mocks['IOC'], app_name="test-module-IOC-02")

    def test_given_area_is_ioc_and_not_BL_and_slash_separated_with_fullname_true_but_no_ioc_number_then_new_module_creator_with_apps_returned_with_correct_args(self):

        new_ioc_creator = new_c.get_new_module_creator_ioc("test/module", fullname=True)

        self.mock_nmc_with_apps.assert_called_once_with("test/test-module-IOC-01", "ioc", self.mt_mocks['IOC'], app_name="test-module-IOC-01")

    def test_given_area_is_ioc_and_not_BL_and_slash_separated_with_fullname_false_and_module_path_not_in_remote_repo_then_new_module_creator_with_apps_returned_with_correct_args(self):

        self.mock_is_repo_path.return_value = False

        new_ioc_creator = new_c.get_new_module_creator_ioc("test/module/01", fullname=False)

        self.mock_is_repo_path.assert_called_once_with(self.git_root_dir+"/ioc/test/module")
        self.mock_nmc_with_apps.assert_called_once_with("test/module", "ioc", self.mt_mocks['IOC'], app_name="test-module-IOC-01")

    def test_given_area_is_ioc_and_not_BL_and_slash_separated_with_fullname_false_and_module_path_in_remote_repo_then_new_module_creator_add_to_module_returned_with_correct_args(self):

        self.mock_is_repo_path.return_value = True

        new_ioc_creator = new_c.get_new_module_creator_ioc("test/module/02", fullname=False)

        self.mock_is_repo_path.assert_called_once_with(self.git_root_dir+"/ioc/test/module")
        self.mock_nmc_add_app.assert_called_once_with("test/module", "ioc", self.mt_mocks['IOC'], app_name="test-module-IOC-02")

    def test_given_area_is_ioc_and_tech_area_is_BL_slash_form_then_new_module_creator_with_apps_returned_with_correct_args(self):

        new_tools_creator = new_c.get_new_module_creator_ioc("test/BL")

        self.mock_nmc_with_apps.assert_called_once_with("test/BL", "ioc", self.mt_mocks['IOCBL'], app_name="test")

    def test_given_area_is_ioc_and_tech_area_is_BL_dash_form_then_new_module_creator_with_apps_returned_with_correct_args(self):

        new_tools_creator = new_c.get_new_module_creator_ioc("test-BL-IOC-01", "ioc")

        self.mock_nmc_with_apps.assert_called_once_with("test/test-BL-IOC-01", "ioc", self.mt_mocks['IOCBL'], app_name="test-BL-IOC-01")


class NewModuleCreatorClassInitTest(unittest.TestCase):

    def setUp(self):

        self.mock_mt = set_up_mock(self, 'dls_ade.module_template.ModuleTemplate')
        self.mock_getlogin = set_up_mock(self, 'os.getlogin')
        self.mock_getlogin.return_value = 'test_login'

    def test_given_reasonable_input_then_initialisation_is_successful(self):

        new_c.NewModuleCreator("test_module", "test_area", self.mock_mt)

    def test_given_extra_template_args_then_module_template_initialisation_includes_them(self):

        expected_dict = {'module_name': "test_module",
                         'module_path': "test_module",
                         'user_login': "test_login",
                         'additional': "value"}

        base_c = new_c.NewModuleCreator("test_module", "test_area", self.mock_mt, additional="value")

        self.mock_mt.assert_called_once_with(expected_dict)

    def test_given_no_extra_template_args_then_module_template_initialisation_behaves_as_normal(self):

        expected_dict = {'module_name': "test_module",
                         'module_path': "test_module",
                         'user_login': "test_login"}

        base_c = new_c.NewModuleCreator("test_module", "test_area", self.mock_mt)

        self.mock_mt.assert_called_once_with(expected_dict)


class NewModuleCreatorVerifyRemoteRepoTest(unittest.TestCase):

    def setUp(self):

        self.mock_is_repo_path = set_up_mock(self, 'dls_ade.vcs_git.is_repo_path')

        self.nmc_obj = new_c.NewModuleCreator("test_module", "test_area", MagicMock())

        self.nmc_obj._remote_repo_valid = False

    def test_given_remote_repo_valid_true_then_function_returns_immediately(self):

        self.nmc_obj._remote_repo_valid = True

        self.nmc_obj.verify_remote_repo()

        self.assertFalse(self.mock_is_repo_path.called)

    def test_given_remote_repo_path_exists_then_exception_raised_with_correct_message(self):

        server_repo_path = self.nmc_obj._server_repo_path

        self.mock_is_repo_path.return_value = True
        comp_message = "The path {dir:s} already exists on gitolite, cannot continue".format(dir=server_repo_path)

        with self.assertRaises(new_c.VerificationError) as e:
            self.nmc_obj.verify_remote_repo()

        self.assertEqual(str(e.exception), comp_message)

    def test_given_remote_repo_does_not_exist_then_remote_repo_valid_set_true(self):

        self.mock_is_repo_path.return_value = False

        self.nmc_obj.verify_remote_repo()

        self.assertTrue(self.nmc_obj._remote_repo_valid)


class NewModuleCreatorVerifyCanCreateLocalModule(unittest.TestCase):

    def setUp(self):

        self.mock_exists = set_up_mock(self, 'dls_ade.new_module_creator.os.path.exists')
        self.mock_is_git_dir = set_up_mock(self, 'dls_ade.new_module_creator.vcs_git.is_git_dir')

        self.nmc_obj = new_c.NewModuleCreator("test_module", "test_area", MagicMock())

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

        with self.assertRaises(new_c.VerificationError) as e:
            self.nmc_obj.verify_can_create_local_module()

        self.assertEqual(str(e.exception), comp_message)

        self.assertFalse(self.nmc_obj._remote_repo_valid)

    def test_given_module_folder_is_in_git_repo_then_flag_set_false_and_error_returned_is_correct(self):

        self.mock_exists.return_value = False
        self.mock_is_git_dir.return_value = True

        comp_message = "Currently in a git repository, please move elsewhere and try again.".format(dir=os.path.join("./", self.nmc_obj.disk_dir))

        with self.assertRaises(new_c.VerificationError) as e:
            self.nmc_obj.verify_can_create_local_module()

        self.assertEqual(str(e.exception), comp_message)

        self.assertFalse(self.nmc_obj._remote_repo_valid)

    def test_given_module_folder_exists_and_is_in_repo_then_flag_set_false_and_error_returned_is_correct(self):

        self.mock_exists.return_value = True
        self.mock_is_git_dir.return_value = True

        comp_message = "Directory {dir:s} already exists, please move elsewhere and try again.\n"
        comp_message += "Currently in a git repository, please move elsewhere and try again."
        comp_message = comp_message.format(dir=self.nmc_obj._module_path)

        with self.assertRaises(new_c.VerificationError) as e:
            self.nmc_obj.verify_can_create_local_module()

        self.assertEqual(str(e.exception), comp_message)

        self.assertFalse(self.nmc_obj._remote_repo_valid)


class NewModuleCreatorVerifyCanPushLocalRepoToRemoteTest(unittest.TestCase):

    def setUp(self):

        self.mock_exists = set_up_mock(self, 'dls_ade.new_module_creator.os.path.exists')
        self.mock_is_git_root_dir = set_up_mock(self, 'dls_ade.new_module_creator.vcs_git.is_git_root_dir')
        self.mock_verify_remote_repo = set_up_mock(self, 'dls_ade.new_module_creator.NewModuleCreator.verify_remote_repo')

        self.nmc_obj = new_c.NewModuleCreator("test_module", "test_area", MagicMock())

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

        self.mock_verify_remote_repo.side_effect = new_c.VerificationError("error")

        self.mock_exists.return_value = True
        self.mock_is_git_root_dir.return_value = True

        with self.assertRaises(new_c.VerificationError) as e:
            self.nmc_obj.verify_can_push_repo_to_remote()

        self.assertEqual(str(e.exception), "error")
        self.assertFalse(self.nmc_obj._can_push_repo_to_remote)

    def test_given_module_folder_does_not_exist_then_flag_set_false_and_error_returned_is_correct(self):

        self.mock_exists.return_value = False
        self.mock_is_git_root_dir.return_value = False

        self.nmc_obj._remote_repo_valid = True

        comp_message = "Directory {dir:s} does not exist.".format(dir=self.nmc_obj._module_path)

        with self.assertRaises(new_c.VerificationError) as e:
            self.nmc_obj.verify_can_push_repo_to_remote()

        self.assertEqual(str(e.exception), comp_message)
        self.assertFalse(self.nmc_obj._can_push_repo_to_remote)

    def test_given_module_folder_is_not_repo_then_flag_set_false_and_error_returned_is_correct(self):

        self.mock_exists.return_value = True
        self.mock_is_git_root_dir.return_value = False

        self.nmc_obj._remote_repo_valid = True

        comp_message = "Directory {dir:s} is not a git repository. Unable to push to remote repository.".format(dir=self.nmc_obj._module_path)

        with self.assertRaises(new_c.VerificationError) as e:
            self.nmc_obj.verify_can_push_repo_to_remote()

        self.assertEqual(str(e.exception), comp_message)
        self.assertFalse(self.nmc_obj._can_push_repo_to_remote)

    def test_given_module_folder_is_not_repo_and_remote_repo_false_then_flag_set_false_and_error_returned_is_correct(self):

        self.mock_verify_remote_repo.side_effect = new_c.VerificationError('error')
        self.mock_exists.return_value = True
        self.mock_is_git_root_dir.return_value = False

        comp_message = "Directory {dir:s} is not a git repository. Unable to push to remote repository.\n"
        comp_message = comp_message.format(dir=self.nmc_obj._module_path)
        comp_message += "error"
        comp_message = comp_message.rstrip()

        with self.assertRaises(new_c.VerificationError) as e:
            self.nmc_obj.verify_can_push_repo_to_remote()

        self.assertEqual(str(e.exception), comp_message)
        self.assertFalse(self.nmc_obj._can_push_repo_to_remote)


class NewModuleCreatorCreateLocalModuleTest(unittest.TestCase):

    def setUp(self):

        self.mock_os = set_up_mock(self, 'dls_ade.new_module_creator.os')
        self.mock_vcs_git = set_up_mock(self, 'dls_ade.new_module_creator.vcs_git')
        self.mock_verify_can_create_local_module = set_up_mock(self, 'dls_ade.new_module_creator.NewModuleCreator.verify_can_create_local_module')

        self.mock_module_template_cls = MagicMock()
        self.mock_module_template = MagicMock()
        self.mock_module_template_cls.return_value = self.mock_module_template
        self.mock_create_files = self.mock_module_template.create_files

        self.nmc_obj = new_c.NewModuleCreator("test_module", "test_area", self.mock_module_template_cls)

    def test_given_verify_can_create_local_module_passes_then_can_create_local_module_set_false(self):

        self.nmc_obj.create_local_module()

        self.assertFalse(self.nmc_obj._can_create_local_module)

    def test_given_verify_can_create_local_module_fails_then_exception_raised_with_correct_message(self):

        self.mock_verify_can_create_local_module.side_effect = new_c.VerificationError("error")

        with self.assertRaises(Exception) as e:
            self.nmc_obj.create_local_module()

        self.assertFalse(self.mock_os.path.isdir.called)
        self.assertEqual(str(e.exception), "error")

    def test_given_can_create_local_module_true_then_rest_of_function_is_run(self):

        self.nmc_obj.create_local_module()

        call_list = [call(self.nmc_obj.disk_dir), call(self.nmc_obj._cwd)]

        self.mock_os.chdir.assert_has_calls(call_list)
        self.assertTrue(self.mock_create_files.called)
        self.mock_vcs_git.init_repo.assert_called_once_with(self.nmc_obj.disk_dir)
        self.mock_vcs_git.stage_all_files_and_commit.assert_called_once_with(self.nmc_obj.disk_dir)


class NewModuleCreatorPrintMessageTest(unittest.TestCase):

    def setUp(self):

        self.mock_module_template = MagicMock()
        self.nmc_obj = new_c.NewModuleCreator("test_module", "test_area", self.mock_module_template)

    def test_given_function_called_then_module_template_print_message_called(self):

        self.nmc_obj.print_message()

        self.mock_module_template.print_message_assert_called_once_with()


class NewModuleCreatorPushRepoToRemoteTest(unittest.TestCase):

    def setUp(self):

        self.mock_verify_can_push_repo_to_remote = set_up_mock(self, 'dls_ade.new_module_creator.NewModuleCreator.verify_can_push_repo_to_remote')
        self.mock_add_new_remote_and_push = set_up_mock(self, 'dls_ade.new_module_creator.vcs_git.add_new_remote_and_push')

        self.nmc_obj = new_c.NewModuleCreator("test_module", "test_area", MagicMock())

    def test_given_verify_can_push_repo_to_remote_passes_then_flag_set_false_and_add_new_remote_and_push_called(self):

        self.nmc_obj.push_repo_to_remote()

        self.assertFalse(self.nmc_obj._can_push_repo_to_remote)

        self.mock_add_new_remote_and_push.assert_called_with(self.nmc_obj._server_repo_path, self.nmc_obj.disk_dir)

    def test_given_verify_can_push_repo_to_remote_fails_then_exception_raised_with_correct_message(self):

        self.nmc_obj._can_push_repo_to_remote = False
        self.mock_verify_can_push_repo_to_remote.side_effect = new_c.VerificationError("error")

        with self.assertRaises(new_c.VerificationError) as e:
            self.nmc_obj.push_repo_to_remote()

        self.assertFalse(self.mock_add_new_remote_and_push.called)
        self.assertEqual(str(e.exception), "error")


class NewModuleCreatorWithAppsClassInitTest(unittest.TestCase):

    def setUp(self):

        self.mock_mt = set_up_mock(self, 'dls_ade.module_template.ModuleTemplate')
        self.mock_getlogin = set_up_mock(self, 'os.getlogin')
        self.mock_getlogin.return_value = 'test_login'

    def test_given_reasonable_input_then_initialisation_is_successful(self):

        new_c.NewModuleCreatorWithApps("test_module", "test_area", self.mock_mt, app_name="test_app")

    def test_given_extra_template_args_then_module_template_initialisation_includes_them(self):

        expected_dict = {'module_name': "test_module",
                         'module_path': "test_module",
                         'user_login': "test_login",
                         'app_name': "test_app",
                         'additional': "value"}

        base_c = new_c.NewModuleCreatorWithApps("test_module", "test_area", self.mock_mt, app_name="test_app", additional="value")

        self.mock_mt.assert_called_once_with(expected_dict)

    def test_given_no_app_name_then_exception_raised_with_correct_message(self):

        comp_message = "'app_name' must be provided as keyword argument."

        with self.assertRaises(new_c.mt.ArgumentError) as e:
            base_c = new_c.NewModuleCreatorWithApps("test_module", "test_area", self.mock_mt, additional="value")

        self.assertEqual(str(e.exception), comp_message)


class NewModuleCreatorAddAppToModuleVerifyRemoteRepoTest(unittest.TestCase):

    def setUp(self):

        self.mock_check_if_remote_repo_has_app = set_up_mock(self, 'dls_ade.new_module_creator.NewModuleCreatorAddAppToModule._check_if_remote_repo_has_app')
        self.mock_is_repo_path = set_up_mock(self, 'dls_ade.new_module_creator.vcs_git.is_repo_path')

        self.nmc_obj = new_c.NewModuleCreatorAddAppToModule("test_module", "test_area", MagicMock(), app_name="test_app")

        self.nmc_obj._remote_repo_valid = False

    def test_given_remote_repo_valid_true_then_function_returns_immediately(self):

        self.nmc_obj._remote_repo_valid = True

        self.nmc_obj.verify_remote_repo()

        self.assertFalse(self.mock_is_repo_path.called)

    def test_given_server_repo_path_does_not_exist_then_exception_raised_with_correct_message(self):

        self.mock_is_repo_path.return_value = False
        self.nmc_obj._server_repo_path = "notinrepo"

        comp_message = "The path {path:s} does not exist on gitolite, so cannot clone from it".format(path="notinrepo")

        with self.assertRaises(new_c.VerificationError) as e:
            self.nmc_obj.verify_remote_repo()

        self.assertEqual(str(e.exception), comp_message)

    def test_given_app_exists_in_server_repo_then_exception_raised_with_correct_error_message(self):

        self.mock_is_repo_path.return_value = True
        self.nmc_obj._server_repo_path = "inrepo1"
        self.mock_check_if_remote_repo_has_app.return_value = True

        comp_message = "The repository {path:s} has an app that conflicts with app name: {app_name:s}".format(path="inrepo1", app_name="test_app")

        with self.assertRaises(new_c.VerificationError) as e:
            self.nmc_obj.verify_remote_repo()

        self.assertEqual(str(e.exception), comp_message)

    def test_given_all_checks_passed_then_remote_repo_valid_set_true(self):

        self.mock_is_repo_path.return_value = True
        self.mock_check_if_remote_repo_has_app.return_value = False

        self.nmc_obj.verify_remote_repo()

        self.assertTrue(self.nmc_obj._remote_repo_valid)


class NewModuleCreatorAddAppToModuleCheckIfRemoteRepoHasApp(unittest.TestCase):

    def setUp(self):

        self.mock_vcs_git = set_up_mock(self, 'dls_ade.new_module_creator.vcs_git')
        self.mock_exists = set_up_mock(self, 'dls_ade.new_module_creator.os.path.exists')
        self.mock_rmtree = set_up_mock(self, 'dls_ade.new_module_creator.shutil.rmtree')

        self.mock_repo = MagicMock()
        self.mock_vcs_git.temp_clone.return_value = self.mock_repo

        self.mock_repo.working_tree_dir = "tempdir"

        self.nmc_obj = new_c.NewModuleCreatorAddAppToModule("test_module", "test_area", MagicMock(), app_name="test_app")

    def test_given_remote_repo_path_is_not_on_server_then_exception_raised_with_correct_message(self):

        self.mock_vcs_git.is_repo_path.return_value = False

        comp_message = ("Remote repo {repo:s} does not exist. Cannot "
                        "clone to determine if there is an app_name "
                        "conflict with {app_name:s}".format(repo="test_repo_path", app_name="test_app"))

        with self.assertRaises(new_c.RemoteRepoError) as e:
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


class NewModuleCreatorAddAppToModulePushRepoToRemoteTest(unittest.TestCase):

    def setUp(self):

        self.mock_verify_can_push_repo_to_remote = set_up_mock(self, 'dls_ade.new_module_creator.NewModuleCreatorAddAppToModule.verify_can_push_repo_to_remote')
        self.mock_push_to_remote = set_up_mock(self, 'dls_ade.new_module_creator.vcs_git.push_to_remote')

        self.nmc_obj = new_c.NewModuleCreatorAddAppToModule("test_module", "test_area", MagicMock(), app_name="test_app")

    def test_given_verify_can_push_repo_to_remote_passes_then_flag_set_false_and_add_new_remote_and_push_called(self):

        self.nmc_obj.push_repo_to_remote()

        self.assertFalse(self.nmc_obj._can_push_repo_to_remote)

        self.mock_push_to_remote.assert_called_with(self.nmc_obj.disk_dir)

    def test_given_verify_can_push_repo_to_remote_fails_then_exception_raised_with_correct_message(self):

        self.nmc_obj._can_push_repo_to_remote = False
        self.mock_verify_can_push_repo_to_remote.side_effect = new_c.VerificationError("error")

        with self.assertRaises(Exception) as e:
            self.nmc_obj.push_repo_to_remote()

        self.assertFalse(self.mock_push_to_remote.called)
        self.assertEqual(str(e.exception), "error")


class NewModuleCreatorAddAppToModuleCreateLocalModuleTest(unittest.TestCase):

    def setUp(self):

            self.mock_chdir = set_up_mock(self, 'dls_ade.new_module_creator.os.chdir')
            self.mock_vcs_git = set_up_mock(self, 'dls_ade.new_module_creator.vcs_git')
            self.mock_verify_can_create_local_module = set_up_mock(self, 'dls_ade.new_module_creator.NewModuleCreator.verify_can_create_local_module')

            self.mock_module_template_cls = MagicMock()
            self.mock_module_template = MagicMock()
            self.mock_module_template_cls.return_value = self.mock_module_template
            self.mock_create_files = self.mock_module_template.create_files

            self.nmc_obj = new_c.NewModuleCreatorAddAppToModule("test_module", "test_area", self.mock_module_template_cls, app_name="test_app")

    def test_given_verify_can_create_local_module_passes_then_flag_set_false_and_clone_and_create_files_called(self):

        self.nmc_obj.create_local_module()

        self.assertFalse(self.nmc_obj._can_create_local_module)

        call_list = [call(self.nmc_obj.disk_dir), call(self.nmc_obj._cwd)]

        self.mock_vcs_git.clone.assert_called_once_with(self.nmc_obj._server_repo_path, self.nmc_obj.disk_dir)
        self.mock_chdir.assert_has_calls(call_list)
        self.assertTrue(self.mock_create_files.called)
        self.mock_vcs_git.stage_all_files_and_commit.assert_called_once_with(self.nmc_obj.disk_dir)

    def test_given_verify_can_create_local_module_fails_then_exception_raised_with_correct_message(self):

        self.mock_verify_can_create_local_module.side_effect = new_c.VerificationError("error")

        with self.assertRaises(new_c.VerificationError) as e:
            self.nmc_obj.create_local_module()

        self.assertFalse(self.mock_vcs_git.clone.called)
        self.assertEqual(str(e.exception), "error")
