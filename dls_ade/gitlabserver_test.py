import os
import unittest
from mock import patch, MagicMock
from collections import namedtuple

from dls_ade.gitlabserver import GitlabServer
from dls_ade.dls_utilities import GIT_ROOT_DIR

FakeProject = namedtuple('FakeProject', ['name', 'namespace'])
FAKE_PROJECT_LIST = [
    FakeProject('BL01I-EA-IOC-01', {'full_path': 'controls/ioc'}),
    FakeProject('support_module', {'full_path': 'controls/support'}),
    FakeProject('python_module', {'full_path': 'controls/python'})
]


class GetServerRepoList(unittest.TestCase):
    @patch('dls_ade.gitlabserver.gitlab.Gitlab')
    def test_get_server_repo_list_returns_correct_path(self, mock_gitlab):
        gl = GitlabServer()
        group_mock = MagicMock()
        gl._anon_gitlab_handle.groups.get.return_value = group_mock
        group_mock.projects.list.return_value = FAKE_PROJECT_LIST
        projects = gl.get_server_repo_list()
        self.assertIn('controls/ioc/BL01I-EA-IOC-01.git', projects)
        self.assertIn('controls/support/support_module.git', projects)
        self.assertIn('controls/python/python_module.git', projects)


class CreateRemoteRepoTest(unittest.TestCase):
    @patch('dls_ade.gitlabserver.gitlab.Gitlab')
    @patch('os.access')
    @patch('os.stat')
    @patch('dls_ade.gitlabserver.open')
    def test_create_remote_repo_with_normal_arguments(self, mock_open,
                                                      mock_stat,
                                                      mock_access,
                                                      mock_gitlab):
        mock_access.return_value = True
        mock_stat.return_value.st_mode = 0o400
        gl = GitlabServer()
        gl.create_remote_repo('controls/support/support_module')
        gl._private_gitlab_handle.projects.create.assert_called_once()

    @patch('dls_ade.gitlabserver.gitlab.Gitlab')
    @patch('os.access')
    def test_create_remote_repo_without_token_file(self, mock_access,
                                                   mock_gitlab):
        mock_access.return_value = False

        gl = GitlabServer()
        with self.assertRaises(ValueError) as e:
            gl.create_remote_repo('controls/support/support_module')

    @patch('dls_ade.gitlabserver.gitlab.Gitlab')
    @patch('os.access')
    @patch('os.stat')
    def test_create_remote_repo_with_wrong_token_file(self, mock_stat,
                                                      mock_access,
                                                      mock_gitlab):
        mock_access.return_value = True
        mock_stat.return_value.st_mode = 0o664
        gl = GitlabServer()
        with self.assertRaises(ValueError) as e:
            gl.create_remote_repo('controls/support/support_module')


class DevAreaPathTest(unittest.TestCase):

    def test_returns_correct_paths(self):
        path = GitlabServer.dev_area_path()
        self.assertEqual(os.path.join(GIT_ROOT_DIR, "support"), path)
        path = GitlabServer.dev_area_path("ioc")
        self.assertEqual(os.path.join(GIT_ROOT_DIR, "ioc"), path)
        path = GitlabServer.dev_area_path("python")
        self.assertEqual(os.path.join(GIT_ROOT_DIR, "python"), path)


class GetClonePathTest(unittest.TestCase):

    def test_returns_correct_path(self):
        path = GitlabServer.get_clone_path("controls/support/mysupport")
        self.assertEqual("controls/support/mysupport", path)
