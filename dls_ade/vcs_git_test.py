import unittest
from mock import patch, ANY, MagicMock, PropertyMock, call  # @UnresolvedImport

from dls_ade import vcs_git, gitserver, Server


class FakeCommit(str):
    def __init__(self, name):
        pass


def setUpModule():
    Server.GIT_SSH_ROOT = "ssh://GIT_SSH_ROOT/"
    Server.GIT_ROOT_DIR = "controlstest"
    gitserver.GIT_ROOT_DIR = "controlstest"


def set_up_mock(test_case_object, path):

    patch_obj = patch(path)

    test_case_object.addCleanup(patch_obj.stop)

    mock_obj = patch_obj.start()

    return mock_obj


class IsInLocalRepoTest(unittest.TestCase):

    def test_given_invalid_file_path_then_error_raised(self):
        path = "/not/a/path"

        with self.assertRaises(vcs_git.VCSGitError):
            vcs_git.is_in_local_repo(path)

    def test_given_not_git_dir_then_returns_false(self):
        path = "/"

        return_value = vcs_git.is_in_local_repo(path)

        self.assertFalse(return_value)

    @patch('dls_ade.vcs_git.git')
    def test_given_git_dir_then_returns_true(self, mock_git):
        path = "/"

        git_inst = MagicMock()
        git_inst.git.git_rev_parse.return_value = 'dummy'
        mock_git.Repo.return_value = git_inst

        return_value = vcs_git.is_in_local_repo(path)

        self.assertTrue(return_value)


class IsLocalRepoRootTest(unittest.TestCase):

    @patch('dls_ade.vcs_git.is_in_local_repo', return_value=True)
    @patch('dls_ade.vcs_git.git')
    def test_given_git_dir_then_git_repo_assigned_to_path(self, mock_git, _2):
        path = "test/path"

        git_inst = MagicMock()
        mock_git.Repo.return_value = git_inst
        git_inst.git = MagicMock()
        git_inst.git.rev_parse = MagicMock(return_value='test/path')

        vcs_git.is_local_repo_root(path)

        mock_git.Repo.assert_called_once_with(path)

    @patch('dls_ade.vcs_git.is_in_local_repo', return_value=False)
    @patch('dls_ade.vcs_git.git')
    def test_given_not_git_dir_then_git_repo_not_assigned(self, mock_git, _2):
        path = "test/path"

        git_inst = MagicMock()
        mock_git.Repo = git_inst

        vcs_git.is_local_repo_root(path)

        self.assertFalse(git_inst.call_count)

    @patch('dls_ade.vcs_git.os.getcwd', return_value="top/level/")
    @patch('dls_ade.vcs_git.is_in_local_repo', return_value=True)
    @patch('dls_ade.vcs_git.git')
    def test_given_git_dir_and_at_top_level_then_return_true(self, mock_git, _2, _3):
        path = "test/path"

        git_inst = MagicMock()
        mock_git.Repo.return_value = git_inst
        git_inst.git.rev_parse.return_value = "top/level/test/path"

        return_value = vcs_git.is_local_repo_root(path)

        self.assertTrue(return_value)

    @patch('dls_ade.vcs_git.os.getcwd', return_value="not/top/level/")
    @patch('dls_ade.vcs_git.is_in_local_repo', return_value=True)
    @patch('dls_ade.vcs_git.git')
    def test_given_git_dir_and_at_top_level_then_return_false(self, mock_git, _2, _3):
        path = "test/path"

        git_inst = MagicMock()
        mock_git.Repo.return_value = git_inst
        git_inst.git.rev_parse.return_value = "top/level/test/path"

        return_value = vcs_git.is_local_repo_root(path)

        self.assertFalse(return_value)

    @patch('dls_ade.vcs_git.is_in_local_repo', return_value=False)
    @patch('dls_ade.vcs_git.git')
    def test_given_not_git_dir_then_git_repo_return_false(self, mock_git, _2):
        path = "/test/path"

        git_inst = MagicMock()
        mock_git.Repo = git_inst
        mock_git.Repo.git.rev_parse.return_value = 'dummy'

        return_value = vcs_git.is_local_repo_root(path)

        self.assertFalse(return_value)


class InitRepoTest(unittest.TestCase):

    def setUp(self):

        self.patch_is_dir = patch('dls_ade.vcs_git.os.path.isdir')
        self.patch_is_local_repo_root = patch('dls_ade.vcs_git.is_local_repo_root')
        self.patch_git_repo_init = patch('dls_ade.vcs_git.git.Repo.init')

        self.addCleanup(self.patch_is_dir.stop)
        self.addCleanup(self.patch_is_local_repo_root.stop)
        self.addCleanup(self.patch_git_repo_init.stop)

        self.mock_is_dir = self.patch_is_dir.start()
        self.mock_is_local_repo_root = self.patch_is_local_repo_root.start()
        self.mock_git_repo_init = self.patch_git_repo_init.start()

    def test_given_is_dir_false_then_exception_raised_with_correct_message(self):

        self.mock_is_dir.return_value = False

        comp_message = "Path {path:s} is not a directory".format(path="fake_path")

        with self.assertRaises(vcs_git.VCSGitError) as e:
            vcs_git.init_repo("fake_path")

        self.mock_is_dir.assert_called_once_with("fake_path")
        self.assertEqual(str(e.exception), comp_message)

    @patch('git.Repo')
    def test_given_repo_exists_then_return_it(self, repo_mock):

        self.mock_is_dir.return_value = True
        self.mock_is_local_repo_root.return_value = True

        vcs_git.init_repo("existing_path")

        repo_mock.assert_called_once_with("existing_path")

    def test_given_both_tests_pass_then_repo_initialised_correctly(self):

        self.mock_is_dir.return_value = True
        self.mock_is_local_repo_root.return_value = False

        vcs_git.init_repo("test_path")

        self.mock_git_repo_init.assert_called_once_with("test_path")

    def test_given_no_input_then_sensible_default_applied(self):

        self.mock_is_dir.return_value = True
        self.mock_is_local_repo_root.return_value = False

        vcs_git.init_repo()

        self.mock_is_dir.assert_called_once_with("./")


class StageAllFilesAndCommitTest(unittest.TestCase):

    def setUp(self):
        self.patch_is_dir = patch('dls_ade.vcs_git.os.path.isdir')
        self.patch_is_local_repo_root = patch('dls_ade.vcs_git.is_local_repo_root')
        self.patch_git_repo = patch('dls_ade.vcs_git.git.Repo')

        self.addCleanup(self.patch_is_dir.stop)
        self.addCleanup(self.patch_is_local_repo_root.stop)
        self.addCleanup(self.patch_git_repo.stop)

        self.mock_is_dir = self.patch_is_dir.start()
        self.mock_is_local_repo_root = self.patch_is_local_repo_root.start()
        self.mock_git_repo = self.patch_git_repo.start()

        self.mock_repo = MagicMock()

        self.mock_git_repo.return_value = self.mock_repo

    def test_given_both_tests_pass_and_both_arguments_supplied_then_repo_committed_with_correct_arguments(self):

        self.mock_is_dir.return_value = True
        self.mock_is_local_repo_root.return_value = True

        vcs_git.stage_all_files_and_commit(self.mock_repo, "test_message")

        self.mock_repo.git.add.assert_called_once_with("--all")
        self.mock_repo.index.commit.assert_called_once_with("test_message")

    def test_given_git_commit_raises_exception_then_function_does_not_raise_exception(self):

        self.mock_is_dir.return_value = True
        self.mock_is_local_repo_root.return_value = True
        self.mock_repo.git.commit.side_effect = \
            vcs_git.git.exc.GitCommandError(["git", "checkout", "master"], 1)

        vcs_git.stage_all_files_and_commit(self.mock_repo, "test_message")

        self.mock_repo.git.add.assert_called_once_with("--all")
        self.mock_repo.index.commit.assert_called_once_with("test_message")


class AddNewRemoteAndPushTest(unittest.TestCase):

    class BranchEntry(object):
        def __init__(self, name):
            self.name = name  # Allows us to specify x.name in list comprehension

    class RemoteEntry(object):
        def __init__(self, name):
            self.name = name

    class StubGitRepo(object):  # Used to mock out the git.Repo() function
        def __init__(self, branches_list, remotes_list, mock_remote, mock_create_remote):
            self.branches = branches_list  # set this to a list eg. [BranchEntry("branch_name")] for list comprehension
            self.remotes = remotes_list
            self.mock_remote = mock_remote
            self.mock_create_remote = mock_create_remote

        def create_remote(self, *args):
            self.mock_create_remote(*args)  # allows us to interrogate the calls to repo.create_remote()
            return self.mock_remote

    def setUp(self):
        self.patch_is_local_repo_root = patch('dls_ade.vcs_git.is_local_repo_root')
        self.patch_create_remote_repo = patch('dls_ade.gitserver.GitServer.create_remote_repo')
        self.patch_git = patch('dls_ade.vcs_git.git')

        self.addCleanup(self.patch_is_local_repo_root.stop)
        self.addCleanup(self.patch_create_remote_repo.stop)
        self.addCleanup(self.patch_git.stop)

        self.mock_is_local_repo_root = self.patch_is_local_repo_root.start()
        self.mock_create_remote_repo = self.patch_create_remote_repo.start()
        self.mock_git = self.patch_git.start()

    def test_given_branch_name_not_in_repo_branches_then_exception_raised_with_correct_message(self):

        self.mock_is_local_repo_root.return_value = True
        branches_list = [self.BranchEntry("branch_1"), self.BranchEntry("branch_2"), self.BranchEntry("branch_3")]
        mock_repo = self.StubGitRepo(branches_list, [], MagicMock(), MagicMock())
        self.mock_git.Repo.return_value = mock_repo

        comp_message = "Local repository branch {branch:s} does not currently exist.".format(branch="test_branch")

        git_inst = vcs_git.Git("test_module", "area")
        git_inst.repo = mock_repo

        with self.assertRaises(vcs_git.VCSGitError) as e:
            git_inst.add_new_remote_and_push("test_destination", branch_name="test_branch")

        self.assertEqual(str(e.exception), comp_message)

    def test_given_remote_name_in_repo_remotes_then_exception_raised_with_correct_message(self):

        self.mock_is_local_repo_root.return_value = True
        branches_list = [self.BranchEntry("test_branch")]
        remotes_list = [self.RemoteEntry("remote_1"), self.RemoteEntry("remote_2"), self.RemoteEntry("test_remote")]
        mock_repo = self.StubGitRepo(branches_list, remotes_list, MagicMock(), MagicMock())

        comp_message = "Cannot push local repository to destination as remote {remote:s} is already defined"
        comp_message = comp_message.format(remote="test_remote")

        git_inst = vcs_git.Git("test_module", "area")
        git_inst.repo = mock_repo

        with self.assertRaises(vcs_git.VCSGitError) as e:
            git_inst.add_new_remote_and_push("test_destination", remote_name="test_remote", branch_name="test_branch")

        self.assertEqual(str(e.exception), comp_message)

    def test_given_all_checks_pass_then_function_runs_correctly(self):

        mock_remote = MagicMock()  # Mock to represent the 'remote' local variable
        mock_create_remote = MagicMock()  # Mock to represent the 'create_remote' function

        self.mock_is_local_repo_root.return_value = True
        branches_list = [self.BranchEntry("test_branch")]
        mock_repo = self.StubGitRepo(branches_list, [], mock_remote, mock_create_remote)
        self.mock_git.Repo.return_value = mock_repo

        server_mock = MagicMock()
        server_mock.url = "test@url.ac.uk"
        server_mock.dev_module_path.return_value = 'dummy-string'
        git_inst = vcs_git.Git("test_module", "area", server_mock)
        git_inst.repo = mock_repo

        git_inst.add_new_remote_and_push("test_destination", remote_name="test_remote", branch_name="test_branch")

        server_mock.create_remote_repo.assert_called_once_with("test_destination")
        mock_create_remote.assert_called_once_with(
            "test_remote", "test@url.ac.uk/test_destination")
        mock_remote.push.assert_called_once_with("test_branch")


    def test_given_only_destination_given_then_sensible_defaults_applied(self):

        mock_remote = MagicMock()  # Mock to represent the 'remote' local variable
        mock_create_remote = MagicMock()  # Mock to represent the 'create_remote' function

        self.mock_is_local_repo_root.return_value = True
        branches_list = [self.BranchEntry("master")]
        mock_repo = self.StubGitRepo(branches_list, [], mock_remote, mock_create_remote)

        server_mock = MagicMock()
        server_mock.url = "test@url.ac.uk"
        server_mock.dev_module_path.return_value = 'dummy-string'
        git_inst = vcs_git.Git("test_module", "area", server_mock)
        git_inst.repo = mock_repo

        git_inst.add_new_remote_and_push("test_destination")

        server_mock.create_remote_repo.assert_called_once_with("test_destination")
        mock_create_remote.assert_called_once_with(
            "gitolite", "test@url.ac.uk/test_destination")
        mock_remote.push.assert_called_once_with("master")


class PushToRemoteTest(unittest.TestCase):

    class BranchEntry(object):
        def __init__(self, name):
            self.name = name  # Allows us to specify x.name in list comprehension

    class TagEntry(object):
        def __init__(self, name):
            self.name = name  # Allows us to specify x.name in list comprehension

    class RemoteEntry(object):
        def __init__(self, name):
            self.name = name

    class StubGitRepo(object):  # Used to mock out the git.Repo() function
        def __init__(self, branches_list, tags_list, remotes_list, mock_remote, remote_name="origin", remote_url=""):

            self.branches = branches_list  # set this to a list eg. [BranchEntry("branch_name")] for list comprehension
            self.tags = tags_list  # set this to a list e.g. [TagEntry("tag name")] for list comprehension
            self.remotes_list = remotes_list
            self.remotes_count = 0

            self.mock_remote = mock_remote
            mock_url = PropertyMock(return_value=remote_url)
            type(self.mock_remote).url = mock_url
            self.remote_name = remote_name

        @property  # Needed to change result for second .branches request - don't want to overload dictionary lookup!
        def remotes(self):
            if self.remotes_count == 0:
                self.remotes_count = 1
                return self.remotes_list
            else:
                return {self.remote_name: self.mock_remote}

    def setUp(self):

        self.patch_is_local_repo_root = patch('dls_ade.vcs_git.is_local_repo_root')
        self.patch_create_remote_repo = patch('dls_ade.Server.create_remote_repo')
        self.patch_is_server_repo = patch('dls_ade.Server.is_server_repo')
        self.patch_git = patch('dls_ade.vcs_git.git')

        self.addCleanup(self.patch_is_local_repo_root.stop)
        self.addCleanup(self.patch_create_remote_repo.stop)
        self.addCleanup(self.patch_is_server_repo.stop)
        self.addCleanup(self.patch_git.stop)

        self.mock_is_local_repo_root = self.patch_is_local_repo_root.start()
        self.mock_create_remote_repo = self.patch_create_remote_repo.start()
        self.mock_is_server_repo = self.patch_is_server_repo.start()
        self.mock_git = self.patch_git.start()

    def test_given_branch_name_not_in_repo_branches_then_exception_raised_with_correct_message(self):

        self.mock_is_local_repo_root.return_value = True
        branches_list = [self.BranchEntry("branch_1"), self.BranchEntry("branch_2"), self.BranchEntry("branch_3")]
        mock_repo = self.StubGitRepo(branches_list, [], [], MagicMock())
        self.mock_git.Repo.return_value = mock_repo

        comp_message = "Local repository branch/tag {branch:s} does not currently exist.".format(branch="test_branch")

        repo = vcs_git.Git("test_module", "area", repo=mock_repo)

        with self.assertRaises(vcs_git.VCSGitError) as e:
            repo.push_to_remote(ref="test_branch")

        self.assertEqual(str(e.exception), comp_message)

    def test_given_tag_name_not_in_repo_branches_then_exception_raised_with_correct_message(self):
            self.mock_is_local_repo_root.return_value = True
            tags_list = [self.TagEntry("tag_1"),
                         self.TagEntry("tag_2"),
                         self.TagEntry("tag_3")]
            mock_repo = self.StubGitRepo([], tags_list, [], MagicMock())
            self.mock_git.Repo.return_value = mock_repo

            comp_message = "Local repository branch/tag {branch:s} does not currently exist.".format(
                branch="test_tag")

            repo = vcs_git.Git("test_module", "area", repo=mock_repo)

            with self.assertRaises(vcs_git.VCSGitError) as e:
                repo.push_to_remote(ref="test_tag")

            self.assertEqual(str(e.exception), comp_message)

    def test_given_remote_name_does_not_exist_then_exception_raised_with_correct_message(self):

        self.mock_is_local_repo_root.return_value = True
        branches_list = [self.BranchEntry("test_branch")]
        remotes_list = [self.RemoteEntry("remote_1"), self.RemoteEntry("remote_2"), self.RemoteEntry("remote_3")]
        mock_repo = self.StubGitRepo(branches_list, [], remotes_list, MagicMock())
        self.mock_git.Repo.return_value = mock_repo

        comp_message = "Local repository does not have remote {remote:s}".format(remote="test_remote")

        repo = vcs_git.Git("test_module", "area", repo=mock_repo)

        with self.assertRaises(vcs_git.VCSGitError) as e:
            repo.push_to_remote(remote_name="test_remote", ref="test_branch")

        self.assertEqual(str(e.exception), comp_message)

    def test_given_remote_url_does_not_start_with_git_ssh_root_then_exception_raised_with_correct_message(self):

        self.mock_is_local_repo_root.return_value = True
        branches_list = [self.BranchEntry("test_branch")]
        remotes_list = [self.RemoteEntry("test_remote")]
        mock_repo = self.StubGitRepo(branches_list, [], remotes_list, MagicMock(), "test_remote", "ssh://GIT_FAKE_SSH_ROOT/test_URL")
        self.mock_git.Repo.return_value = mock_repo

        comp_message = "Remote repository URL {remoteURL:s} does not begin with the parent server path".format(remoteURL="ssh://GIT_FAKE_SSH_ROOT/test_URL")

        server_mock = MagicMock()
        server_mock.url = "ssh://GIT_SSH_ROOT/"
        server_mock.dev_module_path.return_value = 'dummy-string'
        repo = vcs_git.Git("test_module", "area", server_mock, mock_repo)

        with self.assertRaises(vcs_git.VCSGitError) as e:
            repo.push_to_remote(remote_name="test_remote", ref="test_branch")
        self.assertEqual(str(e.exception), comp_message)

    def test_given_is_server_repo_false_then_exception_raised_with_correct_message(self):

        mock_remote = MagicMock()

        self.mock_is_local_repo_root.return_value = True
        branches_list = [self.BranchEntry("test_branch")]
        remotes_list = [self.RemoteEntry("test_remote")]
        mock_repo = self.StubGitRepo(branches_list, [], remotes_list, mock_remote, "test_remote", "ssh://GIT_SSH_ROOT/test_URL")
        self.mock_git.Repo.return_value = mock_repo

        self.mock_is_server_repo.return_value = False

        comp_message = "Server repo path {s_repo_path:s} does not currently exist".format(s_repo_path="test_URL")

        server_mock = MagicMock()
        server_mock.url = "ssh://GIT_SSH_ROOT/"
        server_mock.dev_module_path.return_value = 'dummy-string'
        server_mock.is_server_repo.return_value = False
        repo = vcs_git.Git("test_module", "area", server_mock, mock_repo)

        with self.assertRaises(vcs_git.VCSGitError) as e:
            repo.push_to_remote(remote_name="test_remote", ref="test_branch")

        self.assertEqual(str(e.exception), comp_message)
        server_mock.is_server_repo.assert_called_once_with("test_URL")

    def test_given_all_checks_pass_then_function_runs_correctly(self):

        mock_remote = MagicMock()

        self.mock_is_local_repo_root.return_value = True
        branches_list = [self.BranchEntry("test_branch")]
        remotes_list = [self.RemoteEntry("test_remote")]
        mock_repo = self.StubGitRepo(branches_list, [], remotes_list, mock_remote, "test_remote", "ssh://GIT_SSH_ROOT/test_URL")
        self.mock_git.Repo.return_value = mock_repo

        self.mock_is_server_repo.return_value = True

        server_mock = MagicMock()
        server_mock.url = "ssh://GIT_SSH_ROOT/"
        server_mock.dev_module_path.return_value = 'dummy-string'
        repo = vcs_git.Git("test_module", "area", server_mock, repo=mock_repo)

        repo.push_to_remote(remote_name="test_remote", ref="test_branch")

        mock_remote.push.assert_called_once_with("test_branch")

    def test_given_no_input_then_sensible_defaults_applied(self):

        mock_remote = MagicMock()

        self.mock_is_local_repo_root.return_value = True
        branches_list = [self.BranchEntry("master")]  # Set these to the function's default values
        remotes_list = [self.RemoteEntry("gitolite")]
        mock_repo = self.StubGitRepo(branches_list, [], remotes_list, mock_remote, "gitolite", "ssh://GIT_SSH_ROOT/test_URL")
        self.mock_git.Repo.return_value = mock_repo

        server_mock = MagicMock()
        server_mock.url = "ssh://GIT_SSH_ROOT/"
        server_mock.dev_module_path.return_value = 'dummy-string'
        repo = vcs_git.Git("test_module", "area", server_mock, mock_repo)

        repo.push_to_remote()

        mock_remote.push.assert_called_once_with("master")


class CheckRemoteExistsTest(unittest.TestCase):

    class RemoteEntry(object):
        def __init__(self, name):
            self.name = name

    class StubGitRepo(object):  # Used to mock out the git.Repo() function
        def __init__(self, remotes_list):

            self.remotes_list = remotes_list  # set this to a list eg. [RemoteEntry("branch_name")] for list comprehension

        @property
        def remotes(self):
            return self.remotes_list

    def test_given_remote_name_does_not_exist_then_exception_raised_with_correct_message(self):

        remotes_list = [self.RemoteEntry("remote_1"), self.RemoteEntry("remote_2"), self.RemoteEntry("remote_3")]
        mock_repo = self.StubGitRepo(remotes_list)

        comp_message = "Local repository does not have remote {remote:s}".format(remote="test_remote")

        with self.assertRaises(vcs_git.VCSGitError) as e:
            vcs_git.check_remote_exists(mock_repo, "test_remote")

        self.assertEqual(str(e.exception), comp_message)

    def test_given_remote_name_exists_then_no_exception_raised(self):

        remotes_list = [self.RemoteEntry("test_remote")]
        mock_repo = self.StubGitRepo(remotes_list)

        vcs_git. check_remote_exists(mock_repo, "test_remote")


class HasRemoteTest(unittest.TestCase):

    class RemoteEntry(object):
        def __init__(self, name):
            self.name = name

    class StubGitRepo(object):  # Used to mock out the git.Repo() function
        def __init__(self, remotes_list):

            self.remotes_list = remotes_list  # set this to a list eg. [RemoteEntry("branch_name")] for list comprehension

        @property
        def remotes(self):
            return self.remotes_list

    def test_given_remote_name_does_not_exist_then_function_returns_false(self):

        remotes_list = [self.RemoteEntry("remote_1"), self.RemoteEntry("remote_2"), self.RemoteEntry("remote_3")]
        mock_repo = self.StubGitRepo(remotes_list)

        value = vcs_git.has_remote(mock_repo, "test_remote")

        self.assertFalse(value)

    def test_given_remote_name_exists_then_function_returns_true(self):

        remotes_list = [self.RemoteEntry("test_remote")]
        mock_repo = self.StubGitRepo(remotes_list)

        value = vcs_git.has_remote(mock_repo, "test_remote")

        self.assertTrue(value)


class ListModuleReleases(unittest.TestCase):

    def test_given_repo_with_tags_then_listed(self):

        repo_inst = MagicMock()
        vcs_git.git.repo = repo_inst
        tag_inst_1 = MagicMock()
        tag_inst_1.name = '1-0'
        tag_inst_2 = MagicMock()
        tag_inst_2.name = '2-0'
        tag_inst_3 = MagicMock()
        tag_inst_3.name = '2-1'

        repo_inst.tags = [tag_inst_1, tag_inst_2, tag_inst_3]

        releases = vcs_git.list_module_releases(repo_inst)

        self.assertEqual(releases, ['1-0', '2-0', '2-1'])

    def test_given_repo_with_no_tags_then_empty_list_returned(self):
        repo_inst = MagicMock()
        vcs_git.git.repo = repo_inst

        repo_inst.tags = []

        releases = vcs_git.list_module_releases(repo_inst)

        self.assertFalse(releases)


class ListRemoteBranchesTest(unittest.TestCase):

    @patch('dls_ade.vcs_git.os.chdir')
    @patch('dls_ade.vcs_git.git')
    def test_given_module_with_invalid_entries_then_removed(self, mock_git, _2):

        repo_inst = MagicMock()
        repo_inst.references = ["origin/HEAD", "origin/master",
                                "origin/1-5-8fixes", "master",
                                "waveforms", "1-0, 2-1"]
        repo_inst.branches = ["master", "waveforms"]
        repo_inst.tags = ["1-0, 2-1"]

        branches = vcs_git.list_remote_branches(repo_inst)

        self.assertNotIn('->', branches)
        self.assertNotIn('HEAD', branches)
        self.assertIn('master', branches)
        self.assertNotIn('1-0', branches)
        self.assertNotIn('2-1', branches)

    @patch('dls_ade.vcs_git.os.chdir')
    @patch('dls_ade.vcs_git.git')
    def test_given_module_with_valid_entries_then_not_removed(self, mock_git, _2):

        repo = MagicMock()
        mock_git.Repo = repo
        repo.references = ["origin/1-5-8fixes", "origin/3-x-branch",
                                        "origin/3104_rev14000a_support"]


        branches = vcs_git.list_remote_branches(repo)

        self.assertIn('1-5-8fixes', branches)
        self.assertIn('3-x-branch', branches)
        self.assertIn('3104_rev14000a_support', branches)


class CheckoutRemoteBranchTest(unittest.TestCase):

    @patch('dls_ade.vcs_git.has_remote', return_value=True)
    @patch('dls_ade.vcs_git.list_remote_branches', return_value=['test_module'])
    @patch('dls_ade.vcs_git.git')
    def test_given_valid_branch_then_checkout_called(self, mock_git, _2, _3):
        branch = "test_module"

        repo = MagicMock()
        mock_git.Repo = repo

        vcs_git.checkout_remote_branch(branch, repo)

        repo.remotes.origin.refs.__getitem__().checkout.assert_called_once_with(b=branch)

    @patch('dls_ade.vcs_git.list_remote_branches', return_value=['test_module'])
    @patch('dls_ade.vcs_git.git')
    def test_given_invalid_branch_then_checkout_not_called(self, mock_git, _2):
        branch = "not_a_module"

        repo = MagicMock()
        mock_git.Repo = repo

        vcs_git.checkout_remote_branch(branch, repo)

        self.assertFalse(repo.remotes.origin.refs.__getitem__().checkout.call_count)


class CheckGitAttributesTest(unittest.TestCase):

    @staticmethod
    def check_attr_side_effect(argument):
        if argument == "attr1 -- .".split():
            return ".: attr1: Valueofattr1"
        elif argument == "attr2 -- .".split():
            return ".: attr2: Now_with_spaces"
        elif argument == "attr3-name -- .".split():
            return ".: attr3-name: But_spaces_arent_really_allowed"
        elif argument == "attr-not-exist -- .".split():
            return ".: attr-not-exist: unspecified"

    @patch('dls_ade.vcs_git.git.Repo')
    def test_given_all_attributes_exist_then_function_returns_true(self, mock_repo_class):

        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo

        mock_repo.git.check_attr.side_effect = CheckGitAttributesTest.check_attr_side_effect

        attributes_dict = {
            'attr1': "Valueofattr1",
            'attr2': "Now_with_spaces",
            'attr3-name': "But_spaces_arent_really_allowed"
        }

        return_value = vcs_git.check_git_attributes(mock_repo, attributes_dict)

        self.assertTrue(return_value)

    @patch('dls_ade.vcs_git.git.Repo')
    def test_given_some_attributes_dont_exist_then_function_returns_false(self, mock_repo_class):

        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo

        mock_repo.git.check_attr.side_effect = CheckGitAttributesTest.check_attr_side_effect

        attributes_dict = {
            'attr1': "Valueofattr1",
            'attr2': "Now_with_spaces",
            'attr3-name': "But_spaces_arent_really_allowed",
            'attr-not-exist': "I_do_not_exist"
        }

        return_value = vcs_git.check_git_attributes(mock_repo, attributes_dict)

        self.assertFalse(return_value)

    @patch('dls_ade.vcs_git.git.Repo')
    def test_given_some_attributes_dont_exist_but_we_set_value_to_unspecified_then_function_returns_True(self, mock_repo_class):

        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo

        mock_repo.git.check_attr.side_effect = CheckGitAttributesTest.check_attr_side_effect

        attributes_dict = {
            'attr1': "Valueofattr1",
            'attr2': "Now_with_spaces",
            'attr3-name': "But_spaces_arent_really_allowed",
            'attr-not-exist': "unspecified"
        }

        return_value = vcs_git.check_git_attributes(mock_repo, attributes_dict)

        self.assertTrue(return_value)


class GetActiveBranchTest(unittest.TestCase):

    def test_returns_active_branch_correctly(self):

        mock_repo = MagicMock()
        type(mock_repo.active_branch).name = PropertyMock(return_value="current_active_branch")

        return_value = vcs_git.get_active_branch(mock_repo)

        self.assertEqual(return_value, "current_active_branch")


class DeleteRemoteTest(unittest.TestCase):

    class RemoteEntry(object):
        def __init__(self, name):
            self.name = name

    class StubGitRepo(object):  # Used to mock out the git.Repo() function
        def __init__(self, remotes_list, mock_repo_git=MagicMock()):

            self.remotes_list = remotes_list  # set this to a list eg. [RemoteEntry("branch_name")] for list comprehension
            self.git = mock_repo_git

        @property
        def remotes(self):
            return self.remotes_list

        def delete_remote(self):
            return 0

    def test_given_remote_does_not_exist_then_exception_raised_with_correct_message(self):

        remotes_list = [self.RemoteEntry("remote_1"), self.RemoteEntry("remote_2"), self.RemoteEntry("remote_3")]
        mock_repo = DeleteRemoteTest.StubGitRepo(remotes_list)

        with self.assertRaises(vcs_git.VCSGitError) as e:
            vcs_git.delete_remote(mock_repo, "test_remote")

        self.assertTrue("test_remote" in str(e.exception))

    def test_given_remote_does_exist_then_remote_properly_deleted(self):

        remotes_list = [self.RemoteEntry("test_remote")]
        mock_repo = MagicMock()
        mock_repo.remotes = remotes_list

        vcs_git.delete_remote(mock_repo, "test_remote")

        mock_repo.delete_remote.assert_called_once_with("test_remote")


class PushAllBranchesAndTagsTest(unittest.TestCase):

    def setUp(self):
        self.mock_git = set_up_mock(self, "dls_ade.vcs_git.git")
        self.mock_delete = set_up_mock(self, "dls_ade.vcs_git.delete_remote")
        self.mock_has_remote = set_up_mock(self, "dls_ade.vcs_git.has_remote")

        self.mock_repo = MagicMock()

        self.mock_git.Repo.return_value = self.mock_repo

    def test_given_remote_does_not_exist_then_remote_not_deleted_and_rest_of_function_called_correctly(self):

        self.mock_has_remote.return_value = False

        server_mock = MagicMock()
        server_mock.url = "ssh://GIT_SSH_ROOT/"
        server_mock.dev_module_path.return_value = 'dummy-string'
        repo = vcs_git.Git("test_module", "area", server_mock, self.mock_repo)

        repo.push_all_branches_and_tags("test_server_path", "test_remote")

        self.mock_repo.create_remote.assert_called_once_with("test_remote", "ssh://GIT_SSH_ROOT/test_server_path")

        push_call_list = [call("test_remote", "*:*"), call("test_remote", "--tags")]

        self.mock_repo.git.push.assert_has_calls(push_call_list)

    def test_given_remote_exists_then_remote_deleted_and_rest_of_function_called_correctly(self):

        self.mock_has_remote.return_value = True

        server_mock = MagicMock()
        server_mock.url = "ssh://GIT_SSH_ROOT/"
        server_mock.dev_module_path.return_value = 'dummy-string'
        repo = vcs_git.Git("test_module", "area", server_mock, self.mock_repo)

        repo.push_all_branches_and_tags("test_server_path", "test_remote")

        self.mock_delete.assert_called_once_with(self.mock_repo, "test_remote")

        self.mock_repo.create_remote.assert_called_once_with("test_remote", "ssh://GIT_SSH_ROOT/test_server_path")

        push_call_list = [call("test_remote", "*:*"), call("test_remote", "--tags")]

        self.mock_repo.git.push.assert_has_calls(push_call_list)


class GitClassInitTest(unittest.TestCase):

    def test_given_parent_then_set_remote_repo(self):

        server_mock = MagicMock()
        server_mock.url = "test@server.ac.uk"
        server_mock.dev_module_path.return_value = "controlstest/support/dummy"
        repo_mock = MagicMock()

        git_inst = vcs_git.Git("dummy", "support", server_mock, repo_mock)

        self.assertEqual("dummy", git_inst._module)
        self.assertEqual("support", git_inst.area)
        self.assertEqual(repo_mock, git_inst.repo)
        self.assertIsNone(git_inst._version)

        self.assertEqual(server_mock, git_inst.parent)
        self.assertEqual("test@server.ac.uk/controlstest/support/dummy",
                         git_inst._remote_repo)

    def test_given_no_parent_then_set_as_None(self):
        repo_mock = MagicMock()

        git = vcs_git.Git("dummy", "support", repo=repo_mock)

        self.assertEqual("dummy", git._module)
        self.assertEqual("support", git.area)
        self.assertEqual(repo_mock, git.repo)
        self.assertIsNone(git._version)

        self.assertIsNone(git.parent)
        self.assertIsNone(git._remote_repo)


class GitCatTest(unittest.TestCase):

    @patch('dls_ade.vcs_git.git.Repo.clone_from', return_value=vcs_git.git.Repo)  # @UndefinedVariable
    def setUp(self, mclone):

        self.patch_is_server_repo = patch('dls_ade.Server.is_server_repo')
        self.addCleanup(self.patch_is_server_repo.stop)
        self.mock_is_server_repo = self.patch_is_server_repo.start()

        self.mock_is_server_repo.return_value = True

        client_cat_patch = patch('dls_ade.vcs_git.git.Repo.git')
        self.addCleanup(client_cat_patch.stop)
        self.mgit = client_cat_patch.start()
        self.mgit.cat_file = MagicMock(return_value=1)

        self.module = 'dummy'
        self.area = "support"
        self.repo_mock = MagicMock()
        self.vcs = vcs_git.Git(self.module, self.area, repo=self.repo_mock)

    def test_given_version_not_set_when_called_then_second_argument_to_catfile_starts_with_master(self):

        filename = 'configure/RELEASE'
        expected_arg = 'master:' + filename

        self.vcs.cat(filename)

        self.repo_mock.git.cat_file.assert_called_once_with(ANY, expected_arg)

    def test_when_called_then_first_arg_is_dash_p(self):

        dash_p_arg = '-p'

        self.vcs.cat('file')

        self.repo_mock.git.cat_file.assert_called_once_with(dash_p_arg, ANY)

    @patch('dls_ade.vcs_git.Git.list_releases',return_value='0-2')
    def test_given_version_is_set_when_called_then_second_argument_to_catfile_starts_with_version(self, mlist):

        version = '0-2'
        filename = 'configure/RELEASE'
        expected_arg = version + ':' + filename

        self.vcs.set_version(version)
        self.vcs.cat(filename)

        self.repo_mock.git.cat_file.assert_called_once_with(ANY, expected_arg)

    @patch('dls_ade.vcs_git.Git.list_releases',return_value='0-2')
    def test_given_version_is_set_but_non_existent_then_version_used_for_cat_is_master(self, mlist):

        version = '0-3'
        filename = 'configure/RELEASE'
        expected_arg = 'master:' + filename

        self.vcs._version = version
        self.vcs.cat(filename)

        self.repo_mock.git.cat_file.assert_called_once_with(ANY, expected_arg)

    def test_given_non_existent_target_file_when_called_then_return_empty_string(self):

        self.repo_mock.git.cat_file.side_effect = \
            vcs_git.git.GitCommandError('abc', 123, 'raised in mock of cat_file')
        filename = 'non/existent/file'

        result = self.vcs.cat(filename)

        self.assertIsInstance(result, str)
        self.assertEqual(len(result), 0)


class GitListReleasesTest(unittest.TestCase):

    @patch('dls_ade.vcs_git.git.Repo.clone_from')
    def setUp(self, mclone):

        self.patch_is_server_repo = patch('dls_ade.Server.is_server_repo')
        self.addCleanup(self.patch_is_server_repo.stop)
        self.mock_is_server_repo = self.patch_is_server_repo.start()

        self.mock_is_server_repo.return_value = True

        self.module = 'dummy'
        self.area = "support"

        server_mock = MagicMock()
        server_mock.url = "ssh://GIT_SSH_ROOT/"
        server_mock.dev_module_path.return_value = 'dummy-string'
        repo_mock = MagicMock()
        self.vcs = vcs_git.Git(self.module, self.area, server_mock, repo_mock)
        self.vcs.repo.tags = [FakeTag("1-0"), FakeTag("1-0-1"), FakeTag("2-0")]

    def test_given_repo_with_no_tags_then_return_empty_list(self):

        self.vcs.repo.tags = []
        releases = self.vcs.list_releases()

        self.assertListEqual([], releases)

    def test_given_repo_with_some_tags_then_return_list_inc_version_1_0(self):

        releases = self.vcs.list_releases()

        self.assertTrue('1-0' in releases)

    def test_given_repo_with_some_tags_then_return_all_version_tag_names(self):

        releases = self.vcs.list_releases()

        self.assertListEqual(['1-0', '1-0-1', '2-0'], releases)


class GitListCommitsTest(unittest.TestCase):

    @patch('dls_ade.vcs_git.git.Repo.clone_from')
    def setUp(self, mclone):

        self.patch_is_server_repo = patch('dls_ade.Server.is_server_repo')
        self.addCleanup(self.patch_is_server_repo.stop)
        self.mock_is_server_repo = self.patch_is_server_repo.start()

        self.mock_is_server_repo.return_value = True

        self.module = 'dummy'
        self.area = "support"

        server_mock = MagicMock()
        server_mock.url = "ssh://GIT_SSH_ROOT/"
        repo_mock = MagicMock()
        self.vcs = vcs_git.Git(self.module, self.area, server_mock, repo_mock)

    def test_given_repo_with_no_commits_then_return_empty_list(self):

        self.vcs.repo.iter_commits.return_value = []
        commits = self.vcs.list_commits()

        self.assertListEqual([], commits)

    def test_given_repo_with_some_commits_then_return_list_inc_commit(self):

        self.vcs.repo.iter_commits.return_value = [FakeCommit('32fdsb')]
        commits = self.vcs.list_commits()

        self.assertTrue('32fdsb' in commits)

    def test_given_repo_with_some_commits_then_return_all_commits(self):

        self.vcs.repo.iter_commits.return_value = [FakeCommit('32fdsb'), FakeCommit('2425sb')]
        commits = self.vcs.list_commits()

        self.assertListEqual(['32fdsb', '2425sb'], commits)


class GitSetLogMessageTest(unittest.TestCase):

    @patch('dls_ade.vcs_git.git.Repo.clone_from')
    def setUp(self, mclone):

        self.patch_is_server_repo = patch('dls_ade.Server.is_server_repo')
        self.addCleanup(self.patch_is_server_repo.stop)
        self.mock_is_server_repo = self.patch_is_server_repo.start()

        self.mock_is_server_repo.return_value = True

        self.module = 'dummy'
        self.options = FakeOptions()

        self.vcs = vcs_git.Git(self.module, self.options)

    def test_given_message_arg_when_method_invoked_then_return_None(self):

        result = self.vcs.set_log_message('reason for commit')

        self.assertIsNone(result)


class GitCheckVersionTest(unittest.TestCase):

    @patch('dls_ade.vcs_git.git.Repo.clone_from')
    def setUp(self, mclone):

        self.patch_is_server_repo = patch('dls_ade.Server.is_server_repo')
        self.addCleanup(self.patch_is_server_repo.stop)
        self.mock_is_server_repo = self.patch_is_server_repo.start()

        self.mock_is_server_repo.return_value = True

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

    @patch('dls_ade.vcs_git.Git.list_commits')
    def test_given_commit_in_list_of_commits_then_return_true(self, mlist):

        commit = '8ffb4'
        mlist.return_value = ['8ffb4130','432bdsa','1234bc']

        self.assertTrue(self.vcs.check_commit_exists(commit))

    @patch('dls_ade.vcs_git.Git.list_commits')
    def test_given_version_not_in_list_of_releases_then_return_false(self, mlist):

        commit = '8ff4b4'
        mlist.return_value = ['8fab4130','432bdsa','1234bc']

        self.assertFalse(self.vcs.check_commit_exists(commit))

class ApiInterrogateTest(unittest.TestCase):

    @patch('dls_ade.vcs_git.git.Repo.clone_from')
    def setUp(self, _2):

        self.patch_is_server_repo = patch('dls_ade.Server.is_server_repo')
        self.addCleanup(self.patch_is_server_repo.stop)
        self.mock_is_server_repo = self.patch_is_server_repo.start()

        self.mock_is_server_repo.return_value = True

        self.module = 'dummy'
        self.area = "support"
        server_mock = MagicMock()
        server_mock.url = "ssh://GIT_SSH_ROOT/"
        server_mock.dev_module_path.return_value = "controlstest/support/dummy"
        self.vcs = vcs_git.Git(self.module, self.area, server_mock)

    def test_when_asking_object_for_vcs_type_then_return_git_in_string(self):

        vcs_type = self.vcs.vcs_type

        self.assertEqual(vcs_type, 'git')

    def test_module_returns(self):

        self.assertEqual(self.vcs.module, self.vcs._module)

    def test_when_calling_source_repo_then_return_url_of_repo(self):

        expected_source_repo = 'ssh://GIT_SSH_ROOT/'
        expected_source_repo += 'controlstest/'+self.area+'/'+self.module

        source_repo = self.vcs.source_repo

        self.assertEqual(source_repo, expected_source_repo)


class GitSettersTest(unittest.TestCase):

    @patch('dls_ade.vcs_git.git.Repo.clone_from')
    def setUp(self, mclone):

        self.patch_is_server_repo = patch('dls_ade.Server.is_server_repo')
        self.addCleanup(self.patch_is_server_repo.stop)
        self.mock_is_server_repo = self.patch_is_server_repo.start()

        self.mock_is_server_repo.return_value = True

        self.module = 'dummy'
        self.area = "support"

        server_mock = MagicMock()
        server_mock.url = "ssh://GIT_SSH_ROOT/"
        server_mock.dev_module_path.return_value = 'dummy-string'
        repo_mock = MagicMock()
        self.vcs = vcs_git.Git(self.module, self.area, server_mock, repo_mock)

    def test_given_vcs_when_version_not_set_then_get_version_raise_error(self):

        with self.assertRaises(vcs_git.VCSGitError):
            self.vcs.version

    @patch('dls_ade.vcs_git.Git.check_version_exists', return_value=True)
    def test_given_mock_repo_then_set_version(self, mcheck):

        version = '0-1'
        self.vcs.mock_repo = "/path/to/module/release"
        self.vcs.set_version(version)

        self.assertEqual(self.vcs.version, version)

    @patch('dls_ade.vcs_git.Git.check_version_exists', return_value=True)
    def test_given_vcs_when_version_set_return_version(self, mcheck):

        version = '0-1'

        self.vcs.set_version(version)

        self.assertEqual(self.vcs.version, version)

    @patch('dls_ade.vcs_git.Git.check_version_exists', return_value=False)
    def test_given_nonexistent_version_when_version_set_then_raise_error(self, mcheck):

        version = '0-2'

        with self.assertRaises(vcs_git.VCSGitError):
            self.vcs.set_version(version)

    @patch('dls_ade.vcs_git.has_remote', return_value=True)
    def test_given_branch_then_checkout(self, _1):

        branch = "test_branch"

        self.vcs.set_branch(branch)

        self.vcs.repo.remotes.origin.refs.__getitem__().checkout.assert_called_once_with(b=branch)


class FakeTag(object):
    def __init__(self, name):
        self.name = name


class FakeOptions(object):
    def __init__(self, **kwargs):
        self.area = kwargs.get('area', 'support')


if __name__ == '__main__':

    # buffer option suppresses stdout generated from tested code
    unittest.main(buffer=True)
