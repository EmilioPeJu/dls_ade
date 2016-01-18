#!/bin/env dls-python

import unittest
from dls_ade import dls_logs_since_release
import logging

from pkg_resources import require
require("mock")
from mock import patch, MagicMock, ANY
from argparse import _StoreAction
from argparse import _StoreTrueAction


class MakeParserTest(unittest.TestCase):

    def setUp(self):
        self.parser = dls_logs_since_release.make_parser()

    def test_module_name_has_correct_attributes(self):
        arguments = self.parser._positionals._actions[4]
        self.assertEqual(arguments.type, str)
        self.assertEqual(arguments.dest, 'module_name')

    def test_earlier_argument_has_correct_attributes(self):
        arguments = self.parser._positionals._actions[5]
        self.assertEqual(arguments.type, str)
        self.assertEqual(arguments.dest, 'releases')

    def test_verbose_argument_has_correct_attributes(self):
        option = self.parser._option_string_actions['-v']
        self.assertIsInstance(option, _StoreTrueAction)
        self.assertEqual(option.dest, "verbose")
        self.assertIn("--verbose", option.option_strings)

    def test_raw_argument_has_correct_attributes(self):
        option = self.parser._option_string_actions['-r']
        self.assertIsInstance(option, _StoreTrueAction)
        self.assertEqual(option.dest, "raw")
        self.assertIn("--raw", option.option_strings)


class ColourTest(unittest.TestCase):

    def test_given_word_and_raw_then_return_word(self):
        word = "test_word"
        col = "test_col"

        raw = True

        return_value = dls_logs_since_release.colour(word, col, raw)

        self.assertEqual(return_value, word)

    def test_given_word_and_not_raw_then_return_formatted_word(self):
        word = "test_word"
        col = 5
        expected_return_value = "\x1b[" + str(col) + "m" + str(word) + "\x1b[0m"

        raw = False

        return_value = dls_logs_since_release.colour(word, col, raw)

        self.assertEqual(return_value, expected_return_value)


class CreateReleaseListTest(unittest.TestCase):

    def test_given_repo_with_tags_then_listed(self):

        repo_inst = MagicMock()
        dls_logs_since_release.vcs_git.git.repo = repo_inst
        tag_inst_1 = MagicMock()
        tag_inst_1.name = '1-0'
        tag_inst_2 = MagicMock()
        tag_inst_2.name = '2-0'
        tag_inst_3 = MagicMock()
        tag_inst_3.name = '2-1'

        repo_inst.tags = [tag_inst_1, tag_inst_2, tag_inst_3]

        releases = dls_logs_since_release.create_release_list(repo_inst)

        self.assertEqual(releases, ['1-0', '2-0', '2-1'])

    def test_given_repo_with_no_tags_then_empty_list_returned(self):
        repo_inst = MagicMock()
        dls_logs_since_release.vcs_git.git.repo = repo_inst

        repo_inst.tags = []

        releases = dls_logs_since_release.create_release_list(repo_inst)

        self.assertFalse(releases)


class GetFileChangesTest(unittest.TestCase):

    def setUp(self):
        self.diff_inst = MagicMock()
        self.commit_inst_1 = MagicMock()
        self.commit_inst_1.diff.return_value = [self.diff_inst]
        self.commit_inst_2 = MagicMock()
        self.diff_inst.new_file = False
        self.diff_inst.deleted_file = False
        self.diff_inst.renamed = False

    def test_no_diff_then_return_empty_list(self):
        self.diff_inst.a_blob = False
        self.diff_inst.b_blob = False

        diff = dls_logs_since_release.get_file_changes(self.commit_inst_1, self.commit_inst_2)

        self.assertFalse(diff)

    def test_new_file_then_return_A(self):
        self.diff_inst.new_file = True
        self.diff_inst.b_blob.path = "new_file"

        diffs = dls_logs_since_release.get_file_changes(self.commit_inst_1, self.commit_inst_2)

        self.assertEqual(diffs, ['A     new_file\n'])

    def test_modified_file_then_return_M(self):
        self.diff_inst.b_blob.path = "old_file"

        diffs = dls_logs_since_release.get_file_changes(self.commit_inst_1, self.commit_inst_2)

        self.assertEqual(diffs, ['M     old_file\n'])

    def test_deleted_file_then_return_D(self):
        self.diff_inst.a_blob.path = "old_file"
        self.diff_inst.b_blob = False
        self.diff_inst.deleted_file = True

        diffs = dls_logs_since_release.get_file_changes(self.commit_inst_1, self.commit_inst_2)

        self.assertEqual(diffs, ['D     old_file\n'])

    def test_renamed_file_then_return_renamed(self):
        self.diff_inst.a_blob.path = "old_file"
        self.diff_inst.b_blob.path = "new_file"
        self.diff_inst.deleted_file = True
        self.diff_inst.new_file = True
        self.diff_inst.renamed = True

        diffs = dls_logs_since_release.get_file_changes(self.commit_inst_1, self.commit_inst_2)

        self.assertEqual(diffs, ['A     new_file (Renamed)\n', 'D     old_file (Renamed)\n'])


class FormatMessageWidthTest(unittest.TestCase):

    def test_given_length_OK_then_returned_as_list(self):
        message = "Test commit message"
        max_len = 20

        formatted_message = dls_logs_since_release.format_message_width(message, max_len)

        self.assertEqual(formatted_message, [message])

    def test_given_line_too_long_then_formatted_without_space(self):
        message = "Test commit message that is too long"
        max_len = 20

        formatted_message = dls_logs_since_release.format_message_width(message, max_len)

        self.assertEqual(formatted_message, ["Test commit message", "that is too long"])

    def test_given_list_length_OK_then_returned(self):
        message = ["Test commit message"]
        max_len = 20

        formatted_message = dls_logs_since_release.format_message_width(message, max_len)

        self.assertEqual(formatted_message, message)

    def test_given_list_too_long_then_formatted_without_space(self):
        message = ["Test commit message that is too long"]
        max_len = 20

        formatted_message = dls_logs_since_release.format_message_width(message, max_len)

        self.assertEqual(formatted_message, ["Test commit message", "that is too long"])

    def test_given_line_too_long_no_spaces_then_formatted_with_no_removal(self):
        message = "/dls_sw/prod/R3.14.11/support/"
        max_len = 20

        formatted_message = dls_logs_since_release.format_message_width(message, max_len)

        self.assertEqual(formatted_message, ["/dls_sw/prod/R3.14.1", "1/support/"])

    def test_given_list_too_long_no_spaces_then_formatted_with_no_removal(self):
        message = ["/dls_sw/prod/R3.14.11/support/"]
        max_len = 20

        formatted_message = dls_logs_since_release.format_message_width(message, max_len)

        self.assertEqual(formatted_message, ["/dls_sw/prod/R3.14.1", "1/support/"])
