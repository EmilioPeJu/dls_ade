import unittest
from pkg_resources import require
require("mock")
from mock import patch, MagicMock  # @UnresolvedImport

from dls_ade.bitbucketserver import BitbucketServer, BITBUCKET_SERVER_URL


class InitTest(unittest.TestCase):

    def test_init(self):
        server = BitbucketServer("TestUser", "CrypticPassword123")

        self.assertEqual(BITBUCKET_SERVER_URL, server.url)
        self.assertEqual("TestUser", server.user)
        self.assertEqual("CrypticPassword123", server.pw)


@patch('dls_ade.bitbucketserver.requests.get')
class GetServerRepoListTest(unittest.TestCase):

    def test_get_project_list(self, get_mock):

        content_dict = {'values': [{'key': "S", 'name': "Support"},
                                   {'key': "I", 'name': "IOC"}]}

        get_mock.return_value.json.return_value = content_dict

        server = BitbucketServer("TestUser", "CrypticPassword123")

        project_list = server._get_server_project_list()

        get_mock.assert_called_once_with(
            BITBUCKET_SERVER_URL + '/rest/api/1.0/projects',
            auth=('TestUser', 'CrypticPassword123'))

        self.assertEqual([('S', 'Support'), ('I', 'IOC')], project_list)

    @patch('dls_ade.bitbucketserver.BitbucketServer._get_server_project_list',
           return_value=[('S', 'Support'), ('I', 'IOC')])
    def test_get_server_repo_list(self, _, get_mock):

        expected_list = ['Support/ADCore', 'Support/ethercat',
                         'Support/pmacUtil', 'IOC/BR01C_VA',
                         'IOC/FE02I_CS', 'IOC/SR01C_VA']

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

        server = BitbucketServer("TestUser", "CrypticPassword123")

        repo_list = server.get_server_repo_list()

        calls = [call[0][0] for call in get_mock.call_args_list]
        self.assertIn(
            BITBUCKET_SERVER_URL + '/rest/api/1.0/projects/S/repos', calls)
        self.assertIn(
            BITBUCKET_SERVER_URL + '/rest/api/1.0/projects/I/repos', calls)

        self.assertEqual(expected_list, repo_list)


@patch('dls_ade.bitbucketserver.requests.post')
class CreateRemoteRepoTest(unittest.TestCase):

    def test_create_repo(self, post_mock):

        server = BitbucketServer("TestUser", "CrypticPassword123")

        response = server.create_remote_repo("S/test_module")

        post_mock.assert_called_once_with(
            BITBUCKET_SERVER_URL + '/rest/api/1.0/projects/S/repos',
            auth=('TestUser', 'CrypticPassword123'),
            data='{"scmId": "git", "forkable": true, "name": "test_module"}',
            headers={'Content-type': 'application/json',
                     'Accept': 'application/json'},
            verify=True)

        self.assertEqual(post_mock.return_value, response)

    def test_request_failure_then_extract_message_for_error(self, post_mock):

        expected_error_message = \
            "This repository URL is already taken by 'test_mod' in 'Support'"

        response_mock = MagicMock()
        response_mock.ok = False
        response_mock.json.return_value = \
            {'errors': [{'message': expected_error_message}]}
        post_mock.return_value = response_mock

        server = BitbucketServer("TestUser", "CrypticPassword123")

        with self.assertRaises(IOError) as e:
            server.create_remote_repo("S/test_mod")

        self.assertEqual(expected_error_message + '\n', e.exception.message)
