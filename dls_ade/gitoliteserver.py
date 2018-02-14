import os
import shutil
import tempfile
import subprocess
import logging

from dls_ade.gitserver import GitServer
from dls_ade import path_functions as pathf
from dls_ade.vcs_git import git

GIT_ROOT = "dascgitolite@dasc-git.diamond.ac.uk"
GIT_SSH_ROOT = "ssh://" + GIT_ROOT + "/"

logging.getLogger(__name__).addHandler(logging.NullHandler())
log = logging.getLogger(__name__)
usermsg = logging.getLogger("usermessages")


class GitoliteServer(GitServer):

    def __init__(self):
        super(GitoliteServer, self).__init__(GIT_SSH_ROOT, GIT_SSH_ROOT)

    def is_server_repo(self, server_repo_path):
        """
        Check if path exists on repository.

        Args:
            server_repo_path(str): Path to module to check for

        Returns:
            bool: True if path does exist False if not

        """
        check_repo_cmd = "ssh " + GIT_ROOT + " expand " + server_repo_path
        cmd_output = subprocess.check_output(check_repo_cmd.split())
        return server_repo_path in cmd_output

    def get_server_repo_list(self, area=""):
        """
        Return list of module repository paths from the git server.

        Returns:
            list[str]: Repository paths on the server.
        """
        list_cmd = "ssh " + GIT_ROOT + " expand controls"
        if area:
            list_cmd += "/" + area
        log.debug("area: \"{area}\" ssh: \"{sshcmd}\"".format(area=area, sshcmd=list_cmd))
        list_cmd_output = subprocess.check_output(list_cmd.split())
        log.debug("\"gitolite response\": \"{}\"".format(list_cmd_output))
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

        usermsg.info("Creating remote on gitolite: {}".format(git_dest))
        temp_dir = tempfile.mkdtemp()

        try:
            # Cloning from gitolite server with non-existent repo creates it
            git.Repo.clone_from(git_dest, temp_dir)
        finally:
            shutil.rmtree(temp_dir)

    def dev_area_path(self, area="support"):
        """
        Return the full server path for the given area.

        Args:
            area(str): The area of the module.

        Returns:
            str: The full server path for the given area.

        """
        return os.path.join(self.GIT_ROOT_DIR, area)

    @staticmethod
    def get_clone_path(path):
        """
        Return path; no changes are required for gitolite server

        Args:
            path(str): Full path to repo

        Returns:
            str: Path that can be use to clone repo
        """

        return path
