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

    @patch('vcs_svn.svnClient.pathcheck')
    def test_given_specific_module_options_with_branch_then_pathcheck_called_with_branch_url(self,mock_check):

        module = 'deleteme'
        options = FakeOptions(branch='feature_dev')
        url_to_be_called = svnClient().branchModule(module,options.area)+'/'+options.branch

        vcs = vcs_svn.Svn(module,options)

        mock_check.assert_called_once_with(url_to_be_called)

    @patch('vcs_svn.svnClient.pathcheck',return_value=False)
    def test_given_args_for_nonexistent_repo_then_class_init_should_raise_assertion_error(self, mock_check):

        # simulates svnClient.pathcheck response to invalid path
        module = 'nonexistent'
        options = FakeOptions()

        self.assertRaises(AssertionError,vcs_svn.Svn,module,options)


class SvnListReleasesTest(unittest.TestCase):

    @patch('vcs_svn.svnClient.pathcheck', return_value=True)
    def setUp(self, mock_check):

        self.module = 'deleteme'
        self.options = FakeOptions()
        self.vcs = vcs_svn.Svn(self.module, self.options)

    @patch('vcs_svn.svnClient.pathcheck', return_value=False)
    def test_given_unreleased_module_then_return_empty_list(self, mock_check):

        releases = self.vcs.list_releases(self.module, self.options.area)
        
        self.assertEqual(0, len(releases))

    @patch('vcs_svn.svnClient.prodModule', return_value='svn+ssh://serv0002.cs.diamond.ac.uk/home/subversion/repos/controls/diamond/release/support/deleteme/')
    @patch('vcs_svn.svnClient.pathcheck', return_value=True)
    def test_given_released_module_then_return_list_inc_version_1_0(self, mock_check, mock_list):
        '''
        as of 3.3.15, the above svn source path was correct for module
        "deleteme" with releases 1-0, 1-0-1 and 2-0
        '''
        releases = self.vcs.list_releases(self.module, self.options.area)

        self.assertTrue('1-0' in releases)

    @patch('vcs_svn.svnClient.prodModule', return_value='svn+ssh://serv0002.cs.diamond.ac.uk/home/subversion/repos/controls/diamond/release/support/deleteme/')
    @patch('vcs_svn.svnClient.pathcheck', return_value=True)
    def test_given_released_module_then_return_list_inc_all_rel_versions(self, mock_check, mock_list):
        '''
        as of 3.3.15, the above svn source path was correct for module
        "deleteme" with releases 1-0, 1-0-1 and 2-0
        '''
        releases = self.vcs.list_releases(self.module, self.options.area)
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


class ApiInterrogateTest(unittest.TestCase):

    @patch('vcs_svn.svnClient.pathcheck')
    def test_when_asking_object_for_vcs_type_then_return_svn_in_string(self, _):

        vcs_type = vcs_svn.Svn('dummy',FakeOptions()).vcs_type

        self.assertEqual(vcs_type,'svn')

class FakeOptions(object):
    def __init__(self,**kwargs):
        self.area = kwargs.get('area','support')
        self.branch = kwargs.get('branch',None)


if __name__ == '__main__':

    unittest.main()