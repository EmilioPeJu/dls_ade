from __future__ import print_function

import unittest
import logging

import dls_ade.get_module_creator as get_mc
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


class GetModuleCreatorTest(unittest.TestCase):

    def setUp(self):

        nmc_classes_to_patch = [
            'Creator',
            'CreatorWithApps',
        ]

        self.nmc_mocks = {}
        for cls in nmc_classes_to_patch:
            self.nmc_mocks[cls] = set_up_mock(self, 'dls_ade.module_creator.Module' + cls)

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

        self.mock_get_new_ioc = set_up_mock(self, 'dls_ade.get_module_creator.get_module_creator_ioc')

        # self.mocks['CreatorTools'].return_value = "Example"

    def test_given_unsupported_area_then_exception_raised(self):

        with self.assertRaises(Exception):
            get_mc.get_module_creator("test_module", "fake_area")

    def test_given_area_is_ioc_then_get_module_creator_ioc_called(self):

        new_ioc_creator = get_mc.get_module_creator("test_module", "ioc", fullname=True)

        self.mock_get_new_ioc.assert_called_once_with("test_module", True)

    def test_given_area_is_python_with_invalid_name_then_module_creator_python_not_returned(self):

        with self.assertRaises(Exception):
            new_py_creator = get_mc.get_module_creator("test_module", "python")

        self.assertFalse(self.mock_nmc_base.called)

        with self.assertRaises(Exception):
            new_py_creator = get_mc.get_module_creator("dls_test-module", "python")

        self.assertFalse(self.mock_nmc_base.called)

        with self.assertRaises(Exception):
            new_py_creator = get_mc.get_module_creator("dls_test.module", "python")

        self.assertFalse(self.mock_nmc_base.called)

    def test_given_area_is_python_with_valid_name_then_module_creator_returned_with_correct_args(self):

        new_py_creator = get_mc.get_module_creator("dls_test_module", "python")

        self.mock_nmc_base.assert_called_once_with("dls_test_module", "python", self.mt_mocks['Python'])

    def test_given_area_is_support_then_module_creator_returned_with_correct_args(self):

        new_sup_creator = get_mc.get_module_creator("test_module")  # Area automatically support

        self.mock_nmc_with_apps.assert_called_once_with("test_module", "support", self.mt_mocks['Support'], app_name="test_module")

    def test_given_area_is_tools_then_module_creator_returned_with_correct_args(self):

        new_tools_creator = get_mc.get_module_creator("test_module", "tools")

        self.mock_nmc_base.assert_called_once_with("test_module", "tools", self.mt_mocks['Tools'])


class GetModuleCreatorIOCTest(unittest.TestCase):

    def setUp(self):

        self.git_root_dir = get_mc.vcs_git.GIT_ROOT_DIR

        nmc_classes_to_patch = [
            'CreatorWithApps',
            'CreatorAddAppToModule'
        ]

        self.nmc_mocks = {}
        for cls in nmc_classes_to_patch:
            self.nmc_mocks[cls] = set_up_mock(self, 'dls_ade.module_creator.Module' + cls)

        self.mock_nmc_with_apps = self.nmc_mocks['CreatorWithApps']
        self.mock_nmc_add_app = self.nmc_mocks['CreatorAddAppToModule']

        mt_classes_to_patch = [
            'IOC',
            'IOCBL'
        ]

        self.mt_mocks = {}
        for cls in mt_classes_to_patch:
            self.mt_mocks[cls] = set_up_mock(self, 'dls_ade.module_template.ModuleTemplate' + cls)

        self.mock_is_repo_path = set_up_mock(self, 'dls_ade.vcs_git.is_repo_path')

        # self.mocks['CreatorTools'].return_value = "Example"

    def test_given_module_name_with_no_slash_or_dash_then_exception_raised_with_correct_message(self):

        comp_message = "Need a name with dashes or hyphens in it, got test_module"

        with self.assertRaises(get_mc.ParsingError) as e:
            new_ioc_creator = get_mc.get_module_creator_ioc("test_module")

        self.assertEqual(str(e.exception), comp_message)

    def test_given_not_BL_and_dash_separated_then_module_creator_with_apps_returned_with_correct_args(self):

        new_ioc_creator = get_mc.get_module_creator_ioc("test-module-IOC-01")

        self.mock_nmc_with_apps.assert_called_once_with("test/test-module-IOC-01", "ioc", self.mt_mocks['IOC'], app_name="test-module-IOC-01")

    def test_given_area_is_ioc_and_not_BL_and_slash_separated_with_fullname_true_then_module_creator_with_apps_returned_with_correct_args(self):

        new_ioc_creator = get_mc.get_module_creator_ioc("test/module/02", fullname=True)

        self.mock_nmc_with_apps.assert_called_once_with("test/test-module-IOC-02", "ioc", self.mt_mocks['IOC'], app_name="test-module-IOC-02")

    def test_given_area_is_ioc_and_not_BL_and_slash_separated_with_fullname_true_but_no_ioc_number_then_module_creator_with_apps_returned_with_correct_args(self):

        new_ioc_creator = get_mc.get_module_creator_ioc("test/module", fullname=True)

        self.mock_nmc_with_apps.assert_called_once_with("test/test-module-IOC-01", "ioc", self.mt_mocks['IOC'], app_name="test-module-IOC-01")

    def test_given_area_is_ioc_and_not_BL_and_slash_separated_with_fullname_false_and_module_path_not_in_remote_repo_then_module_creator_with_apps_returned_with_correct_args(self):

        self.mock_is_repo_path.return_value = False

        new_ioc_creator = get_mc.get_module_creator_ioc("test/module/01", fullname=False)

        self.mock_is_repo_path.assert_called_once_with(self.git_root_dir+"/ioc/test/module")
        self.mock_nmc_with_apps.assert_called_once_with("test/module", "ioc", self.mt_mocks['IOC'], app_name="test-module-IOC-01")

    def test_given_area_is_ioc_and_not_BL_and_slash_separated_with_fullname_false_and_module_path_in_remote_repo_then_module_creator_add_to_module_returned_with_correct_args(self):

        self.mock_is_repo_path.return_value = True

        new_ioc_creator = get_mc.get_module_creator_ioc("test/module/02", fullname=False)

        self.mock_is_repo_path.assert_called_once_with(self.git_root_dir+"/ioc/test/module")
        self.mock_nmc_add_app.assert_called_once_with("test/module", "ioc", self.mt_mocks['IOC'], app_name="test-module-IOC-02")

    def test_given_area_is_ioc_and_tech_area_is_BL_slash_form_then_module_creator_with_apps_returned_with_correct_args(self):

        new_tools_creator = get_mc.get_module_creator_ioc("test/BL")

        self.mock_nmc_with_apps.assert_called_once_with("test/BL", "ioc", self.mt_mocks['IOCBL'], app_name="test")

    def test_given_area_is_ioc_and_tech_area_is_BL_dash_form_then_module_creator_with_apps_returned_with_correct_args(self):

        new_tools_creator = get_mc.get_module_creator_ioc("test-BL-IOC-01", "ioc")

        self.mock_nmc_with_apps.assert_called_once_with("test/test-BL-IOC-01", "ioc", self.mt_mocks['IOCBL'], app_name="test-BL-IOC-01")
