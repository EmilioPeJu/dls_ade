#!/bin/env dls-python

import unittest
from pkg_resources import require
require("mock")
from mock import patch, ANY, call, MagicMock
import vcs_svn
from dls_environment.svn import svnClient


class SvnClassInitTest(unittest.TestCase):

    @patch('vcs_svn.svnClient.pathcheck')
    def test_pathcheck_called_at_class_init(self, mock_check):

        vcs = vcs_svn.Svn('',FakeOptions())

        mock_check.assert_called_once_with(ANY)

    @patch('vcs_svn.svnClient.pathcheck')
    def test_given_fake_module_options_args_then_pathcheck_called_at_init_with_ANY(self, mock_check):

        module = 'meow'
        options = FakeOptions()

        vcs = vcs_svn.Svn(module,options)

        mock_check.assert_called_once_with(ANY)

    @patch('vcs_svn.svnClient.pathcheck')
    def test_given_specific_module_options_then_pathcheck_called_with_valid_svn_repo(self, mock_check):

        module = 'deleteme'
        options = FakeOptions()
        url_to_be_called = svnClient().devModule(module,options.area)
        
        vcs = vcs_svn.Svn(module,options)

        mock_check.assert_called_once_with(url_to_be_called)

    @patch('vcs_svn.svnClient.pathcheck',return_value=False)
    def test_given_args_for_nonexistent_repo_then_class_init_should_raise_assertion_error(self, mock_check):

        # simulates svnClient.pathcheck response to invalid path
        module = 'nonexistent'
        options = FakeOptions()

        with self.assertRaises(AssertionError):
            vcs_svn.Svn(module, options)


class SvnListReleasesTest(unittest.TestCase):

    @patch('vcs_svn.svnClient.pathcheck', return_value=True)
    def setUp(self, mock_check):

        self.module = 'deleteme'
        self.options = FakeOptions()
        self.vcs = vcs_svn.Svn(self.module, self.options)

    @patch('vcs_svn.svnClient.pathcheck', return_value=False)
    def test_given_unreleased_module_then_return_empty_list(self, mock_check):

        releases = self.vcs.list_releases()
        
        self.assertEqual(0, len(releases))

    @patch('vcs_svn.svnClient.prodModule', return_value='svn+ssh://serv0002.cs.diamond.ac.uk/home/subversion/repos/controls/diamond/release/support/deleteme/')
    def test_given_released_module_then_return_list_inc_version_1_0(self, mock_list):
        '''
        as of 3.3.15, the above svn source path was correct for module
        "deleteme" with releases 1-0, 1-0-1 and 2-0
        '''
        releases = self.vcs.list_releases()

        self.assertTrue('1-0' in releases)

    @patch('vcs_svn.svnClient.prodModule', return_value='svn+ssh://serv0002.cs.diamond.ac.uk/home/subversion/repos/controls/diamond/release/support/deleteme/')
    def test_given_released_module_then_return_list_inc_all_rel_versions(self, mock_list):
        '''
        as of 3.3.15, the above svn source path was correct for module
        "deleteme" with releases 1-0, 1-0-1 and 2-0
        '''
        releases = self.vcs.list_releases()
        known_releases = ['1-0','1-0-1','2-0']

        for rel in known_releases:
            self.assertTrue(rel in releases)


class SvnSetLogMessageTest(unittest.TestCase):

    @patch('vcs_svn.svnClient.pathcheck', return_value=True)
    def setUp(self, mock_check):

        self.module = 'deleteme'
        self.options = FakeOptions()
        self.vcs = vcs_svn.Svn(self.module, self.options)

    @patch('vcs_svn.svnClient.setLogMessage')
    def test_when_called_with_message_then_svnClient_setLogMessage_called_with_message_argument(self, mlog):

        log_message = 'reason for release'

        self.vcs.set_log_message(log_message)

        mlog.assert_called_once_with(log_message)


class SvnCheckVersionTest(unittest.TestCase):

    @patch('vcs_svn.svnClient.pathcheck', return_value=True)
    def setUp(self, mock_check):

        self.module = 'deleteme'
        self.options = FakeOptions()
        self.vcs = vcs_svn.Svn(self.module, self.options)
        patcher = patch('vcs_svn.Svn.list_releases')
        self.addCleanup(patcher.stop)        
        self.mlist = patcher.start()

    def test_given_version_in_list_of_releases_then_return_true(self):
        
        version = '1-5'
        self.mlist.return_value = ['1-4','1-5','1-6']

        self.assertTrue(self.vcs.check_version_exists(version))

    def test_given_version_not_in_list_of_releases_then_return_false(self):
        
        version = '1-5'
        self.mlist.return_value = ['1-4','2-5','1-6']

        self.assertFalse(self.vcs.check_version_exists(version))


class ApiInterrogateTest(unittest.TestCase):

    def setUp(self):

        patcher = patch('vcs_svn.svnClient.pathcheck')
        self.addCleanup(patcher.stop)
        self.mock_check = patcher.start()

        self.module = 'dummy'
        self.options = FakeOptions()
        self.vcs = vcs_svn.Svn(self.module, self.options)

    def test_when_asking_object_for_vcs_type_then_return_svn_in_string(self):

        vcs_type = self.vcs.vcs_type

        self.assertEqual(vcs_type,'svn')

    def test_when_calling_source_repo_method_then_return_url_with_http_at_start(self):

        expected_source_repo = 'http://serv0002.cs.diamond.ac.uk/repos/'
        expected_source_repo += 'controls/diamond/trunk/' + self.options.area
        expected_source_repo += '/' + self.module

        source_repo = self.vcs.source_repo

        self.assertEqual(source_repo, expected_source_repo)


class SvnSetBranchTest(unittest.TestCase):

    def test_given_nonexistent_branch_then_raise_error(self):

        vcs = vcs_svn.Svn('deleteme', FakeOptions())

        with self.assertRaises(AssertionError):
            vcs.set_branch('not_a_branch')

    @patch('vcs_svn.svnClient.pathcheck', return_value = True)
    def test_given_existing_branch_then_source_repo_changed_to_correct_url(self, _):

        branch_name = 'some_branch'
        module = 'deleteme'
        expected_source_url = 'http://serv0002.cs.diamond.ac.uk/repos/controls'
        expected_source_url += '/diamond/branches/support/' + module
        expected_source_url += '/' + branch_name

        vcs = vcs_svn.Svn(module, FakeOptions())
        try:
            vcs.set_branch(branch_name)
        except AssertionError:
            self.fail('set_branch() raised AssertionError unexpectedly')

        new_source_url = vcs.source_repo

        self.assertEqual(expected_source_url, new_source_url)


class SetVersionTest(unittest.TestCase):

    def setUp(self):

        patcher = patch('vcs_svn.svnClient.pathcheck')
        self.addCleanup(patcher.stop)
        self.mock_check = patcher.start()

        self.module = 'deleteme'
        self.options = FakeOptions()
        self.vcs = vcs_svn.Svn(self.module, self.options)

    def test_given_vcs_when_version_not_set_then_get_version_raise_error(self):

        with self.assertRaises(Exception):
            self.vcs.version

    def test_given_vcs_when_set_version_to_n_then_get_version_return_n(self):

        version = '0-2'

        self.vcs.set_version(version)

        self.assertEqual(self.vcs.version, version)

    @patch('vcs_svn.Svn.list_releases', return_value=['0-2'])
    def test_given_vcs_and_version_exists_when_set_version_called_then_repo_url_change_to_released_version(self, _):

        version = '0-2'
        expected_url = 'http://serv0002.cs.diamond.ac.uk/'
        expected_url += 'repos/controls/diamond/release/' + self.options.area
        expected_url += '/' + self.module + '/' + version

        self.vcs.set_version(version)
        source_url = self.vcs.source_repo

        self.assertEqual(source_url, expected_url)


class ReleaseVersionTest(unittest.TestCase):

    @patch('vcs_svn.svnClient.pathcheck', return_value=True)
    def setUp(self, mock_check):

        self.module = 'meow'
        self.options = FakeOptions()
        self.vcs = vcs_svn.Svn(self.module, self.options)
        self.vcs.client.mkdir = MagicMock()
        self.vcs.client.copy = MagicMock()
        self.version = '0-2'
        self.rel_dir = 'svn+ssh://serv0002.cs.diamond.ac.uk/home/subversion/'
        self.rel_dir += 'repos/controls/diamond/release/' + self.options.area
        self.rel_dir += '/' + self.module + '/' + self.version

    def test_given_vcs_then_call_mkdir_with_correct_release_directory_as_arg(self):

        self.vcs.release_version(self.version)

        self.vcs.client.mkdir.assert_called_once_with(self.rel_dir)

    def test_given_vcs_then_call_copy_with_correct_source_and_release_dirs_as_args(self):

        source_dir = self.vcs._repo_url

        self.vcs.release_version(self.version)

        self.vcs.client.copy.assert_called_once_with(source_dir, self.rel_dir)

    @patch('vcs_svn.Svn.list_releases')
    def test_given_reldir_made_and_copied_into_when_version_released_then_repo_url_should_give_rel_dir(self, mlist):

        # list_releases mocked out as no new releases are made, and the method
        # depends on the list of releases being updated
        mlist.return_value = [self.version]

        self.vcs.release_version(self.version)

        new_source_url = self.vcs.source_repo.replace('http','svn+ssh')
        new_source_url = new_source_url.replace('ac.uk','ac.uk/home/subversion')

        self.assertEqual(new_source_url, self.rel_dir)


    def test_god_function_does_things_in_the_right_order(self):
        self.vcs.set_version = MagicMock()
        manager = MagicMock()
        manager.attach_mock(self.vcs.client.mkdir, 'mkdir')
        manager.attach_mock(self.vcs.client.copy, 'copy')
        manager.attach_mock(self.vcs.set_version, 'set_version')

        old_source_url = self.vcs.source_repo.replace('http','svn+ssh')
        old_source_url = old_source_url.replace('ac.uk','ac.uk/home/subversion')
        self.vcs.release_version(self.version)

        manager.assert_has_calls([call.mkdir(self.rel_dir),
                                  call.copy(old_source_url, self.rel_dir),
                                  call.set_version(self.version)])


class FakeOptions(object):
    def __init__(self,**kwargs):
        self.area = kwargs.get('area','support')
        self.branch = kwargs.get('branch',None)


if __name__ == '__main__':

    # buffer option suppresses stdout generated from tested code
    unittest.main(buffer=True)