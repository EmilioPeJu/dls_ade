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
        gl._gitlab_handle.projects.list.return_value = FAKE_PROJECT_LIST
        projects = gl.get_server_repo_list()
        self.assertIn('controls/ioc/BL01I-EA-IOC-01', projects)
        self.assertIn('controls/support/support_module', projects)
        self.assertIn('controls/python/python_module', projects)


class CreateRemoteRepoTest(unittest.TestCase):
    @patch('dls_ade.gitlabserver.gitlab.Gitlab')
    def test_create_remote_repo_with_normal_arguments(self, mock_gitlab):
        gl = GitlabServer(create_on_push=False)
        gl.create_remote_repo('controls/support/support_module')
        gl._gitlab_handle.projects.create.assert_called_once()

    @patch('dls_ade.gitlabserver.gitlab.Gitlab')
    def test_create_remote_repo_on_push_with_normal_arguments(self, mock_gitlab):
        # create_on_push shouldn't create the project using Gitlab API
        gl = GitlabServer(create_on_push=True)
        gl.create_remote_repo('controls/support/support_module')
        self.assertEqual(gl._gitlab_handle.projects.create.called, False)


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
