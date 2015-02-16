#!/bin/env dls-python

import unittest
from pkg_resources import require
require("mock")
from mock import patch, ANY
import vcs_git


class GitClassTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_given_nonsense_module_options_args_then_class_instance_should_fail(self):

        with self.assertRaises(Exception):
            vcs_git.Git(1,2)

    @patch('vcs_git.subprocess.check_output')
    def test_given_any_args_then_subprocess_called_to_list_repos(self, mock_check):

        repo_list_cmd = 'ssh dascgitolite@dasc-git.diamond.ac.uk expand controls'
        with self.assertRaises(Exception):
            vcs_git.Git(1,2)

        mock_check.assert_called_once_with(repo_list_cmd.split())

    def test_given_args_for_real_repo_then_do_not_raise_exception(self):

        try:
            vcs_git.Git('dummy',FakeOptions())
        except Exception, e:
            self.fail(e)

    # @patch('vcs_git.git.Repo.clone_from')
    # def test_given_new_class_instance_then_clone_of_repo_created(self, mock_clone):

    #     vcs = vcs_git.Git('',FakeOptions())

    #     mock_clone.assert_called_once_with(ANY,ANY)

    # @patch('vcs_git.git.Repo.clone_from')
    # def test_given_specific_module_area_args_then_clone_called_with_correct_remote_repo_url(self, mock_clone):

    #     options = FakeOptions()
    #     module = 'module'
    #     repo_url = "ssh://dascgitolite@dasc-git.diamond.ac.uk/controls/support/module"

    #     vcs = vcs_git.Git(module,options)

    #     mock_clone.assert_called_once_with(repo_url,ANY)

    # @patch('vcs_git.git.Repo.clone_from')
    # def test_specific_module_area_args_then_clone_called_with_temp_dir_name(self, mock_clone):

    #     options = FakeOptions()
    #     module = 'module'
    #     repo_url = "ssh://dascgitolite@dasc-git.diamond.ac.uk/controls/support/module"

    #     vcs = vcs_git.Git(module,options)

    #     args, kwargs = mock_clone.call_args
    #     target_dir = args[1]

    #     self.assertTrue(target_dir.startswith("/tmp/tmp"))
    #     self.assertTrue(target_dir.endswith("_" + module))
    #     self.assertGreater(len(target_dir),len(module)+9)

class FakeOptions(object):
    def __init__(self,**kwargs):
        self.area = kwargs.get('area','support')
        # self.branch = kwargs.get('branch',None)


if __name__ == '__main__':

    unittest.main()