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

        self.parser = make_parser()

        methods_to_patch = [
            'CreatorIOC',
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

        # self.mocks['CreatorTools'].return_value = "Example

    def test_given_unsupported_area_then_exception_raised(self):

        args = self.parser.parse_args("test_module --area fake_area".split())
        with self.assertRaises(Exception):
            new_c.get_new_module_creator(args)

    def test_given_supported_area_then_no_error_raised(self):

        args = self.parser.parse_args("test_module --area python".split())

        new_c.get_new_module_creator(args)  # Just testing that no errors are raised

    def test_given_area_is_ioc_and_no_BL_statement_then_new_module_creator_ioc_returned(self):

        ioc_c_mock = self.mocks['CreatorIOC']

        args = self.parser.parse_args("test_module -i".split())

        new_ioc_creator = new_c.get_new_module_creator(args)

        ioc_c_mock.assert_called_once_with(args.module_name, "ioc", os.getcwd())

    def test_given_area_is_ioc_and_no_BL_statement_and_no_import_then_new_module_creator_ioc_no_import_returned(self):

        ioc_c_mock = self.mocks['CreatorIOC']

        args = self.parser.parse_args("test_module -i --no-import".split())

        new_ioc_creator = new_c.get_new_module_creator(args)

        ioc_c_mock.assert_called_once_with(args.module_name, "ioc", os.getcwd())

    def test_given_area_is_python_then_new_module_creator_python_returned(self):

        py_c_mock = self.mocks['CreatorPython']

        args = self.parser.parse_args("test_module -p".split())

        new_py_creator = new_c.get_new_module_creator(args)

        py_c_mock.assert_called_once_with(args.module_name, "python", os.getcwd())

    def test_given_area_is_python_and_no_import_then_new_module_creator_python_no_import_returned(self):

        py_c_mock = self.mocks['CreatorPython']

        args = self.parser.parse_args("test_module -p --no-import".split())

        new_py_creator = new_c.get_new_module_creator(args)

        py_c_mock.assert_called_once_with(args.module_name, "python", os.getcwd())

    def test_given_area_is_support_then_new_module_creator_support_returned(self):

        sup_c_mock = self.mocks['CreatorSupport']

        args = self.parser.parse_args("test_module".split())  # Area automatically support

        new_sup_creator = new_c.get_new_module_creator(args)

        sup_c_mock.assert_called_once_with(args.module_name, "support", os.getcwd())

    def test_given_area_is_support_no_import_then_new_module_creator_support_no_import_returned(self):

        sup_c_mock = self.mocks['CreatorSupport']

        args = self.parser.parse_args("test_module --no-import".split())  # Area automatically support

        new_sup_creator = new_c.get_new_module_creator(args)

        sup_c_mock.assert_called_once_with(args.module_name, "support", os.getcwd())

    def test_given_area_is_tools_then_new_module_creator_tools_returned(self):

        tools_c_mock = self.mocks['CreatorTools']

        args = self.parser.parse_args("test_module --area tools".split())  # Area automatically support

        new_tools_creator = new_c.get_new_module_creator(args)

        tools_c_mock.assert_called_once_with(args.module_name, "tools", os.getcwd())

    def test_given_area_is_tools_no_import_then_new_module_creator_tools_no_import_returned(self):

        tools_c_mock = self.mocks['CreatorTools']

        args = self.parser.parse_args("test_module --area tools --no-import".split())  # Area automatically support

        new_tools_creator = new_c.get_new_module_creator(args)

        tools_c_mock.assert_called_once_with(args.module_name, "tools", os.getcwd())

    def test_given_area_is_ioc_and_tech_area_is_BL_slash_form_then_new_module_creator_ioc_bl_returned(self):

        iocbl_c_mock = self.mocks['CreatorIOCBL']

        args = self.parser.parse_args("test/BL -i".split())  # Area automatically support

        new_tools_creator = new_c.get_new_module_creator(args)

        iocbl_c_mock.assert_called_once_with(args.module_name, "ioc", os.getcwd())

    def test_given_area_is_ioc_and_tech_area_is_BL_dash_form_then_new_module_creator_ioc_bl_returned(self):

        iocbl_c_mock = self.mocks['CreatorIOCBL']

        args = self.parser.parse_args("test-BL -i".split())  # Area automatically support

        new_tools_creator = new_c.get_new_module_creator(args)

        iocbl_c_mock.assert_called_once_with(args.module_name, "ioc", os.getcwd())

    def test_given_area_is_ioc_and_tech_area_is_BL_no_import_then_new_module_creator_ioc_bl_no_import_returned(self):

        iocbl_c_mock = self.mocks['CreatorIOCBL']

        args = self.parser.parse_args("test/BL -i --no-import".split())  # Area automatically support

        new_tools_creator = new_c.get_new_module_creator(args)

        iocbl_c_mock.assert_called_once_with(args.module_name, "ioc", os.getcwd())


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

        base_c = new_c.NewModuleCreator("test_module", "test_area", os.getcwd())  # non-existent module and area


class NewModuleCreatorGenerateTemplateArgs(unittest.TestCase):

    @patch('os.getlogin', return_value='my_login')
    def test_given_reasonable_input_then_correct_template_args_given(self, mock_getlogin):

        mod_c = new_c.NewModuleCreator("test_module", "test_area", os.getcwd())

        self.assertEqual(mod_c.template_args, {'module': "test_module", 'getlogin': "my_login"})


class NewModuleCreatorCheckRemoteRepoValidTest(unittest.TestCase):

    def setUp(self):
        self.mod_c = new_c.NewModuleCreator("test_module", "test_area", os.getcwd())

    @patch('dls_ade.new_module_creator.NewModuleCreator.get_remote_dir_list', return_value=['inrepo', 'inrepo', 'inrepo'])
    @patch('dls_ade.vcs_git.is_repo_path', return_value=True)
    def test_given_dir_list_exists_then_flag_set_false_and_error_returned_is_correct(self, mock_is_repo, mock_get_dir_list):

        valid, message = self.mod_c.check_remote_repo_valid()
        comp_message = "The path {dir:s} already exists in subversion, cannot continue".format(dir="inrepo")

        self.assertFalse(valid)
        self.assertEqual(message, comp_message)

    @patch('dls_ade.new_module_creator.NewModuleCreator.get_remote_dir_list', return_value=['notinrepo', 'notinrepo', 'notinrepo'])
    @patch('dls_ade.vcs_git.is_repo_path', return_value=False)
    def test_given_dir_list_does_not_exist_then_flag_set_true_and_error_returned_is_blank(self, mock_is_repo, mock_get_dir_list):

        valid, message = self.mod_c.check_remote_repo_valid()
        comp_message = ""

        self.assertTrue(valid)
        self.assertEqual(message, comp_message)

    @patch('dls_ade.new_module_creator.NewModuleCreator.get_remote_dir_list', return_value=['notinrepo', 'inrepo', 'notinrepo'])
    @patch('dls_ade.vcs_git.is_repo_path')
    def test_given_one_dir_does_exist_then_flag_set_false_and_error_returned_is_correct(self, mock_is_repo, mock_get_dir_list):

        mock_is_repo.side_effect = [False, True, False]  # return value iterates through this list

        valid, message = self.mod_c.check_remote_repo_valid()
        comp_message = "The path {dir:s} already exists in subversion, cannot continue".format(dir="inrepo")

        self.assertFalse(valid)
        self.assertEqual(message, comp_message)

    @patch('dls_ade.new_module_creator.NewModuleCreator.get_remote_dir_list', return_value=['notinrepo', 'inrepo', 'notinrepo'])
    @patch('dls_ade.vcs_git.is_repo_path')
    def test_given_final_flag_is_false_then_returned_flag_and_object_flag_match(self, mock_is_repo, mock_get_dir_list):

        mock_is_repo.side_effect = [False, True, False]  # return value iterates through this list

        valid, message = self.mod_c.check_remote_repo_valid()

        self.assertFalse(valid)
        self.assertEqual(valid, self.mod_c.remote_repo_valid)

    @patch('dls_ade.new_module_creator.NewModuleCreator.get_remote_dir_list', return_value=['notinrepo', 'notinrepo', 'notinrepo'])
    @patch('dls_ade.vcs_git.is_repo_path', return_value=False)
    def test_given_final_flag_is_true_then_returned_flag_and_object_flag_match(self, mock_is_repo, mock_get_dir_list):

        valid, message = self.mod_c.check_remote_repo_valid()

        self.assertTrue(valid)
        self.assertEqual(valid, self.mod_c.remote_repo_valid)


class NewModuleCreatorGetRemoteDirListTest(unittest.TestCase):

    @patch('dls_ade.new_module_creator.pathf.vendorModule', return_value = 'vendor_module')
    @patch('dls_ade.new_module_creator.pathf.prodModule', return_value = 'prod_module')
    def test_correct_dir_list_returned(self, mock_prod, mock_vend):

        mod_c = new_c.NewModuleCreator("test_module", "test_area", os.getcwd())
        dir_list = mod_c.get_remote_dir_list()

        self.assertEqual(dir_list, [mod_c.dest, 'vendor_module', 'prod_module'])


class NewModuleCreatorCheckCreateModuleValidTest(unittest.TestCase):

    def setUp(self):
        self.mod_c = new_c.NewModuleCreator("test_module", "test_area", os.getcwd())

    @patch('dls_ade.new_module_creator.os.path.isdir', return_value=False)
    @patch('dls_ade.new_module_creator.vcs_git.is_git_dir', return_value=False)
    def test_given_module_folder_does_not_exist_and_is_not_in_git_repo_then_flag_set_true_and_error_returned_is_blank(self, mock_is_git_dir, mock_is_dir):

        valid, return_message = self.mod_c.check_create_module_valid()
        comp_message = ""

        self.assertTrue(valid)
        self.assertEqual(return_message, comp_message)

    @patch('dls_ade.new_module_creator.os.path.isdir', return_value=True)
    @patch('dls_ade.new_module_creator.vcs_git.is_git_dir', return_value=False)
    def test_given_module_folder_exists_then_flag_set_false_and_error_returned_is_correct(self, mock_is_git_dir, mock_is_dir):

        valid, return_message = self.mod_c.check_create_module_valid()
        comp_message = "Directory {dir:s} already exists, please move elsewhere and try again".format(dir=os.path.join("./", self.mod_c.disk_dir))

        self.assertFalse(valid)
        self.assertEqual(return_message, comp_message)

    @patch('dls_ade.new_module_creator.os.path.isdir', return_value=False)
    @patch('dls_ade.new_module_creator.vcs_git.is_git_dir', return_value=True)
    def test_given_module_folder_is_in_git_repo_then_flag_set_false_and_error_returned_is_correct(self, mock_is_git_dir, mock_is_dir):

        valid, return_message = self.mod_c.check_create_module_valid()
        comp_message = "Currently in a git repository, please move elsewhere and try again"

        self.assertFalse(valid)
        self.assertEqual(return_message, comp_message)

    @patch('dls_ade.new_module_creator.os.path.isdir', return_value=True)
    @patch('dls_ade.new_module_creator.vcs_git.is_git_dir', return_value=True)
    def test_given_module_folder_exists_and_is_in_repo_then_flag_set_false_and_error_returned_is_correct(self, mock_is_git_dir, mock_is_dir):

        valid, return_message = self.mod_c.check_create_module_valid()
        comp_message = "Directory {dir:s} already exists AND currently in a git repository."
        comp_message += " Please move elsewhere and try again"
        comp_message = comp_message.format(dir=os.path.join("./", self.mod_c.disk_dir))

        self.assertFalse(valid)
        self.assertEqual(return_message, comp_message)

    @patch('dls_ade.new_module_creator.os.path.isdir', return_value=False)
    @patch('dls_ade.new_module_creator.vcs_git.is_git_dir', return_value=False)
    def test_given_final_flag_is_true_then_returned_flag_and_object_flag_match(self, mock_is_git_dir, mock_is_dir):

        valid, return_message = self.mod_c.check_create_module_valid()

        self.assertTrue(valid)
        self.assertEqual(valid, self.mod_c.create_module_valid)

    @patch('dls_ade.new_module_creator.os.path.isdir', return_value=True)
    @patch('dls_ade.new_module_creator.vcs_git.is_git_dir', return_value=True)
    def test_given_final_flag_is_false_then_returned_flag_and_object_flag_match(self, mock_is_git_dir, mock_is_dir):

        valid, return_message = self.mod_c.check_create_module_valid()

        self.assertFalse(valid)
        self.assertEqual(valid, self.mod_c.create_module_valid)


class NewModuleCreatorCheckInitStageAndCommitValidTest(unittest.TestCase):

    def setUp(self):
        self.mod_c = new_c.NewModuleCreator("test_module", "test_area", os.getcwd())

    @patch('dls_ade.new_module_creator.os.path.isdir', return_value=True)
    @patch('dls_ade.new_module_creator.vcs_git.is_git_dir', return_value=False)
    def test_given_module_folder_exists_and_is_not_in_repo_then_flag_set_true_and_error_returned_is_blank(self, mock_is_git_dir, mock_is_dir):

        valid, return_message = self.mod_c.check_create_local_repo_valid()
        comp_message = ""

        self.assertTrue(valid)
        self.assertEqual(return_message, comp_message)

    @patch('dls_ade.new_module_creator.os.path.isdir', return_value=False)
    @patch('dls_ade.new_module_creator.vcs_git.is_git_dir', return_value=False)
    def test_given_module_folder_does_not_exist_then_flag_set_false_and_error_returned_is_correct(self, mock_is_git_dir, mock_is_dir):

        valid, return_message = self.mod_c.check_create_local_repo_valid()
        comp_message = "Directory {dir:s} does not exist".format(dir=os.path.join("./", self.mod_c.disk_dir))

        self.assertFalse(valid)
        self.assertEqual(return_message, comp_message)

    @patch('dls_ade.new_module_creator.os.path.isdir', return_value=True)
    @patch('dls_ade.new_module_creator.vcs_git.is_git_dir', return_value=True)
    def test_given_module_folder_is_in_repo_then_flag_set_false_and_error_returned_is_correct(self, mock_is_git_dir, mock_is_dir):

        valid, return_message = self.mod_c.check_create_local_repo_valid()
        comp_message = "Directory {dir:s} is inside git repository. Cannot initialise git repository".format(dir=os.path.join("./", self.mod_c.disk_dir))

        self.assertFalse(valid)
        self.assertEqual(return_message, comp_message)

    @patch('dls_ade.new_module_creator.os.path.isdir', return_value=True)
    @patch('dls_ade.new_module_creator.vcs_git.is_git_dir', return_value=False)
    def test_given_final_flag_is_true_then_returned_flag_and_object_flag_match(self, mock_is_git_dir, mock_is_dir):

        valid, return_message = self.mod_c.check_create_local_repo_valid()

        self.assertTrue(valid)
        self.assertEqual(valid, self.mod_c.create_local_repo_valid)

    @patch('dls_ade.new_module_creator.os.path.isdir', return_value=False)
    @patch('dls_ade.new_module_creator.vcs_git.is_git_dir', return_value=False)
    def test_given_final_flag_is_false_then_returned_flag_and_object_flag_match(self, mock_is_git_dir, mock_is_dir):

        valid, return_message = self.mod_c.check_create_local_repo_valid()

        self.assertFalse(valid)
        self.assertEqual(valid, self.mod_c.create_local_repo_valid)


class NewModuleCreatorCheckPushRepoToRemoteValidTest(unittest.TestCase):

    def setUp(self):
        self.mod_c = new_c.NewModuleCreator("test_module", "test_area", os.getcwd())

    @patch('dls_ade.new_module_creator.os.path.isdir', return_value=True)
    @patch('dls_ade.new_module_creator.vcs_git.is_git_root_dir', return_value=True)
    def test_given_module_folder_exists_and_is_repo_and_remote_repo_valid_then_flag_set_true_and_error_returned_is_blank(self, mock_is_git_root_dir, mock_is_dir):

        self.mod_c.remote_repo_valid = True
        valid, return_message = self.mod_c.check_push_repo_to_remote_valid()
        comp_message = ""

        self.assertTrue(valid)
        self.assertEqual(return_message, comp_message)

    @patch('dls_ade.new_module_creator.NewModuleCreator.get_remote_dir_list', return_value=['notinrepo', 'notinrepo', 'notinrepo'])
    @patch('dls_ade.vcs_git.is_repo_path', return_value=False)
    @patch('dls_ade.new_module_creator.os.path.isdir', return_value=True)
    @patch('dls_ade.new_module_creator.vcs_git.is_git_root_dir', return_value=True)
    def test_given_remote_repo_valid_not_previously_set_but_true_then_flag_set_true_and_error_returned_is_blank(self,
                                                        mock_is_git_root_dir, mock_is_dir, mock_is_repo_path, mock_get_remote_dir_list):

        valid, return_message = self.mod_c.check_push_repo_to_remote_valid()
        comp_message = ""

        self.assertTrue(valid)
        self.assertEqual(return_message, comp_message)

    @patch('dls_ade.new_module_creator.NewModuleCreator.get_remote_dir_list', return_value=['inrepo', 'inrepo', 'inrepo'])
    @patch('dls_ade.vcs_git.is_repo_path', return_value=True)
    @patch('dls_ade.new_module_creator.os.path.isdir', return_value=True)
    @patch('dls_ade.new_module_creator.vcs_git.is_git_root_dir', return_value=True)
    def test_given_remote_repo_valid_false_then_flag_set_false_and_error_returned_is_correct(self, mock_is_git_root_dir, mock_is_dir, mock_is_repo_path, mock_get_remote_dir_list):

        valid, return_message = self.mod_c.check_push_repo_to_remote_valid()
        _, comp_message = self.mod_c.check_remote_repo_valid()  # Don't want to constrain return message of check_remote_repo_valid()

        self.assertFalse(valid)
        self.assertEqual(return_message, comp_message)

    @patch('dls_ade.new_module_creator.os.path.isdir', return_value=False)
    @patch('dls_ade.new_module_creator.vcs_git.is_git_root_dir', return_value=False)
    def test_given_module_folder_does_not_exist_then_flag_set_false_and_error_returned_is_correct(self,
                                                        mock_is_git_root_dir, mock_is_dir):

        self.mod_c.remote_repo_valid = True

        valid, return_message = self.mod_c.check_push_repo_to_remote_valid()
        comp_message = "Directory {dir:s} does not exist".format(dir=os.path.join("./", self.mod_c.disk_dir))

        self.assertFalse(valid)
        self.assertEqual(return_message, comp_message)

    @patch('dls_ade.new_module_creator.os.path.isdir', return_value=True)
    @patch('dls_ade.new_module_creator.vcs_git.is_git_root_dir', return_value=False)
    def test_given_module_folder_is_not_repo_then_flag_set_false_and_error_returned_is_correct(self, mock_is_git_root_dir, mock_is_dir):

        self.mod_c.remote_repo_valid = True

        valid, return_message = self.mod_c.check_push_repo_to_remote_valid()
        comp_message = "Directory {dir:s} is not a git repository. Unable to push to remote repository".format(dir=os.path.join("./", self.mod_c.disk_dir))

        self.assertFalse(valid)
        self.assertEqual(return_message, comp_message)

    @patch('dls_ade.new_module_creator.NewModuleCreator.get_remote_dir_list', return_value=['inrepo', 'inrepo', 'inrepo'])
    @patch('dls_ade.vcs_git.is_repo_path', return_value=True)
    @patch('dls_ade.new_module_creator.os.path.isdir', return_value=True)
    @patch('dls_ade.new_module_creator.vcs_git.is_git_root_dir', return_value=False)
    def test_given_module_folder_is_not_repo_and_remote_repo_false_then_flag_set_false_and_error_returned_is_correct(self, mock_is_git_root_dir, mock_is_dir, mock_is_repo_path, mock_get_remote_dir_list):

        repo_valid, repo_return_message = self.mod_c.check_remote_repo_valid()
        valid, return_message = self.mod_c.check_push_repo_to_remote_valid()
        comp_message = "Directory {dir:s} is not a git repository. Unable to push to remote repository".format(dir=os.path.join("./", self.mod_c.disk_dir))
        comp_message += "\nAND: " + repo_return_message

        print(comp_message)

        self.assertFalse(valid)
        self.assertEqual(return_message, comp_message)

    @patch('dls_ade.new_module_creator.os.path.isdir', return_value=True)
    @patch('dls_ade.new_module_creator.vcs_git.is_git_root_dir', return_value=False)
    def test_given_final_flag_is_false_then_returned_flag_and_object_flag_match(self, mock_is_git_root_dir, mock_is_dir):

        self.mod_c.remote_repo_valid = True

        valid, return_message = self.mod_c.check_push_repo_to_remote_valid()

        self.assertFalse(valid)
        self.assertEqual(valid, self.mod_c.push_repo_to_remote_valid)

    @patch('dls_ade.new_module_creator.os.path.isdir', return_value=True)
    @patch('dls_ade.new_module_creator.vcs_git.is_git_root_dir', return_value=True)
    def test_given_final_flag_is_true_then_returned_flag_and_object_flag_match(self, mock_is_git_root_dir, mock_is_dir):

        self.mod_c.remote_repo_valid = True
        valid, return_message = self.mod_c.check_push_repo_to_remote_valid()

        self.assertTrue(valid)
        self.assertEqual(valid, self.mod_c.push_repo_to_remote_valid)


class NewModuleCreatorCreateModuleTest(unittest.TestCase):

    def setUp(self):
        self.mod_c = new_c.NewModuleCreator("test_module", "test_area", os.getcwd())

    @patch('dls_ade.new_module_creator.NewModuleCreator.check_create_module_valid', return_value=(True, ""))
    @patch('dls_ade.new_module_creator.os.chdir')
    @patch('dls_ade.new_module_creator.NewModuleCreator._create_files')
    def test_given_create_module_valid_true_then_create_files_called(self, mock_create_files, mock_chdir, mock_check_valid):

        self.mod_c.create_module_valid = True

        chdir_call_list = []  # Using call list to aid readability

        print_mock = MagicMock()

        with patch.object(builtins, 'print', print_mock):
            self.mod_c.create_module()

        print_mock.assert_called_once_with("Making clean directory structure for " + self.mod_c.disk_dir)

        chdir_call_list.append(call(os.path.join(self.mod_c.cwd, self.mod_c.disk_dir)))
        mock_create_files.assert_called_with()
        chdir_call_list.append(call(self.mod_c.cwd))

        call(os.path.join(self.mod_c.cwd, self.mod_c.disk_dir))
        mock_chdir.assert_has_calls(chdir_call_list)

    @patch('dls_ade.new_module_creator.NewModuleCreator.check_create_module_valid', return_value=(False, "return_message"))
    @patch('dls_ade.new_module_creator.os.chdir')
    @patch('dls_ade.new_module_creator.NewModuleCreator._create_files')
    def test_given_create_module_valid_false_then_exception_raised_with_correct_message(self, mock_create_files, mock_chdir, mock_check_valid):

        self.mod_c.create_module_valid = False

        with self.assertRaises(Exception) as e:
            self.mod_c.create_module()

        self.assertEqual(str(e.exception), "return_message")

    @patch('dls_ade.new_module_creator.NewModuleCreator.check_create_module_valid', return_value=(True, ""))
    @patch('dls_ade.new_module_creator.os.chdir')
    @patch('dls_ade.new_module_creator.NewModuleCreator._create_files')
    def test_given_create_module_valid_original_false_but_check_function_true_then_create_files_called(self, mock_create_files, mock_chdir, mock_check_valid):

        self.mod_c.create_module_valid = False

        chdir_call_list = []  # Using call list to aid readability

        print_mock = MagicMock()

        with patch.object(builtins, 'print', print_mock):
            self.mod_c.create_module()

        print_mock.assert_called_once_with("Making clean directory structure for " + self.mod_c.disk_dir)
        chdir_call_list.append(call(os.path.join(self.mod_c.cwd, self.mod_c.disk_dir)))
        mock_create_files.assert_called_once_with()
        chdir_call_list.append(call(self.mod_c.cwd))

        call(os.path.join(self.mod_c.cwd, self.mod_c.disk_dir))
        mock_chdir.assert_has_calls(chdir_call_list)


class NewModuleCreatorCreateFilesTest(unittest.TestCase):

    def setUp(self):
        self.mod_c = new_c.NewModuleCreator("test_module", "test_area", os.getcwd())

    @patch('dls_ade.new_module_creator.NewModuleCreator.create_files_from_template_dict')
    def test_create_files_from_template_called(self, mock_create_files_from_template):

        self.mod_c._create_files()

        mock_create_files_from_template.assert_called_once_with()

class NewModuleCreatorCreateFilesFromTemplateDictTest(unittest.TestCase):

    def setUp(self):

        self.patch_isdir = patch('dls_ade.new_module_creator.os.path.isdir')
        self.patch_makedirs = patch('dls_ade.new_module_creator.os.makedirs')
        self.addCleanup(self.patch_isdir.stop)
        self.addCleanup(self.patch_makedirs.stop)
        self.mock_isdir = self.patch_isdir.start()
        self.mock_makedirs = self.patch_makedirs.start()

        self.mod_c = new_c.NewModuleCreator("test_module", "test_area", os.getcwd())
        self.mod_c.template_args = {"arg1": "argument_1", "arg2": "argument_2"}
        self.open_mock = mock_open()  # mock_open is function designed to help mock the 'open' built-in function

    def test_given_folder_name_in_template_files_then_exception_raised_with_correct_message(self): #, mock_makedirs, mock_isdir):

        self.mock_isdir.return_value = False

        self.mod_c.template_files = {"folder_name/": "Written contents"}

        with patch.object(builtins, 'open', self.open_mock):  # This is to prevent accidental file creation
            with self.assertRaises(Exception):
                self.mod_c.create_files_from_template_dict()

        self.assertFalse(self.open_mock.called)
        file_handle_mock = self.open_mock()
        self.assertFalse(file_handle_mock.write.called)

    def test_given_single_file_then_file_created_and_correctly_written_to(self):

        self.mod_c.template_files = {"file1.txt": "Written contents"}

        with patch.object(builtins, 'open', self.open_mock):
            self.mod_c.create_files_from_template_dict()

        self.open_mock.assert_called_once_with("file1.txt", "w")

        file_handle_mock = self.open_mock()
        file_handle_mock.write.assert_any_call("Written contents")

    def test_given_single_file_in_folder_that_does_not_exist_then_folder_and_file_created_and_file_correctly_written_to(self):

        self.mock_isdir.return_value = False

        self.mod_c.template_files = {"test_folder/file1.txt": "Written contents"}

        with patch.object(builtins, 'open', self.open_mock):
            self.mod_c.create_files_from_template_dict()

        self.mock_makedirs.asset_called_once_with("test_folder")
        self.open_mock.assert_called_once_with("test_folder/file1.txt", "w")

        file_handle_mock = self.open_mock()
        file_handle_mock.write.assert_any_call("Written contents")

    def test_given_single_file_in_folder_that_exists_then_folder_not_created_but_file_created_and_file_correctly_written_to(self):

        self.mock_isdir.return_value = True

        self.mod_c.template_files = {"test_folder/file1.txt": "Written contents"}

        with patch.object(builtins, 'open', self.open_mock):
            self.mod_c.create_files_from_template_dict()

        self.assertFalse(self.mock_makedirs.called)
        self.open_mock.assert_called_once_with("test_folder/file1.txt", "w")

        file_handle_mock = self.open_mock()
        file_handle_mock.write.assert_any_call("Written contents")

    def test_given_two_files_in_separate_folders_then_both_folders_created_and_files_correctly_written_to(self):

        self.mock_isdir.return_value = False

        self.mod_c.template_files = {"test_folder1/file1.txt": "Written contents1", "test_folder2/file2.txt": "Written contents2"}

        with patch.object(builtins, 'open', self.open_mock):
            self.mod_c.create_files_from_template_dict()

        self.mock_makedirs.assert_has_calls([call("test_folder1"), call("test_folder2")], any_order=True)

        self.open_mock.assert_has_calls([call("test_folder1/file1.txt", "w"), call("test_folder2/file2.txt", "w")], any_order=True)

        file_handle_mock = self.open_mock()
        file_handle_mock.write.assert_has_calls([call("Written contents1"), call("Written contents2")], any_order=True)

    def test_given_two_files_in_same_folder_then_both_created_and_written_to_but_directory_only_made_once(self):

        self.mock_isdir.side_effect = [False, True]

        self.mod_c.template_files = {"test_folder/file1.txt": "Written contents1", "test_folder/file2.txt": "Written contents2"}

        with patch.object(builtins, 'open', self.open_mock):
            self.mod_c.create_files_from_template_dict()

        self.mock_makedirs.assert_called_once_with("test_folder")

        self.open_mock.assert_has_calls([call("test_folder/file1.txt", "w"), call("test_folder/file2.txt", "w")], any_order=True)

        file_handle_mock = self.open_mock()
        file_handle_mock.write.assert_has_calls([call("Written contents1"), call("Written contents2")], any_order=True)

    def test_given_args_and_template_then_arguments_are_inserted_correctly(self):

        self.mod_c.template_files = {"file1.txt": "{arg1:s} and {arg2:s}"}

        with patch.object(builtins, 'open', self.open_mock):
            self.mod_c.create_files_from_template_dict()

        self.open_mock.assert_called_once_with("file1.txt", "w")

        file_handle_mock = self.open_mock()
        file_handle_mock.write.assert_called_once_with("argument_1 and argument_2")

    def test_given_nested_directory_then_folder_and_file_both_created_and_file_correctly_written_to(self):

        self.mock_isdir.return_value = False

        self.mod_c.template_files = {"test_folder/another_folder/yet_another_folder/file.txt": "Written contents"}

        with patch.object(builtins, 'open', self.open_mock):
            self.mod_c.create_files_from_template_dict()

        self.mock_makedirs.assert_called_once_with("test_folder/another_folder/yet_another_folder")

        self.open_mock.assert_called_once_with("test_folder/another_folder/yet_another_folder/file.txt", "w")

        file_handle_mock = self.open_mock()
        file_handle_mock.write.assert_called_once_with("Written contents")


# TODO -----------------------------------------------------------------------------------------------------------------
class NewModuleCreatorAddContactTest(unittest.TestCase):
    pass
# TODO -----------------------------------------------------------------------------------------------------------------


class NewModuleCreatorPrintMessagesTest(unittest.TestCase):

    def test_given_function_called_then_message_printed_correctly(self):

        self.mod_c = new_c.NewModuleCreator("test_module", "test_area", os.getcwd())

        self.mod_c.message = "Test_Message"

        print_mock = MagicMock()

        with patch.object(builtins, 'print', print_mock):
            self.mod_c.print_messages()

        print_mock.assert_called_once_with("Test_Message")


class NewModuleCreatorInitStageAndCommitTest(unittest.TestCase):

    def setUp(self):
        self.mod_c = new_c.NewModuleCreator("test_module", "test_area", os.getcwd())

    @patch('dls_ade.new_module_creator.NewModuleCreator.check_create_local_repo_valid', return_value=(True, ""))
    @patch('dls_ade.new_module_creator.vcs_git.stage_all_files_and_commit')
    def test_given_create_local_repo_true_then_init_and_commit_called(self, mock_init_and_commit, mock_check_valid):

        self.mod_c.create_local_repo_valid = True

        self.mod_c.create_local_repo()

        mock_init_and_commit.assert_called_with(self.mod_c.disk_dir)

    @patch('dls_ade.new_module_creator.NewModuleCreator.check_create_local_repo_valid', return_value=(False, "return_message"))
    @patch('dls_ade.new_module_creator.vcs_git.stage_all_files_and_commit')
    def test_given_create_local_repo_valid_false_then_exception_raised_with_correct_message(self, mock_init_and_commit, mock_check_valid):
    
        self.mod_c.create_local_repo_valid = False
    
        with self.assertRaises(Exception) as e:
            self.mod_c.create_local_repo()
    
        self.assertEqual(str(e.exception), "return_message")
    
    @patch('dls_ade.new_module_creator.NewModuleCreator.check_create_local_repo_valid', return_value=(True, ""))
    @patch('dls_ade.new_module_creator.vcs_git.stage_all_files_and_commit')
    def test_given_create_local_repo_original_false_but_check_function_true_then_init_and_commit_called(self, mock_init_and_commit, mock_check_valid):

        self.mod_c.create_local_repo_valid = False

        self.mod_c.create_local_repo()

        mock_init_and_commit.assert_called_with(self.mod_c.disk_dir)


class NewModuleCreatorPushRepoToRemoteTest(unittest.TestCase):

    def setUp(self):
        self.mod_c = new_c.NewModuleCreator("test_module", "test_area", os.getcwd())

    @patch('dls_ade.new_module_creator.NewModuleCreator.check_push_repo_to_remote_valid', return_value=(True, ""))
    @patch('dls_ade.new_module_creator.vcs_git.create_new_remote_and_push')
    def test_given_push_repo_to_remote_valid_true_then_create_new_remote_and_push_called(self, mock_create_new_remote_and_push, mock_check_valid):

        self.mod_c.push_repo_to_remote_valid = True

        self.mod_c.push_repo_to_remote()

        mock_create_new_remote_and_push.assert_called_with(self.mod_c.area, self.mod_c.module_name, self.mod_c.disk_dir)

    @patch('dls_ade.new_module_creator.NewModuleCreator.check_push_repo_to_remote_valid', return_value=(False, "return_message"))
    @patch('dls_ade.new_module_creator.vcs_git.create_new_remote_and_push')
    def test_given_push_repo_to_remote_valid_false_then_exception_raised_with_correct_message(self, mock_create_new_remote_and_push, mock_check_valid):

        self.mod_c.push_repo_to_remote_valid = False

        with self.assertRaises(Exception) as e:
            self.mod_c.push_repo_to_remote()

        self.assertEqual(str(e.exception), "return_message")

    @patch('dls_ade.new_module_creator.NewModuleCreator.check_push_repo_to_remote_valid', return_value=(True, ""))
    @patch('dls_ade.new_module_creator.vcs_git.create_new_remote_and_push')
    def test_given_push_repo_to_remote_valid_original_false_but_check_function_true_then_create_new_remote_and_push_called(self, mock_create_new_remote_and_push, mock_check_valid):

        self.mod_c.push_repo_to_remote_valid = False

        self.mod_c.push_repo_to_remote()

        mock_create_new_remote_and_push.assert_called_with(self.mod_c.area, self.mod_c.module_name, self.mod_c.disk_dir)

# Add tests for all derived NewModuleCreator classes
