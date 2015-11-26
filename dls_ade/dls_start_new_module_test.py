#!/bin/env dls-python

import unittest
import dls_start_new_module
from pkg_resources import require
require("mock")
from mock import patch, ANY, MagicMock, mock_open
from new_module_templates import py_files, tools_files
import new_module_format_templates
import os

from sys import version_info
if version_info.major == 2:
    import __builtin__ as builtins  # Allows for Python 2/3 compatibility, 'builtins' is namespace for inbuilt functions
else:
    import builtins


class MakeFilesPythonTest(unittest.TestCase):

    def setUp(self):
        self.test_input = {"module": "test_module_name", "getlogin": "test_login_name"}

        self.open_mock = mock_open()  # mock_open is function designed to help mock the 'open' built-in function

    @patch('dls_start_new_module.os.mkdir')
    def test_opens_correct_file_and_writes_setup(self, mkdir_mock):

        module = self.test_input['module']
        getlogin = self.test_input['getlogin']

        mock_login = patch('dls_start_new_module.os.getlogin', return_value=getlogin)

        with patch.object(builtins, 'open', self.open_mock):
            with mock_login:
                dls_start_new_module.make_files_python(module)

        file_handle_mock = self.open_mock()  # Allows us to interrogate the 'write' function
        self.open_mock.assert_any_call("setup.py", "w")
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

    @patch('dls_start_new_module.os.mkdir')
    def test_opens_correct_file_and_writes_makefile(self, mkdir_mock):

        module = self.test_input['module']

        with patch.object(builtins, 'open', self.open_mock):
            dls_start_new_module.make_files_python(module)

        file_handle_mock = self.open_mock()
        self.open_mock.assert_any_call("Makefile", "w")
        file_handle_mock.write.assert_any_call(py_files['Makefile'] % module)

    @patch('dls_start_new_module.os.mkdir')
    def test_mkdir_module_called(self, mkdir_mock):

        module = self.test_input['module']

        with patch.object(builtins, 'open', self.open_mock):
            dls_start_new_module.make_files_python(module)

        mkdir_mock.assert_any_call(module)

    @patch('dls_start_new_module.os.mkdir')
    def test_opens_correct_file_and_writes_module_module_py(self, mkdir_mock):

        module = self.test_input['module']

        with patch.object(builtins, 'open', self.open_mock):
            dls_start_new_module.make_files_python(module)

        file_handle_mock = self.open_mock()
        self.open_mock.assert_any_call(os.path.join(module, module + ".py"), "w")
        file_handle_mock.write.assert_any_call(py_files['module/module.py'] % module)

    @patch('dls_start_new_module.os.mkdir')
    def test_opens_correct_file_and_writes_module_init_py(self, mkdir_mock):

        module = self.test_input['module']

        with patch.object(builtins, 'open', self.open_mock):
            dls_start_new_module.make_files_python(module)

        file_handle_mock = self.open_mock()
        self.open_mock.assert_any_call(os.path.join(module, "__init__.py"), "w")
        file_handle_mock.write.assert_any_call(py_files['module/__init__.py'])

    @patch('dls_start_new_module.os.mkdir')
    def test_mkdir_documentation_called(self, mkdir_mock):

        module = self.test_input['module']

        with patch.object(builtins, 'open', self.open_mock):
            dls_start_new_module.make_files_python(module)

        mkdir_mock.assert_any_call("documentation")

    @patch('dls_start_new_module.os.mkdir')
    def test_opens_correct_file_and_writes_documentation_makefile(self, mkdir_mock):

        module = self.test_input['module']

        with patch.object(builtins, 'open', self.open_mock):
            dls_start_new_module.make_files_python(module)

        file_handle_mock = self.open_mock()
        self.open_mock.assert_any_call("documentation/Makefile", "w")
        file_handle_mock.write.assert_any_call(py_files['documentation/Makefile'])

    @patch('dls_start_new_module.os.mkdir')
    def test_opens_correct_file_and_writes_documentation_index(self, mkdir_mock):

        module = self.test_input['module']

        with patch.object(builtins, 'open', self.open_mock):
            dls_start_new_module.make_files_python(module)

        file_handle_mock = self.open_mock()
        self.open_mock.assert_any_call("documentation/index.html", "w")
        file_handle_mock.write.assert_any_call(py_files['documentation/index.html'])

    @patch('dls_start_new_module.os.mkdir')
    def test_opens_correct_file_and_writes_documentation_config(self, mkdir_mock):

        module = self.test_input['module']

        with patch.object(builtins, 'open', self.open_mock):
            dls_start_new_module.make_files_python(module)

        file_handle_mock = self.open_mock()
        self.open_mock.assert_any_call("documentation/config.cfg", "w")
        file_handle_mock.write.assert_any_call(py_files['documentation/config.cfg'] % self.test_input)

    @patch('dls_start_new_module.os.mkdir')
    def test_opens_correct_file_and_writes_documentation_manual(self, mkdir_mock):

        module = self.test_input['module']

        with patch.object(builtins, 'open', self.open_mock):
            dls_start_new_module.make_files_python(module)

        file_handle_mock = self.open_mock()
        self.open_mock.assert_any_call("documentation/manual.src", "w")
        file_handle_mock.write.assert_any_call(py_files['documentation/manual.src'] % self.test_input)

        # TODO
        # Check if setup called on same number as write
        # Create test functions for all of the individual writes and directory creation
        # Add function to check total number of calls
        # Migrate all tests to compare overloaded % with .format
        # Migrate all actual code to implement .format


class MakeFilesToolsTest(unittest.TestCase):

    pass
