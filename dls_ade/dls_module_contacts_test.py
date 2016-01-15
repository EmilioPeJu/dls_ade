#!/bin/env dls-python

from __future__ import print_function
from dls_ade import dls_module_contacts
from argparse import _StoreAction
from argparse import _StoreTrueAction
import unittest
from pkg_resources import require
require("mock")
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

    def test_given_imp_not_contact_not_cc_then_no_error_raised(self):
        imp = True
        contact = False
        cc = False

        dls_module_contacts.check_parsed_args_compatible(imp, contact, cc)

    def test_given_not_imp_contact_not_cc_then_no_error_raised(self):
        imp = False
        contact = True
        cc = False

        dls_module_contacts.check_parsed_args_compatible(imp, contact, cc)

    def test_given_not_imp_not_contact_cc_then_no_error_raised(self):
        imp = False
        contact = False
        cc = True

        dls_module_contacts.check_parsed_args_compatible(imp, contact, cc)

    def test_given_imp_contact_not_cc_then_error_raised(self):
        imp = True
        contact = True
        cc = False
        expected_error_message = "--import cannot be used with --contact or --cc"

        try:
            dls_module_contacts.check_parsed_args_compatible(imp, contact, cc)
        except Exception as error:
            self.assertEqual(error.message, expected_error_message)

    def test_given_imp_not_contact_cc_then_error_raised(self):
        imp = True
        contact = False
        cc = True
        expected_error_message = "--import cannot be used with --contact or --cc"

        try:
            dls_module_contacts.check_parsed_args_compatible(imp, contact, cc)
        except Exception as error:
            self.assertEqual(error.message, expected_error_message)

    def test_given_imp_contact_cc_then_error_raised(self):
        imp = True
        contact = True
        cc = True
        expected_error_message = "--import cannot be used with --contact or --cc"

        try:
            dls_module_contacts.check_parsed_args_compatible(imp, contact, cc)
        except Exception as error:
            self.assertEqual(error.message, expected_error_message)


class GetAreaModuleListTest(unittest.TestCase):

    @patch('dls_ade.vcs_git.get_repository_list', return_value=['controls/support/ADCore', 'controls/support/ethercat', 'controls/support/vacuum'])
    def test_given_area_then_return_final_element_of_list(self, _1):
        area = "support"

        module_list = dls_module_contacts.get_area_module_list(area)

        self.assertEqual(module_list, ['ADCore', 'ethercat', 'vacuum'])


class LookupContactNameTest(unittest.TestCase):

    @patch('dls_ade.dls_module_contacts.ldap')
    def test_search_parameters_correct(self, mock_ldap):
        fed_id = "fed123"
        basedn = "dc=fed,dc=cclrc,dc=ac,dc=uk"
        search_filter = "(&(cn={}))".format(fed_id)
        search_attribute = ["givenName", "sn"]
        mock_ldap.SCOPE_SUBTREE.return_value = "test_scope_subtree"
        search_scope = mock_ldap.SCOPE_SUBTREE

        ldap_inst = MagicMock()
        mock_ldap.initialize.return_value = ldap_inst

        dls_module_contacts.lookup_contact_name(fed_id)

        mock_ldap.initialize.assert_called_once_with("ldap://altfed.cclrc.ac.uk")
        ldap_inst.search.assert_called_once_with(basedn, search_scope, search_filter, search_attribute)

    @patch('dls_ade.dls_module_contacts.ldap')
    def test_given_unsuccessful_fed_id_search_then_error_raised(self, mock_ldap):
        fed_id = "not_a_fed123"

        ldap_inst = MagicMock()
        mock_ldap.initialize.return_value = ldap_inst
        ldap_inst.result.return_value = \
            (115, [(None, ['ldap://res02.fed.cclrc.ac.uk/DC=res02,DC=fed,DC=cclrc,DC=ac,DC=uk'])])

        with self.assertRaises(Exception):
            dls_module_contacts.lookup_contact_name(fed_id)

    @patch('dls_ade.dls_module_contacts.ldap')
    def test_given_successful_fed_id_search_then_no_error_raised(self, mock_ldap):
        fed_id = "fed123"

        ldap_inst = MagicMock()
        mock_ldap.initialize.return_value = ldap_inst
        ldap_inst.result.return_value = \
            (100, [('CN=<FED-ID>,OU=DLS,DC=fed,DC=cclrc,DC=ac,DC=uk',
                    {'givenName': ['<FirstName>'], 'sn': ['<Surname>']})])

        contact_name = dls_module_contacts.lookup_contact_name(fed_id)

        self.assertEqual(contact_name, "<FirstName> <Surname>")


class OutputContactInfoTest(unittest.TestCase):

    def setUp(self):
        self.args = MagicMock()

    @patch('dls_ade.dls_module_contacts.lookup_contact_name', side_effect=["test_contact_name", "test_cc_name"])
    @patch('dls_ade.vcs_git.git')
    @patch('dls_ade.vcs_git.clone')
    def test_given_contacts_then_print_csv_format(self, mock_clone, mock_git, _2):
        self.args.csv = True
        module = "test_module"
        contact = "test_contact"
        cc = "test_cc"

        with patch.object(builtins, 'print') as mock_print:
            dls_module_contacts.output_csv_format(contact, cc, module)

        call_args = mock_print.call_args_list
        self.assertEqual(call_args[0][0][0], "test_module,test_contact,test_contact_name,test_cc,test_cc_name")


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
            self.assertEqual(error.message, expected_error_message)

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
            self.assertEqual(error.message, expected_error_message)

    @patch('dls_ade.dls_module_contacts.csv')
    def test_given_title_module_contact_then_no_error_raised(self, mock_csv):
        modules = ["test_module"]
        area = "test_area"
        imp = "test_file"
        mock_csv.reader.return_value = \
            [["Module", "Contact", "Contact Name", "CC", "CC Name"], ["test_module", "user"]]

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
            self.assertEqual(error.message, expected_error_message)

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
            self.assertEqual(error.message, expected_error_message)


class EditContactInfoTest(unittest.TestCase):

    @patch('dls_ade.dls_module_contacts.lookup_contact_name')
    def test_given_contact_then_set(self, _1):
        repo_inst = MagicMock()
        repo_inst.working_tree_dir.return_value = "test/test_module"

        with patch.object(builtins, 'open', mock_open(read_data='test_data')):
            with open('test_file') as mock_file:
                dls_module_contacts.edit_contact_info(repo_inst, "user123", "user456")

        self.assertEqual(mock_file.write.call_args_list[0][0][0], "* module-contact=user123\n")
        self.assertEqual(mock_file.write.call_args_list[1][0][0], "* module-cc=user456\n")
