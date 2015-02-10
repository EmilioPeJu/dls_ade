#!/bin/env dls-python

import unittest
from pkg_resources import require
require("mock")
from mock import patch, ANY
import vcs_svn
from dls_environment.svn import svnClient


class SvnClassTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

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
        print url_to_be_called
        vcs = vcs_svn.Svn(module,options)

        mock_check.assert_called_once_with(url_to_be_called)

    @patch('vcs_svn.svnClient.pathcheck',return_value=False)
    def test_given_args_for_nonexistent_repo_then_class_init_should_raise_assertion_error(self, mock_check):

         # simulates svnClient.pathcheck response to invalid path
        module = 'nonexistent'
        options = FakeOptions()

        self.assertRaises(AssertionError,vcs_svn.Svn,module,options)


class FakeOptions(object):
    def __init__(self,**kwargs):
        self.area = kwargs.get('area','support')
        self.branch = kwargs.get('branch',None)


if __name__ == '__main__':

    unittest.main()