import os
import json
import requests

from dls_ade.gitserver import GitServer

BITBUCKET_SERVER_URL = "http://localhost:7990"
BITBUCKET_CLONE_URL = "ssh://git@localhost:7999"


class BitbucketServer(GitServer):

    def __init__(self, user=None, pw=None):
        super(BitbucketServer, self).__init__(BITBUCKET_SERVER_URL,
                                              BITBUCKET_CLONE_URL)

        if user is None or pw is None:
            self.user = "TestUser"
            self.pw = "CrypticPassword123"

            # Get read only Bitbucket account by default TODO: Make account
            # self.user = os.environ.get("BB_USER")
            # self.pw = os.environ.get("BB_PASS")

    def _get_server_project_list(self):
        """
        Get list of project keys and names on server

        Returns:
            list(tuple(str)): List of project keys and names
        """

        r = requests.get(os.path.join(self.url, "rest/api/1.0/projects"),
                         auth=(self.user, self.pw))

        content = r.json()

        self._check_response_ok(r)

        return [(project['key'], project['name'])
                for project in content['values']]

    def get_server_repo_list(self):
        """
        Returns list of module repository paths from all projects

        Returns:
            List[str]: Repository paths on the server.
        """

        repos = []
        for key, project in self._get_server_project_list():

            r = requests.get(
                os.path.join(self.url,
                             "rest/api/1.0/projects", key, "repos"),
                auth=(self.user, self.pw))

            self._check_response_ok(r)

            content = r.json()

            for repo in content['values']:
                path = os.path.join("projects", key, "repos", repo['name'])
                repos.append(path)

        return repos

    def create_remote_repo(self, dest):
        """
        Create a git repository on the given bitbucket server path.

        Args:
            dest(str): The server path for the git repository to be created.

        Raises:
            :class:`~dls_ade.exceptions.VCSGitError`: If a git repository
            already exists on the destination path.
        """

        # Need a writable account to create a repository
        # self.user = os.environ.get("USER")
        # self.pw = raw_input("Enter Bitbucket password: ")

        project, repo_name = dest.rsplit('/', 1)

        response = requests.post(
            os.path.join(self.url, "rest/api/1.0/projects",
                         project.replace('/', '_').upper(), "repos"),
            auth=(self.user, self.pw),
            # Sort json output for help with testing.
            data=json.dumps({'name': repo_name,
                             'scmId': "git",
                             'forkable': True}, sort_keys=True),
            headers={'Content-type': 'application/json',
                     'Accept': 'application/json'},
            verify=True)

        return self._check_response_ok(response)

    @staticmethod
    def _check_response_ok(response):
        """
        Check response to see if request was successful. If not OK, raise an
        error with the returned message.

        Args:
            response: Response from server

        Raises:
            IOError: Message from response
        """

        if response.ok:
            return response
        else:
            response_dict = response.json()

            message = ""
            for error in response_dict['errors']:
                message += error['message'] + "\n"

            raise IOError(message)

    @staticmethod
    def dev_area_path(area="support"):
        """
        Return the full server path for the given area.

        Args:
            area(str): The area of the module.

        Returns:
            str: The full server path for the given area.

        """

        return os.path.join("projects", area.upper(), "repos")

    @staticmethod
    def get_clone_path(path):
        """
        Generate clone path with projects/ and repos/ removed

        Args:
            path(str): Full path to repo

        Returns:
            str: Path that can be use to clone repo
        """

        return path.replace("projects/", "").replace("repos/", "")
