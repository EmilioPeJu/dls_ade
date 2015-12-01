import unittest
import os

import new_module_creator as new_c
from dls_start_new_module import make_parser
from pkg_resources import require
require("mock")
from mock import patch, ANY, MagicMock, mock_open


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
            self.patch[method] = patch('new_module_creator.NewModule' + method)
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

        ioc_c_mock.assert_called_once_with(args.module_name, args.area, os.getcwd())

    def test_given_area_is_python_then_new_module_creator_python_returned(self):

        py_c_mock = self.mocks['CreatorPython']

        args = self.parser.parse_args("test_module -p".split())

        new_py_creator = new_c.get_new_module_creator(args)

        py_c_mock.assert_called_once_with(args.module_name, args.area, os.getcwd())

    def test_given_area_is_support_then_new_module_creator_support_returned(self):

        sup_c_mock = self.mocks['CreatorSupport']

        args = self.parser.parse_args("test_module".split())  # Area automatically support

        new_sup_creator = new_c.get_new_module_creator(args)

        sup_c_mock.assert_called_once_with(args.module_name, args.area, os.getcwd())

    def test_given_area_is_tools_then_new_module_creator_tools_returned(self):

        tools_c_mock = self.mocks['CreatorTools']

        args = self.parser.parse_args("test_module --area tools".split())  # Area automatically support

        new_tools_creator = new_c.get_new_module_creator(args)

        tools_c_mock.assert_called_once_with(args.module_name, args.area, os.getcwd())

    def test_given_area_is_ioc_and_tech_area_is_BL_slash_form_then_new_module_creator_ioc_bl_returned(self):

        iocbl_c_mock = self.mocks['CreatorIOCBL']

        args = self.parser.parse_args("test/BL -i".split())  # Area automatically support

        new_tools_creator = new_c.get_new_module_creator(args)

        iocbl_c_mock.assert_called_once_with(args.module_name, args.area, os.getcwd())

    # def test_given_area_is_ioc_and_tech_area_is_BL_dash_form_then_new_module_creator_ioc_bl_returned(self):
    #
    #     iocbl_c_mock = self.mocks['CreatorIOCBL']
    #
    #     args = self.parser.parse_args("test_module --area tools".split())  # Area automatically support
    #
    #     new_tools_creator = new_c.get_new_module_creator(args)
    #
    #     iocbl_c_mock.assert_called_once_with(args.module_name, args.area, os.getcwd())

    # TODO Test if area ioc and technical area is BL then BL returned


class NewModuleCreatorClassInitTest(unittest.TestCase):
    pass


class NewModuleCreatorCheckRemoteRepoTest(unittest.TestCase):
    pass


class NewModuleCreatorCheckLocalRepoTest(unittest.TestCase):
    pass


class NewModuleCreatorMessageGenerator(unittest.TestCase):
    pass


class NewModuleCreatorCreateFiles(unittest.TestCase):
    pass


class NewModuleCreatorCreateGitignore(unittest.TestCase):
    pass


class NewModuleCreatorAddContact(unittest.TestCase):
    pass


class NewModuleCreatorPrintMessages(unittest.TestCase):
    pass


class NewModuleCreatorStageAndCommit(unittest.TestCase):
    pass


class NewModuleCreatorPushRepoToRemote(unittest.TestCase):
    pass


# Add tests for all derived NewModuleCreator classes