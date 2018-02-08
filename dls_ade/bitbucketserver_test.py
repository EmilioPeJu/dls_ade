import unittest
from mock import patch, MagicMock  # @UnresolvedImport

from dls_ade.bitbucketserver import BitbucketServer, BITBUCKET_SERVER_URL


class InitTest(unittest.TestCase):

    def test_init(self):
        server = BitbucketServer()

        self.assertEqual(BITBUCKET_SERVER_URL, server.url)
        self.assertEqual("TestUser", server.user)
        self.assertEqual("CrypticPassword123", server.pw)


class DevAreaPathTest(unittest.TestCase):

    def test_returns_correct_paths(self):

        path = BitbucketServer.dev_area_path()
        self.assertEqual("projects/SUPPORT/repos", path)
        path = BitbucketServer.dev_area_path("ioc")
        self.assertEqual("projects/IOC/repos", path)


class GetClonePathTest(unittest.TestCase):

    def test_returns_correct_path(self):

        path = BitbucketServer.get_clone_path("projects/SUPPORT/repos/ADCore")
        self.assertEqual("SUPPORT/ADCore", path)


@patch('dls_ade.bitbucketserver.requests.get')
class GetServerRepoListTest(unittest.TestCase):

    def test_get_project_list(self, get_mock):

        content_dict = {'values': [{'key': "SUPPORT", 'name': "Support"},
                                   {'key': "IOC", 'name': "IOC"}]}

        get_mock.return_value.json.return_value = content_dict

        server = BitbucketServer()

        project_list = server._get_server_project_list()

        get_mock.assert_called_once_with(
            BITBUCKET_SERVER_URL + '/rest/api/1.0/projects',
            auth=('TestUser', 'CrypticPassword123'))

        self.assertEqual([('SUPPORT', 'Support'), ('IOC', 'IOC')], project_list)

    @patch('dls_ade.bitbucketserver.BitbucketServer._get_server_project_list',
           return_value=[('SUPPORT', 'Support'), ('IOC', 'IOC')])
    def test_get_server_repo_list(self, _, get_mock):

        expected_list = ['projects/SUPPORT/repos/ADCore',
                         'projects/SUPPORT/repos/ethercat',
                         'projects/SUPPORT/repos/pmacUtil',
                         'projects/IOC/repos/BR01C_VA',
                         'projects/IOC/repos/FE02I_CS',
                         'projects/IOC/repos/SR01C_VA']

        content_dict1 = {'values': [{'name': "ADCore"},
                                    {'name': "ethercat"},
                                    {'name': "pmacUtil"}]}
        get_mock1 = MagicMock()
        get_mock1.json.return_value = content_dict1

        content_dict2 = {'values': [{'name': "BR01C_VA"},
                                    {'name': "FE02I_CS"},
                                    {'name': "SR01C_VA"}]}
        get_mock2 = MagicMock()
        get_mock2.json.return_value = content_dict2

        get_mock.side_effect = [get_mock1, get_mock2]

        server = BitbucketServer()

        repo_list = server.get_server_repo_list()

        calls = [call[0][0] for call in get_mock.call_args_list]
        self.assertIn(
            BITBUCKET_SERVER_URL + '/rest/api/1.0/projects/SUPPORT/repos', calls)
        self.assertIn(
            BITBUCKET_SERVER_URL + '/rest/api/1.0/projects/IOC/repos', calls)

        self.assertEqual(expected_list, repo_list)


@patch('dls_ade.bitbucketserver.requests.post')
class CreateRemoteRepoTest(unittest.TestCase):

    def test_create_repo(self, post_mock):

        server = BitbucketServer()

        response = server.create_remote_repo("Support/test_module")

        post_mock.assert_called_once_with(
            BITBUCKET_SERVER_URL + '/rest/api/1.0/projects/SUPPORT/repos',
            auth=('TestUser', 'CrypticPassword123'),
            data='{"scmId": "git", "forkable": true, "name": "test_module"}',
            headers={'Content-type': 'application/json',
                     'Accept': 'application/json'},
            verify=True)

        self.assertEqual(post_mock.return_value, response)


class CheckResponseOKTest(unittest.TestCase):

    def test_response_OK_then_return(self):

        response_mock = MagicMock()
        response_mock.ok = True

        server = BitbucketServer("TestUser", "CrypticPassword123")

        response = server._check_response_ok(response_mock)

        self.assertEqual(response_mock, response)

    def test_response_not_OK_then_error(self):

        example_error_message = \
            "This repository URL is already taken by 'test_mod' in 'Support'"

        response_mock = MagicMock()
        response_mock.ok = False
        response_mock.json.return_value = \
            {'errors': [{'message': example_error_message}]}

        server = BitbucketServer()

        with self.assertRaises(IOError) as e:
            server._check_response_ok(response_mock)

        self.assertEqual(example_error_message + '\n', e.exception.message)
