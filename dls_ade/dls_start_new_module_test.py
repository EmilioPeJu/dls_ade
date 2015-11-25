#!/bin/env dls-python

import unittest
import dls_start_new_module
from pkg_resources import require
require("mock")
from mock import patch, ANY, MagicMock, mock_open
from new_module_templates import py_files, tools_files

from sys import version_info
if version_info.major == 2:
    import __builtin__ as builtins  # Allows for Python 2/3 compatibility
else:
    import builtins


class MakeFilesPythonTest(unittest.TestCase):

    def setUp(self):
        self.test_input = {"module": "test_module_name", "getlogin": "test_login_name"}

    def test_setup_opens_correct_file(self):

        module = self.test_input['module']
        getlogin = self.test_input['getlogin']

        open_mock = mock_open()  # mock_open specifically designed to mock the 'open' function

        with patch.object(builtins, 'open', open_mock):  # 'builtins' is namespace for inbuilt functions
            dls_start_new_module.make_files_python(module)

        open_mock.assert_called_once_with("setup.py", "w")

    def test_setup_prints_correctly(self):

        module = self.test_input['module']
        getlogin = self.test_input['getlogin']

        mock_login = patch('dls_start_new_module.os.getlogin', return_value=self.test_input['getlogin'])

        open_mock = mock_open()
        file_handle_mock = open_mock()  # Allows us to mock the 'write' function

        with patch.object(builtins, 'open', open_mock):
            with mock_login:
                dls_start_new_module.make_files_python(module)

        file_handle_mock.write.assert_called_once_with(py_files['setup.py'] % (module, getlogin, getlogin, module, module, module))



class MakeFilesToolsTest(unittest.TestCase):

    pass