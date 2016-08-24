import os
import shutil
import tempfile
import subprocess

from dls_ade.gitserver import GitServer
from dls_ade.vcs_git import git

GIT_ROOT = "dascgitolite@dasc-git.diamond.ac.uk"
GIT_SSH_ROOT = "ssh://" + GIT_ROOT + "/"


class GitoliteServer(GitServer):

    def __init__(self):
        super(GitoliteServer, self).__init__(GIT_SSH_ROOT)

    def get_server_repo_list(self):
        """
        Returns list of module repository paths from the git server.

        Returns:
            List[str]: Repository paths on the server.
        """

        list_cmd = "ssh " + GIT_ROOT + " expand controls"
        list_cmd_output = subprocess.check_output(list_cmd.split())
        # list_cmd_output is a heading followed by a module list in the form:
        # R   W 	(alan.greer)	controls/support/ADAndor
        # R   W 	(ronaldo.mercado)	controls/support/ethercat
        # This is split and entries with a '/' are added to a list of the
        # module file paths

        split_list = []
        for entry in list_cmd_output.split():
            if '/' in entry:
                split_list.append(entry)

        return split_list

    def create_remote_repo(self, dest):
        """
        Create a git repository on the given gitolite server path.

        Args:
            dest(str): The server path for the git repository to be created.

        Raises:
            :class:`~dls_ade.exceptions.VCSGitError`: If a git repository
            already exists on the destination path.
        """

        if self.is_server_repo(dest):
            raise ValueError("{dest:s} already exists".format(dest=dest))

        git_dest = os.path.join(self.url, dest)

        print("Creating remote...")
        temp_dir = tempfile.mkdtemp()

        try:
            # Cloning from gitolite server with non-existent repo creates it
            git.Repo.clone_from(git_dest, temp_dir)
        finally:
            shutil.rmtree(temp_dir)
