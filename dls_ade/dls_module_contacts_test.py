#!/bin/env dls-python

from __future__ import print_function
from dls_ade import dls_module_contacts
import unittest
from mock import patch, MagicMock, mock_open, ANY
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

    def test_modules_argument_is_correctly_understood(self):
        args = self.parser.parse_args("a b c".split())
        self.assertEqual(args.modules, ["a", "b", "c"])

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

    def test_given_imp_not_contact_not_cc_then_no_error_raised(self):
        imp = "test_file"
        modules = "test_module"
        contact = ""
        cc = ""

        dls_module_contacts.check_parsed_args_compatible(imp, modules, contact, cc, self.parser)

        self.assertFalse(self.mock_error.call_count)

    def test_given_imp_contact_not_cc_then_error_raised(self):
        imp = "test_file"
        modules = "test_module"
        contact = "test_contact"
        cc = ""
        expected_error_message = "--import cannot be used with --contact or --cc"

        dls_module_contacts.check_parsed_args_compatible(imp, modules, contact, cc, self.parser)

        self.mock_error.assert_called_once_with(expected_error_message)

    def test_given_imp_not_contact_cc_then_error_raised(self):
        imp = "test_file"
        modules = "test_module"
        contact = ""
        cc = "test_cc"
        expected_error_message = "--import cannot be used with --contact or --cc"

        dls_module_contacts.check_parsed_args_compatible(imp, modules, contact, cc, self.parser)

        self.mock_error.assert_called_once_with(expected_error_message)

    def test_given_imp_contact_cc_then_error_raised(self):
        imp = "test_file"
        modules = "test"
        contact = "test_contact"
        cc = "test_cc"
        expected_error_message = "--import cannot be used with --contact or --cc"

        dls_module_contacts.check_parsed_args_compatible(imp, modules, contact, cc, self.parser)

        self.mock_error.assert_called_once_with(expected_error_message)

    def test_no_imp_contact_no_module_then_error(self):
        imp = ""
        modules = ""
        contact = "test_contact"
        cc = ""
        expected_error_message = "You cannot set all modules in an area to one contact/cc, enter a specific module."

        dls_module_contacts.check_parsed_args_compatible(imp, modules, contact, cc, self.parser)

        self.mock_error.assert_called_once_with(expected_error_message)

    def test_no_imp_cc_no_module_then_error(self):
        imp = ""
        modules = ""
        contact = ""
        cc = "test_cc"
        expected_error_message = "You cannot set all modules in an area to one contact/cc, enter a specific module."

        dls_module_contacts.check_parsed_args_compatible(imp, modules, contact, cc, self.parser)

        self.mock_error.assert_called_once_with(expected_error_message)

    def test_no_imp_cc_and_contact_no_module_then_error(self):
        imp = ''
        modules = ''
        contact = "test_contact"
        cc = "test_cc"
        expected_error_message = "You cannot set all modules in an area to one contact/cc, enter a specific module."

        dls_module_contacts.check_parsed_args_compatible(imp, modules, contact, cc, self.parser)

        self.mock_error.assert_called_once_with(expected_error_message)

    def test_no_imp_contact_module_then_no_error(self):
        imp = ""
        modules = "test_module"
        contact = "test_contact"
        cc = ""

        dls_module_contacts.check_parsed_args_compatible(imp, modules, contact, cc, self.parser)

        self.assertFalse(self.mock_error.call_count)

    def test_no_imp_cc_module_then_no_error(self):
        imp = ""
        modules = "test_module"
        contact = ""
        cc = "test_cc"

        dls_module_contacts.check_parsed_args_compatible(imp, modules, contact, cc, self.parser)

        self.assertFalse(self.mock_error.call_count)


class OutputContactInfoTest(unittest.TestCase):

    def setUp(self):
        self.args = MagicMock()

    @patch('dls_ade.dls_module_contacts.lookup_contact_name',
           side_effect=["test_contact_name", "test_cc_name"])
    @patch('dls_ade.vcs_git.git')
    def test_given_contacts_then_output_csv_format(self, _, _2):
        self.args.csv = True
        module = "test_module"
        contact = "test_contact"
        cc = "test_cc"

        output = dls_module_contacts.output_csv_format(contact, cc, module)

        self.assertEqual(output, "test_module,test_contact,test_contact_name,test_cc,test_cc_name")

    @patch('dls_ade.vcs_git.git')
    def test_given_unspecified_contacts_then_output_csv_format(self, _):
        self.args.csv = True
        module = "test_module"
        contact = "unspecified"
        cc = "unspecified"

        output = dls_module_contacts.output_csv_format(contact, cc, module)

        self.assertEqual(output, "test_module,unspecified,unspecified,unspecified,unspecified")


class ImportFromCSVTest(unittest.TestCase):

    @patch('dls_ade.dls_module_contacts.csv')
    def test_given_empty_file_then_error_raised(self, mock_csv):
        modules = []
        area = "test_area"
        imp = "test_file"
        expected_error_message = "CSV file is empty"
        mock_csv.reader.return_value = []

        try:
            with patch.object(builtins, 'open', mock_open(read_data="mock_read")):
                dls_module_contacts.import_from_csv(modules, area, imp)
        except Exception as error:
            self.assertEqual(str(error), expected_error_message)

    @patch('dls_ade.dls_module_contacts.csv')
    def test_given_title_module_no_contact_then_error_raised(self, mock_csv):
        modules = ["test_module"]
        area = "test_area"
        imp = "test_file"
        expected_error_message = "Module test_module has no corresponding contact in CSV file"
        mock_csv.reader.return_value = [["Module", "Contact", "Contact Name", "CC", "CC Name"], ["test_module"]]

        try:
            with patch.object(builtins, 'open', mock_open(read_data="mock_read")):
                dls_module_contacts.import_from_csv(modules, area, imp)
        except Exception as error:
            self.assertEqual(str(error), expected_error_message)

    @patch('dls_ade.dls_module_contacts.csv')
    def test_given_title_module_contact_then_no_error_raised(self, mock_csv):
        modules = ["test_module"]
        area = "test_area"
        imp = "test_file"
        mock_csv.reader.return_value = \
            [["Module", "Contact", "Contact Name", "CC", "CC Name"],
             ["test_module", "user1", "user1"]]

        with patch.object(builtins, 'open', mock_open(read_data="mock_read")):
            dls_module_contacts.import_from_csv(modules, area, imp)

    @patch('dls_ade.dls_module_contacts.csv')
    def test_given_title_module_contact_and_cc_then_no_error_raised(self, mock_csv):
        modules = ["test_module"]
        area = "test_area"
        imp = "test_file"
        mock_csv.reader.return_value = \
            [["Module", "Contact", "Contact Name", "CC", "CC Name"],
             ["test_module", "user1", "user1", "user2", "user2"]]

        with patch.object(builtins, 'open', mock_open(read_data="mock_read")):
            dls_module_contacts.import_from_csv(modules, area, imp)

    @patch('dls_ade.dls_module_contacts.csv')
    def test_given_title_module_contact_not_in_modules_then_error_raised(self, mock_csv):
        modules = ["test_module"]
        area = "test_area"
        imp = "test_file"
        expected_error_message = \
            "Module not_test_module not in " + area + " area"
        mock_csv.reader.return_value = \
            [["Module", "Contact", "Contact Name", "CC", "CC Name"], ["not_test_module", "user"]]

        try:
            with patch.object(builtins, 'open', mock_open(read_data="mock_read")):
                dls_module_contacts.import_from_csv(modules, area, imp)
        except Exception as error:
            self.assertEqual(str(error), expected_error_message)

    @patch('dls_ade.dls_module_contacts.csv')
    def test_given_title_module_contact_defined_twice_then_error_raised(self, mock_csv):
        modules = ["test_module"]
        area = "test_area"
        imp = "test_file"
        expected_error_message = \
            "Module test_module defined twice in CSV file"
        mock_csv.reader.return_value = \
            [["Module", "Contact", "Contact Name", "CC", "CC Name"],
             ["test_module", "user"], ["test_module", "other_user"]]

        try:
            with patch.object(builtins, 'open', mock_open(read_data="mock_read")):
                dls_module_contacts.import_from_csv(modules, area, imp)
        except Exception as error:
            self.assertEqual(str(error), expected_error_message)


class EditContactInfoTest(unittest.TestCase):

    @patch('dls_ade.dls_module_contacts.lookup_contact_name')
    def test_given_contact_then_set(self, _1):
        repo_inst = MagicMock()
        repo_inst.working_tree_dir = "test/test_module"
        repo_inst.git.check_attr.side_effect = ['', '']

        with patch.object(builtins, 'open', mock_open(read_data='test_data')):
            with open('test_file') as mock_file:
                dls_module_contacts.edit_contact_info(repo_inst, "user123", "user456")

        self.assertEqual(mock_file.write.call_args_list[0][0][0], "* module-contact=user123\n")
        self.assertEqual(mock_file.write.call_args_list[1][0][0], "* module-cc=user456\n")

    @patch('dls_ade.dls_module_contacts.lookup_contact_name')
    def test_given_unchanged_contacts_then_do_not_set(self, _1):
        repo_inst = MagicMock()
        repo_inst.working_tree_dir = "test/test_module"
        repo_inst.git.check_attr.side_effect = ['user123', 'user456']

        with patch.object(builtins, 'open', mock_open(read_data='test_data')):
            with open('test_file') as mock_file:
                dls_module_contacts.edit_contact_info(repo_inst, "user123", "user456")

        self.assertFalse(len(mock_file.write.call_args_list))

    @patch('dls_ade.dls_module_contacts.lookup_contact_name')
    def test_given_changed_and_empty_contact_then_do_not_set(self, _1):
        repo_inst = MagicMock()
        repo_inst.working_tree_dir = "test/test_module"
        repo_inst.git.check_attr.side_effect = ['user123', 'user456']

        with patch.object(builtins, 'open', mock_open(read_data='test_data')):
            with open('test_file') as mock_file:
                dls_module_contacts.edit_contact_info(repo_inst, "user789", "")

        self.assertEqual(mock_file.write.call_args_list[0][0][0], "* module-contact=user789\n")
        self.assertEqual(mock_file.write.call_args_list[1][0][0], "* module-cc=user456\n")

    @patch('dls_ade.dls_module_contacts.lookup_contact_name')
    def test_given_empty_and_changed_contact_then_change_one_keep_other(self, _1):
        repo_inst = MagicMock()
        repo_inst.working_tree_dir = "test/test_module"
        repo_inst.git.check_attr.side_effect = ['user123', 'user456']

        with patch.object(builtins, 'open', mock_open(read_data='test_data')):
            with open('test_file') as mock_file:
                dls_module_contacts.edit_contact_info(repo_inst, "", "user789")

        self.assertEqual(mock_file.write.call_args_list[0][0][0], "* module-contact=user123\n")
        self.assertEqual(mock_file.write.call_args_list[1][0][0], "* module-cc=user789\n")
