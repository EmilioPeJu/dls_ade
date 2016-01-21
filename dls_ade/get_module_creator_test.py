from __future__ import print_function

import unittest
import logging

import dls_ade.get_module_creator as get_mc
from exceptions import ParsingError
from pkg_resources import require
require("mock")
from mock import patch, ANY, MagicMock, call

logging.basicConfig(level=logging.DEBUG)


def set_up_mock(test_case_object, path):

    patch_obj = patch(path)

    test_case_object.addCleanup(patch_obj.stop)

    mock_obj = patch_obj.start()

    return mock_obj


class GetModuleCreatorTest(unittest.TestCase):

    def setUp(self):

        self.git_root_dir = get_mc.vcs_git.GIT_ROOT_DIR

        self.mock_nmc_base = set_up_mock(self, 'dls_ade.module_creator.ModuleCreator')
        self.mock_nmc_base.return_value = "ModuleCreatorBase"

        self.mock_nmc_with_apps = set_up_mock(self, 'dls_ade.module_creator.ModuleCreatorWithApps')
        self.mock_nmc_with_apps.return_value = "ModuleCreatorWithApps"

        self.mock_nmc_add_app = set_up_mock(self, 'dls_ade.module_creator.ModuleCreatorAddAppToModule')
        self.mock_nmc_add_app.return_value = "ModuleCreatorAddApp"

        mt_classes_to_patch = [
            'Python',
            'Support',
            'Tools',
            'IOC',
            'IOCBL'
        ]

        self.mt_mocks = {}
        for cls in mt_classes_to_patch:
            self.mt_mocks[cls] = set_up_mock(self, 'dls_ade.module_template.ModuleTemplate' + cls)

        self.mock_is_repo_path = set_up_mock(self, 'dls_ade.vcs_git.is_repo_path')

        # self.mocks['CreatorTools'].return_value = "Example"


class GetModuleCreatorTestBase(GetModuleCreatorTest):

    def test_given_unsupported_area_then_exception_raised(self):

        with self.assertRaises(ParsingError) as e:
            get_mc.get_module_creator("test_module", "fake_area")

        self.assertTrue("fake_area" in str(e.exception))


class GetModuleCreatorTestPython(GetModuleCreatorTest):

    def test_given_area_is_python_with_invalid_name_then_module_creator_python_not_returned(self):

        with self.assertRaises(ParsingError) as e:
            new_py_creator = get_mc.get_module_creator("test_module", "python")

        self.assertFalse(self.mock_nmc_base.called)

        with self.assertRaises(ParsingError) as e:
            new_py_creator = get_mc.get_module_creator("dls_test-module", "python")

        self.assertFalse(self.mock_nmc_base.called)

        with self.assertRaises(ParsingError) as e:
            new_py_creator = get_mc.get_module_creator("dls_test.module", "python")

        self.assertFalse(self.mock_nmc_base.called)

    def test_given_area_is_python_with_valid_name_then_module_creator_returned_with_correct_args(self):

        new_py_creator = get_mc.get_module_creator("dls_test_module", "python")

        self.assertEqual(new_py_creator, "ModuleCreatorBase")
        self.mock_nmc_base.assert_called_once_with("dls_test_module", "python", self.mt_mocks['Python'])

class GetModuleCreatorTestTools(GetModuleCreatorTest):

    def test_given_area_is_tools_then_module_creator_returned_with_correct_args(self):

        new_tools_creator = get_mc.get_module_creator("test_module", "tools")

        self.assertEqual(new_tools_creator, "ModuleCreatorBase")
        self.mock_nmc_base.assert_called_once_with("test_module", "tools", self.mt_mocks['Tools'])


class GetModuleCreatorTestSupport(GetModuleCreatorTest):

    def test_given_area_is_support_then_module_creator_returned_with_correct_args(self):

        new_sup_creator = get_mc.get_module_creator("test_module")  # Area automatically support

        self.assertEqual(new_sup_creator, "ModuleCreatorWithApps")
        self.mock_nmc_with_apps.assert_called_once_with("test_module", "support", self.mt_mocks['Support'], app_name="test_module")


class GetModuleCreatorTestIOC(GetModuleCreatorTest):

    def test_given_module_name_with_invalid_separators_then_exception_raised_with_correct_message(self):

        with self.assertRaises(ParsingError) as e:
            new_ioc_creator = get_mc.get_module_creator_ioc("test_module")

        self.assertTrue("test_module" in str(e.exception))

    def test_given_not_BL_and_dash_separated_then_module_creator_with_apps_returned_with_correct_args(self):

        new_ioc_creator = get_mc.get_module_creator_ioc("test-module-IOC-01")

        self.assertEqual(new_ioc_creator, "ModuleCreatorWithApps")
        self.mock_nmc_with_apps.assert_called_once_with("test/test-module-IOC-01", "ioc", self.mt_mocks['IOC'], app_name="test-module-IOC-01")

    def test_given_area_is_ioc_and_not_BL_and_slash_separated_with_fullname_true_then_module_creator_with_apps_returned_with_correct_args(self):

        new_ioc_creator = get_mc.get_module_creator_ioc("test/module/02", fullname=True)

        self.assertEqual(new_ioc_creator, "ModuleCreatorWithApps")
        self.mock_nmc_with_apps.assert_called_once_with("test/test-module-IOC-02", "ioc", self.mt_mocks['IOC'], app_name="test-module-IOC-02")

    def test_given_area_is_ioc_and_not_BL_and_slash_separated_with_fullname_true_but_no_ioc_number_then_module_creator_with_apps_returned_with_correct_args(self):

        new_ioc_creator = get_mc.get_module_creator_ioc("test/module", fullname=True)

        self.assertEqual(new_ioc_creator, "ModuleCreatorWithApps")
        self.mock_nmc_with_apps.assert_called_once_with("test/test-module-IOC-01", "ioc", self.mt_mocks['IOC'], app_name="test-module-IOC-01")

    def test_given_area_is_ioc_and_not_BL_and_slash_separated_with_fullname_false_and_module_path_not_in_remote_repo_then_module_creator_with_apps_returned_with_correct_args(self):

        self.mock_is_repo_path.return_value = False

        new_ioc_creator = get_mc.get_module_creator_ioc("test/module/01", fullname=False)

        self.assertEqual(new_ioc_creator, "ModuleCreatorWithApps")
        self.mock_is_repo_path.assert_called_once_with(self.git_root_dir+"/ioc/test/module")
        self.mock_nmc_with_apps.assert_called_once_with("test/module", "ioc", self.mt_mocks['IOC'], app_name="test-module-IOC-01")

    def test_given_area_is_ioc_and_not_BL_and_slash_separated_with_fullname_false_and_module_path_in_remote_repo_then_module_creator_add_to_module_returned_with_correct_args(self):

        self.mock_is_repo_path.return_value = True

        new_ioc_creator = get_mc.get_module_creator_ioc("test/module/02", fullname=False)

        self.assertEqual(new_ioc_creator, "ModuleCreatorAddApp")
        self.mock_is_repo_path.assert_called_once_with(self.git_root_dir+"/ioc/test/module")
        self.mock_nmc_add_app.assert_called_once_with("test/module", "ioc", self.mt_mocks['IOC'], app_name="test-module-IOC-02")


class GetModuleCreatorTestIOCBL(GetModuleCreatorTest):

    def test_given_module_name_with_invalid_separators_then_exception_raised_with_correct_message(self):

        with self.assertRaises(ParsingError) as e:
            new_ioc_bl_creator = get_mc.get_module_creator_ioc("test_BL_module")

        self.assertTrue("test_BL_module" in str(e.exception))

    def test_given_area_is_ioc_and_tech_area_is_BL_slash_form_then_module_creator_with_apps_returned_with_correct_args(self):

        new_ioc_bl_creator = get_mc.get_module_creator_ioc("test/BL")

        self.assertEqual(new_ioc_bl_creator, "ModuleCreatorWithApps")
        self.mock_nmc_with_apps.assert_called_once_with("test/BL", "ioc", self.mt_mocks['IOCBL'], app_name="test")

    def test_given_area_is_ioc_and_tech_area_is_BL_dash_form_then_module_creator_with_apps_returned_with_correct_args(self):

        new_ioc_bl_creator = get_mc.get_module_creator_ioc("test-BL-IOC-01", "ioc")

        self.assertEqual(new_ioc_bl_creator, "ModuleCreatorWithApps")
        self.mock_nmc_with_apps.assert_called_once_with("test/test-BL-IOC-01", "ioc", self.mt_mocks['IOCBL'], app_name="test-BL-IOC-01")


class SplitIOCModuleNameTest(unittest.TestCase):

    def test_given_module_splits_by_slash_with_second_part_not_empty_then_function_returns_correctly(self):

        dash_sep, cols = get_mc.split_ioc_module_name("part_one/part_two")

        self.assertFalse(dash_sep)
        self.assertEqual(cols, ["part_one", "part_two"])

    def test_given_module_splits_by_slash_with_second_part_empty_then_function_raises_exception_with_correct_message(self):

        comp_message = "Need a name with dashes or hyphens in it, got part_one/"

        with self.assertRaises(ParsingError) as e:
            get_mc.split_ioc_module_name("part_one/")

        self.assertEqual(str(e.exception), comp_message)

    def test_given_module_splits_by_hyphen_with_second_part_not_empty_then_function_returns_correctly(self):

        dash_sep, cols = get_mc.split_ioc_module_name("part_one-part_two")

        self.assertTrue(dash_sep)
        self.assertEqual(cols, ["part_one", "part_two"])

    def test_given_module_splits_by_dash_with_second_part_empty_then_function_returns_correctly(self):

        dash_sep, cols = get_mc.split_ioc_module_name("part_one-")

        self.assertTrue(dash_sep)
        self.assertEqual(cols, ["part_one", ""])

    def test_given_neither_slash_nor_dash_then_exception_raised_with_correct_message(self):

        comp_message = "Need a name with dashes or hyphens in it, got this_has_no_separator"

        with self.assertRaises(ParsingError) as e:
            get_mc.split_ioc_module_name("this_has_no_separator")

        self.assertEqual(str(e.exception), comp_message)