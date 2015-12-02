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

        mock_c = new_c.NewModuleCreator("test_module", "test_area", os.getcwd())

        self.assertEqual(mock_c.template_args, {'module': "test_module", 'getlogin': "my_login"})


class NewModuleCreatorCheckRemoteRepoTest(unittest.TestCase):

    @patch('dls_ade.new_module_creator.NewModuleCreator.get_remote_dir_list', return_value = ['inrepo', 'inrepo', 'inrepo'])
    @patch('dls_ade.vcs_git.is_repo_path', return_value = True)
    def test_given_dir_list_exists_then_remote_repo_valid_set_false(self, mock_is_repo, mock_get_dir_list):

        mock_c = new_c.NewModuleCreator("test_module", "test_area", os.getcwd())

        mock_c.check_remote_repo()

        self.assertFalse(mock_c.remote_repo_valid)

    @patch('dls_ade.new_module_creator.NewModuleCreator.get_remote_dir_list', return_value = ['notinrepo', 'notinrepo', 'notinrepo'])
    @patch('dls_ade.vcs_git.is_repo_path', return_value = False)
    def test_given_dir_list_does_not_exist_then_remote_repo_valid_set_true(self, mock_is_repo, mock_get_dir_list):

        mock_c = new_c.NewModuleCreator("test_module", "test_area", os.getcwd())

        mock_c.check_remote_repo()

        self.assertTrue(mock_c.remote_repo_valid)

    @patch('dls_ade.new_module_creator.NewModuleCreator.get_remote_dir_list', return_value = ['notinrepo', 'inrepo', 'notinrepo'])
    @patch('dls_ade.vcs_git.is_repo_path')
    def test_given_one_dir_does_exist_then_remote_repo_valid_set_false(self, mock_is_repo, mock_get_dir_list):

        mock_is_repo.side_effect = [False, True, False]  # return value iterates through this list

        mock_c = new_c.NewModuleCreator("test_module", "test_area", os.getcwd())

        mock_c.check_remote_repo()

        self.assertFalse(mock_c.remote_repo_valid)


class NewModuleCreatorGetRemoteDirListTest(unittest.TestCase):

    @patch('dls_ade.new_module_creator.pathf.vendorModule')
    @patch('dls_ade.new_module_creator.pathf.prodModule')
    def test_given_reasonable_args_then_correct_dir_list_returned(self, mock_prod, mock_vend):

        mock_c = new_c.NewModuleCreator("test_module", "test_area", os.getcwd())
        dir_list = mock_c.get_remote_dir_list()

        mock_prod.assert_called_once_with(mock_c.module_name, mock_c.area)
        mock_vend.assert_called_once_with(mock_c.module_name, mock_c.area)


class NewModuleCreatorCheckLocalRepoTest(unittest.TestCase):
    pass


class NewModuleCreatorCreateFilesTest(unittest.TestCase):
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
