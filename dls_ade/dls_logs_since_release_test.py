#!/bin/env dls-python

import unittest
from dls_ade import dls_logs_since_release
from mock import patch, MagicMock, ANY
from argparse import _StoreTrueAction


class MakeParserTest(unittest.TestCase):

    def setUp(self):
        self.parser = dls_logs_since_release.make_parser()

    @patch('dls_ade.dls_changes_since_release.ArgParser.add_module_name_arg')
    def test_module_name_set(self, parser_mock):

        dls_logs_since_release.make_parser()

        parser_mock.assert_called_once_with()

    def test_earlier_argument_has_correct_attributes(self):
        args = self.parser.parse_args("module1 -e 0-1".split())
        self.assertEqual(args.module_name, "module1")
        self.assertEqual(args.earlier_release, "0-1")

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


class SetRawArgumentTest(unittest.TestCase):

    def test_given_raw_then_return_true(self):
        raw = True

        set_raw = dls_logs_since_release.set_raw_argument(raw)

        self.assertEqual(set_raw, True)

    @patch('dls_ade.dls_logs_since_release.sys.stdout.isatty', return_value=False)
    def test_given_not_raw_isatty_then_return_true(self, _1):
        raw = False

        set_raw = dls_logs_since_release.set_raw_argument(raw)

        self.assertTrue(set_raw)

    @patch('dls_ade.dls_logs_since_release.sys.stdout.isatty', return_value=True)
    @patch('dls_ade.dls_logs_since_release.os.getenv', return_value=None)
    def test_given_not_raw_term_none_then_return_true(self, _1, _2):
        raw = False

        set_raw = dls_logs_since_release.set_raw_argument(raw)

        self.assertTrue(set_raw)

    @patch('dls_ade.dls_logs_since_release.sys.stdout.isatty', return_value=True)
    @patch('dls_ade.dls_logs_since_release.os.getenv', return_value="dumb")
    def test_given_not_raw_term_dumb_then_return_true(self, _1, _2):
        raw = False

        set_raw = dls_logs_since_release.set_raw_argument(raw)

        self.assertTrue(set_raw)

    @patch('dls_ade.dls_logs_since_release.sys.stdout.isatty', return_value=True)
    @patch('dls_ade.dls_logs_since_release.os.getenv', return_value="emacs")
    def test_given_not_raw_environment_good_then_return_false(self, _1, _2):
        raw = False

        set_raw = dls_logs_since_release.set_raw_argument(raw)

        self.assertEqual(set_raw, False)


class CheckParsedArgumentsCompatible(unittest.TestCase):

    def setUp(self):
        self.parser = dls_logs_since_release.make_parser()
        parse_error_patch = patch('dls_ade.dls_logs_since_release.ArgParser.error')
        self.addCleanup(parse_error_patch.stop)
        self.mock_error = parse_error_patch.start()

    def test_given_releases_and_earlier_then_error(self):
        releases = ['4-4']
        earlier = '4-1'
        later = ''
        expected_error_message = "To specify both start and end point, use format " \
                                 "'ethercat 3-1 4-1', not -l and -e flags."

        dls_logs_since_release.check_parsed_args_compatible(releases, earlier, later, self.parser)

        self.mock_error.assert_called_once_with(expected_error_message)

    def test_given_releases_and_later_then_error(self):
        releases = ['4-1']
        earlier = ''
        later = '4-4'
        expected_error_message = "To specify both start and end point, use format " \
                                 "'ethercat 3-1 4-1', not -l and -e flags."

        dls_logs_since_release.check_parsed_args_compatible(releases, earlier, later, self.parser)

        self.mock_error.assert_called_once_with(expected_error_message)

    def test_given_earlier_and_later_then_error(self):
        releases = []
        earlier = '4-1'
        later = '4-4'
        expected_error_message = "To specify both start and end point, use format " \
                                 "'ethercat 3-1 4-1', not -l and -e flags."

        dls_logs_since_release.check_parsed_args_compatible(releases, earlier, later, self.parser)

        self.mock_error.assert_called_once_with(expected_error_message)

    def test_given_releases_then_no_error(self):
        releases = ['4-1', '4-4']
        earlier = ''
        later = ''

        dls_logs_since_release.check_parsed_args_compatible(releases, earlier, later, self.parser)

    def test_given_earlier_then_no_error(self):
        releases = []
        earlier = '4-1'
        later = ''

        dls_logs_since_release.check_parsed_args_compatible(releases, earlier, later, self.parser)

    def test_given_later_then_no_error(self):
        releases = []
        earlier = ''
        later = '4-4'

        dls_logs_since_release.check_parsed_args_compatible(releases, earlier, later, self.parser)


class CheckReleasesValidTest(unittest.TestCase):

    def setUp(self):
        self.parser = dls_logs_since_release.make_parser()
        parse_error_patch = patch('dls_ade.dls_logs_since_release.ArgParser.error')
        self.addCleanup(parse_error_patch.stop)
        self.mock_error = parse_error_patch.start()

    def test_given_releases_1_then_error(self):
        releases = ['4-1']
        expected_error_message = "To specify just start or just end point, use -e or -l flag."

        dls_logs_since_release.check_releases_valid(releases, self.parser)

        self.mock_error.assert_called_once_with(expected_error_message)

    def test_given_releases_more_than_2_then_error(self):
        releases = ['4-1', '4-4', '4-5']
        expected_error_message = "Only two releases can be specified (start and end point)"

        dls_logs_since_release.check_releases_valid(releases, self.parser)

        self.mock_error.assert_called_once_with(expected_error_message)

    @patch('dls_ade.dls_logs_since_release.environment.sortReleases', return_value=['4-1', '4-4'])
    def test_given_releases_wrong_order_then_error(self, _1):
        releases = ['4-4', '4-1']
        expected_error_message = "Input releases in correct order (<earlier> <later>)"

        dls_logs_since_release.check_releases_valid(releases, self.parser)

        self.mock_error.assert_called_once_with(expected_error_message)

    @patch('dls_ade.dls_logs_since_release.environment.sortReleases', return_value=['4-1', '4-4'])
    def test_given_releases_correct_order_then_error(self, _1):
        releases = ['4-1', '4-4']

        dls_logs_since_release.check_releases_valid(releases, self.parser)

    @patch('dls_ade.dls_logs_since_release.environment.sortReleases', return_value=['4-1', 'HEAD'])
    def test_given_releases_with_HEAD_then_no_error(self, _1):
        releases = ['4-1', 'HEAD']

        dls_logs_since_release.check_releases_valid(releases, self.parser)


class SetLogRangeTest(unittest.TestCase):

    def setUp(self):
        self.module = 'test_module'
        self.releases_list = ['1-0', '4-1', '4-4']

    def test_given_2_releases_then_set(self):
        releases = ['4-1', '4-4']
        earlier = ''
        later = ''

        start, end = dls_logs_since_release.set_log_range(self.module, releases, earlier, later, self.releases_list)

        self.assertEqual(start, '4-1')
        self.assertEqual(end, '4-4')

    def test_given_earlier_then_set_and_use_default_end(self):
        releases = []
        earlier = '4-1'
        later = ''

        start, end = dls_logs_since_release.set_log_range(self.module, releases, earlier, later, self.releases_list)

        self.assertEqual(start, '4-1')
        self.assertEqual(end, 'HEAD')

    def test_given_later_then_set_and_use_default_start(self):
        releases = []
        earlier = ''
        later = '4-4'

        start, end = dls_logs_since_release.set_log_range(self.module, releases, earlier, later, self.releases_list)

        self.assertEqual(start, '')
        self.assertEqual(end, '4-4')

    def test_given_none_then_use_defaults(self):
        releases = []
        earlier = ''
        later = ''

        start, end = dls_logs_since_release.set_log_range(self.module, releases, earlier, later, self.releases_list)

        self.assertEqual(start, '')
        self.assertEqual(end, 'HEAD')

    def test_given_invalid_start_then_error(self):
        releases = ['1-1', '4-4']
        earlier = ''
        later = ''
        expected_error_message = "Module " + self.module + " does not have a release 1-1"

        try:
            dls_logs_since_release.set_log_range(self.module, releases, earlier, later, self.releases_list)
        except ValueError as error:
            self.assertEqual(str(error), expected_error_message)

    def test_given_invalid_end_then_error(self):
        releases = ['1-0', '4-5']
        earlier = ''
        later = ''
        expected_error_message = "Module " + self.module + " does not have a release 4-5"

        try:
            dls_logs_since_release.set_log_range(self.module, releases, earlier, later, self.releases_list)
        except ValueError as error:
            self.assertEqual(str(error), expected_error_message)


class GetLogMessagesTest(unittest.TestCase):

    @patch('dls_ade.dls_logs_since_release.time.localtime', return_value=[2014, 8, 12, 13, 50, 10, 1, 224, 1])
    def test_extracts_commit_information(self, _1):

        repo_inst = MagicMock()
        commit = MagicMock()
        commit.authored_date = 1407847810
        commit.hexsha = 'e327e92'
        commit.author.name = 'Ronaldo Mercado'
        commit.summary = 'add on_sdo_message to process scanner MSG_SDO_READ messages'
        commit.message = 'add on_sdo_message to process scanner MSG_SDO_READ messages ' \
                         'make "sdos" public to allow checks on the sdo_observers list'
        commit_list = [commit]
        repo_inst.iter_commits.return_value = commit_list

        log_info = dls_logs_since_release.get_log_messages(repo_inst)

        self.assertEqual(log_info, {u'commit_objects': {'e327e92': commit}, u'max_author_length': 15,
                                    u'logs': [[1407847810, 'e327e92', 'Ronaldo Mercado',
                                               u'add on_sdo_message to process ' u'scanner MSG_SDO_READ messages',
                                               u'12/08/2014 13:50:10',
                                               u' make "sdos" public to allow checks on the sdo_observers list']]})


class GetTagsListTest(unittest.TestCase):

    def test_given_range_then_extract(self):
        start = '4-1'
        end = '4-2'
        last_release = '4-4'
        tag_1 = MagicMock()
        tag_1.name = '3-3'
        tag_2 = MagicMock()
        tag_2.name = '4-1'
        tag_3 = MagicMock()
        tag_3.name = '4-2'
        tag_4 = MagicMock()
        tag_4.name = '4-3'

        repo_inst = MagicMock()
        repo_inst.tags = [tag_1, tag_2, tag_3, tag_4]

        tags_range = dls_logs_since_release.get_tags_list(repo_inst, start, end, last_release)

        self.assertEqual(tags_range, [tag_2, tag_3])

    def test_given_range_with_HEAD_then_extract(self):
        start = '4-1'
        end = 'HEAD'
        last_release = '4-4'
        tag_1 = MagicMock()
        tag_1.name = '3-3'
        tag_2 = MagicMock()
        tag_2.name = '4-1'
        tag_3 = MagicMock()
        tag_3.name = '4-2'
        tag_4 = MagicMock()
        tag_4.name = '4-3'
        tag_5 = MagicMock()
        tag_5.name = '4-4'

        repo_inst = MagicMock()
        repo_inst.tags = [tag_1, tag_2, tag_3, tag_4, tag_5]

        tags_range = dls_logs_since_release.get_tags_list(repo_inst, start, end, last_release)

        self.assertEqual(tags_range, [tag_2, tag_3, tag_4, tag_5])


class GetTagMessagesTest(unittest.TestCase):

    @patch('dls_ade.dls_logs_since_release.time.localtime', return_value=[2014, 8, 12, 13, 50, 10, 1, 224, 1])
    def test_extracts_lightweight_tag_information(self, _1):
        self.maxDiff = None

        tag = MagicMock()
        commit = tag.commit
        tag.name = '4-1'
        tag.object.committed_date = 1407847810
        tag.object.hexsha = 'e327e92'
        tag.object.author.name = 'Ronaldo Mercado'
        tag.object.summary = 'add on_sdo_message to process scanner MSG_SDO_READ messages'
        tag.object.message = 'add on_sdo_message to process scanner MSG_SDO_READ messages ' \
                             'make "sdos" public to allow checks on the sdo_observers list'
        tag_list = [tag]

        log_info = {u'commit_objects': {}, u'max_author_length': 0, u'logs': []}
        log_info = dls_logs_since_release.get_tag_messages(tag_list, log_info)

        self.assertEqual(log_info, {u'commit_objects': {'e327e92': commit}, u'max_author_length': 15,
                                    u'logs': [[1407847810, 'e327e92', 'Ronaldo Mercado',
                                               u'add on_sdo_message to process ' u'scanner MSG_SDO_READ messages (RELEASE: 4-1)',
                                               u'12/08/2014 13:50:10',
                                               u' make "sdos" public to allow checks on the sdo_observers list']]})

    @patch('dls_ade.dls_logs_since_release.time.localtime', return_value=[2014, 8, 12, 13, 50, 10, 1, 224, 1])
    def test_extracts_annotated_tag_information(self, _1):
        self.maxDiff = None

        tag = MagicMock()
        del tag.object.author  # Make sure hasattr(mock, author) fails

        commit = tag.commit
        tag.name = '4-1'
        tag.object.object.committed_date = 1407847810
        tag.object.hexsha = 'e327e92'
        tag.object.object.author.name = 'Ronaldo Mercado'
        tag.object.object.summary = 'add on_sdo_message to process scanner MSG_SDO_READ messages'
        tag.object.object.message = 'add on_sdo_message to process scanner MSG_SDO_READ messages ' \
                                    'make "sdos" public to allow checks on the sdo_observers list'
        tag_list = [tag]

        log_info = {u'commit_objects': {}, u'max_author_length': 0, u'logs': []}
        log_info = dls_logs_since_release.get_tag_messages(tag_list, log_info)

        self.assertEqual(log_info, {u'commit_objects': {'e327e92': commit}, u'max_author_length': 15,
                                    u'logs': [[1407847810, 'e327e92', 'Ronaldo Mercado',
                                               u'add on_sdo_message to process ' u'scanner MSG_SDO_READ messages (RELEASE: 4-1)',
                                               u'12/08/2014 13:50:10',
                                               u' make "sdos" public to allow checks on the sdo_observers list']]})

    @patch('dls_ade.dls_logs_since_release.time.localtime', return_value=[2014, 8, 12, 13, 50, 10, 1, 224, 1])
    def test_given_tag_with_no_information_then_error(self, _1):
        expected_error_message = "Can't find tag info"

        tag = MagicMock()

        del tag.object.author  # Make sure hasattr(mock, author) fails
        del tag.object.object.author

        tag_list = [tag]
        log_info = {u'commit_objects': {}, u'max_author_length': 0, u'logs': []}

        try:
            dls_logs_since_release.get_tag_messages(tag_list, log_info)
        except ValueError as error:
            self.assertEqual(str(error), expected_error_message)


class ConvertTimeStamp(unittest.TestCase):

    def test_given_not_int_then_return_default(self):
        time_stamp = ''

        time_and_date = dls_logs_since_release.convert_time_stamp(time_stamp)

        self.assertEqual(time_and_date, 'no time/date')

    @patch('dls_ade.dls_logs_since_release.time.localtime',
           return_value=[])
    def test_given_time_returns_bad_entry_then_return_default(self, _1):
        time_stamp = 1407847810

        time_and_date = dls_logs_since_release.convert_time_stamp(time_stamp)

        self.assertEqual(time_and_date, 'no time/date')

    def test_given_good_entries_then_return(self):
        time_stamp = 1407847810

        time_and_date = dls_logs_since_release.convert_time_stamp(time_stamp)

        reg_ex = "\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}"
        self.assertRegexpMatches(time_and_date, reg_ex)


class FormatLogMessagesTest(unittest.TestCase):

    def setUp(self):
        commit = "dummy"
        self.log_info = {u'commit_objects': {'e327e92': commit}, u'max_author_length': 15,
                         u'logs': [[1407847810, 'e327e92', 'Ronaldo Mercado',
                                    u'add on_sdo_message to process ' u'scanner MSG_SDO_READ messages (4-1)',
                                    u'12/08/2014 13:50:10',
                                    u' make "sdos" public to allow checks on the sdo_observers list']]}
        self.log_info_verbose = {u'commit_objects': {'e327e92': commit}, u'max_author_length': 15,
                                 u'logs': [[1407847810, 'e327e92', 'Ronaldo Mercado',
                                            u'add on_sdo_message to process ' u'scanner MSG_SDO_READ messages (4-1)',
                                            u'12/08/2014 13:50:10',
                                            u' make "sdos" public to allow checks on the sdo_observers list'],
                                           [1407847810, 'e327e92', 'Ronaldo Mercado',
                                            u'add on_sdo_message to process ' u'scanner MSG_SDO_READ messages (4-1)',
                                            u'12/08/2014 13:50:10',
                                            u' make "sdos" public to allow checks on the sdo_observers list']]}

    def test_given_not_verbose_not_raw_then_format(self):

        log = dls_logs_since_release.format_log_messages(self.log_info, raw=False, verbose=False)

        self.assertEqual(log, [u'\x1b[34me327e92\x1b[0m \x1b[32mRonaldo Mercado\x1b[0m: add '
                               u'on_sdo_message to process scanner MSG_SDO_READ messages (4-1)'])

    def test_given_not_verbose_raw_then_format(self):

        log = dls_logs_since_release.format_log_messages(self.log_info, raw=True, verbose=False)

        self.assertEqual(log, [u'e327e92 Ronaldo Mercado: add on_sdo_message to process scanner'
                               u' MSG_SDO_READ messages (4-1)'])

    @patch('dls_ade.dls_logs_since_release.get_file_changes', return_value="u'M     ethercatApp/src/ecAsyn.cpp\n', "
                                                                           "u'M     ethercatApp/src/ecAsyn.h\n'")
    def test_given_verbose_raw_then_format(self, _1):

        log = dls_logs_since_release.format_log_messages(self.log_info_verbose, raw=True, verbose=True)

        self.assertEqual(log[0], u'e327e92 12/08/2014 13:50:10 Ronaldo Mercado: '
                                 u'add on_sdo_message to process scanner MSG_SDO_READ\n'
                                 u'...                                          messages (4-1)\n'
                                 u'...                                          '
                                 u'make "sdos" public to allow checks on the sdo_observers\n'
                                 u'...                                          list\n\n'
                                 u'Changes:\n'
                                 u'u\'M     ethercatApp/src/ecAsyn.cpp\n'
                                 u'\', u\'M     ethercatApp/src/ecAsyn.h\n'
                                 u'\'')

    @patch('dls_ade.dls_logs_since_release.get_file_changes', return_value="u'M     ethercatApp/src/ecAsyn.cpp\n', "
                                                                           "u'M     ethercatApp/src/ecAsyn.h\n'")
    def test_given_verbose_not_raw_then_format(self, _1):

        log = dls_logs_since_release.format_log_messages(self.log_info_verbose, raw=False, verbose=True)

        self.assertEqual(log[0], u'\x1b[34me327e92\x1b[0m \x1b[36m12/08/2014 '
                                 u'13:50:10\x1b[0m \x1b[32mRonaldo Mercado\x1b[0m: '
                                 u'add on_sdo_message to process scanner MSG_SDO_READ\n'
                                 u'...                                          messages (4-1)\n'
                                 u'...                                          '
                                 u'make "sdos" public to allow checks on the sdo_observers\n'
                                 u'...                                          list\n\n'
                                 u'Changes:\n'
                                 u'u\'M     ethercatApp/src/ecAsyn.cpp\n'
                                 u'\', u\'M     ethercatApp/src/ecAsyn.h\n'
                                 u'\'')

    def test_given_bad_entries_no_error(self):
        log_info = {u'commit_objects': {}, u'max_author_length': 0,
                    u'logs': [[]]}

        log = dls_logs_since_release.format_log_messages(log_info, raw=True, verbose=False)

        self.assertEqual(log, [u'no sha no name: \n'])

    def test_given_bad_entries_verbose_no_error(self):
        log_info = {u'commit_objects': {}, u'max_author_length': 0,
                    u'logs': [[]]}

        log = dls_logs_since_release.format_log_messages(log_info, raw=True, verbose=True)

        self.assertEqual(log, [u'no sha no date/time no name: \n'])


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
