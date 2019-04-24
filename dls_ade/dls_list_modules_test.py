#!/bin/env dls-python

from sys import version_info
if version_info.major == 2:
    import __builtin__ as builtins  # Allows for Python 2/3 compatibility, 'builtins' is namespace for inbuilt functions
else:
    import builtins

import unittest
from mock import patch, MagicMock


p = patch('dls_ade.Server')
server_mock = MagicMock()
m = p.start()
m.return_value = server_mock
from dls_ade import dls_list_modules
p.stop()


class ParserTest(unittest.TestCase):

    def setUp(self):
        self.parser = dls_list_modules.make_parser()

    def test_parser_understands_domain(self):
        args = self.parser.parse_args("-i TS".split())
        self.assertEqual(args.area, "ioc")
        self.assertEqual(args.domain_name, "TS")


class PrintModuleListTest(unittest.TestCase):

    def setUp(self):
        self.server_mock = server_mock

    def tearDown(self):
        self.server_mock.reset_mock()

    def test_server_repo_list_called(self):
        source = "test/source"

        dls_list_modules.get_module_list(source)

        self.server_mock.get_server_repo_list.assert_called_once_with()

    def test_given_valid_source_then_list_of_modules(self):
        self.server_mock.get_server_repo_list.return_value =\
            ["test/source/module", "test/source2/module2"]

        source = "test/source"

        module_list = dls_list_modules.get_module_list(source)
        self.assertIsNotNone(module_list)
        self.assertListEqual(module_list, ['module'])

    def test_given_invalid_source_then_empty_list_of_modules(self):
        self.server_mock.get_server_repo_list.return_value = \
            ["test/not_source/module"]

        source = "test/source"

        module_list = dls_list_modules.get_module_list(source)
        self.assertIsNotNone(module_list)
        self.assertListEqual(module_list, [])
