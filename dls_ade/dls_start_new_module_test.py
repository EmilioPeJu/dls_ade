#!/bin/env dls-python

import unittest
import dls_start_new_module
from pkg_resources import require
require("mock")
from mock import patch, ANY, MagicMock, mock_open
from new_module_templates import py_files, tools_files
import os
from argparse import _StoreTrueAction

from sys import version_info
if version_info.major == 2:
    import __builtin__ as builtins  # Allows for Python 2/3 compatibility, 'builtins' is namespace for inbuilt functions
else:
    import builtins


class MakeParserTest(unittest.TestCase):

    def setUp(self):
        self.parser = dls_start_new_module.make_parser()

    def test_module_name_has_correct_attributes(self):
        arguments = self.parser._positionals._actions[4]
        self.assertEqual(arguments.type, str)
        self.assertEqual(arguments.dest, 'module_name')

    def test_branch_argument_has_correct_attributes(self):
        option = self.parser._option_string_actions['-n']
        self.assertIsInstance(option, _StoreTrueAction)
        self.assertEqual(option.dest, "no_import")
        self.assertIn("--no_import", option.option_strings)

    def test_force_argument_has_correct_attributes(self):
        option = self.parser._option_string_actions['-f']
        self.assertIsInstance(option, _StoreTrueAction)
        self.assertEqual(option.dest, "fullname")
        self.assertIn("--fullname", option.option_strings)


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

        file_handle_mock.write.assert_any_call(py_files['setup.py'].format(**self.test_input))

    @patch('dls_start_new_module.os.mkdir')
    def test_opens_correct_file_and_writes_makefile(self, mkdir_mock):

        module = self.test_input['module']

        with patch.object(builtins, 'open', self.open_mock):
            dls_start_new_module.make_files_python(module)

        file_handle_mock = self.open_mock()
        self.open_mock.assert_any_call("Makefile", "w")

        file_handle_mock.write.assert_any_call(py_files['Makefile'].format(**self.test_input))

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

        file_handle_mock.write.assert_any_call(py_files['module/module.py'].format(**self.test_input))

    @patch('dls_start_new_module.os.mkdir')
    def test_opens_correct_file_and_writes_module_init_py(self, mkdir_mock):

        module = self.test_input['module']

        with patch.object(builtins, 'open', self.open_mock):
            dls_start_new_module.make_files_python(module)

        file_handle_mock = self.open_mock()
        self.open_mock.assert_any_call(os.path.join(module, "__init__.py"), "w")

        file_handle_mock.write.assert_any_call(py_files['module/__init__.py'].format(**self.test_input))

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

        file_handle_mock.write.assert_any_call(py_files['documentation/Makefile'].format(**self.test_input))

    @patch('dls_start_new_module.os.mkdir')
    def test_opens_correct_file_and_writes_documentation_index(self, mkdir_mock):

        module = self.test_input['module']

        with patch.object(builtins, 'open', self.open_mock):
            dls_start_new_module.make_files_python(module)

        file_handle_mock = self.open_mock()
        self.open_mock.assert_any_call("documentation/index.html", "w")

        file_handle_mock.write.assert_any_call(py_files['documentation/index.html'].format(**self.test_input))

    @patch('dls_start_new_module.os.mkdir')
    def test_opens_correct_file_and_writes_documentation_config(self, mkdir_mock):

        module = self.test_input['module']

        with patch.object(builtins, 'open', self.open_mock):
            dls_start_new_module.make_files_python(module)

        file_handle_mock = self.open_mock()
        self.open_mock.assert_any_call("documentation/config.cfg", "w")

        file_handle_mock.write.assert_any_call(py_files['documentation/config.cfg'].format(**self.test_input))

    @patch('dls_start_new_module.os.mkdir')
    def test_opens_correct_file_and_writes_documentation_manual(self, mkdir_mock):

        module = self.test_input['module']

        with patch.object(builtins, 'open', self.open_mock):
            dls_start_new_module.make_files_python(module)

        file_handle_mock = self.open_mock()
        self.open_mock.assert_any_call("documentation/manual.src", "w")

        file_handle_mock.write.assert_any_call(py_files['documentation/manual.src'].format(**self.test_input))

    @patch('dls_start_new_module.os.mkdir')
    def test_opens_correct_file_and_writes_gitignore(self, mkdir_mock):

        module = self.test_input['module']

        with patch.object(builtins, 'open', self.open_mock):
            dls_start_new_module.make_files_python(module)

        file_handle_mock = self.open_mock()
        self.open_mock.assert_any_call(".gitignore", "w")

        file_handle_mock.write.assert_any_call(py_files['.gitignore'].format(**self.test_input))


class MakeFilesToolsTest(unittest.TestCase):

    def setUp(self):
        self.test_input = {"module": "test_module_name"}

        self.open_mock = mock_open()  # mock_open is function designed to help mock the 'open' built-in function

    def test_opens_correct_file_and_writes_build(self):

        module = self.test_input['module']

        with patch.object(builtins, 'open', self.open_mock):
            dls_start_new_module.make_files_tools(module)

        file_handle_mock = self.open_mock()  # Allows us to interrogate the 'write' function
        self.open_mock.assert_any_call("build", "w")

        file_handle_mock.write.assert_any_call(tools_files['build'].format(**self.test_input))

    def test_correct_print_message(self):

        module = self.test_input['module']

        print_mock = MagicMock()

        with patch.object(builtins, 'open', self.open_mock):
            with patch.object(builtins, 'print', print_mock):
                dls_start_new_module.make_files_tools(module)

        print_mock.assert_called_once_with("\nPlease add your patch files to the {module:s} directory and edit "
              "{module:s}/build script appropriately".format(**self.test_input))


if __name__ == '__main__':

    # buffer option suppresses stdout generated from tested code
    unittest.main(buffer=True)
