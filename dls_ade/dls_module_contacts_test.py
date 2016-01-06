#!/bin/env dls-python

from dls_ade import dls_module_contacts
from argparse import _StoreAction
from argparse import _StoreTrueAction
import unittest
from pkg_resources import require
require("mock")
from mock import patch, MagicMock, mock_open
from argparse import _StoreAction
from argparse import _StoreTrueAction

from sys import version_info
if version_info.major == 2:
    import __builtin__ as builtins
else:
    import builtins


class MakeParserTest(unittest.TestCase):

    def setUp(self):
        self.parser = dls_module_contacts.make_parser()

    def test_modules_argument_has_correct_attributes(self):
        argument = self.parser._positionals._actions[4]
        self.assertEqual(argument.type, str)
        self.assertEqual(argument.dest, 'modules')
        self.assertEqual(argument.nargs, '*')

    def test_contact_argument_has_correct_attributes(self):
        option = self.parser._option_string_actions['-c']
        self.assertIsInstance(option, _StoreAction)
        self.assertEqual(option.type, str)
        self.assertEqual(option.dest, "contact")
        self.assertEqual(option.metavar, "FED_ID")
        self.assertIn("--contact", option.option_strings)

    def test_cc_argument_has_correct_attributes(self):
        option = self.parser._option_string_actions['-d']
        self.assertIsInstance(option, _StoreAction)
        self.assertEqual(option.type, str)
        self.assertEqual(option.dest, "cc")
        self.assertEqual(option.metavar, "FED_ID")
        self.assertIn("--cc", option.option_strings)

    def test_csv_argument_has_correct_attributes(self):
        option = self.parser._option_string_actions['-s']
        self.assertIsInstance(option, _StoreTrueAction)
        self.assertEqual(option.dest, "csv")
        self.assertIn("--csv", option.option_strings)

    def test_import_argument_has_correct_attributes(self):
        option = self.parser._option_string_actions['-m']
        self.assertIsInstance(option, _StoreAction)
        self.assertEqual(option.type, str)
        self.assertEqual(option.dest, "imp")
        self.assertEqual(option.metavar, "CSV_FILE")
        self.assertIn("--import", option.option_strings)


class CheckParsedArgsCompatibleTest(unittest.TestCase):

    def setUp(self):
        self.parser = dls_module_contacts.make_parser()
        parse_error_patch = patch('dls_ade.dls_module_contacts.ArgParser.error')
        self.addCleanup(parse_error_patch.stop)
        self.mock_error = parse_error_patch.start()

        self.args = MagicMock()
        self.args.imp = True
        self.args.contact = False
        self.args.cc = False

    def test_given_imp_not_contact_not_cc_then_no_error_raised(self):
        dls_module_contacts.check_parsed_args_compatible(self.parser, self.args)

        self.assertFalse(self.mock_error.call_count)

    def test_given_not_imp_contact_not_cc_then_no_error_raised(self):
        self.args.imp = False
        self.args.cc = False

        dls_module_contacts.check_parsed_args_compatible(self.parser, self.args)

        self.assertFalse(self.mock_error.call_count)

    def test_given_not_imp_not_contact_cc_then_no_error_raised(self):
        self.args.imp = False
        self.args.contact = False
        self.args.cc = True

        dls_module_contacts.check_parsed_args_compatible(self.parser, self.args)

        self.assertFalse(self.mock_error.call_count)

    def test_given_imp_contact_not_cc_then_error_raised(self):
        self.args.contact = True
        expected_error_message = "--import cannot be used with --contact or --cc"

        dls_module_contacts.check_parsed_args_compatible(self.parser, self.args)

        self.mock_error.assert_called_once_with(expected_error_message)

    def test_given_imp_not_contact_cc_then_error_raised(self):
        self.args.cc = True
        expected_error_message = "--import cannot be used with --contact or --cc"

        dls_module_contacts.check_parsed_args_compatible(self.parser, self.args)

        self.mock_error.assert_called_once_with(expected_error_message)

    def test_given_imp_contact_cc_then_error_raised(self):
        self.args.cc = True
        self.args.contact = True
        expected_error_message = "--import cannot be used with --contact or --cc"

        dls_module_contacts.check_parsed_args_compatible(self.parser, self.args)

        self.mock_error.assert_called_once_with(expected_error_message)


class GetModuleListTest(unittest.TestCase):

    def setUp(self):
        self.args = MagicMock()
        self.args.modules = ['module_1', 'module_2', 'module_3']

    def test_given_modules_then_returned(self):

        module_list = dls_module_contacts.get_module_list(self.args)

        self.assertEqual(module_list, self.args.modules)

    @patch('dls_ade.dls_module_contacts.get_repo_module_list',
           return_value=['repo_module_1', 'repo_module_2', 'repo_module_3'])
    def test_not_given_modules_then_repo_list_returned(self, _1):
        self.args.modules = []

        module_list = dls_module_contacts.get_module_list(self.args)

        self.assertEqual(module_list, ['repo_module_1', 'repo_module_2', 'repo_module_3'])


class LookupContactNameTest(unittest.TestCase):
    pass


class OutputContactInfoTest(unittest.TestCase):

    # >>> Don't what function is going to be yet.
    pass


class ImportFromCSVTest(unittest.TestCase):

    def setUp(self):
        self.parser = dls_module_contacts.make_parser()
        parse_error_patch = patch('dls_ade.dls_module_contacts.ArgParser.error')
        self.addCleanup(parse_error_patch.stop)
        self.mock_error = parse_error_patch.start()
        # >>> Make mock_parser raise exception?

        self.args = MagicMock()

    @patch('dls_ade.dls_module_contacts.csv')
    def test_given_empty_file_then_error_raised(self, mock_csv):
        modules = []
        expected_error_message = "CSV file is empty"
        mock_csv.reader.return_value = []

        with patch.object(builtins, 'open', mock_open(read_data="mock_read")):
            dls_module_contacts.import_from_csv(modules, self.args, self.parser)

        self.mock_error.assert_called_once_with(expected_error_message)

    @patch('dls_ade.dls_module_contacts.csv')
    def test_given_title_no_module_then_error_raised(self, mock_csv):
        modules = []
        expected_error_message = "Module table is empty"
        mock_csv.reader.return_value = \
            [["Module", "Contact", "Contact Name", "CC", "CC Name"]]

        with patch.object(builtins, 'open', mock_open(read_data="mock_read")):
            dls_module_contacts.import_from_csv(modules, self.args, self.parser)

        self.mock_error.assert_called_once_with(expected_error_message)

    @patch('dls_ade.dls_module_contacts.csv')
    def test_given_title_module_no_contact_then_error_raised(self, mock_csv):
        modules = ["test_module"]
        expected_error_message = \
            "Module test_module has no corresponding contact in CSV file"
        mock_csv.reader.return_value = \
            [["Module", "Contact", "Contact Name", "CC", "CC Name"], ["test_module"]]

        with patch.object(builtins, 'open', mock_open(read_data="mock_read")):
            dls_module_contacts.import_from_csv(modules, self.args, self.parser)

        self.mock_error.assert_called_once_with(expected_error_message)

    @patch('dls_ade.dls_module_contacts.csv')
    def test_given_title_module_contact_then_no_error_raised(self, mock_csv):
        modules = ["test_module"]
        mock_csv.reader.return_value = \
            [["Module", "Contact", "Contact Name", "CC", "CC Name"], ["test_module", "user"]]

        with patch.object(builtins, 'open', mock_open(read_data="mock_read")):
            dls_module_contacts.import_from_csv(modules, self.args, self.parser)

        self.assertFalse(self.mock_error.call_count)

    @patch('dls_ade.dls_module_contacts.csv')
    def test_given_title_module_contact_not_in_modules_then_error_raised(self, mock_csv):
        modules = ["test_module"]
        module = modules[0]
        self.args.area = "test_area"
        expected_error_message = \
            "Module not_test_module not in " + self.args.area + " area"
        mock_csv.reader.return_value = \
            [["Module", "Contact", "Contact Name", "CC", "CC Name"], ["not_test_module", "user"]]

        with patch.object(builtins, 'open', mock_open(read_data="mock_read")):
            dls_module_contacts.import_from_csv(modules, self.args, self.parser)

        self.mock_error.assert_called_once_with(expected_error_message)

    @patch('dls_ade.dls_module_contacts.csv')
    def test_given_title_module_contact_defined_twice_then_error_raised(self, mock_csv):
        modules = ["test_module"]
        self.args.area = "test_area"
        expected_error_message = \
            "Module test_module defined twice"
        mock_csv.reader.return_value = \
            [["Module", "Contact", "Contact Name", "CC", "CC Name"],
             ["test_module", "user"], ["test_module", "other_user"]]

        with patch.object(builtins, 'open', mock_open(read_data="mock_read")):
            dls_module_contacts.import_from_csv(modules, self.args, self.parser)

        self.mock_error.assert_called_once_with(expected_error_message)


class EditContactInfoTest(unittest.TestCase):

    def test_given_contact_then_set(self):
        pass
        # repo_inst = MagicMock()
        #
        # with patch.object(builtins, 'open') as mock_file:
        #     dls_module_contacts.edit_contact_info("user123", "user456", "test_module", repo_inst)
        #     output = mock_file.read()
        #
        # self.assertEqual(output, "* module-contact=" + "user123\n" + "* module-cc=user456/n")
