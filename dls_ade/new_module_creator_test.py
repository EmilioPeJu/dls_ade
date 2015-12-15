import unittest
import os

import dls_ade.new_module_creator as new_c
from dls_ade.dls_start_new_module import make_parser
from pkg_resources import require
require("mock")
from mock import patch, ANY, MagicMock, mock_open, call, mock_open
from new_module_templates import py_files, tools_files, default_files

from sys import version_info
if version_info.major == 2:
    import __builtin__ as builtins  # Allows for Python 2/3 compatibility, 'builtins' is namespace for inbuilt functions
else:
    import builtins


class GetNewModuleCreator(unittest.TestCase):

    def setUp(self):

        methods_to_patch = [
            'CreatorIOC',
            'CreatorIOCAddToModule',
            'CreatorIOCBL',
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

        # self.mocks['CreatorTools'].return_value = "Example"

    def test_given_unsupported_area_then_exception_raised(self):

        with self.assertRaises(Exception):
            new_c.get_new_module_creator("test_module", "fake_area")

    def test_given_area_is_ioc_and_no_BL_statement_and_dash_separated_then_new_module_creator_ioc_called_with_correct_args(self):

        ioc_c_mock = self.mocks['CreatorIOC']

        new_ioc_creator = new_c.get_new_module_creator("test-module-IOC-01", "ioc")

        ioc_c_mock.assert_called_once_with("test/test-module-IOC-01", "test-module-IOC-01", "ioc")

    def test_given_area_is_ioc_and_no_BL_statement_and_slash_separated_with_fullname_true_then_new_module_creator_ioc_called_with_correct_args(self):

        ioc_c_mock = self.mocks['CreatorIOC']

        new_ioc_creator = new_c.get_new_module_creator("test/module/01", "ioc", fullname=True)

        ioc_c_mock.assert_called_once_with("test/test-module-IOC-01", "test-module-IOC-01", "ioc")

    @patch('dls_ade.new_module_creator.vcs_git.is_repo_path', return_value = False)
    def test_given_area_is_ioc_and_no_BL_statement_and_slash_separated_with_fullname_false_and_module_path_not_in_remote_repo_then_new_module_creator_ioc_called_with_correct_args(self, mock_is_repo_path):

        ioc_c_mock = self.mocks['CreatorIOC']

        new_ioc_creator = new_c.get_new_module_creator("test/module/01", "ioc")

        mock_is_repo_path.assert_called_once_with("controls/ioc/test/module")
        ioc_c_mock.assert_called_once_with("test/module", "test-module-IOC-01", "ioc")

    @patch('dls_ade.new_module_creator.vcs_git.is_repo_path', return_value = True)
    def test_given_area_is_ioc_and_no_BL_statement_and_slash_separated_with_fullname_false_and_module_path_in_remote_repo_then_new_module_creator_ioc_add_to_module_called_with_correct_args(self, mock_is_repo_path):

        ioc_os_c_mock = self.mocks['CreatorIOCAddToModule']

        new_ioc_creator = new_c.get_new_module_creator("test/module/02", "ioc")

        mock_is_repo_path.assert_called_once_with("controls/ioc/test/module")
        ioc_os_c_mock.assert_called_once_with("test/module", "test-module-IOC-02", "ioc")

    def test_given_area_is_ioc_and_tech_area_is_BL_slash_form_then_new_module_creator_ioc_bl_called_with_correct_args(self):

        iocbl_c_mock = self.mocks['CreatorIOCBL']

        new_tools_creator = new_c.get_new_module_creator("test/BL", "ioc")

        iocbl_c_mock.assert_called_once_with("test/BL", "test", "ioc")

    def test_given_area_is_ioc_and_tech_area_is_BL_dash_form_then_new_module_creator_ioc_bl_called_with_correct_args(self):

        iocbl_c_mock = self.mocks['CreatorIOCBL']

        new_tools_creator = new_c.get_new_module_creator("test-BL-IOC-01", "ioc")

        iocbl_c_mock.assert_called_once_with("test/test-BL-IOC-01", "test-BL-IOC-01", "ioc")

    def test_given_area_is_python_with_invalid_name_then_new_module_creator_python_not_returned(self):

        py_c_mock = self.mocks['CreatorPython']

        with self.assertRaises(Exception):
            new_py_creator = new_c.get_new_module_creator("test_module", "python")

        self.assertFalse(py_c_mock.called)

        with self.assertRaises(Exception):
            new_py_creator = new_c.get_new_module_creator("dls_test-module", "python")

        self.assertFalse(py_c_mock.called)

        with self.assertRaises(Exception):
            new_py_creator = new_c.get_new_module_creator("dls_test.module", "python")

        self.assertFalse(py_c_mock.called)

    def test_given_area_is_python_with_valid_name_then_new_module_creator_python_called_with_correct_args(self):

        py_c_mock = self.mocks['CreatorPython']

        new_py_creator = new_c.get_new_module_creator("dls_test_module", "python")

        py_c_mock.assert_called_once_with("dls_test_module", "python")

    def test_given_area_is_support_then_new_module_creator_support_returned(self):

        sup_c_mock = self.mocks['CreatorSupport']

        new_sup_creator = new_c.get_new_module_creator("test_module")  # Area automatically support

        sup_c_mock.assert_called_once_with("test_module", "support")

    def test_given_area_is_tools_then_new_module_creator_tools_returned(self):

        tools_c_mock = self.mocks['CreatorTools']

        new_tools_creator = new_c.get_new_module_creator("test_module", "tools")

        tools_c_mock.assert_called_once_with("test_module", "tools")


class NewModuleCreatorObtainTemplateFilesTest(unittest.TestCase):

    def test_given_area_is_unknown_then_returns_empty_dictionary(self):

        template_dict = new_c.obtain_template_files("test_area")

        self.assertEqual(template_dict, {})

    def test_given_area_is_default_then_returns_default_dictionary(self):

        template_dict = new_c.obtain_template_files("default")

        self.assertEqual(template_dict, default_files)

    def test_given_area_is_ioc_then_returns_default_dictionary(self):

        template_dict = new_c.obtain_template_files("ioc")

        self.assertEqual(template_dict, default_files)

    def test_given_area_is_support_then_returns_default_dictionary(self):

        template_dict = new_c.obtain_template_files("support")

        self.assertEqual(template_dict, default_files)

    def test_given_area_is_python_then_returns_python_dictionary(self):

        template_dict = new_c.obtain_template_files("python")

        self.assertEqual(template_dict, py_files)

    def test_given_area_is_tools_then_returns_tools_dictionary(self):

        template_dict = new_c.obtain_template_files("tools")

        self.assertEqual(template_dict, tools_files)


class NewModuleCreatorClassInitTest(unittest.TestCase):

    def test_given_reasonable_input_then_initialisation_is_successful(self):

        base_c = new_c.NewModuleCreator("test_module", "test_area")  # non-existent module and area


class NewModuleCreatorGenerateTemplateArgs(unittest.TestCase):

    @patch('os.getlogin', return_value='my_login')
    def test_given_reasonable_input_then_correct_template_args_given(self, mock_getlogin):

        mod_c = new_c.NewModuleCreator("test_module", "test_area")

        self.assertEqual(mod_c.template_args, {'module': "test_module", 'getlogin': "my_login"})


class NewModuleCreatorVerifyRemoteRepoTest(unittest.TestCase):

    def setUp(self):

        self.patch_check_if_remote_repo_exists = patch('dls_ade.new_module_creator.NewModuleCreator._check_if_remote_repo_exists')

        self.addCleanup(self.patch_check_if_remote_repo_exists.stop)

        self.mock_check_if_remote_repo_exists = self.patch_check_if_remote_repo_exists.start()

        self.mod_c = new_c.NewModuleCreator("test_module", "test_area")

    def test_given_exists_true_then_exception_raised_with_correct_message_including_directory(self):

        self.mock_check_if_remote_repo_exists.return_value = (True, "test_directory")
        comp_message = "The path {dir:s} already exists on gitolite, cannot continue".format(dir="test_directory")

        with self.assertRaises(new_c.VerificationError) as e:
            self.mod_c.verify_remote_repo()

        self.assertEqual(str(e.exception), comp_message)

    def test_given_exists_false_then_remote_repo_valid_set_true(self):

        self.mock_check_if_remote_repo_exists.return_value = (False, "")

        self.mod_c.verify_remote_repo()

        self.assertTrue(self.mod_c._remote_repo_valid)


class NewModuleCreatorCheckIfRemoteRepoExistsTest(unittest.TestCase):

    def setUp(self):

        self.patch_get_remote_dir_list = patch('dls_ade.new_module_creator.NewModuleCreator.get_remote_dir_list')
        self.patch_is_repo_path = patch('dls_ade.vcs_git.is_repo_path')

        self.addCleanup(self.patch_get_remote_dir_list.stop)
        self.addCleanup(self.patch_is_repo_path.stop)

        self.mock_get_remote_dir_list = self.patch_get_remote_dir_list.start()
        self.mock_is_repo_path = self.patch_is_repo_path.start()

        self.mod_c = new_c.NewModuleCreator("test_module", "test_area")

    def test_given_one_of_dir_list_exists_then_flag_set_true_and_directory_returned(self):

        self.mock_get_remote_dir_list.return_value = ['inrepo', 'inrepo', 'inrepo']
        self.mock_is_repo_path.return_value = True

        exists, dir_path = self.mod_c._check_if_remote_repo_exists()

        self.assertTrue(exists)

        self.assertEqual(dir_path, "inrepo")

    def test_given_dir_list_does_not_exist_then_flag_set_false_and_directory_returned_is_blank(self):

        self.mock_get_remote_dir_list.return_value = ['notinrepo', 'notinrepo', 'notinrepo']
        self.mock_is_repo_path.return_value = False

        exists, dir_path = self.mod_c._check_if_remote_repo_exists()

        self.assertFalse(exists)

        self.assertEqual(dir_path, "")

    def test_given_one_dir_does_exist_then_flag_set_true_and_directory_returned_is_correct(self):

        self.mock_get_remote_dir_list.return_value = ['notinrepo', 'inrepo', 'notinrepo']
        self.mock_is_repo_path.side_effect = [False, True, False]

        exists, dir_path = self.mod_c._check_if_remote_repo_exists()

        self.assertTrue(exists)

        self.assertEqual(dir_path, "inrepo")


class NewModuleCreatorGetRemoteDirListTest(unittest.TestCase):

    @patch('dls_ade.new_module_creator.pathf.vendorModule', return_value = 'vendor_module')
    @patch('dls_ade.new_module_creator.pathf.prodModule', return_value = 'prod_module')
    def test_correct_dir_list_returned(self, mock_prod, mock_vend):

        mod_c = new_c.NewModuleCreator("test_module", "test_area")
        dir_list = mod_c.get_remote_dir_list()

        self.assertEqual(dir_list, [mod_c.server_repo_path, 'vendor_module', 'prod_module'])


class NewModuleCreatorVerifyCanCreateLocalModule(unittest.TestCase):

    def setUp(self):

        self.patch_is_dir = patch('dls_ade.new_module_creator.os.path.isdir')
        self.patch_is_git_dir = patch('dls_ade.new_module_creator.vcs_git.is_git_dir')

        self.addCleanup(self.patch_is_dir.stop)
        self.addCleanup(self.patch_is_git_dir.stop)

        self.mock_is_dir = self.patch_is_dir.start()
        self.mock_is_git_dir = self.patch_is_git_dir.start()

        self.mod_c = new_c.NewModuleCreator("test_module", "test_area")

    def test_given_module_folder_does_not_exist_and_is_not_in_git_repo_then_flag_set_true(self):

        self.mock_is_dir.return_value = False
        self.mock_is_git_dir.return_value = False

        self.mod_c.verify_can_create_local_module()

        self.assertTrue(self.mod_c._can_create_local_module)

    def test_given_module_folder_exists_then_flag_set_false_and_error_returned_is_correct(self):

        self.mock_is_dir.return_value = True
        self.mock_is_git_dir.return_value = False

        comp_message = "Directory {dir:s} already exists, please move elsewhere and try again.".format(dir=os.path.join("./", self.mod_c.disk_dir))

        with self.assertRaises(new_c.VerificationError) as e:
            self.mod_c.verify_can_create_local_module()

        self.assertEqual(str(e.exception), comp_message)

        self.assertFalse(self.mod_c._remote_repo_valid)

    def test_given_module_folder_is_in_git_repo_then_flag_set_false_and_error_returned_is_correct(self):

        self.mock_is_dir.return_value = False
        self.mock_is_git_dir.return_value = True

        comp_message = "Currently in a git repository, please move elsewhere and try again.".format(dir=os.path.join("./", self.mod_c.disk_dir))

        with self.assertRaises(new_c.VerificationError) as e:
            self.mod_c.verify_can_create_local_module()

        self.assertEqual(str(e.exception), comp_message)

        self.assertFalse(self.mod_c._remote_repo_valid)

    def test_given_module_folder_exists_and_is_in_repo_then_flag_set_false_and_error_returned_is_correct(self):

        self.mock_is_dir.return_value = True
        self.mock_is_git_dir.return_value = True

        comp_message = "Directory {dir:s} already exists, please move elsewhere and try again.\n"
        comp_message += "Currently in a git repository, please move elsewhere and try again."
        comp_message = comp_message.format(dir=os.path.join("./", self.mod_c.disk_dir))

        with self.assertRaises(new_c.VerificationError) as e:
            self.mod_c.verify_can_create_local_module()

        self.assertEqual(str(e.exception), comp_message)

        self.assertFalse(self.mod_c._remote_repo_valid)


class NewModuleCreatorVerifyCanPushLocalRepoToRemoteTest(unittest.TestCase):

    def setUp(self):

        self.patch_is_dir = patch('dls_ade.new_module_creator.os.path.isdir')
        self.patch_is_git_root_dir = patch('dls_ade.new_module_creator.vcs_git.is_git_root_dir')
        self.patch_verify_remote_repo = patch('dls_ade.new_module_creator.NewModuleCreator.verify_remote_repo')

        self.addCleanup(self.patch_is_dir.stop)
        self.addCleanup(self.patch_is_git_root_dir.stop)
        self.addCleanup(self.patch_verify_remote_repo.stop)

        self.mock_is_dir = self.patch_is_dir.start()
        self.mock_is_git_root_dir = self.patch_is_git_root_dir.start()
        self.mock_verify_remote_repo = self.patch_verify_remote_repo.start()

        self.mod_c = new_c.NewModuleCreator("test_module", "test_area")

    def test_given_module_folder_exists_and_is_repo_and_remote_repo_valid_then_flag_set_true(self):

        self.mock_is_dir.return_value = True
        self.mock_is_git_root_dir.return_value = True

        self.mod_c._remote_repo_valid = True
        self.mod_c.verify_can_push_repo_to_remote()

        self.assertTrue(self.mod_c._can_push_repo_to_remote)

    def test_given_remote_repo_valid_not_previously_set_but_true_then_flag_set_true(self):

        self.mock_is_dir.return_value = True
        self.mock_is_git_root_dir.return_value = True

        self.mod_c._can_push_repo_to_remote = False

        self.mod_c.verify_can_push_repo_to_remote()

        self.assertTrue(self.mod_c._can_push_repo_to_remote)

    def test_given_remote_repo_valid_false_then_flag_set_false_and_error_returned_is_correct(self):

        self.mod_c._remote_repo_valid = False

        self.mock_verify_remote_repo.side_effect = new_c.VerificationError("error")

        self.mock_is_dir.return_value = True
        self.mock_is_git_root_dir.return_value = True

        with self.assertRaises(new_c.VerificationError) as e:
            self.mod_c.verify_can_push_repo_to_remote()

        self.assertEqual(str(e.exception), "error")
        self.assertFalse(self.mod_c._can_push_repo_to_remote)

    def test_given_module_folder_does_not_exist_then_flag_set_false_and_error_returned_is_correct(self):

        self.mock_is_dir.return_value = False
        self.mock_is_git_root_dir.return_value = False

        self.mod_c._remote_repo_valid = True

        comp_message = "Directory {dir:s} does not exist.".format(dir=os.path.join("./", self.mod_c.disk_dir))

        with self.assertRaises(new_c.VerificationError) as e:
            self.mod_c.verify_can_push_repo_to_remote()

        self.assertEqual(str(e.exception), comp_message)
        self.assertFalse(self.mod_c._can_push_repo_to_remote)

    def test_given_module_folder_is_not_repo_then_flag_set_false_and_error_returned_is_correct(self):

        self.mock_is_dir.return_value = True
        self.mock_is_git_root_dir.return_value = False

        self.mod_c._remote_repo_valid = True

        comp_message = "Directory {dir:s} is not a git repository. Unable to push to remote repository.".format(dir=os.path.join("./", self.mod_c.disk_dir))

        with self.assertRaises(new_c.VerificationError) as e:
            self.mod_c.verify_can_push_repo_to_remote()

        self.assertEqual(str(e.exception), comp_message)
        self.assertFalse(self.mod_c._can_push_repo_to_remote)

    def test_given_module_folder_is_not_repo_and_remote_repo_false_then_flag_set_false_and_error_returned_is_correct(self):

        self.mock_verify_remote_repo.side_effect = new_c.VerificationError('error')
        self.mock_is_dir.return_value = True
        self.mock_is_git_root_dir.return_value = False

        comp_message = "Directory {dir:s} is not a git repository. Unable to push to remote repository.\n"
        comp_message = comp_message.format(dir=os.path.join("./", self.mod_c.disk_dir))
        comp_message += "error"
        comp_message = comp_message.rstrip()

        with self.assertRaises(new_c.VerificationError) as e:
            self.mod_c.verify_can_push_repo_to_remote()

        self.assertEqual(str(e.exception), comp_message)
        self.assertFalse(self.mod_c._can_push_repo_to_remote)


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

        self.mod_c = new_c.NewModuleCreator("test_module", "test_area")

    def test_given_can_create_local_module_true_then_flag_set_false(self):

        self.mod_c._can_create_local_module = True

        self.mod_c.create_local_module()

        self.assertFalse(self.mod_c._can_create_local_module)

    def test_given_can_create_local_module_false_then_exception_raised_with_correct_message(self):

        self.mod_c._can_create_local_module = False
        self.mock_verify_can_create_local_module.side_effect = new_c.VerificationError("error")

        with self.assertRaises(Exception) as e:
            self.mod_c.create_local_module()

        self.assertFalse(self.mock_os.path.isdir.called)
        self.assertEqual(str(e.exception), "error")

    def test_given_can_create_local_module_true_then_rest_of_function_is_run(self):

        self.mod_c._can_create_local_module = True

        self.mod_c.create_local_module()

        call_list = [call(self.mod_c.disk_dir), call(self.mod_c.cwd)]

        self.mock_os.path.isdir.assert_called_once_with(self.mod_c.disk_dir)
        self.mock_os.chdir.assert_has_calls(call_list)
        self.assertTrue(self.mock_create_files.called)
        self.mock_vcs_git.init_repo.assert_called_once_with(self.mod_c.disk_dir)
        self.mock_vcs_git.stage_all_files_and_commit.assert_called_once_with(self.mod_c.disk_dir)

    def test_given_can_create_local_module_originally_false_but_verify_function_does_not_raise_exception_then_rest_of_function_is_run(self):

        self.mod_c._can_create_local_module = False

        self.mod_c.create_local_module()

        call_list = [call(self.mod_c.disk_dir), call(self.mod_c.cwd)]

        self.mock_os.path.isdir.assert_called_once_with(self.mod_c.disk_dir)
        self.mock_os.chdir.assert_has_calls(call_list)
        self.assertTrue(self.mock_create_files.called)
        self.mock_vcs_git.init_repo.assert_called_once_with(self.mod_c.disk_dir)
        self.mock_vcs_git.stage_all_files_and_commit.assert_called_once_with(self.mod_c.disk_dir)

    def test_given_can_create_local_module_true_and_disk_dir_already_exists_then_makedirs_is_not_called(self):

        self.mod_c._can_create_local_module = True
        self.mock_os.path.isdir.return_value = True

        self.mod_c.create_local_module()

        self.assertFalse(self.mock_os.makedirs.called)

    def test_given_can_create_local_module_false_and_disk_dir_does_not_exist_then_makedirs_is_called(self):

        self.mod_c._can_create_local_module = True
        self.mock_os.path.isdir.return_value = False

        self.mod_c.create_local_module()

        self.mock_os.makedirs.assert_called_once_with(self.mod_c.disk_dir)


class NewModuleCreatorCreateFilesTest(unittest.TestCase):

    def setUp(self):

        self.mod_c = new_c.NewModuleCreator("test_module", "test_area")

    @patch('dls_ade.new_module_creator.NewModuleCreator._create_files_from_template_dict')
    def test_create_files_from_template_called(self, mock_create_files_from_template):

        self.mod_c._create_files()

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

        self.mod_c = new_c.NewModuleCreator("test_module", "test_area")
        self.mod_c.template_args = {"arg1": "argument_1", "arg2": "argument_2"}
        self.open_mock = mock_open()  # mock_open is function designed to help mock the 'open' built-in function

    def test_given_folder_name_in_template_files_then_exception_raised_with_correct_message(self):

        self.mod_c.template_files = {"folder_name/": "Written contents"}
        comp_message = "{dir:s} in template dictionary is not a valid file name".format(dir="folder_name")

        with patch.object(builtins, 'open', self.open_mock):  # This is to prevent accidental file creation
            with self.assertRaises(Exception) as e:
                self.mod_c._create_files_from_template_dict()

        self.assertEqual(str(e.exception), comp_message)
        self.assertFalse(self.open_mock.called)
        file_handle_mock = self.open_mock()
        self.assertFalse(file_handle_mock.write.called)

    def test_given_single_file_that_already_exists_then_file_not_created(self):

        self.mod_c.template_files = {"already_exists.txt": "Written contents"}
        self.mock_isfile.return_value = True

        with patch.object(builtins, 'open', self.open_mock):
            self.mod_c._create_files_from_template_dict()

        self.assertFalse(self.open_mock.called)

        file_handle_mock = self.open_mock()
        self.assertFalse(file_handle_mock.called)

    def test_given_single_file_then_file_created_and_correctly_written_to(self):

        self.mod_c.template_files = {"file1.txt": "Written contents"}

        with patch.object(builtins, 'open', self.open_mock):
            self.mod_c._create_files_from_template_dict()

        self.open_mock.assert_called_once_with("file1.txt", "w")

        file_handle_mock = self.open_mock()
        file_handle_mock.write.assert_any_call("Written contents")

    def test_given_single_file_in_folder_that_does_not_exist_then_folder_and_file_created_and_file_correctly_written_to(self):

        self.mod_c.template_files = {"test_folder/file1.txt": "Written contents"}

        with patch.object(builtins, 'open', self.open_mock):
            self.mod_c._create_files_from_template_dict()

        self.mock_makedirs.asset_called_once_with("test_folder")
        self.open_mock.assert_called_once_with("test_folder/file1.txt", "w")

        file_handle_mock = self.open_mock()
        file_handle_mock.write.assert_any_call("Written contents")

    def test_given_single_file_in_folder_that_exists_then_folder_not_created_but_file_created_and_file_correctly_written_to(self):

        self.mock_isdir.return_value = True

        self.mod_c.template_files = {"test_folder/file1.txt": "Written contents"}

        with patch.object(builtins, 'open', self.open_mock):
            self.mod_c._create_files_from_template_dict()

        self.assertFalse(self.mock_makedirs.called)
        self.open_mock.assert_called_once_with("test_folder/file1.txt", "w")

        file_handle_mock = self.open_mock()
        file_handle_mock.write.assert_any_call("Written contents")

    def test_given_two_files_in_separate_folders_then_both_folders_created_and_files_correctly_written_to(self):

        self.mod_c.template_files = {"test_folder1/file1.txt": "Written contents1", "test_folder2/file2.txt": "Written contents2"}

        with patch.object(builtins, 'open', self.open_mock):
            self.mod_c._create_files_from_template_dict()

        self.mock_makedirs.assert_has_calls([call("test_folder1"), call("test_folder2")], any_order=True)

        self.open_mock.assert_has_calls([call("test_folder1/file1.txt", "w"), call("test_folder2/file2.txt", "w")], any_order=True)

        file_handle_mock = self.open_mock()
        file_handle_mock.write.assert_has_calls([call("Written contents1"), call("Written contents2")], any_order=True)

    def test_given_two_files_in_same_folder_then_both_created_and_written_to_but_directory_only_made_once(self):

        self.mock_isdir.side_effect = [False, True]

        self.mod_c.template_files = {"test_folder/file1.txt": "Written contents1", "test_folder/file2.txt": "Written contents2"}

        with patch.object(builtins, 'open', self.open_mock):
            self.mod_c._create_files_from_template_dict()

        self.mock_makedirs.assert_called_once_with("test_folder")

        self.open_mock.assert_has_calls([call("test_folder/file1.txt", "w"), call("test_folder/file2.txt", "w")], any_order=True)

        file_handle_mock = self.open_mock()
        file_handle_mock.write.assert_has_calls([call("Written contents1"), call("Written contents2")], any_order=True)

    def test_given_single_file_with_placeholder_in_name_then_file_created_and_correctly_written_to(self):

        self.mod_c.template_files = {"{arg:s}.txt": "Written contents"}
        self.mod_c.template_args = {'arg': "my_argument"}

        with patch.object(builtins, 'open', self.open_mock):
            self.mod_c._create_files_from_template_dict()

        self.open_mock.assert_called_once_with("my_argument.txt", "w")

        file_handle_mock = self.open_mock()
        file_handle_mock.write.assert_any_call("Written contents")

    def test_given_args_and_template_then_arguments_are_inserted_correctly(self):

        self.mod_c.template_files = {"file1.txt": "{arg1:s} and {arg2:s}"}

        with patch.object(builtins, 'open', self.open_mock):
            self.mod_c._create_files_from_template_dict()

        self.open_mock.assert_called_once_with("file1.txt", "w")

        file_handle_mock = self.open_mock()
        file_handle_mock.write.assert_called_once_with("argument_1 and argument_2")

    def test_given_nested_directory_then_folder_and_file_both_created_and_file_correctly_written_to(self):

        self.mod_c.template_files = {"test_folder/another_folder/yet_another_folder/file.txt": "Written contents"}

        with patch.object(builtins, 'open', self.open_mock):
            self.mod_c._create_files_from_template_dict()

        self.mock_makedirs.assert_called_once_with("test_folder/another_folder/yet_another_folder")

        self.open_mock.assert_called_once_with("test_folder/another_folder/yet_another_folder/file.txt", "w")

        file_handle_mock = self.open_mock()
        file_handle_mock.write.assert_called_once_with("Written contents")


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

        self.mod_c = new_c.NewModuleCreator("test_module", "test_area")

    def test_given_can_push_repo_to_remote_true_then_flag_set_false(self):

        self.mod_c._can_push_repo_to_remote = True

        self.mod_c.push_repo_to_remote()

        self.assertFalse(self.mod_c._can_push_repo_to_remote)

    def test_given_can_push_repo_to_remote_true_then_add_new_remote_and_push_called(self):

        self.mod_c._can_push_repo_to_remote = True

        self.mod_c.push_repo_to_remote()

        self.mock_add_new_remote_and_push.assert_called_with(self.mod_c.server_repo_path, self.mod_c.disk_dir)

    def test_given_can_push_repo_to_remote_false_then_exception_raised_with_correct_message(self):

        self.mod_c._can_push_repo_to_remote = False
        self.mock_verify_can_push_repo_to_remote.side_effect = new_c.VerificationError("error")

        with self.assertRaises(Exception) as e:
            self.mod_c.push_repo_to_remote()

        self.assertFalse(self.mock_add_new_remote_and_push.called)
        self.assertEqual(str(e.exception), "error")

    def test_given_can_push_repo_to_remote_originally_false_but_verify_function_does_not_raise_exception_then_add_new_remote_and_push_called(self):

        self.mod_c._can_push_repo_to_remote = False

        self.mod_c.push_repo_to_remote()

        self.mock_add_new_remote_and_push.assert_called_with(self.mod_c.server_repo_path, self.mod_c.disk_dir)

# Add tests for all derived NewModuleCreator classes

class NewModuleCreatorSupportCreateFiles(unittest.TestCase):

    @patch('dls_ade.new_module_creator.os.system')
    @patch('dls_ade.new_module_creator.NewModuleCreatorSupport._create_files_from_template_dict')
    def test_given_create_files_called_then_correct_functions_called(self, mock_create_from_dict, mock_os_system):

        mod_c = new_c.NewModuleCreatorSupport('test_module_path', 'test_area')

        mod_c._create_files()

        os_system_call_list = [call("makeBaseApp.pl -t dls {mod_path:s}".format(mod_path="test_module_path")), call("dls-make-etc-dir.py && make clean uninstall")]

        mock_os_system.assert_has_calls(os_system_call_list)
        mock_create_from_dict.assert_called_once_with()


class NewModuleCreatorIOCCreateFiles(unittest.TestCase):

    @patch('dls_ade.new_module_creator.shutil.rmtree')
    @patch('dls_ade.new_module_creator.os.system')
    @patch('dls_ade.new_module_creator.NewModuleCreatorIOC._create_files_from_template_dict')
    def test_given_create_files_called_then_correct_functions_called(self, mock_create_from_dict, mock_os_system, mock_rmtree):

        mod_c = new_c.NewModuleCreatorIOC('test_module_path', 'test_app_name', 'test_area')

        mod_c._create_files()

        os_system_call_list = [call("makeBaseApp.pl -t dls {app_name:s}".format(app_name="test_app_name")), call("makeBaseApp.pl -i -t dls {app_name:s}".format(app_name="test_app_name"))]

        mock_rmtree.assert_called_once_with(os.path.join("{app_name:s}App".format(app_name="test_app_name"), 'opi'))
        mock_os_system.assert_has_calls(os_system_call_list)
        mock_create_from_dict.assert_called_once_with()


class NewModuleCreatorIOCBLCreateFiles(unittest.TestCase):

    @patch('dls_ade.new_module_creator.os.system')
    @patch('dls_ade.new_module_creator.NewModuleCreatorIOCBL._create_files_from_template_dict')
    def test_given_create_files_called_then_correct_functions_called(self, mock_create_from_dict, mock_os_system):

        mod_c = new_c.NewModuleCreatorIOCBL('test_module_path', 'test_app_name', 'test_area')

        mod_c._create_files()

        mock_os_system.assert_called_once_with("makeBaseApp.pl -t dlsBL {app_name:s}".format(app_name="test_app_name"))
        mock_create_from_dict.assert_called_once_with()


class NewModuleCreatorIOCAddToModuleVerifyRemoteRepoTest(unittest.TestCase):

    def setUp(self):

        self.patch_clone = patch('dls_ade.new_module_creator.vcs_git.clone')
        self.patch_mkdtemp = patch('dls_ade.new_module_creator.tempfile.mkdtemp', return_value = 'tempdir')
        self.patch_isdir = patch('dls_ade.new_module_creator.os.path.isdir')
        self.patch_rmtree = patch('dls_ade.new_module_creator.shutil.rmtree')

        self.addCleanup(self.patch_clone.stop)
        self.addCleanup(self.patch_mkdtemp.stop)
        self.addCleanup(self.patch_isdir.stop)
        self.addCleanup(self.patch_rmtree.stop)

        self.mock_clone = self.patch_clone.start()
        self.mock_mkdtemp = self.patch_mkdtemp.start()
        self.mock_isdir = self.patch_isdir.start()
        self.mock_rmtree = self.patch_rmtree.start()

        self.mod_c = new_c.NewModuleCreatorIOCAddToModule("test_module", "test_app", "test_area")

    def test_given_function_called_then_mkdtemp_and_clone_called_correctly(self):

        try:
            self.mod_c.verify_remote_repo()
        except:
            pass

        self.mock_mkdtemp.assert_called_once_with()
        self.mock_clone.assert_called_once_with(self.mod_c.server_repo_path, "tempdir")

    def test_given_isdir_false_then_exception_raised_with_correct_message(self):

        self.mock_isdir.return_value = True
        comp_message =  "The app {app_name:s} already exists on gitolite, cannot continue".format(app_name="test_app")

        with self.assertRaises(new_c.VerificationError) as e:
            self.mod_c.verify_remote_repo()

        self.assertEqual(str(e.exception), comp_message)

    def test_given_isdir_false_and_exception_raised_outside_mkdtemp_then_rmtree_called_and_flag_still_false(self):

        self.mock_isdir.return_value = True

        with self.assertRaises(new_c.VerificationError):
            self.mod_c.verify_remote_repo()

        self.mock_rmtree.assert_called_once_with("tempdir")
        self.assertFalse(self.mod_c._remote_repo_valid)

    def test_given_mkdtemp_raises_exception_then_rmtree_not_called_and_correct_exception_passed_up(self):

        self.mock_mkdtemp.side_effect = Exception("generic exception message")

        with self.assertRaises(new_c.VerificationError) as e:
            self.mod_c.verify_remote_repo()

        self.assertFalse(self.mock_rmtree.called)
        self.assertFalse(self.mod_c._remote_repo_valid)
        self.assertEqual(str(e.exception), "generic exception message")

    def test_given_isdir_true_and_no_exception_raised_then_rmtree_called_and_flag_set_true(self):

        self.mock_isdir.return_value = False

        self.mod_c.verify_remote_repo()

        self.mock_rmtree.assert_called_once_with("tempdir")
        self.assertTrue(self.mod_c._remote_repo_valid)


class NewModuleCreatorIOCAddToModulePushRepoToRemoteTest(unittest.TestCase):

    def setUp(self):

        self.patch_verify_can_push_repo_to_remote = patch('dls_ade.new_module_creator.NewModuleCreatorIOCAddToModule.verify_can_push_repo_to_remote')
        self.patch_push_to_remote = patch('dls_ade.new_module_creator.vcs_git.push_to_remote')

        self.addCleanup(self.patch_verify_can_push_repo_to_remote.stop)
        self.addCleanup(self.patch_push_to_remote.stop)

        self.mock_verify_can_push_repo_to_remote = self.patch_verify_can_push_repo_to_remote.start()
        self.mock_push_to_remote = self.patch_push_to_remote.start()

        self.mod_c = new_c.NewModuleCreatorIOCAddToModule("test_module", "test_app", "test_area")

    def test_given_can_push_repo_to_remote_true_then_flag_set_false(self):

        self.mod_c._can_push_repo_to_remote = True

        self.mod_c.push_repo_to_remote()

        self.assertFalse(self.mod_c._can_push_repo_to_remote)

    def test_given_can_push_repo_to_remote_true_then_add_new_remote_and_push_called(self):

        self.mod_c._can_push_repo_to_remote = True

        self.mod_c.push_repo_to_remote()

        self.mock_push_to_remote.assert_called_with(self.mod_c.disk_dir)

    def test_given_can_push_repo_to_remote_false_then_exception_raised_with_correct_message(self):

        self.mod_c._can_push_repo_to_remote = False
        self.mock_verify_can_push_repo_to_remote.side_effect = new_c.VerificationError("error")

        with self.assertRaises(Exception) as e:
            self.mod_c.push_repo_to_remote()

        self.assertFalse(self.mock_push_to_remote.called)
        self.assertEqual(str(e.exception), "error")

    def test_given_can_push_repo_to_remote_originally_false_but_verify_function_does_not_raise_exception_then_add_new_remote_and_push_called(self):

        self.mod_c._can_push_repo_to_remote = False

        self.mod_c.push_repo_to_remote()

        self.mock_push_to_remote.assert_called_with(self.mod_c.disk_dir)

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

            self.mod_c = new_c.NewModuleCreatorIOCAddToModule("test_module", "test_app", "test_area")

    def test_given_can_create_local_module_true_then_flag_set_false(self):

        self.mod_c._can_create_local_module = True

        self.mod_c.create_local_module()

        self.assertFalse(self.mod_c._can_create_local_module)

    def test_given_can_create_local_module_false_then_exception_raised_with_correct_message(self):

        self.mod_c._can_create_local_module = False
        self.mock_verify_can_create_local_module.side_effect = new_c.VerificationError("error")

        with self.assertRaises(new_c.VerificationError) as e:
            self.mod_c.create_local_module()

        self.assertFalse(self.mock_vcs_git.clone.called)
        self.assertEqual(str(e.exception), "error")

    def test_given_can_create_local_module_true_then_rest_of_function_is_run(self):

        self.mod_c._can_create_local_module = True

        self.mod_c.create_local_module()

        call_list = [call(self.mod_c.disk_dir), call(self.mod_c.cwd)]

        self.mock_vcs_git.clone.assert_called_once_with(self.mod_c.server_repo_path, self.mod_c.disk_dir)
        self.mock_chdir.assert_has_calls(call_list)
        self.assertTrue(self.mock_create_files.called)
        self.mock_vcs_git.stage_all_files_and_commit.assert_called_once_with(self.mod_c.disk_dir)

    def test_given_can_create_local_module_originally_false_but_verify_function_does_not_raise_exception_then_rest_of_function_is_run(self):

        self.mod_c._can_create_local_module = False

        self.mod_c.create_local_module()

        call_list = [call(self.mod_c.disk_dir), call(self.mod_c.cwd)]

        self.mock_vcs_git.clone.assert_called_once_with(self.mod_c.server_repo_path, self.mod_c.disk_dir)
        self.mock_chdir.assert_has_calls(call_list)
        self.assertTrue(self.mock_create_files.called)
        self.mock_vcs_git.stage_all_files_and_commit.assert_called_once_with(self.mod_c.disk_dir)
