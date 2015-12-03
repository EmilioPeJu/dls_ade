import unittest
import os


import dls_ade.new_module_creator as new_c
from dls_ade.dls_start_new_module import make_parser
from pkg_resources import require
require("mock")
from mock import patch, ANY, MagicMock, mock_open
from new_module_templates import py_files, tools_files, default_files


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

        self.manager = MagicMock()

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

        message = self.mod_c.check_remote_repo_valid()
        comp_message = "The path {dir:s} already exists in subversion, cannot continue".format(dir="inrepo")

        self.assertFalse(self.mod_c.remote_repo_valid)
        self.assertEqual(message, comp_message)

    @patch('dls_ade.new_module_creator.NewModuleCreator.get_remote_dir_list', return_value=['notinrepo', 'notinrepo', 'notinrepo'])
    @patch('dls_ade.vcs_git.is_repo_path', return_value=False)
    def test_given_dir_list_does_not_exist_then_flag_set_true_and_error_returned_is_blank(self, mock_is_repo, mock_get_dir_list):

        message = self.mod_c.check_remote_repo_valid()
        comp_message = ""

        self.assertTrue(self.mod_c.remote_repo_valid)
        self.assertEqual(message, comp_message)

    @patch('dls_ade.new_module_creator.NewModuleCreator.get_remote_dir_list', return_value=['notinrepo', 'inrepo', 'notinrepo'])
    @patch('dls_ade.vcs_git.is_repo_path')
    def test_given_one_dir_does_exist_then_flag_set_false_and_error_returned_is_correct(self, mock_is_repo, mock_get_dir_list):

        mock_is_repo.side_effect = [False, True, False]  # return value iterates through this list

        message = self.mod_c.check_remote_repo_valid()
        comp_message = "The path {dir:s} already exists in subversion, cannot continue".format(dir="inrepo")

        self.assertFalse(self.mod_c.remote_repo_valid)
        self.assertEqual(message, comp_message)


class NewModuleCreatorGetRemoteDirListTest(unittest.TestCase):

    @patch('dls_ade.new_module_creator.pathf.vendorModule')
    @patch('dls_ade.new_module_creator.pathf.prodModule')
    def test_given_reasonable_args_then_correct_dir_list_returned(self, mock_prod, mock_vend):

        mod_c = new_c.NewModuleCreator("test_module", "test_area", os.getcwd())
        mod_c.get_remote_dir_list()

        mock_prod.assert_called_once_with(mod_c.module_name, mod_c.area)
        mock_vend.assert_called_once_with(mod_c.module_name, mod_c.area)


class NewModuleCreatorCheckCreateModuleValidTest(unittest.TestCase):

    def setUp(self):
        self.mod_c = new_c.NewModuleCreator("test_module", "test_area", os.getcwd())

    @patch('dls_ade.new_module_creator.os.path.isdir', return_value=False)
    @patch('dls_ade.new_module_creator.vcs_git.is_git_dir', return_value=False)
    def test_given_module_folder_does_not_exist_and_is_not_in_git_repo_then_flag_set_true_and_error_returned_is_blank(self, mock_is_git_dir, mock_is_dir):

        err_message = self.mod_c.check_create_module_valid()
        comp_message = ""

        self.assertTrue(self.mod_c.create_module_valid)
        self.assertEqual(err_message, comp_message)

    @patch('dls_ade.new_module_creator.os.path.isdir', return_value=True)
    @patch('dls_ade.new_module_creator.vcs_git.is_git_dir', return_value=False)
    def test_given_module_folder_exists_then_flag_set_false_and_error_returned_is_correct(self, mock_is_git_dir, mock_is_dir):

        err_message = self.mod_c.check_create_module_valid()
        comp_message = "Directory ./{dir:s} already exists, please move elsewhere and try again".format(dir=self.mod_c.disk_dir)

        self.assertFalse(self.mod_c.create_module_valid)
        self.assertEqual(err_message, comp_message)

    @patch('dls_ade.new_module_creator.os.path.isdir', return_value=False)
    @patch('dls_ade.new_module_creator.vcs_git.is_git_dir', return_value=True)
    def test_given_module_folder_is_in_git_repo_then_flag_set_false_and_error_returned_is_correct(self, mock_is_git_dir, mock_is_dir):

        err_message = self.mod_c.check_create_module_valid()
        comp_message = "Currently in a git repository, please move elsewhere and try again"

        self.assertFalse(self.mod_c.create_module_valid)
        self.assertEqual(err_message, comp_message)

    @patch('dls_ade.new_module_creator.os.path.isdir', return_value=True)
    @patch('dls_ade.new_module_creator.vcs_git.is_git_dir', return_value=True)
    def test_given_module_folder_exists_and_is_in_repo_then_flag_set_false(self, mock_is_git_dir, mock_is_dir):

        self.mod_c.check_create_module_valid()

        self.assertFalse(self.mod_c.create_module_valid)


class NewModuleCreatorCheckInitStageAndCommitValidTest(unittest.TestCase):

    def setUp(self):
        self.mod_c = new_c.NewModuleCreator("test_module", "test_area", os.getcwd())

    @patch('dls_ade.new_module_creator.os.path.isdir', return_value=True)
    @patch('dls_ade.new_module_creator.vcs_git.is_git_dir', return_value=False)
    def test_given_module_folder_exists_and_is_not_in_repo_then_flag_set_true_and_error_returned_is_blank(self, mock_is_git_dir, mock_is_dir):

        err_message = self.mod_c.check_init_stage_and_commit_valid()
        comp_message = ""

        self.assertTrue(self.mod_c.init_stage_and_commit_valid)
        self.assertEqual(err_message, comp_message)

    @patch('dls_ade.new_module_creator.os.path.isdir', return_value=False)
    @patch('dls_ade.new_module_creator.vcs_git.is_git_dir', return_value=False)
    def test_given_module_folder_does_not_exist_then_flag_set_false_and_error_returned_is_correct(self, mock_is_git_dir, mock_is_dir):

        err_message = self.mod_c.check_init_stage_and_commit_valid()
        comp_message = "Directory ./{dir:s} does not exist".format(dir=self.mod_c.disk_dir)

        self.assertFalse(self.mod_c.init_stage_and_commit_valid)
        self.assertEqual(err_message, comp_message)

    @patch('dls_ade.new_module_creator.os.path.isdir', return_value=True)
    @patch('dls_ade.new_module_creator.vcs_git.is_git_dir', return_value=True)
    def test_given_module_folder_is_in_repo_then_flag_set_false_and_error_returned_is_correct(self, mock_is_git_dir, mock_is_dir):

        err_message = self.mod_c.check_init_stage_and_commit_valid()
        comp_message = "Directory ./{dir:s} is inside git repository. Cannot initialise git repository".format(dir=self.mod_c.disk_dir)

        self.assertFalse(self.mod_c.init_stage_and_commit_valid)
        self.assertEqual(err_message, comp_message)


class NewModuleCreatorCheckPushRepoToRemoteValidTest(unittest.TestCase):

    def setUp(self):
        self.mod_c = new_c.NewModuleCreator("test_module", "test_area", os.getcwd())

    @patch('dls_ade.new_module_creator.os.path.isdir', return_value=True)
    @patch('dls_ade.new_module_creator.vcs_git.is_git_root_dir', return_value=True)
    def test_given_module_folder_exists_and_is_repo_and_remote_repo_valid_then_flag_set_true_and_error_returned_is_blank(self, mock_is_git_root_dir, mock_is_dir):

        self.mod_c.remote_repo_valid = True
        err_message = self.mod_c.check_push_repo_to_remote_valid()
        comp_message = ""

        self.assertTrue(self.mod_c.push_repo_to_remote_valid)
        self.assertEqual(err_message, comp_message)

    @patch('dls_ade.new_module_creator.NewModuleCreator.get_remote_dir_list', return_value=['notinrepo', 'notinrepo', 'notinrepo'])
    @patch('dls_ade.vcs_git.is_repo_path', return_value=False)
    @patch('dls_ade.new_module_creator.os.path.isdir', return_value=True)
    @patch('dls_ade.new_module_creator.vcs_git.is_git_root_dir', return_value=True)
    def test_given_remote_repo_valid_not_previously_set_but_true_then_flag_set_true_and_error_returned_is_blank(self,
                                                        mock_is_git_root_dir, mock_is_dir, mock_is_repo_path, mock_get_remote_dir_list):

        err_message = self.mod_c.check_push_repo_to_remote_valid()
        comp_message = ""

        self.assertTrue(self.mod_c.push_repo_to_remote_valid)
        self.assertEqual(err_message, comp_message)

    @patch('dls_ade.new_module_creator.NewModuleCreator.get_remote_dir_list', return_value=['inrepo', 'inrepo', 'inrepo'])
    @patch('dls_ade.vcs_git.is_repo_path', return_value=True)
    @patch('dls_ade.new_module_creator.os.path.isdir', return_value=True)
    @patch('dls_ade.new_module_creator.vcs_git.is_git_root_dir', return_value=True)
    def test_given_remote_repo_valid_false_then_flag_set_false_and_error_returned_is_correct(self, mock_is_git_root_dir, mock_is_dir, mock_is_repo_path, mock_get_remote_dir_list):

        err_message = self.mod_c.check_push_repo_to_remote_valid()
        comp_message = self.mod_c.check_remote_repo_valid()  # Don't want to constrain return message of check_remote_repo_valid()

        self.assertFalse(self.mod_c.push_repo_to_remote_valid)
        self.assertEqual(err_message, comp_message)

    @patch('dls_ade.new_module_creator.NewModuleCreator.get_remote_dir_list', return_value=['inrepo', 'inrepo', 'inrepo'])
    @patch('dls_ade.vcs_git.is_repo_path', return_value=True)
    @patch('dls_ade.new_module_creator.os.path.isdir', return_value=True)
    @patch('dls_ade.new_module_creator.vcs_git.is_git_root_dir', return_value=True)
    def test_given_remote_repo_valid_false_then_flag_set_false(self, mock_is_git_root_dir, mock_is_dir, mock_is_repo_path, mock_get_remote_dir_list):

        err_message = self.mod_c.check_push_repo_to_remote_valid()

        self.assertFalse(self.mod_c.push_repo_to_remote_valid)

    @patch('dls_ade.new_module_creator.os.path.isdir', return_value=False)
    @patch('dls_ade.new_module_creator.vcs_git.is_git_root_dir', return_value=False)
    def test_given_module_folder_does_not_exist_then_flag_set_false_and_error_returned_is_correct(self,
                                                        mock_is_git_root_dir, mock_is_dir):

        self.mod_c.remote_repo_valid = True

        err_message = self.mod_c.check_push_repo_to_remote_valid()
        comp_message = "Directory ./{dir:s} does not exist".format(dir=self.mod_c.disk_dir)

        self.assertFalse(self.mod_c.push_repo_to_remote_valid)
        self.assertEqual(err_message, comp_message)

    @patch('dls_ade.new_module_creator.os.path.isdir', return_value=True)
    @patch('dls_ade.new_module_creator.vcs_git.is_git_root_dir', return_value=False)
    def test_given_module_folder_is_not_repo_then_flag_set_false_and_error_returned_is_correct(self, mock_is_git_root_dir, mock_is_dir):

        self.mod_c.remote_repo_valid = True

        err_message = self.mod_c.check_push_repo_to_remote_valid()
        comp_message = "Directory ./{dir:s} is not git repository. Unable to push to remote repository".format(dir=self.mod_c.disk_dir)

        self.assertFalse(self.mod_c.push_repo_to_remote_valid)
        self.assertEqual(err_message, comp_message)


class NewModuleCreatorCreateModuleTest(unittest.TestCase):
    
    pass


class NewModuleCreatorCreateFilesTest(unittest.TestCase):
    pass


class NewModuleCreatorCreateFilesFromTemplateDictTest(unittest.TestCase):
    pass


class NewModuleCreatorAddContactTest(unittest.TestCase):
    pass


class NewModuleCreatorPrintMessagesTest(unittest.TestCase):
    pass


class NewModuleCreatorStageAndCommitTest(unittest.TestCase):
    pass


class NewModuleCreatorPushRepoToRemoteTest(unittest.TestCase):
    pass

# Add tests for all derived NewModuleCreator classes
