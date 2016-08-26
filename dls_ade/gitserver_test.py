import unittest
from pkg_resources import require
require("mock")
from mock import ANY, patch, MagicMock  # @UnresolvedImport

from dls_ade.gitserver import GitServer


class IsServerRepoTest(unittest.TestCase):

    @patch('dls_ade.gitserver.GitServer.get_server_repo_list',
           return_value=['controls/test/path'])
    def test_given_path_exists_then_return_true(self, _):

        server = GitServer("test@url.ac.uk", "test@url.ac.uk")

        self.assertTrue(server.is_server_repo("controls/test/path"))

    @patch('dls_ade.gitserver.GitServer.get_server_repo_list',
           return_value=['controls/test/path'])
    def test_given_path_does_not_exist_then_return_false(self, _):

        server = GitServer("test@url.ac.uk", "test@url.ac.uk")

        self.assertFalse(server.is_server_repo("controls/test/not_a_path"))


class NotImplementedTest(unittest.TestCase):

    def test_area_path_raises(self):

        with self.assertRaises(NotImplementedError):
            GitServer.dev_area_path()

    def test_get_clone_path_raises(self):

        with self.assertRaises(NotImplementedError):
            GitServer.get_clone_path("")

    def test_create_remote_repo_raises(self):

        server = GitServer("test@url.ac.uk", "test@url.ac.uk")

        with self.assertRaises(NotImplementedError):
            server.create_remote_repo("")

    def test_get_server_repo_list_raises(self):

        server = GitServer("test@url.ac.uk", "test@url.ac.uk")

        with self.assertRaises(NotImplementedError):
            server.get_server_repo_list()


class DevPathTest(unittest.TestCase):

    @patch('os.path.join')
    @patch('dls_ade.gitserver.GitServer.dev_area_path')
    def test_module_path_calls_dev_area(self, area_path_mock, join_mock):

        server = GitServer("test@url.ac.uk", "test@url.ac.uk")

        server.dev_module_path("test_module")
        join_mock.assert_called_once_with(area_path_mock.return_value,
                                          "test_module")


class CloneTest(unittest.TestCase):

    @patch('dls_ade.gitserver.GitServer.is_server_repo', return_value=False)
    @patch('git.Repo.clone_from')
    def test_given_invalid_source_then_error_raised(self, mock_clone_from, mock_is_server_repo):
        source = "does/not/exist"
        module = "test_module"

        server = GitServer("test@url.ac.uk", "test@url.ac.uk")

        with self.assertRaises(ValueError):
            server.clone(source, module)

    @patch('os.path.isdir', return_value=True)
    @patch('dls_ade.gitserver.GitServer.is_server_repo', return_value=True)
    @patch('git.Repo.clone_from')
    def test_given_existing_module_name_then_error_raised(self, mock_clone_from, mock_is_server_repo, mock_isdir):
        source = "test/source"
        module = "already_exists"

        server = GitServer("test@url.ac.uk", "test@url.ac.uk")

        with self.assertRaises(ValueError):
            server.clone(source, module)

    @patch('dls_ade.gitserver.GitServer.get_clone_path',
           return_value="test/source")
    @patch('dls_ade.gitserver.GitServer.dev_area_path')
    @patch('dls_ade.gitserver.GitServer.is_server_repo', return_value=True)
    @patch('os.path.isdir', return_value=False)
    @patch('git.Repo.clone_from')
    def test_given_valid_inputs_then_clone_from_called(self, mock_clone_from, _1, is_server_repo_mock, _2, _3):
        source = "test/source/test_module"
        module = "test_module"

        server = GitServer("test@url.ac.uk", "test@url.ac.uk")

        server.clone(source, module)

        is_server_repo_mock.assert_called_once_with("test/source/test_module")
        mock_clone_from.assert_called_once_with(
            "test@url.ac.uk/test/source", "./test_module")


@patch('tempfile.mkdtemp', return_value="tempdir")
class TempCloneTest(unittest.TestCase):

    @patch('dls_ade.gitserver.GitServer.is_server_repo', return_value=False)
    @patch('git.Repo.clone_from')
    def test_given_invalid_source_then_error_raised(self, mock_clone_from, mock_is_server_repo, mock_mkdtemp):
        source = "/does/not/exist"

        server = GitServer("test@url.ac.uk", "test@url.ac.uk")

        with self.assertRaises(ValueError):
            server.temp_clone(source)

        self.assertFalse(mock_clone_from.call_count)

    @patch('dls_ade.gitserver.GitServer.get_clone_path',
           return_value="controls/area/test_module")
    @patch('dls_ade.gitserver.GitServer.dev_area_path')
    @patch('dls_ade.gitserver.GitServer.is_server_repo', return_value=True)
    @patch('git.Repo.clone_from')
    def test_given_valid_inputs_then_clone_from_called(self, mock_clone_from, _1, _2, _3, mock_mkdtemp):
        source = "controls/area/test_module"

        server = GitServer("test@url.ac.uk", "test@url.ac.uk")

        server.temp_clone(source)

        mock_mkdtemp.assert_called_once_with(suffix="_test_module")
        mock_clone_from.assert_called_once_with(
            "test@url.ac.uk/controls/area/test_module", "tempdir")

    @patch('dls_ade.gitserver.GitServer.get_clone_path',
           return_value="controls/ioc/domain/test_module")
    @patch('dls_ade.gitserver.GitServer.dev_area_path')
    @patch('dls_ade.gitserver.GitServer.is_server_repo', return_value=True)
    @patch('git.Repo.clone_from')
    def test_given_repo_with_domain_code_then_tempdir_arg_has_forwardslash_removed(self, mock_clone_from, _1, _2, _3, mock_mkdtemp):

        source = "controls/ioc/domain/test_module"

        server = GitServer("test@url.ac.uk", "test@url.ac.uk")

        server.temp_clone(source)

        mock_mkdtemp.assert_called_once_with(suffix="_domain_test_module")
        mock_clone_from.assert_called_once_with(
            "test@url.ac.uk/controls/ioc/domain/test_module", "tempdir")


class CloneMultiTest(unittest.TestCase):

    @patch('dls_ade.gitserver.GitServer.get_server_repo_list',
           return_value=["controls/area/test_module"])
    @patch('dls_ade.gitserver.GitServer.is_server_repo', return_value=False)
    @patch('dls_ade.gitserver.git.Repo.clone_from')
    def test_given_invalid_source_then_clone_not_called(self, mock_clone_from, _2, _3):
        source = "/does/not/exist"

        server = GitServer("test@url.ac.uk", "test@url.ac.uk")

        server.clone_multi(source)

        self.assertFalse(mock_clone_from.call_count)

    @patch('dls_ade.gitserver.GitServer.get_clone_path',
           return_value="controls/ioc/domain/test_module")
    @patch('dls_ade.gitserver.GitServer.get_server_repo_list',
           return_value=["controls/area/test_module", "controls/area/test_module2"])
    @patch('os.listdir', return_value=["test_module"])
    @patch('dls_ade.gitserver.GitServer.is_server_repo', return_value=True)
    @patch('dls_ade.gitserver.git.Repo.clone_from')
    def test_given_one_existing_module_one_not_then_clone_one(self, mock_clone_from, _1, _2, _3, _4):
        source = "controls/area"

        server = GitServer("test@url.ac.uk", "test@url.ac.uk")

        server.clone_multi(source)

        mock_clone_from.assert_called_once_with(
            "test@url.ac.uk/controls/ioc/domain/test_module", "./test_module2")

    @patch('dls_ade.gitserver.GitServer.get_clone_path',
           return_value="controls/area/test_module")
    @patch('dls_ade.gitserver.GitServer.get_server_repo_list',
           return_value=["controls/area/test_module"])
    @patch('os.listdir', return_value=["not_test_module"])
    @patch('dls_ade.gitserver.git.Repo.clone_from')
    def test_given_valid_module_name_then_clone(self, mock_clone_from, _1, _2, _3):
        source = "controls/area/"

        server = GitServer("test@url.ac.uk", "test@url.ac.uk")

        server.clone_multi(source)

        mock_clone_from.assert_called_once_with(
            "test@url.ac.uk/controls/area/test_module", "./test_module")

    @patch('dls_ade.gitserver.GitServer.get_clone_path',
           return_value="controls/ioc/BL/module")
    @patch('dls_ade.gitserver.GitServer.get_server_repo_list',
           return_value=["controls/ioc/BL/module"])
    @patch('os.listdir', return_value=["not_test_module"])
    @patch('dls_ade.gitserver.git.Repo.clone_from')
    def test_given_ioc_area_name_then_clone_with_domain_in_file_name(self, mock_clone_from, _1, _2, _3):
        source = "controls/ioc/"

        server = GitServer("test@url.ac.uk", "test@url.ac.uk")

        server.clone_multi(source)

        mock_clone_from.assert_called_once_with(
            "test@url.ac.uk/controls/ioc/BL/module", "./BL/module")
