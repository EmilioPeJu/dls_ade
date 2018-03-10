import unittest
from pkg_resources import require
require("mock")
from mock import patch, MagicMock  # @UnresolvedImport

from dls_ade.gitoliteserver import GitoliteServer, GIT_SSH_ROOT


class IsServerRepoTest(unittest.TestCase):

    @patch('dls_ade.gitoliteserver.subprocess.check_output',
           return_value=
           "hello user, this is gitolite running on git 1.7.1\n"
           "you have access to the following repos on the server:\n"
           "     R   W      (user)  controls/test/path")
    def test_given_path_exists_then_return_true(self, _):

        server = GitoliteServer()

        self.assertTrue(server.is_server_repo("controls/test/path"))

    @patch('dls_ade.gitoliteserver.subprocess.check_output',
           return_value=
           "hello user, this is gitolite running on git 1.7.1\n"
           "you have access to the following repos on the server:\n"
           "     R   W      (user)  controls/test/path")
    def test_given_path_does_not_exist_then_return_false(self, _):

        server = GitoliteServer()

        self.assertFalse(server.is_server_repo("controls/test/not_a_path"))


class GetServerRepoListTest(unittest.TestCase):

    @patch('subprocess.check_output')
    def test_given_expand_output_then_format_and_return(self, sub_mock):

        sub_mock.return_value = "R   W 	(alan.greer)	controls/support/ADAndor\n" \
                                "R   W 	(ronaldo.mercado)	controls/support/ethercat\n"

        server = GitoliteServer()

        repo_list = server.get_server_repo_list()

        self.assertEqual(repo_list, ["controls/support/ADAndor", "controls/support/ethercat"])


@patch('tempfile.mkdtemp', return_value='tempdir')
@patch('dls_ade.gitserver.git.Repo.clone_from')
@patch('shutil.rmtree')
class CreateRemoteRepoTest(unittest.TestCase):

    @patch('dls_ade.gitoliteserver.GitoliteServer.is_server_repo',
           return_value=False)
    def test_given_arguments_reasonable_then_function_runs_correctly(self, mock_is_server_repo, mock_rmtree, mock_clone_from, mock_mkdtemp):

        server = GitoliteServer()

        server.create_remote_repo("test_destination")

        mock_is_server_repo.assert_called_once_with("test_destination")
        mock_clone_from.assert_called_once_with(
            '{git_ssh_root}test_destination'.format(git_ssh_root=GIT_SSH_ROOT), "tempdir")
        mock_mkdtemp.assert_called_once_with()
        mock_rmtree.assert_called_once_with("tempdir")

    @patch('dls_ade.gitoliteserver.GitoliteServer.is_server_repo',
           return_value=True)
    def test_given_is_server_repo_true_then_exception_raised_with_correct_message(self, mock_is_server_repo, mock_rmtree, mock_clone_from, mock_mkdtemp):

        comp_message = "{dest:s} already exists".format(dest="test_destination")

        server = GitoliteServer()

        with self.assertRaises(ValueError) as e:
            server.create_remote_repo("test_destination")

        mock_is_server_repo.assert_called_once_with("test_destination")
        self.assertFalse(mock_clone_from.call_count)
        self.assertFalse(mock_mkdtemp.call_count)
        self.assertFalse(mock_rmtree.call_count)

        self.assertEqual(str(e.exception), comp_message)


class GetClonePathTest(unittest.TestCase):

    def test_returns_same_path(self):

        path = GitoliteServer.get_clone_path("controls/support/ADCore")
        self.assertEqual("controls/support/ADCore", path)
