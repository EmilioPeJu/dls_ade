#!/bin/env dls-python

from dls_ade import vcs_git
import os
import unittest
from pkg_resources import require
require("mock")
from mock import patch, ANY, MagicMock, PropertyMock  # @UnresolvedImport


class IsGitDirTest(unittest.TestCase):

    def test_given_reasonable_input_then_function_called_correctly(self):
        pass
        # Method procedural and taken from internet - not sure how to test!


class NewIsGitDirTest(unittest.TestCase):

    def test_given_invalid_file_path_then_error_raised(self):
        path = "/not/a/path"

        with self.assertRaises(Exception):
            vcs_git.new_is_git_dir(path)

    def test_given_not_git_dir_then_returns_false(self):
        path = "/"

        return_value = vcs_git.new_is_git_dir(path)

        self.assertFalse(return_value)

    @patch('dls_ade.vcs_git.git')
    def test_given_git_dir_then_returns_true(self, mock_git):
        path = "/"

        git_inst = MagicMock()
        mock_git.Repo.return_value = git_inst

        return_value = vcs_git.new_is_git_dir(path)

        self.assertTrue(return_value)


class IsGitRootDirTest(unittest.TestCase):

    @patch('dls_ade.vcs_git.is_git_dir', return_value=True)
    @patch('dls_ade.vcs_git.git')
    def test_given_git_dir_then_git_repo_assigned_to_path(self, mock_git, _2):
        path = "test/path"

        git_inst = MagicMock()
        mock_git.Repo = git_inst

        vcs_git.is_git_root_dir(path)

        git_inst.assert_called_once_with(path)

    @patch('dls_ade.vcs_git.is_git_dir', return_value=False)
    @patch('dls_ade.vcs_git.git')
    def test_given_not_git_dir_then_git_repo_not_assigned(self, mock_git, _2):
        path = "test/path"

        git_inst = MagicMock()
        mock_git.Repo = git_inst

        vcs_git.is_git_root_dir(path)

        self.assertFalse(git_inst.call_count)

    @patch('dls_ade.vcs_git.os.getcwd', return_value="top/level/")
    @patch('dls_ade.vcs_git.is_git_dir', return_value=True)
    @patch('dls_ade.vcs_git.git')
    def test_given_git_dir_and_at_top_level_then_return_true(self, mock_git, _2, _3):
        path = "test/path"

        git_inst = MagicMock()
        mock_git.Repo.return_value = git_inst
        git_inst.git.rev_parse.return_value = "top/level/test/path"

        return_value = vcs_git.is_git_root_dir(path)

        self.assertTrue(return_value)

    @patch('dls_ade.vcs_git.os.getcwd', return_value="not/top/level/")
    @patch('dls_ade.vcs_git.is_git_dir', return_value=True)
    @patch('dls_ade.vcs_git.git')
    def test_given_git_dir_and_at_top_level_then_return_false(self, mock_git, _2, _3):
        path = "test/path"

        git_inst = MagicMock()
        mock_git.Repo.return_value = git_inst
        git_inst.git.rev_parse.return_value = "top/level/test/path"

        return_value = vcs_git.is_git_root_dir(path)

        self.assertFalse(return_value)

    @patch('dls_ade.vcs_git.is_git_dir', return_value=False)
    @patch('dls_ade.vcs_git.git')
    def test_given_not_git_dir_then_git_repo_return_false(self, mock_git, _2):
        path = "/test/path"

        git_inst = MagicMock()
        mock_git.Repo = git_inst

        return_value = vcs_git.is_git_root_dir(path)

        self.assertFalse(return_value)


class IsInRepoTest(unittest.TestCase):

    @patch('dls_ade.vcs_git.subprocess.check_output', return_value=['controls/test/path'])
    def test_given_path_exists_then_return_true(self, mock_check):

        self.assertTrue(vcs_git.is_repo_path("controls/test/path"))

    @patch('dls_ade.vcs_git.subprocess.check_output', return_value=['controls/test/otherpath'])
    def test_given_path_does_not_exist_then_return_false(self, mock_check):

        self.assertFalse(vcs_git.is_repo_path("controls/test/path"))


class StageAllFilesAndCommitTest(unittest.TestCase):

    @patch('dls_ade.vcs_git.git')
    def test_given_valid_path_then_repo_initialised(self, mock_git):
        path = "/"

        git_inst = MagicMock()
        mock_git.Repo.init = git_inst

        vcs_git.stage_all_files_and_commit(path)

        git_inst.assert_called_once_with(path)

    @patch('dls_ade.vcs_git.git')
    def test_given_valid_path_then_files_staged(self, mock_git):
        path = "/"

        git_inst = MagicMock()
        mock_git.Repo.init.return_value = git_inst

        vcs_git.stage_all_files_and_commit(path)

        git_inst.git.add.assert_called_once_with('--all')

    @patch('dls_ade.vcs_git.git')
    def test_given_valid_path_then_files_committed(self, mock_git):
        path = "/"

        git_inst = MagicMock()
        mock_git.Repo.init.return_value = git_inst

        vcs_git.stage_all_files_and_commit(path)

        git_inst.git.commit.assert_called_once_with(m="Initial commit")

    @patch('dls_ade.vcs_git.git')
    def test_given_invalid_path_then_raise_error(self, mock_git):
        path = "does/not/exist"

        git_inst = MagicMock()
        mock_git.Repo.init = git_inst

        with self.assertRaises(Exception):
            vcs_git.stage_all_files_and_commit(path)

        self.assertFalse(git_inst.call_count)


class AddNewRemoteAndPushTest(unittest.TestCase):

    def setUp(self):
        self.patch_is_git_root_dir = patch('dls_ade.vcs_git.is_git_root_dir')
        self.patch_create_remote_repo = patch('dls_ade.vcs_git.create_remote_repo')
        self.patch_is_repo_path = patch('dls_ade.vcs_git.is_repo_path')
        self.patch_git = patch('dls_ade.vcs_git.git')

        self.addCleanup(self.patch_is_git_root_dir.stop)
        self.addCleanup(self.patch_create_remote_repo.stop)
        self.addCleanup(self.patch_is_repo_path.stop)
        self.addCleanup(self.patch_git.stop)

        self.mock_is_git_root_dir = self.patch_is_git_root_dir.start()
        self.mock_create_remote_repo = self.patch_create_remote_repo.start()
        self.mock_is_repo_path = self.patch_is_repo_path.start()
        self.mock_git = self.patch_git.start()

        self.mock_repo = MagicMock()  # This code here allows us to interrogate the objects created from git.Repo()
        self.mock_remotes_property = PropertyMock()
        type(self.mock_repo).remotes = self.mock_remotes_property

        self.mock_remote = MagicMock()
        self.mock_repo.create_remote.return_value = self.mock_remote

        self.mock_git.Repo.return_value = self.mock_repo

        # The mocks below allow us to test the list comprehension
        self.mock_property_not_in_repo = PropertyMock(return_value = "notinrepo")
        self.mock_property_in_repo = PropertyMock(return_value = "inrepo")

        self.mock_not_in_repo = MagicMock()
        type(self.mock_not_in_repo).name = self.mock_property_not_in_repo

        self.mock_in_repo = MagicMock()
        type(self.mock_in_repo).name = self.mock_property_in_repo

        # Need to set:
        # self.mock_remotes_property.return_value = [...]

    def test_given_is_git_root_dir_false_then_exception_raised_with_correct_message(self):

        self.mock_is_git_root_dir.return_value = False

        comp_message = "Path {path:s} is not a git repository"
        comp_message = comp_message.format(path="test_path")

        with self.assertRaises(Exception) as e:
            vcs_git.add_new_remote_and_push("test_destination", path="test_path")

        self.assertEqual(str(e.exception), comp_message)

    def test_given_is_git_root_dir_true_then_git_repo_init_called_with_correct_arguments(self):

        self.mock_is_git_root_dir.return_value = True

        try:
            vcs_git.add_new_remote_and_push("test_destination", path="test_path")
        except:
            pass

        self.mock_git.Repo.assert_called_once_with("test_path")

    def test_given_remote_name_in_repo_remotes_then_exception_raised_with_correct_message(self):

        self.mock_is_git_root_dir.return_value = True
        self.mock_remotes_property.return_value = [self.mock_not_in_repo, self.mock_in_repo, self.mock_not_in_repo]

        comp_message = "Cannot push local repository to destination as remote {remote:s} is already defined"
        comp_message = comp_message.format(remote="inrepo")

        with self.assertRaises(Exception) as e:
            vcs_git.add_new_remote_and_push("test_destination", remote_name="inrepo")

        self.assertEqual(str(e.exception), comp_message)

    def test_given_is_repo_path_true_then_exception_raised_with_correct_message(self):

        self.mock_is_git_root_dir.return_value = True
        self.mock_remotes_property.return_value = [self.mock_not_in_repo, self.mock_not_in_repo, self.mock_not_in_repo]

        comp_message = "{dest:s} already exists".format(dest="test_destination")

        with self.assertRaises(Exception) as e:
            vcs_git.add_new_remote_and_push("test_destination")

        self.assertEqual(str(e.exception), comp_message)

    def test_given_all_checks_pass_then_function_runs_correctly(self):

        self.mock_is_git_root_dir.return_value = True
        self.mock_remotes_property.return_value = [self.mock_not_in_repo, self.mock_not_in_repo, self.mock_not_in_repo]
        self.mock_is_repo_path.return_value = False

        vcs_git.add_new_remote_and_push("test_destination", remote_name="test_remote", branch_name="test_branch")

        self.mock_create_remote_repo.assert_called_once_with("test_destination")
        self.mock_repo.create_remote.assert_called_once_with("test_remote", "test_destination")
        self.mock_remote.push.assert_called_once_with("test_branch")


class CreateRemoteRepoTest(unittest.TestCase):
    pass


class PushToRemoteTest(unittest.TestCase):
    pass


class CloneTest(unittest.TestCase):

    @patch('dls_ade.vcs_git.is_repo_path', return_value=False)
    @patch('git.Repo.clone_from')
    def test_given_invalid_source_then_error_raised(self, mock_clone_from, mock_is_repo_path):
        source = "does/not/exist"
        module = "test_module"

        with self.assertRaises(Exception):
            vcs_git.clone(source, module)

    @patch('dls_ade.vcs_git.is_repo_path', return_value=True)
    @patch('git.Repo.clone_from')
    def test_given_valid_source_then_no_error_raised(self, mock_clone_from, mock_is_repo_path):
        source = "does/exist"
        module = "test_module"

        vcs_git.clone(source, module)

    @patch('os.path.isdir', return_value=True)
    @patch('dls_ade.vcs_git.is_repo_path', return_value=True)
    @patch('git.Repo.clone_from')
    def test_given_existing_module_name_then_error_raised(self, mock_clone_from, mock_is_repo_path, mock_isdir):
        source = "test/source"
        module = "already_exists"

        with self.assertRaises(Exception):
            vcs_git.clone(source, module)

    @patch('os.path.isdir', return_value=False)
    @patch('dls_ade.vcs_git.is_repo_path', return_value=True)
    @patch('git.Repo.clone_from')
    def test_given_valid_module_name_then_no_error_raised(self, mock_clone_from, mock_is_repo_path, mock_isdir):
        source = "test/source"
        module = "test_module"

        vcs_git.clone(source, module)

    @patch('dls_ade.vcs_git.is_repo_path', return_value=True)
    @patch('dls_ade.vcs_git.os.path.isdir', return_value=False)
    @patch('git.Repo.clone_from')
    def test_given_valid_inputs_then_clone_from_function_called(self, mock_clone_from,
                                                              mock_is_repo_path, mock_clone):
        source = "test/source"
        module = "test_module"

        vcs_git.clone(source, module)

        mock_clone.assert_called_once_with(ANY)


class CloneMultiTest(unittest.TestCase):

    @patch('dls_ade.vcs_git.is_repo_path', return_value=False)
    @patch('git.Repo.clone_from')
    def test_given_invalid_source_then_error_raised(self, mock_clone_from, mock_is_repo_path):
        source = "does/not/exist"
        module = "test_module"

        with self.assertRaises(Exception):
            vcs_git.clone(source, module)

    @patch('dls_ade.vcs_git.is_repo_path', return_value=True)
    @patch('git.Repo.clone_from')
    def test_given_valid_source_then_no_error_raised(self, mock_clone_from, mock_is_repo_path):
        source = "does/exist"
        module = "test_module"

        vcs_git.clone(source, module)

    @patch('os.path.isdir', return_value=True)
    @patch('dls_ade.vcs_git.is_repo_path', return_value=True)
    @patch('git.Repo.clone_from')
    def test_given_existing_module_name_then_error_raised(self, mock_clone_from, mock_is_repo_path, mock_isdir):
        source = "test/source"
        module = "already_exists"

        with self.assertRaises(Exception):
            vcs_git.clone(source, module)

    @patch('os.path.isdir', return_value=False)
    @patch('dls_ade.vcs_git.is_repo_path', return_value=True)
    @patch('git.Repo.clone_from')
    def test_given_valid_module_name_then_no_error_raised(self, mock_clone_from, mock_is_repo_path, mock_isdir):
        source = "test/source"
        module = "test_module"

        vcs_git.clone(source, module)

    @patch('dls_ade.vcs_git.is_repo_path', return_value=True)
    @patch('dls_ade.vcs_git.os.path.isdir', return_value=False)
    @patch('git.Repo.clone_from')
    def test_given_valid_inputs_then_clone_from_function_called(self, mock_clone_from,
                                                              mock_is_repo_path, mock_clone):
        source = "test/source"
        module = "test_module"

        vcs_git.clone(source, module)

        mock_clone.assert_called_once_with(ANY)


class GitClassInitTest(unittest.TestCase):

    def test_given_nonsense_module_options_args_then_class_instance_should_fail(self):

        with self.assertRaises(Exception):
            vcs_git.Git(1, 2)

    @patch('dls_ade.vcs_git.subprocess.check_output')
    def test_given_any_module_and_options_args_then_subprocess_called_to_list_repos(self, mock_check):

        repo_list_cmd = 'ssh dascgitolite@dasc-git.diamond.ac.uk expand controls'

        with self.assertRaises(Exception):
            vcs_git.Git("FakeModuleNumberOne", FakeOptions())

        mock_check.assert_called_once_with(repo_list_cmd.split())

    @patch('dls_ade.vcs_git.tempfile.mkdtemp')
    @patch('dls_ade.vcs_git.git.Repo.clone_from')
    def test_given_args_for_real_repo_then_do_not_raise_exception(self, _1, _2):

        try:
            vcs_git.Git('dummy', FakeOptions())
        except Exception, e:
            self.fail(e)

    @patch('dls_ade.vcs_git.subprocess.check_output', return_value=['controls/support/dummy'])
    @patch('dls_ade.vcs_git.tempfile.mkdtemp')
    @patch('dls_ade.vcs_git.git.Repo.clone_from')
    def test_given_repo_exists_then_create_temp_dir_to_clone_into(self, mock_clone, mock_temp, _):

        module = "dummy"
        options = FakeOptions()

        vcs_git.Git(module, options)

        mock_temp.assert_called_once_with(suffix="_dummy")

    @patch('dls_ade.vcs_git.subprocess.check_output', return_value=['dummy'])
    @patch('dls_ade.vcs_git.tempfile.mkdtemp')
    @patch('dls_ade.vcs_git.git.Repo.clone_from')
    def test_given_repo_does_not_exist_then_git_clone_should_not_be_called(self, mock_clone, mock_temp, mock_check):

        module = "dummy"
        options = FakeOptions()

        with self.assertRaises(Exception):
            vcs_git.Git(module, options)

        n_clone_calls = mock_clone.call_count
        n_temp_calls = mock_temp.call_count

        self.assertEqual(0, n_clone_calls)
        self.assertEqual(0, n_temp_calls)

    @patch('dls_ade.vcs_git.subprocess.check_output', return_value=['controls/support/dummy'])
    @patch('dls_ade.vcs_git.tempfile.mkdtemp')
    @patch('dls_ade.vcs_git.git.Repo.clone_from')
    def test_given_repo_exists_then_git_clone_called(self, mock_clone, _, mock_check):

        repo_url = "ssh://dascgitolite@dasc-git.diamond.ac.uk/controls/support/dummy"
        module = "dummy"
        options = FakeOptions()

        vcs = vcs_git.Git(module, options)

        n_clone_calls = mock_clone.call_count

        self.assertEqual(1, n_clone_calls)

    @patch('dls_ade.vcs_git.subprocess.check_output', return_value=['controls/support/dummy'])
    @patch('dls_ade.vcs_git.git.Repo.clone_from')
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

    @patch('dls_ade.vcs_git.subprocess.check_output', return_value=['controls/ioc/domain/mod'])
    @patch('dls_ade.vcs_git.git.Repo.clone_from')
    def test_given_repo_with_domain_code_then_tempdir_arg_has_forwardslash_removed(self, mock_clone, mock_check):

        repo_url = "ssh://dascgitolite@dasc-git.diamond.ac.uk/controls/ioc/domain/mod"
        module = "domain/mod"
        options = FakeOptions(area="ioc")

        vcs = vcs_git.Git(module, options)

        args, kwargs = mock_clone.call_args
        target_dir = args[1]

        os.rmdir(target_dir)

        self.assertTrue(target_dir.startswith("/tmp/tmp"))
        self.assertTrue(target_dir.endswith("_" + module.replace("/","_")))


class GitCatTest(unittest.TestCase):

    @patch('dls_ade.vcs_git.subprocess.check_output', return_value=['controls/support/dummy'])
    @patch('dls_ade.vcs_git.git.Repo.clone_from', return_value=vcs_git.git.Repo)  # @UndefinedVariable
    @patch('dls_ade.vcs_git.tempfile.mkdtemp')
    def setUp(self, mtemp, mclone, mcheckout):

        client_cat_patch = patch('dls_ade.vcs_git.git.Repo.git')
        self.addCleanup(client_cat_patch.stop)
        self.mgit = client_cat_patch.start()
        self.mgit.cat_file = MagicMock(return_value=1)

        self.module = 'dummy'
        self.options = FakeOptions()
        self.vcs = vcs_git.Git(self.module, self.options)

    def test_given_version_not_set_when_called_then_second_argument_to_catfile_starts_with_master(self):

        filename = 'configure/RELEASE'
        expected_arg = 'master:' + filename

        self.vcs.cat(filename)

        self.mgit.cat_file.assert_called_once_with(ANY, expected_arg)

    def test_when_called_then_first_arg_is_dash_p(self):

        dash_p_arg = '-p'

        self.vcs.cat('file')

        self.mgit.cat_file.assert_called_once_with(dash_p_arg, ANY)

    @patch('dls_ade.vcs_git.Git.list_releases',return_value='0-2')
    def test_given_version_is_set_when_called_then_second_argument_to_catfile_starts_with_version(self, mlist):

        version = '0-2'
        filename = 'configure/RELEASE'
        expected_arg = version + ':' + filename

        self.vcs.set_version(version)
        self.vcs.cat(filename)

        self.mgit.cat_file.assert_called_once_with(ANY, expected_arg)

    @patch('dls_ade.vcs_git.Git.list_releases',return_value='0-2')
    def test_given_version_is_set_but_non_existent_then_version_used_for_cat_is_master(self, mlist):

        version = '0-3'
        filename = 'configure/RELEASE'
        expected_arg = 'master:' + filename

        self.vcs._version = version
        self.vcs.cat(filename)

        self.mgit.cat_file.assert_called_once_with(ANY, expected_arg)


class GitListReleasesTest(unittest.TestCase):

    @patch('dls_ade.vcs_git.subprocess.check_output', return_value=['controls/support/dummy'])
    @patch('dls_ade.vcs_git.git.Repo.clone_from')
    @patch('dls_ade.vcs_git.tempfile.mkdtemp')
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

    @patch('dls_ade.vcs_git.subprocess.check_output', return_value=['controls/support/dummy'])
    @patch('dls_ade.vcs_git.git.Repo.clone_from')
    @patch('dls_ade.vcs_git.tempfile.mkdtemp')
    def setUp(self, mtemp, mclone, mcheck):

        self.module = 'dummy'
        self.options = FakeOptions()

        self.vcs = vcs_git.Git(self.module, self.options)

    def test_given_message_arg_when_method_invoked_then_return_None(self):

        result = self.vcs.set_log_message('reason for commit')

        self.assertIsNone(result)


class GitCheckVersionTest(unittest.TestCase):

    @patch('dls_ade.vcs_git.subprocess.check_output', return_value=['controls/support/dummy'])
    @patch('dls_ade.vcs_git.git.Repo.clone_from')
    @patch('dls_ade.vcs_git.tempfile.mkdtemp')
    def setUp(self, mtemp, mclone, mcheck):

        self.module = 'dummy'
        self.options = FakeOptions()

        self.vcs = vcs_git.Git(self.module, self.options)

    @patch('dls_ade.vcs_git.Git.list_releases')
    def test_given_version_in_list_of_releases_then_return_true(self, mlist):
        
        version = '1-5'
        mlist.return_value = ['1-4','1-5','1-6']

        self.assertTrue(self.vcs.check_version_exists(version))

    @patch('dls_ade.vcs_git.Git.list_releases')
    def test_given_version_not_in_list_of_releases_then_return_false(self, mlist):
        
        version = '1-5'
        mlist.return_value = ['1-4','2-5','1-6']

        self.assertFalse(self.vcs.check_version_exists(version))


class ApiInterrogateTest(unittest.TestCase):

    @patch('dls_ade.vcs_git.subprocess.check_output', return_value=['controls/support/dummy'])
    @patch('dls_ade.vcs_git.git.Repo.clone_from')
    @patch('dls_ade.vcs_git.tempfile.mkdtemp')
    def setUp(self, _1, _2, _3):

        self.module = 'dummy'
        self.options = FakeOptions()
        self.vcs = vcs_git.Git(self.module, self.options)

    def test_when_asking_object_for_vcs_type_then_return_git_in_string(self):

        vcs_type = self.vcs.vcs_type

        self.assertEqual(vcs_type, 'git')

    def test_when_calling_source_repo_then_return_url_of_gitolite_repo(self):

        expected_source_repo = 'ssh://dascgitolite@dasc-git.diamond.ac.uk/'
        expected_source_repo += 'controls/'+self.options.area+'/'+self.module

        source_repo = self.vcs.source_repo

        self.assertEqual(source_repo, expected_source_repo)


class GitSettersTest(unittest.TestCase):

    @patch('dls_ade.vcs_git.subprocess.check_output', return_value=['controls/support/dummy'])
    @patch('dls_ade.vcs_git.git.Repo.clone_from')
    @patch('dls_ade.vcs_git.tempfile.mkdtemp')
    def setUp(self, mtemp, mclone, mcheck):

        self.module = 'dummy'
        self.options = FakeOptions()

        self.vcs = vcs_git.Git(self.module, self.options)

    def test_when_set_branch_called_then_raise_notimplementederror(self):

        with self.assertRaises(NotImplementedError):
            self.vcs.set_branch('some_branch')

    def test_given_vcs_when_version_not_set_then_get_version_raise_error(self):

        with self.assertRaises(Exception):
            self.vcs.version

    @patch('dls_ade.vcs_git.Git.check_version_exists', return_value=True)
    def test_given_vcs_when_version_set_return_version(self, mcheck):

        version = '0-1'

        self.vcs.set_version(version)

        self.assertEqual(self.vcs.version, version)

    @patch('dls_ade.vcs_git.Git.check_version_exists', return_value=False)
    def test_given_nonexistent_version_when_version_set_then_raise_error(self, mcheck):

        version = '0-2'

        with self.assertRaises(Exception):
            self.vcs.set_version(version);


class GitReleaseVersionTest(unittest.TestCase):

    @patch('dls_ade.vcs_git.subprocess.check_output', return_value=['controls/support/dummy'])
    @patch('dls_ade.vcs_git.git.Repo.clone_from')
    @patch('dls_ade.vcs_git.tempfile.mkdtemp')
    def setUp(self, mtemp, mclone, mcheck):

        self.module = 'dummy'
        self.options = FakeOptions()

        self.vcs = vcs_git.Git(self.module, self.options)

    def test_method_is_not_implemented(self):

        with self.assertRaises(NotImplementedError):
            self.vcs.release_version('some-version')


class FakeTag(object):
    def __init__(self, name):
        self.name = name


class FakeOptions(object):
    def __init__(self, **kwargs):
        self.area = kwargs.get('area', 'support')


if __name__ == '__main__':

    # buffer option suppresses stdout generated from tested code
    unittest.main(buffer=True)
