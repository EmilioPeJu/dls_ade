from __future__ import print_function

import unittest
import os

import dls_ade.new_module_creator as nmc
from pkg_resources import require
require("mock")
from mock import patch, ANY, MagicMock, mock_open, call, mock_open
from new_module_templates import py_files, tools_files, default_files

from sys import version_info
if version_info.major == 2:
    import __builtin__ as builtins  # Allows for Python 2/3 compatibility, 'builtins' is namespace for inbuilt functions
else:
    import builtins


class GetNewModuleCreatorTest(unittest.TestCase):

    def setUp(self):

        methods_to_patch = [
            'CreatorPython',
            'CreatorSupport',
            'CreatorTools'
        ]

        self.patch = {}
        self.mocks = {}
        for method in methods_to_patch:
            self.patch[method] = patch('dls_ade.new_module_creator.NewModule' + method)
            self.addCleanup(self.patch[method].stop)
            self.mocks[method] = self.patch[method].start()

        self.patch_get_new_ioc = patch('dls_ade.new_module_creator.get_new_module_creator_ioc')
        self.addCleanup(self.patch_get_new_ioc.stop)
        self.mock_get_new_ioc = self.patch_get_new_ioc.start()

        # self.mocks['CreatorTools'].return_value = "Example"

    def test_given_unsupported_area_then_exception_raised(self):

        with self.assertRaises(Exception):
            nmc.get_new_module_creator("test_module", "fake_area")

    def test_given_area_is_ioc_then_get_new_module_creator_ioc_called(self):

        new_ioc_creator = nmc.get_new_module_creator("test_module", "ioc", fullname=True)

        self.mock_get_new_ioc.assert_called_once_with("test_module", True)

    def test_given_area_is_python_with_invalid_name_then_new_module_creator_python_not_returned(self):

        py_c_mock = self.mocks['CreatorPython']

        with self.assertRaises(Exception):
            new_py_creator = nmc.get_new_module_creator("test_module", "python")

        self.assertFalse(py_c_mock.called)

        with self.assertRaises(Exception):
            new_py_creator = nmc.get_new_module_creator("dls_test-module", "python")

        self.assertFalse(py_c_mock.called)

        with self.assertRaises(Exception):
            new_py_creator = nmc.get_new_module_creator("dls_test.module", "python")

        self.assertFalse(py_c_mock.called)

    def test_given_area_is_python_with_valid_name_then_new_module_creator_python_called_with_correct_args(self):

        py_c_mock = self.mocks['CreatorPython']

        new_py_creator = nmc.get_new_module_creator("dls_test_module", "python")

        py_c_mock.assert_called_once_with("dls_test_module", "python")

    def test_given_area_is_support_then_new_module_creator_support_returned(self):

        sup_c_mock = self.mocks['CreatorSupport']

        new_sup_creator = nmc.get_new_module_creator("test_module")  # Area automatically support

        sup_c_mock.assert_called_once_with("test_module", "support")

    def test_given_area_is_tools_then_new_module_creator_tools_returned(self):

        tools_c_mock = self.mocks['CreatorTools']

        new_tools_creator = nmc.get_new_module_creator("test_module", "tools")

        tools_c_mock.assert_called_once_with("test_module", "tools")


class GetNewModuleCreatorIOCTest(unittest.TestCase):

    def setUp(self):

        methods_to_patch = [
            'CreatorIOC',
            'CreatorIOCAddToModule',
            'CreatorIOCBL',
        ]

        self.patch = {}
        self.mocks = {}
        for method in methods_to_patch:
            self.patch[method] = patch('dls_ade.new_module_creator.NewModule' + method)
            self.addCleanup(self.patch[method].stop)
            self.mocks[method] = self.patch[method].start()

        # self.mocks['CreatorTools'].return_value = "Example"

    def test_given_module_name_with_no_slash_or_dash_then_exception_raised_with_correct_message(self):

        comp_message = "Need a name with dashes or hyphens in it, got test_module"

        with self.assertRaises(nmc.Error) as e:
            new_ioc_creator = nmc.get_new_module_creator_ioc("test_module")

        self.assertEqual(str(e.exception), comp_message)

    def test_given_not_BL_and_dash_separated_then_new_module_creator_ioc_called_with_correct_args(self):

        ioc_c_mock = self.mocks['CreatorIOC']

        new_ioc_creator = nmc.get_new_module_creator_ioc("test-module-IOC-01")

        ioc_c_mock.assert_called_once_with("test/test-module-IOC-01", "test-module-IOC-01", "ioc")

    def test_given_area_is_ioc_and_not_BL_and_slash_separated_with_fullname_true_then_new_module_creator_ioc_called_with_correct_args(self):

        ioc_c_mock = self.mocks['CreatorIOC']

        new_ioc_creator = nmc.get_new_module_creator_ioc("test/module/02", fullname=True)

        ioc_c_mock.assert_called_once_with("test/test-module-IOC-02", "test-module-IOC-02", "ioc")

    def test_given_area_is_ioc_and_not_BL_and_slash_separated_with_fullname_true_but_no_ioc_number_then_new_module_creator_ioc_called_with_correct_args(self):

        ioc_c_mock = self.mocks['CreatorIOC']

        new_ioc_creator = nmc.get_new_module_creator_ioc("test/module", fullname=True)

        ioc_c_mock.assert_called_once_with("test/test-module-IOC-01", "test-module-IOC-01", "ioc")

    @patch('dls_ade.new_module_creator.vcs_git.is_repo_path', return_value=False)
    def test_given_area_is_ioc_and_not_BL_and_slash_separated_with_fullname_false_and_module_path_not_in_remote_repo_then_new_module_creator_ioc_called_with_correct_args(self, mock_is_repo_path):

        ioc_c_mock = self.mocks['CreatorIOC']

        new_ioc_creator = nmc.get_new_module_creator_ioc("test/module/01", fullname=False)

        mock_is_repo_path.assert_called_once_with("controls/ioc/test/module")
        ioc_c_mock.assert_called_once_with("test/module", "test-module-IOC-01", "ioc")

    @patch('dls_ade.new_module_creator.vcs_git.is_repo_path', return_value=True)
    def test_given_area_is_ioc_and_not_BL_and_slash_separated_with_fullname_false_and_module_path_in_remote_repo_then_new_module_creator_ioc_add_to_module_called_with_correct_args(self, mock_is_repo_path):

        ioc_os_c_mock = self.mocks['CreatorIOCAddToModule']

        new_ioc_creator = nmc.get_new_module_creator_ioc("test/module/02", fullname=False)

        mock_is_repo_path.assert_called_once_with("controls/ioc/test/module")
        ioc_os_c_mock.assert_called_once_with("test/module", "test-module-IOC-02", "ioc")

    def test_given_area_is_ioc_and_tech_area_is_BL_slash_form_then_new_module_creator_ioc_bl_called_with_correct_args(self):

        iocbl_c_mock = self.mocks['CreatorIOCBL']

        new_tools_creator = nmc.get_new_module_creator_ioc("test/BL")

        iocbl_c_mock.assert_called_once_with("test/BL", "test", "ioc")

    def test_given_area_is_ioc_and_tech_area_is_BL_dash_form_then_new_module_creator_ioc_bl_called_with_correct_args(self):

        iocbl_c_mock = self.mocks['CreatorIOCBL']

        new_tools_creator = nmc.get_new_module_creator_ioc("test-BL-IOC-01", "ioc")

        iocbl_c_mock.assert_called_once_with("test/test-BL-IOC-01", "test-BL-IOC-01", "ioc")


class NewModuleCreatorObtainTemplateFilesTest(unittest.TestCase):

    def test_given_area_is_unknown_then_returns_empty_dictionary(self):

        template_dict = nmc.obtain_template_files("test_area")

        self.assertEqual(template_dict, {})

    def test_given_area_is_default_then_returns_default_dictionary(self):

        template_dict = nmc.obtain_template_files("default")

        self.assertEqual(template_dict, default_files)

    def test_given_area_is_ioc_then_returns_default_dictionary(self):

        template_dict = nmc.obtain_template_files("ioc")

        self.assertEqual(template_dict, default_files)

    def test_given_area_is_support_then_returns_default_dictionary(self):

        template_dict = nmc.obtain_template_files("support")

        self.assertEqual(template_dict, default_files)

    def test_given_area_is_python_then_returns_python_dictionary(self):

        template_dict = nmc.obtain_template_files("python")

        self.assertEqual(template_dict, py_files)

    def test_given_area_is_tools_then_returns_tools_dictionary(self):

        template_dict = nmc.obtain_template_files("tools")

        self.assertEqual(template_dict, tools_files)


class NewModuleCreatorClassInitTest(unittest.TestCase):

    def test_given_reasonable_input_then_initialisation_is_successful(self):

        base_c = nmc.NewModuleCreator("test_module", "test_area")  # non-existent module and area


class NewModuleCreatorSetTemplateFilesFromFolderTest(unittest.TestCase):

    def setUp(self):

        self.patch_os = patch('dls_ade.new_module_creator.os')

        self.addCleanup(self.patch_os.stop)

        self.mock_os = self.patch_os.start()

        self.nmc_obj = nmc.NewModuleCreator("test_module", "test_area")

        self.open_mock = mock_open()  # mock_open is a function designed to help mock the 'open' built-in function

    def test_given_template_folder_is_not_directory_then_exception_raised_with_correct_message(self):

        self.mock_os.path.isdir.return_value = False

        comp_message = "The template folder {template_folder:s} does not exist".format(template_folder="test_template_folder")

        with patch.object(builtins, 'open', self.open_mock):
            with self.assertRaises(nmc.Error) as e:
                self.nmc_obj.set_template_files_from_folder("test_template_folder")

        self.assertEqual(str(e.exception), comp_message)

    def test_given_files_directly_in_folder_then_template_dict_correctly_created(self):

        self.mock_os.path.join = os.path.join  # We want 'join' and 'relpath' to work as normal here
        self.mock_os.path.relpath = os.path.relpath
        self.mock_os.path.isdir.return_value = True
        file_handle_mock = self.open_mock()

        self.mock_os.walk.return_value = iter([["test_template_folder", "", ["file1.txt", "file2.txt"]]])

        file_handle_mock.read.side_effect = ["file1 text goes here", "file2 text goes here"]

        with patch.object(builtins, 'open', self.open_mock):
            self.nmc_obj.set_template_files_from_folder("test_template_folder")

        comp_dict = {"file1.txt": "file1 text goes here", "file2.txt": "file2 text goes here"}

        self.assertEqual(comp_dict, self.nmc_obj.template_files)

    def test_given_files_nested_then_template_dict_correctly_created(self):

        self.mock_os.path.join = os.path.join  # We want 'join' and 'relpath' to work as normal here
        self.mock_os.path.relpath = os.path.relpath
        self.mock_os.path.isdir.return_value = True
        file_handle_mock = self.open_mock()

        self.mock_os.walk.return_value = iter([["test_template_folder/extra_folder", "", ["file1.txt", "file2.txt"]]])

        file_handle_mock.read.side_effect = ["file1 text goes here", "file2 text goes here"]

        with patch.object(builtins, 'open', self.open_mock):
            self.nmc_obj.set_template_files_from_folder("test_template_folder")

        comp_dict = {"extra_folder/file1.txt": "file1 text goes here", "extra_folder/file2.txt": "file2 text goes here"}

        self.assertEqual(comp_dict, self.nmc_obj.template_files)

    def test_given_multiple_nested_files_then_template_dict_correctly_created(self):

        self.mock_os.path.join = os.path.join  # We want 'join' and 'relpath' to work as normal here
        self.mock_os.path.relpath = os.path.relpath
        self.mock_os.path.isdir.return_value = True
        file_handle_mock = self.open_mock()

        self.mock_os.walk.return_value = iter([["test_template_folder/extra_folder1", "", ["file1.txt", "file2.txt"]], ["test_template_folder/extra_folder2", "", ["file3.txt", "file4.txt"]]])

        file_handle_mock.read.side_effect = ["file1 text goes here", "file2 text goes here", "file3 text goes here", "file4 text goes here"]

        with patch.object(builtins, 'open', self.open_mock):
            self.nmc_obj.set_template_files_from_folder("test_template_folder")

        comp_dict = {"extra_folder1/file1.txt": "file1 text goes here", "extra_folder1/file2.txt": "file2 text goes here", "extra_folder2/file3.txt": "file3 text goes here", "extra_folder2/file4.txt": "file4 text goes here"}

        self.assertEqual(comp_dict, self.nmc_obj.template_files)

    def test_given_update_true_then_template_dict_includes_non_conflicting_file_names(self):

        self.mock_os.path.join = os.path.join  # We want 'join' and 'relpath' to work as normal here
        self.mock_os.path.relpath = os.path.relpath
        self.mock_os.path.isdir.return_value = True
        file_handle_mock = self.open_mock()

        self.nmc_obj.template_files = {"non_conflicting_file.txt": "I am the non-conflicting file text"}

        self.mock_os.walk.return_value = iter([["test_template_folder/extra_folder1", "", ["file1.txt", "file2.txt"]], ["test_template_folder/extra_folder2", "", ["file3.txt", "file4.txt"]]])

        file_handle_mock.read.side_effect = ["file1 text goes here", "file2 text goes here", "file3 text goes here", "file4 text goes here"]

        with patch.object(builtins, 'open', self.open_mock):
            self.nmc_obj.set_template_files_from_folder("test_template_folder", True)

        comp_dict = {"extra_folder1/file1.txt": "file1 text goes here",
                     "extra_folder1/file2.txt": "file2 text goes here",
                     "extra_folder2/file3.txt": "file3 text goes here",
                     "extra_folder2/file4.txt": "file4 text goes here",
                     "non_conflicting_file.txt": "I am the non-conflicting file text"}

        self.assertEqual(comp_dict, self.nmc_obj.template_files)

    def test_given_update_false_then_template_dict_does_not_include_non_conflicting_file_names(self):

        self.mock_os.path.join = os.path.join  # We want 'join' and 'relpath' to work as normal here
        self.mock_os.path.relpath = os.path.relpath
        self.mock_os.path.isdir.return_value = True
        file_handle_mock = self.open_mock()

        self.nmc_obj.template_files = {"non_conflicting_file.txt": "I am the non-conflicting file text"}

        self.mock_os.walk.return_value = iter([["test_template_folder/extra_folder1", "", ["file1.txt", "file2.txt"]], ["test_template_folder/extra_folder2", "", ["file3.txt", "file4.txt"]]])

        file_handle_mock.read.side_effect = ["file1 text goes here", "file2 text goes here", "file3 text goes here", "file4 text goes here"]

        with patch.object(builtins, 'open', self.open_mock):
            self.nmc_obj.set_template_files_from_folder("test_template_folder", False)

        comp_dict = {"extra_folder1/file1.txt": "file1 text goes here",
                     "extra_folder1/file2.txt": "file2 text goes here",
                     "extra_folder2/file3.txt": "file3 text goes here",
                     "extra_folder2/file4.txt": "file4 text goes here"}

        self.assertEqual(comp_dict, self.nmc_obj.template_files)

    def test_given_update_true_then_template_dict_overwrites_conflicting_file_names(self):

        self.mock_os.path.join = os.path.join  # We want 'join' and 'relpath' to work as normal here
        self.mock_os.path.relpath = os.path.relpath
        self.mock_os.path.isdir.return_value = True
        file_handle_mock = self.open_mock()

        self.nmc_obj.template_files = {"conflicting_file.txt": "I am the original conflicting file text"}

        self.mock_os.walk.return_value = iter([["test_template_folder", "", ["conflicting_file.txt"]], ["test_template_folder/extra_folder1", "", ["file1.txt", "file2.txt"]], ["test_template_folder/extra_folder2", "", ["file3.txt", "file4.txt"]]])

        file_handle_mock.read.side_effect = ["I am the modified conflicting file text", "file1 text goes here", "file2 text goes here", "file3 text goes here", "file4 text goes here"]

        with patch.object(builtins, 'open', self.open_mock):
            self.nmc_obj.set_template_files_from_folder("test_template_folder", True)

        comp_dict = {"extra_folder1/file1.txt": "file1 text goes here",
                     "extra_folder1/file2.txt": "file2 text goes here",
                     "extra_folder2/file3.txt": "file3 text goes here",
                     "extra_folder2/file4.txt": "file4 text goes here",
                     "conflicting_file.txt": "I am the modified conflicting file text"}

        self.assertEqual(comp_dict, self.nmc_obj.template_files)


class NewModuleCreatorSetTemplateArgs(unittest.TestCase):

    @patch('os.getlogin', return_value='my_login')
    def test_given_reasonable_input_then_correct_template_args_given(self, mock_getlogin):

        nmc_obj = nmc.NewModuleCreator("test_module", "test_area")

        self.assertEqual(nmc_obj.template_args, {'module_name': "test_module", 'getlogin': "my_login"})


class NewModuleCreatorVerifyRemoteRepoTest(unittest.TestCase):

    def setUp(self):

        self.patch_get_existing_remote_repo_paths = patch('dls_ade.new_module_creator.NewModuleCreator._get_existing_remote_repo_paths')

        self.addCleanup(self.patch_get_existing_remote_repo_paths.stop)

        self.mock_get_existing_remote_repo_paths = self.patch_get_existing_remote_repo_paths.start()

        self.nmc_obj = nmc.NewModuleCreator("test_module", "test_area")

    def test_given_get_existing_remote_repo_paths_returns_non_empty_list_then_exception_raised_with_correct_message(self):

        self.mock_get_existing_remote_repo_paths.return_value = ["inrepo1", "inrepo2", "inrepo3"]
        comp_message = ("The paths {dirs:s} already exist on gitolite, cannot continue").format(dirs=", ".join(["inrepo1", "inrepo2", "inrepo3"]))

        with self.assertRaises(nmc.VerificationError) as e:
            self.nmc_obj.verify_remote_repo()

        self.assertEqual(str(e.exception), comp_message)

    def test_given_get_existing_remote_repo_paths_returns_empty_list_then_remote_repo_valid_set_true(self):

        self.mock_get_existing_remote_repo_paths.return_value = []

        self.nmc_obj.verify_remote_repo()

        self.assertTrue(self.nmc_obj._remote_repo_valid)


class NewModuleCreatorGetExistingRemoteRepoPathsTest(unittest.TestCase):

    def setUp(self):

        self.patch_get_remote_dir_list = patch('dls_ade.new_module_creator.NewModuleCreator._get_remote_dir_list')
        self.patch_is_repo_path = patch('dls_ade.vcs_git.is_repo_path')

        self.addCleanup(self.patch_get_remote_dir_list.stop)
        self.addCleanup(self.patch_is_repo_path.stop)

        self.mock_get_remote_dir_list = self.patch_get_remote_dir_list.start()
        self.mock_is_repo_path = self.patch_is_repo_path.start()

        self.nmc_obj = nmc.NewModuleCreator("test_module", "test_area")

    def test_given_one_of_dir_list_exists_then_directory_returned_in_list(self):

        self.mock_get_remote_dir_list.return_value = ["inrepo1", "inrepo2", "inrepo3"]
        self.mock_is_repo_path.return_value = True

        existing_dir_paths = self.nmc_obj._get_existing_remote_repo_paths()

        self.assertEqual(existing_dir_paths, ["inrepo1", "inrepo2", "inrepo3"])

    def test_given_none_in_dir_list_exist_then_list_returned_is_empty(self):

        self.mock_get_remote_dir_list.return_value = ["notinrepo1", "notinrepo2", "notinrepo3"]
        self.mock_is_repo_path.return_value = False

        existing_dir_paths = self.nmc_obj._get_existing_remote_repo_paths()

        self.assertFalse(existing_dir_paths)

    def test_given_one_dir_does_exist_then_list_returned_is_correct(self):

        self.mock_get_remote_dir_list.return_value = ["notinrepo1", "inrepo2", "notinrepo3"]
        self.mock_is_repo_path.side_effect = [False, True, False]

        existing_dir_paths = self.nmc_obj._get_existing_remote_repo_paths()

        self.assertEqual(existing_dir_paths, ["inrepo2"])


class NewModuleCreatorGetRemoteDirListTest(unittest.TestCase):

    @patch('dls_ade.new_module_creator.pathf.vendorModule', return_value='vendor_module')
    @patch('dls_ade.new_module_creator.pathf.prodModule', return_value='prod_module')
    def test_correct_dir_list_returned(self, mock_prod, mock_vend):

        nmc_obj = nmc.NewModuleCreator("test_module", "test_area")
        dir_list = nmc_obj._get_remote_dir_list()

        self.assertEqual(dir_list, [nmc_obj.server_repo_path, 'vendor_module', 'prod_module'])


class NewModuleCreatorVerifyCanCreateLocalModule(unittest.TestCase):

    def setUp(self):

        self.patch_exists = patch('dls_ade.new_module_creator.os.path.exists')
        self.patch_is_git_dir = patch('dls_ade.new_module_creator.vcs_git.is_git_dir')

        self.addCleanup(self.patch_exists.stop)
        self.addCleanup(self.patch_is_git_dir.stop)

        self.mock_exists = self.patch_exists.start()
        self.mock_is_git_dir = self.patch_is_git_dir.start()

        self.nmc_obj = nmc.NewModuleCreator("test_module", "test_area")

    def test_given_module_folder_does_not_exist_and_is_not_in_git_repo_then_flag_set_true(self):

        self.mock_exists.return_value = False
        self.mock_is_git_dir.return_value = False

        self.nmc_obj.verify_can_create_local_module()

        self.assertTrue(self.nmc_obj._can_create_local_module)

    def test_given_module_folder_exists_then_flag_set_false_and_error_returned_is_correct(self):

        self.mock_exists.return_value = True
        self.mock_is_git_dir.return_value = False

        comp_message = "Directory {dir:s} already exists, please move elsewhere and try again.".format(dir=self.nmc_obj.module_path)

        with self.assertRaises(nmc.VerificationError) as e:
            self.nmc_obj.verify_can_create_local_module()

        self.assertEqual(str(e.exception), comp_message)

        self.assertFalse(self.nmc_obj._remote_repo_valid)

    def test_given_module_folder_is_in_git_repo_then_flag_set_false_and_error_returned_is_correct(self):

        self.mock_exists.return_value = False
        self.mock_is_git_dir.return_value = True

        comp_message = "Currently in a git repository, please move elsewhere and try again.".format(dir=os.path.join("./", self.nmc_obj.disk_dir))

        with self.assertRaises(nmc.VerificationError) as e:
            self.nmc_obj.verify_can_create_local_module()

        self.assertEqual(str(e.exception), comp_message)

        self.assertFalse(self.nmc_obj._remote_repo_valid)

    def test_given_module_folder_exists_and_is_in_repo_then_flag_set_false_and_error_returned_is_correct(self):

        self.mock_exists.return_value = True
        self.mock_is_git_dir.return_value = True

        comp_message = "Directory {dir:s} already exists, please move elsewhere and try again.\n"
        comp_message += "Currently in a git repository, please move elsewhere and try again."
        comp_message = comp_message.format(dir=self.nmc_obj.module_path)

        with self.assertRaises(nmc.VerificationError) as e:
            self.nmc_obj.verify_can_create_local_module()

        self.assertEqual(str(e.exception), comp_message)

        self.assertFalse(self.nmc_obj._remote_repo_valid)


class NewModuleCreatorVerifyCanPushLocalRepoToRemoteTest(unittest.TestCase):

    def setUp(self):

        self.patch_exists = patch('dls_ade.new_module_creator.os.path.exists')
        self.patch_is_git_root_dir = patch('dls_ade.new_module_creator.vcs_git.is_git_root_dir')
        self.patch_verify_remote_repo = patch('dls_ade.new_module_creator.NewModuleCreator.verify_remote_repo')

        self.addCleanup(self.patch_exists.stop)
        self.addCleanup(self.patch_is_git_root_dir.stop)
        self.addCleanup(self.patch_verify_remote_repo.stop)

        self.mock_exists = self.patch_exists.start()
        self.mock_is_git_root_dir = self.patch_is_git_root_dir.start()
        self.mock_verify_remote_repo = self.patch_verify_remote_repo.start()

        self.nmc_obj = nmc.NewModuleCreator("test_module", "test_area")

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

        self.mock_verify_remote_repo.side_effect = nmc.VerificationError("error")

        self.mock_exists.return_value = True
        self.mock_is_git_root_dir.return_value = True

        with self.assertRaises(nmc.VerificationError) as e:
            self.nmc_obj.verify_can_push_repo_to_remote()

        self.assertEqual(str(e.exception), "error")
        self.assertFalse(self.nmc_obj._can_push_repo_to_remote)

    def test_given_module_folder_does_not_exist_then_flag_set_false_and_error_returned_is_correct(self):

        self.mock_exists.return_value = False
        self.mock_is_git_root_dir.return_value = False

        self.nmc_obj._remote_repo_valid = True

        comp_message = "Directory {dir:s} does not exist.".format(dir=self.nmc_obj.module_path)

        with self.assertRaises(nmc.VerificationError) as e:
            self.nmc_obj.verify_can_push_repo_to_remote()

        self.assertEqual(str(e.exception), comp_message)
        self.assertFalse(self.nmc_obj._can_push_repo_to_remote)

    def test_given_module_folder_is_not_repo_then_flag_set_false_and_error_returned_is_correct(self):

        self.mock_exists.return_value = True
        self.mock_is_git_root_dir.return_value = False

        self.nmc_obj._remote_repo_valid = True

        comp_message = "Directory {dir:s} is not a git repository. Unable to push to remote repository.".format(dir=self.nmc_obj.module_path)

        with self.assertRaises(nmc.VerificationError) as e:
            self.nmc_obj.verify_can_push_repo_to_remote()

        self.assertEqual(str(e.exception), comp_message)
        self.assertFalse(self.nmc_obj._can_push_repo_to_remote)

    def test_given_module_folder_is_not_repo_and_remote_repo_false_then_flag_set_false_and_error_returned_is_correct(self):

        self.mock_verify_remote_repo.side_effect = nmc.VerificationError('error')
        self.mock_exists.return_value = True
        self.mock_is_git_root_dir.return_value = False

        comp_message = "Directory {dir:s} is not a git repository. Unable to push to remote repository.\n"
        comp_message = comp_message.format(dir=self.nmc_obj.module_path)
        comp_message += "error"
        comp_message = comp_message.rstrip()

        with self.assertRaises(nmc.VerificationError) as e:
            self.nmc_obj.verify_can_push_repo_to_remote()

        self.assertEqual(str(e.exception), comp_message)
        self.assertFalse(self.nmc_obj._can_push_repo_to_remote)


class NewModuleCreatorCreateLocalModuleTest(unittest.TestCase):

    def setUp(self):

        self.patch_os = patch('dls_ade.new_module_creator.os')
        self.patch_vcs_git = patch('dls_ade.new_module_creator.vcs_git')
        self.patch_create_files = patch('dls_ade.new_module_creator.NewModuleCreator._create_files')
        self.patch_verify_can_create_local_module = patch('dls_ade.new_module_creator.NewModuleCreator.verify_can_create_local_module')

        self.addCleanup(self.patch_os.stop)
        self.addCleanup(self.patch_vcs_git.stop)
        self.addCleanup(self.patch_create_files.stop)
        self.addCleanup(self.patch_verify_can_create_local_module.stop)

        self.mock_os = self.patch_os.start()
        self.mock_vcs_git = self.patch_vcs_git.start()
        self.mock_create_files = self.patch_create_files.start()
        self.mock_verify_can_create_local_module = self.patch_verify_can_create_local_module.start()

        # self.mock_os.return_value = "Example"

        self.nmc_obj = nmc.NewModuleCreator("test_module", "test_area")

    def test_given_can_create_local_module_true_then_flag_set_false(self):

        self.nmc_obj._can_create_local_module = True

        self.nmc_obj.create_local_module()

        self.assertFalse(self.nmc_obj._can_create_local_module)

    def test_given_can_create_local_module_false_then_exception_raised_with_correct_message(self):

        self.nmc_obj._can_create_local_module = False
        self.mock_verify_can_create_local_module.side_effect = nmc.VerificationError("error")

        with self.assertRaises(Exception) as e:
            self.nmc_obj.create_local_module()

        self.assertFalse(self.mock_os.path.isdir.called)
        self.assertEqual(str(e.exception), "error")

    def test_given_can_create_local_module_true_then_rest_of_function_is_run(self):

        self.nmc_obj._can_create_local_module = True

        self.nmc_obj.create_local_module()

        call_list = [call(self.nmc_obj.disk_dir), call(self.nmc_obj.cwd)]

        self.mock_os.path.isdir.assert_called_once_with(self.nmc_obj.disk_dir)
        self.mock_os.chdir.assert_has_calls(call_list)
        self.assertTrue(self.mock_create_files.called)
        self.mock_vcs_git.init_repo.assert_called_once_with(self.nmc_obj.disk_dir)
        self.mock_vcs_git.stage_all_files_and_commit.assert_called_once_with(self.nmc_obj.disk_dir)

    def test_given_can_create_local_module_originally_false_but_verify_function_does_not_raise_exception_then_rest_of_function_is_run(self):

        self.nmc_obj._can_create_local_module = False

        self.nmc_obj.create_local_module()

        call_list = [call(self.nmc_obj.disk_dir), call(self.nmc_obj.cwd)]

        self.mock_os.path.isdir.assert_called_once_with(self.nmc_obj.disk_dir)
        self.mock_os.chdir.assert_has_calls(call_list)
        self.assertTrue(self.mock_create_files.called)
        self.mock_vcs_git.init_repo.assert_called_once_with(self.nmc_obj.disk_dir)
        self.mock_vcs_git.stage_all_files_and_commit.assert_called_once_with(self.nmc_obj.disk_dir)

    def test_given_can_create_local_module_true_and_disk_dir_already_exists_then_makedirs_is_not_called(self):

        self.nmc_obj._can_create_local_module = True
        self.mock_os.path.isdir.return_value = True

        self.nmc_obj.create_local_module()

        self.assertFalse(self.mock_os.makedirs.called)

    def test_given_can_create_local_module_false_and_disk_dir_does_not_exist_then_makedirs_is_called(self):

        self.nmc_obj._can_create_local_module = True
        self.mock_os.path.isdir.return_value = False

        self.nmc_obj.create_local_module()

        self.mock_os.makedirs.assert_called_once_with(self.nmc_obj.disk_dir)


class NewModuleCreatorCreateFilesTest(unittest.TestCase):

    def setUp(self):

        self.nmc_obj = nmc.NewModuleCreator("test_module", "test_area")

    @patch('dls_ade.new_module_creator.NewModuleCreator._create_files_from_template_dict')
    def test_create_files_from_template_called(self, mock_create_files_from_template):

        self.nmc_obj._create_files()

        mock_create_files_from_template.assert_called_once_with()


class NewModuleCreatorCreateFilesFromTemplateDictTest(unittest.TestCase):

    def setUp(self):

        self.patch_isdir = patch('dls_ade.new_module_creator.os.path.isdir')
        self.patch_makedirs = patch('dls_ade.new_module_creator.os.makedirs')
        self.patch_isfile = patch('dls_ade.new_module_creator.os.path.isfile')
        self.addCleanup(self.patch_isdir.stop)
        self.addCleanup(self.patch_makedirs.stop)
        self.addCleanup(self.patch_isfile.stop)
        self.mock_isdir = self.patch_isdir.start()
        self.mock_makedirs = self.patch_makedirs.start()
        self.mock_isfile = self.patch_isfile.start()

        self.mock_isdir.return_value = False
        self.mock_isfile.return_value = False

        self.nmc_obj = nmc.NewModuleCreator("test_module", "test_area")
        self.nmc_obj.template_args = {"arg1": "argument_1", "arg2": "argument_2"}
        self.open_mock = mock_open()  # mock_open is function designed to help mock the 'open' built-in function

    def test_given_folder_name_in_template_files_then_exception_raised_with_correct_message(self):

        self.nmc_obj.template_files = {"folder_name/": "Written contents"}
        comp_message = "{dir:s} in template dictionary is not a valid file name".format(dir="folder_name")

        with patch.object(builtins, 'open', self.open_mock):  # This is to prevent accidental file creation
            with self.assertRaises(Exception) as e:
                self.nmc_obj._create_files_from_template_dict()

        self.assertEqual(str(e.exception), comp_message)
        self.assertFalse(self.open_mock.called)
        file_handle_mock = self.open_mock()
        self.assertFalse(file_handle_mock.write.called)

    def test_given_single_file_that_already_exists_then_file_not_created(self):

        self.nmc_obj.template_files = {"already_exists.txt": "Written contents"}
        self.mock_isfile.return_value = True

        with patch.object(builtins, 'open', self.open_mock):
            self.nmc_obj._create_files_from_template_dict()

        self.assertFalse(self.open_mock.called)

        file_handle_mock = self.open_mock()
        self.assertFalse(file_handle_mock.called)

    def test_given_single_file_then_file_created_and_correctly_written_to(self):

        self.nmc_obj.template_files = {"file1.txt": "Written contents"}

        with patch.object(builtins, 'open', self.open_mock):
            self.nmc_obj._create_files_from_template_dict()

        self.open_mock.assert_called_once_with("file1.txt", "w")

        file_handle_mock = self.open_mock()
        file_handle_mock.write.assert_any_call("Written contents")

    def test_given_single_file_in_folder_that_does_not_exist_then_folder_and_file_created_and_file_correctly_written_to(self):

        self.nmc_obj.template_files = {"test_folder/file1.txt": "Written contents"}

        with patch.object(builtins, 'open', self.open_mock):
            self.nmc_obj._create_files_from_template_dict()

        self.mock_makedirs.asset_called_once_with("test_folder")
        self.open_mock.assert_called_once_with("test_folder/file1.txt", "w")

        file_handle_mock = self.open_mock()
        file_handle_mock.write.assert_any_call("Written contents")

    def test_given_single_file_in_folder_that_exists_then_folder_not_created_but_file_created_and_file_correctly_written_to(self):

        self.mock_isdir.return_value = True

        self.nmc_obj.template_files = {"test_folder/file1.txt": "Written contents"}

        with patch.object(builtins, 'open', self.open_mock):
            self.nmc_obj._create_files_from_template_dict()

        self.assertFalse(self.mock_makedirs.called)
        self.open_mock.assert_called_once_with("test_folder/file1.txt", "w")

        file_handle_mock = self.open_mock()
        file_handle_mock.write.assert_any_call("Written contents")

    def test_given_two_files_in_separate_folders_then_both_folders_created_and_files_correctly_written_to(self):

        self.nmc_obj.template_files = {"test_folder1/file1.txt": "Written contents1", "test_folder2/file2.txt": "Written contents2"}

        with patch.object(builtins, 'open', self.open_mock):
            self.nmc_obj._create_files_from_template_dict()

        self.mock_makedirs.assert_has_calls([call("test_folder1"), call("test_folder2")], any_order=True)

        self.open_mock.assert_has_calls([call("test_folder1/file1.txt", "w"), call("test_folder2/file2.txt", "w")], any_order=True)

        file_handle_mock = self.open_mock()
        file_handle_mock.write.assert_has_calls([call("Written contents1"), call("Written contents2")], any_order=True)

    def test_given_two_files_in_same_folder_then_both_created_and_written_to_but_directory_only_made_once(self):

        self.mock_isdir.side_effect = [False, True]

        self.nmc_obj.template_files = {"test_folder/file1.txt": "Written contents1", "test_folder/file2.txt": "Written contents2"}

        with patch.object(builtins, 'open', self.open_mock):
            self.nmc_obj._create_files_from_template_dict()

        self.mock_makedirs.assert_called_once_with("test_folder")

        self.open_mock.assert_has_calls([call("test_folder/file1.txt", "w"), call("test_folder/file2.txt", "w")], any_order=True)

        file_handle_mock = self.open_mock()
        file_handle_mock.write.assert_has_calls([call("Written contents1"), call("Written contents2")], any_order=True)

    def test_given_single_file_with_placeholder_in_name_then_file_created_and_correctly_written_to(self):

        self.nmc_obj.template_files = {"{arg:s}.txt": "Written contents"}
        self.nmc_obj.template_args = {'arg': "my_argument"}

        with patch.object(builtins, 'open', self.open_mock):
            self.nmc_obj._create_files_from_template_dict()

        self.open_mock.assert_called_once_with("my_argument.txt", "w")

        file_handle_mock = self.open_mock()
        file_handle_mock.write.assert_any_call("Written contents")

    def test_given_args_and_template_then_arguments_are_inserted_correctly(self):

        self.nmc_obj.template_files = {"file1.txt": "{arg1:s} and {arg2:s}"}

        with patch.object(builtins, 'open', self.open_mock):
            self.nmc_obj._create_files_from_template_dict()

        self.open_mock.assert_called_once_with("file1.txt", "w")

        file_handle_mock = self.open_mock()
        file_handle_mock.write.assert_called_once_with("argument_1 and argument_2")

    def test_given_nested_directory_then_folder_and_file_both_created_and_file_correctly_written_to(self):

        self.nmc_obj.template_files = {"test_folder/another_folder/yet_another_folder/file.txt": "Written contents"}

        with patch.object(builtins, 'open', self.open_mock):
            self.nmc_obj._create_files_from_template_dict()

        self.mock_makedirs.assert_called_once_with("test_folder/another_folder/yet_another_folder")

        self.open_mock.assert_called_once_with("test_folder/another_folder/yet_another_folder/file.txt", "w")

        file_handle_mock = self.open_mock()
        file_handle_mock.write.assert_called_once_with("Written contents")

    def test_given_file_with_no_folder_then_makedirs_not_called(self):

        self.nmc_obj.template_files = {"file.txt": "Written contents"}

        with patch.object(builtins, 'open', self.open_mock):
            self.nmc_obj._create_files_from_template_dict()

        self.assertFalse(self.mock_makedirs.called)


# TODO -----------------------------------------------------------------------------------------------------------------
class NewModuleCreatorAddContactTest(unittest.TestCase):
    pass
# TODO -----------------------------------------------------------------------------------------------------------------


class NewModuleCreatorPushRepoToRemoteTest(unittest.TestCase):

    def setUp(self):

        self.patch_verify_can_push_repo_to_remote = patch('dls_ade.new_module_creator.NewModuleCreator.verify_can_push_repo_to_remote')
        self.patch_add_new_remote_and_push = patch('dls_ade.new_module_creator.vcs_git.add_new_remote_and_push')

        self.addCleanup(self.patch_verify_can_push_repo_to_remote.stop)
        self.addCleanup(self.patch_add_new_remote_and_push.stop)

        self.mock_verify_can_push_repo_to_remote = self.patch_verify_can_push_repo_to_remote.start()
        self.mock_add_new_remote_and_push = self.patch_add_new_remote_and_push.start()

        self.nmc_obj = nmc.NewModuleCreator("test_module", "test_area")

    def test_given_can_push_repo_to_remote_true_then_flag_set_false(self):

        self.nmc_obj._can_push_repo_to_remote = True

        self.nmc_obj.push_repo_to_remote()

        self.assertFalse(self.nmc_obj._can_push_repo_to_remote)

    def test_given_can_push_repo_to_remote_true_then_add_new_remote_and_push_called(self):

        self.nmc_obj._can_push_repo_to_remote = True

        self.nmc_obj.push_repo_to_remote()

        self.mock_add_new_remote_and_push.assert_called_with(self.nmc_obj.server_repo_path, self.nmc_obj.disk_dir)

    def test_given_can_push_repo_to_remote_false_then_exception_raised_with_correct_message(self):

        self.nmc_obj._can_push_repo_to_remote = False
        self.mock_verify_can_push_repo_to_remote.side_effect = nmc.VerificationError("error")

        with self.assertRaises(Exception) as e:
            self.nmc_obj.push_repo_to_remote()

        self.assertFalse(self.mock_add_new_remote_and_push.called)
        self.assertEqual(str(e.exception), "error")

    def test_given_can_push_repo_to_remote_originally_false_but_verify_function_does_not_raise_exception_then_add_new_remote_and_push_called(self):

        self.nmc_obj._can_push_repo_to_remote = False

        self.nmc_obj.push_repo_to_remote()

        self.mock_add_new_remote_and_push.assert_called_with(self.nmc_obj.server_repo_path, self.nmc_obj.disk_dir)


# Add tests for all derived NewModuleCreator classes


class NewModuleCreatorToolsPrintMessageTest(unittest.TestCase):

    @patch('dls_ade.new_module_creator.print', create=True)
    def test_given_print_message_called_then_message_printed(self, mock_print):

        nmc_obj = nmc.NewModuleCreatorTools('test_module_path', 'test_area')

        comp_message = ("\nPlease add your patch files to the test_module_path "
                        "\ndirectory and edit test_module_path/build script "
                        "appropriately")

        nmc_obj.print_message()

        mock_print.assert_called_once_with(comp_message)


class NewModuleCreatorPythonPrintMessageTest(unittest.TestCase):

    @patch('dls_ade.new_module_creator.print', create=True)
    def test_given_print_message_called_then_message_printed(self, mock_print):

        nmc_obj = nmc.NewModuleCreatorPython('test_module_path', 'test_area')

        message_dict = {'module_path': "test_module_path",
                        'setup_path': "test_module_path/setup.py"}

        comp_message = ("\nPlease add your python files to the {module_path:s} "
                        "\ndirectory and edit {setup_path} appropriately.")
        comp_message = comp_message.format(**message_dict)

        nmc_obj.print_message()

        mock_print.assert_called_once_with(comp_message)


class NewModuleCreatorWithAppsPrintMessageTest(unittest.TestCase):

    @patch('dls_ade.new_module_creator.print', create=True)
    def test_given_print_message_called_then_message_printed(self, mock_print):

        nmc_obj = nmc.NewModuleCreatorWithApps('test_module_path', 'test_area')

        message_dict = {
            'RELEASE': "test_module_path/configure/RELEASE",
            'srcMakefile': "test_module_path/test_module_pathApp/src/Makefile",
            'DbMakefile': "test_module_path/test_module_pathApp/Db/Makefile"
        }

        comp_message = ("\nPlease now edit {RELEASE:s} to put in correct paths "
                        "for dependencies.\nYou can also add dependencies to "
                        "{srcMakefile:s}\nand {DbMakefile:s} if appropriate.")
        comp_message = comp_message.format(**message_dict)

        nmc_obj.print_message()

        mock_print.assert_called_once_with(comp_message)


class NewModuleCreatorSupportCreateFiles(unittest.TestCase):

    @patch('dls_ade.new_module_creator.os.system')
    @patch('dls_ade.new_module_creator.NewModuleCreatorSupport._create_files_from_template_dict')
    def test_given_create_files_called_then_correct_functions_called(self, mock_create_from_dict, mock_os_system):

        nmc_obj = nmc.NewModuleCreatorSupport('test_module_path', 'test_area')

        nmc_obj._create_files()

        os_system_call_list = [call("makeBaseApp.pl -t dls {mod_path:s}".format(mod_path="test_module_path")), call("dls-make-etc-dir.py && make clean uninstall")]

        mock_os_system.assert_has_calls(os_system_call_list)
        mock_create_from_dict.assert_called_once_with()


class NewModuleCreatorIOCCreateFiles(unittest.TestCase):

    @patch('dls_ade.new_module_creator.shutil.rmtree')
    @patch('dls_ade.new_module_creator.os.system')
    @patch('dls_ade.new_module_creator.NewModuleCreatorIOC._create_files_from_template_dict')
    def test_given_create_files_called_then_correct_functions_called(self, mock_create_from_dict, mock_os_system, mock_rmtree):

        nmc_obj = nmc.NewModuleCreatorIOC('test_module_path', 'test_app_name', 'test_area')

        nmc_obj._create_files()

        os_system_call_list = [call("makeBaseApp.pl -t dls {app_name:s}".format(app_name="test_app_name")), call("makeBaseApp.pl -i -t dls {app_name:s}".format(app_name="test_app_name"))]

        mock_rmtree.assert_called_once_with(os.path.join("{app_name:s}App".format(app_name="test_app_name"), 'opi'))
        mock_os_system.assert_has_calls(os_system_call_list)
        mock_create_from_dict.assert_called_once_with()


class NewModuleCreatorIOCBLCreateFiles(unittest.TestCase):

    @patch('dls_ade.new_module_creator.os.system')
    @patch('dls_ade.new_module_creator.NewModuleCreatorIOCBL._create_files_from_template_dict')
    def test_given_create_files_called_then_correct_functions_called(self, mock_create_from_dict, mock_os_system):

        nmc_obj = nmc.NewModuleCreatorIOCBL('test_module_path', 'test_app_name', 'test_area')

        nmc_obj._create_files()

        mock_os_system.assert_called_once_with("makeBaseApp.pl -t dlsBL {app_name:s}".format(app_name="test_app_name"))
        mock_create_from_dict.assert_called_once_with()


class NewModuleCreatorIOCBLPrintMessageTest(unittest.TestCase):

    @patch('dls_ade.new_module_creator.print', create=True)
    def test_given_print_message_called_then_message_printed(self, mock_print):

        nmc_obj = nmc.NewModuleCreatorIOCBL('test_module_path', 'test_app', 'test_area')

        message_dict = {
            'RELEASE': "test_module_path/configure/RELEASE",
            'srcMakefile': "test_module_path/test_appApp/src/Makefile",
            'opi/edl': "test_module_path/test_appApp/opi/edl"
        }

        comp_message = ("\nPlease now edit {RELEASE:s} to put in correct paths "
                        "for the ioc's other technical areas and path to scripts."
                        "\nAlso edit {srcMakefile:s} to add all database files "
                        "from these technical areas.\nAn example set of screens"
                        " has been placed in {opi/edl} . Please modify these.\n")

        comp_message = comp_message.format(**message_dict)

        nmc_obj.print_message()

        mock_print.assert_called_once_with(comp_message)


class NewModuleCreatorIOCAddToModuleVerifyRemoteRepoTest(unittest.TestCase):

    def setUp(self):

        self.patch_get_existing_remote_repo_paths = patch('dls_ade.new_module_creator.NewModuleCreatorIOCAddToModule._get_existing_remote_repo_paths')
        self.patch_check_if_remote_repo_has_app = patch('dls_ade.new_module_creator.NewModuleCreatorIOCAddToModule._check_if_remote_repo_has_app')

        self.addCleanup(self.patch_get_existing_remote_repo_paths.stop)
        self.addCleanup(self.patch_check_if_remote_repo_has_app.stop)

        self.mock_get_existing_remote_repo_paths = self.patch_get_existing_remote_repo_paths.start()
        self.mock_check_if_remote_repo_has_app = self.patch_check_if_remote_repo_has_app.start()

        self.nmc_obj = nmc.NewModuleCreatorIOCAddToModule("test_module", "test_app", "test_area")

    def test_given_server_repo_path_not_in_existing_remote_repo_paths_then_exception_raised_with_correct_message(self):

        self.mock_get_existing_remote_repo_paths.return_value = ["inrepo1", "inrepo2", "inrepo3"]
        self.nmc_obj.server_repo_path = "notinrepo"

        comp_message = "The path {path:s} does not exist on gitolite, so cannot clone from it".format(path="notinrepo")

        with self.assertRaises(nmc.VerificationError) as e:
            self.nmc_obj.verify_remote_repo()

        self.assertEqual(str(e.exception), comp_message)

    def test_given_app_exists_in_remote_repo_path_then_exception_raised_with_correct_error_message(self):

        self.mock_get_existing_remote_repo_paths.return_value = ["inrepo1", "inrepo2", "inrepo3"]
        self.nmc_obj.server_repo_path = "inrepo1"
        self.mock_check_if_remote_repo_has_app.side_effect = [True, False, True]

        comp_message = "The repositories {paths:s} have apps that conflict with {app_name:s}".format(paths=", ".join(["inrepo1", "inrepo3"]), app_name="test_app")

        with self.assertRaises(nmc.VerificationError) as e:
            self.nmc_obj.verify_remote_repo()

        self.assertEqual(str(e.exception), comp_message)

    def test_given_all_checks_passed_then_remote_repo_valid_set_true(self):

        self.mock_get_existing_remote_repo_paths.return_value = ["inrepo1", "inrepo2", "inrepo3"]
        self.nmc_obj.server_repo_path = "inrepo1"
        self.mock_check_if_remote_repo_has_app.return_value = False

        self.nmc_obj.verify_remote_repo()

        self.assertTrue(self.nmc_obj._remote_repo_valid)


class NewModuleCreatorIOCAddToModuleCheckIfRemoteRepoHasApp(unittest.TestCase):

    def setUp(self):

        self.patch_vcs_git = patch('dls_ade.new_module_creator.vcs_git')
        self.patch_mkdtemp = patch('dls_ade.new_module_creator.tempfile.mkdtemp', return_value='tempdir')
        self.patch_exists = patch('dls_ade.new_module_creator.os.path.exists')
        self.patch_rmtree = patch('dls_ade.new_module_creator.shutil.rmtree')

        self.addCleanup(self.patch_vcs_git.stop)
        self.addCleanup(self.patch_mkdtemp.stop)
        self.addCleanup(self.patch_exists.stop)
        self.addCleanup(self.patch_rmtree.stop)

        self.mock_vcs_git = self.patch_vcs_git.start()
        self.mock_mkdtemp = self.patch_mkdtemp.start()
        self.mock_exists = self.patch_exists.start()
        self.mock_rmtree = self.patch_rmtree.start()

        self.nmc_obj = nmc.NewModuleCreatorIOCAddToModule("test_module", "test_app", "test_area")

    def test_given_remote_repo_path_is_not_on_server_then_exception_raised_with_correct_message(self):

        self.mock_vcs_git.is_repo_path.return_value = False

        comp_message = ("Remote repo {repo:s} does not exist. Cannot "
                        "clone to determine if there is an app_name "
                        "conflict with {app_name:s}".format(repo="test_repo_path", app_name="test_app"))

        with self.assertRaises(nmc.Error) as e:
            self.nmc_obj._check_if_remote_repo_has_app("test_repo_path")

        self.assertEqual(str(e.exception), comp_message)

    def test_given_remote_repo_exists_on_server_then_mkdtemp_and_clone_called_correctly(self):

        self.mock_vcs_git.is_repo_path.return_value = True

        try:
            self.nmc_obj._check_if_remote_repo_has_app("test_repo_path")
        except:
            pass

        self.mock_mkdtemp.assert_called_once_with()
        self.mock_vcs_git.clone.assert_called_once_with("test_repo_path", "tempdir")

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

    def test_given_exception_raised_in_mkdtemp_then_rmtree_not_called(self):

        self.mock_mkdtemp.side_effect = Exception("test_exception")
        self.mock_vcs_git.is_repo_path.return_value = True

        with self.assertRaises(Exception) as e:
            self.nmc_obj._check_if_remote_repo_has_app("test_repo_path")

        self.assertEqual(str(e.exception), "test_exception")
        self.assertFalse(self.mock_rmtree.called)

    def test_given_exception_raised_after_mkdtemp_then_rmtree_called(self):

        self.mock_vcs_git.clone.side_effect = Exception("test_exception")
        self.mock_vcs_git.is_repo_path.return_value = True

        with self.assertRaises(Exception) as e:
            self.nmc_obj._check_if_remote_repo_has_app("test_repo_path")

        self.assertEqual(str(e.exception), "test_exception")
        self.mock_rmtree.assert_called_once_with("tempdir")


class NewModuleCreatorIOCAddToModulePushRepoToRemoteTest(unittest.TestCase):

    def setUp(self):

        self.patch_verify_can_push_repo_to_remote = patch('dls_ade.new_module_creator.NewModuleCreatorIOCAddToModule.verify_can_push_repo_to_remote')
        self.patch_push_to_remote = patch('dls_ade.new_module_creator.vcs_git.push_to_remote')

        self.addCleanup(self.patch_verify_can_push_repo_to_remote.stop)
        self.addCleanup(self.patch_push_to_remote.stop)

        self.mock_verify_can_push_repo_to_remote = self.patch_verify_can_push_repo_to_remote.start()
        self.mock_push_to_remote = self.patch_push_to_remote.start()

        self.nmc_obj = nmc.NewModuleCreatorIOCAddToModule("test_module", "test_app", "test_area")

    def test_given_can_push_repo_to_remote_true_then_flag_set_false(self):

        self.nmc_obj._can_push_repo_to_remote = True

        self.nmc_obj.push_repo_to_remote()

        self.assertFalse(self.nmc_obj._can_push_repo_to_remote)

    def test_given_can_push_repo_to_remote_true_then_add_new_remote_and_push_called(self):

        self.nmc_obj._can_push_repo_to_remote = True

        self.nmc_obj.push_repo_to_remote()

        self.mock_push_to_remote.assert_called_with(self.nmc_obj.disk_dir)

    def test_given_can_push_repo_to_remote_false_then_exception_raised_with_correct_message(self):

        self.nmc_obj._can_push_repo_to_remote = False
        self.mock_verify_can_push_repo_to_remote.side_effect = nmc.VerificationError("error")

        with self.assertRaises(Exception) as e:
            self.nmc_obj.push_repo_to_remote()

        self.assertFalse(self.mock_push_to_remote.called)
        self.assertEqual(str(e.exception), "error")

    def test_given_can_push_repo_to_remote_originally_false_but_verify_function_does_not_raise_exception_then_add_new_remote_and_push_called(self):

        self.nmc_obj._can_push_repo_to_remote = False

        self.nmc_obj.push_repo_to_remote()

        self.mock_push_to_remote.assert_called_with(self.nmc_obj.disk_dir)

class NewModuleCreatorIOCAddToModuleCreateLocalModuleTest(unittest.TestCase):

    def setUp(self):

            self.patch_chdir = patch('dls_ade.new_module_creator.os.chdir')
            self.patch_vcs_git = patch('dls_ade.new_module_creator.vcs_git')
            self.patch_create_files = patch('dls_ade.new_module_creator.NewModuleCreatorIOCAddToModule._create_files')
            self.patch_verify_can_create_local_module = patch('dls_ade.new_module_creator.NewModuleCreator.verify_can_create_local_module')

            self.addCleanup(self.patch_chdir.stop)
            self.addCleanup(self.patch_vcs_git.stop)
            self.addCleanup(self.patch_create_files.stop)
            self.addCleanup(self.patch_verify_can_create_local_module.stop)

            self.mock_chdir = self.patch_chdir.start()
            self.mock_vcs_git = self.patch_vcs_git.start()
            self.mock_create_files = self.patch_create_files.start()
            self.mock_verify_can_create_local_module = self.patch_verify_can_create_local_module.start()

            # self.mock_os.return_value = "Example"

            self.nmc_obj = nmc.NewModuleCreatorIOCAddToModule("test_module", "test_app", "test_area")

    def test_given_can_create_local_module_true_then_flag_set_false(self):

        self.nmc_obj._can_create_local_module = True

        self.nmc_obj.create_local_module()

        self.assertFalse(self.nmc_obj._can_create_local_module)

    def test_given_can_create_local_module_false_then_exception_raised_with_correct_message(self):

        self.nmc_obj._can_create_local_module = False
        self.mock_verify_can_create_local_module.side_effect = nmc.VerificationError("error")

        with self.assertRaises(nmc.VerificationError) as e:
            self.nmc_obj.create_local_module()

        self.assertFalse(self.mock_vcs_git.clone.called)
        self.assertEqual(str(e.exception), "error")

    def test_given_can_create_local_module_true_then_rest_of_function_is_run(self):

        self.nmc_obj._can_create_local_module = True

        self.nmc_obj.create_local_module()

        call_list = [call(self.nmc_obj.disk_dir), call(self.nmc_obj.cwd)]

        self.mock_vcs_git.clone.assert_called_once_with(self.nmc_obj.server_repo_path, self.nmc_obj.disk_dir)
        self.mock_chdir.assert_has_calls(call_list)
        self.assertTrue(self.mock_create_files.called)
        self.mock_vcs_git.stage_all_files_and_commit.assert_called_once_with(self.nmc_obj.disk_dir)

    def test_given_can_create_local_module_originally_false_but_verify_function_does_not_raise_exception_then_rest_of_function_is_run(self):

        self.nmc_obj._can_create_local_module = False

        self.nmc_obj.create_local_module()

        call_list = [call(self.nmc_obj.disk_dir), call(self.nmc_obj.cwd)]

        self.mock_vcs_git.clone.assert_called_once_with(self.nmc_obj.server_repo_path, self.nmc_obj.disk_dir)
        self.mock_chdir.assert_has_calls(call_list)
        self.assertTrue(self.mock_create_files.called)
        self.mock_vcs_git.stage_all_files_and_commit.assert_called_once_with(self.nmc_obj.disk_dir)
