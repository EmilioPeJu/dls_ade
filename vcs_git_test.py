#!/bin/env dls-python

import os
import unittest
from pkg_resources import require
require("mock")
from mock import patch, ANY, MagicMock
import vcs_git


class GitClassInitTest(unittest.TestCase):

    def test_given_nonsense_module_options_args_then_class_instance_should_fail(self):

        with self.assertRaises(Exception):
            vcs_git.Git(1, 2)

    @patch('vcs_git.subprocess.check_output')
    def test_given_any_module_and_options_args_then_subprocess_called_to_list_repos(self, mock_check):

        repo_list_cmd = 'ssh dascgitolite@dasc-git.diamond.ac.uk expand controls'
        with self.assertRaises(Exception):
            vcs_git.Git(1, FakeOptions())

        mock_check.assert_called_once_with(repo_list_cmd.split())

    @patch('vcs_git.tempfile.mkdtemp')
    @patch('vcs_git.git.Repo.clone_from')
    def test_given_args_for_real_repo_then_do_not_raise_exception(self, _1, _2):

        try:
            vcs_git.Git('dummy', FakeOptions())
        except Exception, e:
            self.fail(e)

    @patch('vcs_git.subprocess.check_output', return_value=['controls/support/dummy'])
    @patch('vcs_git.tempfile.mkdtemp')
    @patch('vcs_git.git.Repo.clone_from')
    def test_given_repo_exists_then_create_temp_dir_to_clone_into(self, mock_clone, mock_temp, _):

        module = "dummy"
        options = FakeOptions()

        vcs_git.Git(module, options)

        mock_temp.assert_called_once_with(suffix="_dummy")

    @patch('vcs_git.subprocess.check_output', return_value=['dummy'])
    @patch('vcs_git.tempfile.mkdtemp')
    @patch('vcs_git.git.Repo.clone_from')
    def test_given_repo_does_not_exist_then_git_clone_should_not_be_called(self, mock_clone, mock_temp, mock_check):

        module = "dummy"
        options = FakeOptions()

        with self.assertRaises(Exception):
            vcs_git.Git(module, options)

        n_clone_calls = mock_clone.call_count
        n_temp_calls = mock_temp.call_count

        self.assertEquals(0, n_clone_calls)
        self.assertEquals(0, n_temp_calls)

    @patch('vcs_git.subprocess.check_output', return_value=['controls/support/dummy'])
    @patch('vcs_git.tempfile.mkdtemp')
    @patch('vcs_git.git.Repo.clone_from')
    def test_given_repo_exists_then_git_clone_called(self, mock_clone, _, mock_check):

        repo_url = "ssh://dascgitolite@dasc-git.diamond.ac.uk/controls/support/dummy"
        module = "dummy"
        options = FakeOptions()

        vcs = vcs_git.Git(module, options)

        n_clone_calls = mock_clone.call_count

        self.assertEquals(1, n_clone_calls)

    @patch('vcs_git.subprocess.check_output', return_value=['controls/support/dummy'])
    @patch('vcs_git.git.Repo.clone_from')
    def test_given_repo_exists_then_git_clone_called_with_remote_url_and_tempdir_args(self, mock_clone, mock_check):

        repo_url = "ssh://dascgitolite@dasc-git.diamond.ac.uk/controls/support/dummy"
        module = "dummy"
        options = FakeOptions()

        vcs = vcs_git.Git(module, options)

        args, kwargs = mock_clone.call_args
        target_dir = args[1]
        remote_repo_called = args[0]

        os.rmdir(target_dir)

        self.assertTrue(target_dir.startswith("/tmp/tmp"))
        self.assertTrue(target_dir.endswith("_" + module))
        self.assertGreater(len(target_dir), len(module)+9)


class GitListReleasesTest(unittest.TestCase):

    @patch('vcs_git.subprocess.check_output', return_value=['controls/support/dummy'])
    @patch('vcs_git.git.Repo.clone_from')
    @patch('vcs_git.tempfile.mkdtemp')
    def setUp(self, mtemp, mclone, mcheck):

        self.module = 'dummy'
        self.options = FakeOptions()

        self.vcs = vcs_git.Git(self.module, self.options)
        self.vcs.client.tags = [FakeTag("1-0"), FakeTag("1-0-1"), FakeTag("2-0")]

    def test_given_repo_with_no_tags_then_return_empty_list(self):

        self.vcs.client.tags = []
        releases = self.vcs.list_releases()

        self.assertListEqual([], releases)

    def test_given_repo_with_some_tags_then_return_list_inc_version_1_0(self):

        releases = self.vcs.list_releases()

        self.assertTrue('1-0' in releases)

    def test_given_repo_with_some_tags_then_return_all_version_tag_names(self):

        releases = self.vcs.list_releases()

        self.assertListEqual(['1-0', '1-0-1', '2-0'], releases)


class GitSetLogMessageTest(unittest.TestCase):

    @patch('vcs_git.subprocess.check_output', return_value=['controls/support/dummy'])
    @patch('vcs_git.git.Repo.clone_from')
    @patch('vcs_git.tempfile.mkdtemp')
    def setUp(self, mtemp, mclone, mcheck):

        self.module = 'dummy'
        self.options = FakeOptions()

        self.vcs = vcs_git.Git(self.module, self.options)

    def test_given_message_arg_when_method_invoked_then_return_None(self):

        result = self.vcs.set_log_message('reason for commit')

        self.assertIsNone(result)


class GitCheckVersionTest(unittest.TestCase):

    @patch('vcs_git.subprocess.check_output', return_value=['controls/support/dummy'])
    @patch('vcs_git.git.Repo.clone_from')
    @patch('vcs_git.tempfile.mkdtemp')
    def setUp(self, mtemp, mclone, mcheck):

        self.module = 'dummy'
        self.options = FakeOptions()

        self.vcs = vcs_git.Git(self.module, self.options)

    @patch('vcs_git.Git.list_releases')
    def test_given_version_in_list_of_releases_then_return_true(self, mlist):
        
        version = '1-5'
        mlist.return_value = ['1-4','1-5','1-6']

        self.assertTrue(self.vcs.check_version_exists(version))

    @patch('vcs_git.Git.list_releases')
    def test_given_version_not_in_list_of_releases_then_return_false(self, mlist):
        
        version = '1-5'
        mlist.return_value = ['1-4','2-5','1-6']

        self.assertFalse(self.vcs.check_version_exists(version))


class ApiInterrogateTest(unittest.TestCase):

    @patch('vcs_git.subprocess.check_output', return_value=['controls/support/dummy'])
    @patch('vcs_git.git.Repo.clone_from')
    @patch('vcs_git.tempfile.mkdtemp')
    def test_when_asking_object_for_vcs_type_then_return_git_in_string(self, _1, _2, _3):

        vcs_type = vcs_git.Git('dummy', FakeOptions()).vcs_type

        self.assertEqual(vcs_type, 'git')


class FakeTag(object):
    def __init__(self, name):
        self.name = name


class FakeOptions(object):
    def __init__(self, **kwargs):
        self.area = kwargs.get('area', 'support')


if __name__ == '__main__':

    unittest.main()
