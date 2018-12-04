import unittest
from mock import patch, MagicMock
from collections import namedtuple

from dls_ade.gitlabserver import GitlabServer

FakeProject = namedtuple('FakeProject', ['name', 'namespace'])
FAKE_PROJECT_LIST = [
    FakeProject('BL01-EA-IOC-01', {'full_path': 'controls/ioc'}),
    FakeProject('support_module', {'full_path': 'controls/support'}),
    FakeProject('python_module', {'full_path': 'controls/python'})
]


class GetServerRepoList(unittest.TestCase):
    @patch('dls_ade.gitlabserver.gitlab.Gitlab')
    def test_get_server_repo_list_returns_correct_path(self, mock_gitlab):
        gl = GitlabServer()
        gl._gitlab_handle.projects.list.return_value = FAKE_PROJECT_LIST
        projects = gl.get_server_repo_list()
        self.assertIn('controls/ioc/BL01-EA-IOC-01', projects)
        self.assertIn('controls/support/support_module', projects)
        self.assertIn('controls/python/python_module', projects)


class CreateRemoteRepoTest(unittest.TestCase):
    @patch('dls_ade.gitlabserver.gitlab.Gitlab')
    def test_create_remote_repo_with_normal_arguments(self, mock_gitlab):
        gl = GitlabServer()
        gl.create_remote_repo('controls/support/support_module')
        gl._gitlab_handle.projects.create.assert_called_once()


class DevAreaPathTest(unittest.TestCase):

    def test_returns_correct_paths(self):
        path = GitlabServer.dev_area_path()
        self.assertEqual("controls/support", path)
        path = GitlabServer.dev_area_path("ioc")
        self.assertEqual("controls/ioc", path)
        path = GitlabServer.dev_area_path("python")
        self.assertEqual("controls/python", path)


class GetClonePathTest(unittest.TestCase):

    def test_returns_correct_path(self):
        path = GitlabServer.get_clone_path("controls/support/mysupport")
        self.assertEqual("controls/support/mysupport", path)
