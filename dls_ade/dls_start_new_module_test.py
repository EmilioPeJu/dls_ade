#!/bin/env dls-python

import unittest
import dls_start_new_module
from pkg_resources import require
require("mock")
from mock import patch, ANY, MagicMock, mock_open

from sys import version_info
if version_info.major == 2:
    import __builtin__ as builtins # Allows for Python 2/3 compatibility
else:
    import builtins


class MakeFilesPythonTest(unittest.TestCase):

    def test_setup_opens_correct_file(self):

        open_mock = mock_open() # Mocks the 'open' command

        with patch.object(builtins, 'open', open_mock):
            dls_start_new_module.make_files_python("test_module_name")

        open_mock.assert_called_once_with("setup.py", "w")

    @patch('dls_start_new_module.os.getlogin', return_value="TestLogin")
    def test_setup_prints_correctly(self, mock_login):

        open_mock = mock_open() # Mocks the 'open' command

        with patch.object(builtins, 'open', open_mock):
            dls_start_new_module.make_files_python("testmodulename")



class MakeFilesToolsTest(unittest.TestCase):

    pass