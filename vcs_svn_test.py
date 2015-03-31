#!/bin/env dls-python

import unittest
from pkg_resources import require
require("mock")
from mock import patch, ANY
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
    @patch('vcs_svn.svnClient.pathcheck', return_value=True)
    def test_given_released_module_then_return_list_inc_version_1_0(self, mock_check, mock_list):
        '''
        as of 3.3.15, the above svn source path was correct for module
        "deleteme" with releases 1-0, 1-0-1 and 2-0
        '''
        releases = self.vcs.list_releases()

        self.assertTrue('1-0' in releases)

    @patch('vcs_svn.svnClient.prodModule', return_value='svn+ssh://serv0002.cs.diamond.ac.uk/home/subversion/repos/controls/diamond/release/support/deleteme/')
    @patch('vcs_svn.svnClient.pathcheck', return_value=True)
    def test_given_released_module_then_return_list_inc_all_rel_versions(self, mock_check, mock_list):
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

    @patch('vcs_svn.Svn.list_releases')
    def test_given_version_in_list_of_releases_then_return_true(self, mlist):
        
        version = '1-5'
        mlist.return_value = ['1-4','1-5','1-6']

        self.assertTrue(self.vcs.check_version_exists(version))

    @patch('vcs_svn.Svn.list_releases')
    def test_given_version_not_in_list_of_releases_then_return_false(self, mlist):
        
        version = '1-5'
        mlist.return_value = ['1-4','2-5','1-6']

        self.assertFalse(self.vcs.check_version_exists(version))


class ApiInterrogateTest(unittest.TestCase):

    def setUp(self):

        patcher = patch('vcs_svn.svnClient.pathcheck')
        self.addCleanup(patcher.stop)
        self.mock_check = patcher.start()

    def test_when_asking_object_for_vcs_type_then_return_svn_in_string(self):

        vcs_type = vcs_svn.Svn('dummy', FakeOptions()).vcs_type

        self.assertEqual(vcs_type,'svn')

    def test_when_calling_source_repo_method_then_return_url_with_http_at_start(self):

        module = 'dummy'
        options = FakeOptions()
        vcs = vcs_svn.Svn(module, options)
        expected_source_repo = 'http://serv0002.cs.diamond.ac.uk/home/subversion/repos/controls/diamond/trunk/'+options.area+'/'+module

        source_repo = vcs.source_repo

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
        expected_source_url = 'http://serv0002.cs.diamond.ac.uk/home/subversion/repos/controls/diamond/branches/support/'+module+'/'+branch_name

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

    def test_given_vcs_when_version_not_set_then_get_version_raise_error(self):

        module = 'deleteme'

        vcs = vcs_svn.Svn(module, FakeOptions())

        with self.assertRaises(Exception):
            vcs.version

    def test_given_vcs_when_set_version_to_n_then_get_version_return_n(self):

        module = 'deleteme'
        version = '0-2'

        vcs = vcs_svn.Svn(module, FakeOptions())
        vcs.set_version(version)

        self.assertEqual(vcs.version, version)

    @patch('vcs_svn.Svn.list_releases', return_value=['0-2'])
    def test_given_vcs_and_version_exists_when_set_version_called_then_repo_url_change_to_released_version(self, _):

        module = 'deleteme'
        version = '0-2'
        options = FakeOptions()
        expected_url = 'http://serv0002.cs.diamond.ac.uk/home/subversion/'
        expected_url += 'repos/controls/diamond/release/' + options.area + '/'
        expected_url += module + '/' + version

        vcs = vcs_svn.Svn(module, options)
        vcs.set_version(version)
        source_url = vcs.source_repo

        self.assertEqual(source_url, expected_url)


class FakeOptions(object):
    def __init__(self,**kwargs):
        self.area = kwargs.get('area','support')
        self.branch = kwargs.get('branch',None)


if __name__ == '__main__':

    unittest.main()