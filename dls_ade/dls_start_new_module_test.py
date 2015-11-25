#!/bin/env dls-python

import unittest
import dls_start_new_module
from pkg_resources import require
require("mock")
from mock import patch, ANY, MagicMock, mock_open
from new_module_templates import py_files, tools_files
import new_module_format_templates

from sys import version_info
if version_info.major == 2:
    import __builtin__ as builtins  # Allows for Python 2/3 compatibility
else:
    import builtins


class MakeFilesPythonTest(unittest.TestCase):

    def setUp(self):
        self.test_input = {"module": "test_module_name", "getlogin": "test_login_name"}

        self.open_mock = mock_open()

    def test_setup_opens_correct_file(self):

        with patch.object(builtins, 'open', self.open_mock):  # 'builtins' is namespace for inbuilt functions
            dls_start_new_module.make_files_python(self.test_input['module'])

        self.open_mock.assert_any_call("setup.py", "w")

    def test_setup_prints_correctly(self):

        module = self.test_input['module']
        getlogin = self.test_input['getlogin']

        mock_login = patch('dls_start_new_module.os.getlogin', return_value=self.test_input['getlogin'])

        file_handle_mock = self.open_mock()  # Allows us to interrogate the 'write' function

        with patch.object(builtins, 'open', self.open_mock):
            with mock_login:
                dls_start_new_module.make_files_python(module)

        file_handle_mock.write.assert_any_call(py_files['setup.py'] % (module, getlogin, getlogin, module, module, module))

        # mock_login = patch('dls_start_new_module.os.getlogin', return_value=self.test_input['getlogin'])
        #
        # file_handle_mock = self.open_mock()  # Allows us to interrogate the 'write' function
        #
        # with patch.object(builtins, 'open', self.open_mock):
        #     with mock_login:
        #         dls_start_new_module.make_files_python(self.test_input['module'])
        #
        # file_handle_mock.write.assert_called_once_with(new_module_format_templates.py_files['setup.py'].format(**self.test_input))



        # TODO
        # Create functions for all of the individual writes
        # Add function to check total number of calls
        # Migrate all tests to compare overloaded % with .format
        # Migrate all actual code to implement .format



class MakeFilesToolsTest(unittest.TestCase):

    pass