import os
from pkg_resources import require
require('requests')
import requests
import json

from dls_ade.gitserver import GitServer


class BitbucketServer(GitServer):

    def __init__(self, url, user, pw):
        super(BitbucketServer, self).__init__(url)

        self.user = user
        self.pw = pw

    def _get_server_project_list(self):
        """
        Get list of project keys and names on server

        Returns:
            list(tuple(str)): List of project keys and names
        """

        r = requests.get(os.path.join(self.url, "rest/api/1.0/projects"),
                         auth=(self.user, self.pw))

        content = r.json()

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

            content = r.json()

            repos.extend([project + '/' + repo['name']
                          for repo in content['values']])

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

        project, repo_name = dest.rsplit('/', 1)

        response = requests.post(
            os.path.join(self.url, "rest/api/1.0/projects", project, "repos"),
            auth=(self.user, self.pw),
            data=json.dumps({'name': repo_name,
                             'scmId': "git",
                             'forkable': True}),
            headers={'Content-type': 'application/json',
                     'Accept': 'application/json'},
            verify=True)

        if response.ok:
            return response
        else:
            response_dict = response.json()

            message = ""
            for error in response_dict['errors']:
                message += error['message'] + "\n"

            raise IOError(message)
