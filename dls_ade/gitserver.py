import os
import tempfile
import logging

from dls_ade.vcs_git import Git, git

from dls_ade import dls_utilities as dls_util

log = logging.getLogger(__name__)
usermsg = logging.getLogger("usermessages")


class GitServer(object):

    GIT_ROOT_DIR = dls_util.GIT_ROOT_DIR

    def __init__(self, url, clone_url, release_url):
        # url used for cloning
        self.clone_url = clone_url
        # url that the build server will use
        self.release_url = release_url
        # url used for everything else e.g: for starting a new module
        self.url = url

    def is_server_repo(self, server_repo_path):
        """
        Checks if path exists on repository

        Args:
            server_repo_path(str): Path to module to check for

        Returns:
            bool: True if path does exist False if not

        """
        repo_list = self.get_server_repo_list()
        return server_repo_path in repo_list

    def get_server_repo_list(self):
        """
        Returns list of module repository paths from the git server.

        Returns:
            List[str]: Repository paths on the server.
        """

        raise NotImplementedError("Must be implemented in child classes")

    def create_new_local_repo(self, module, area, path):
        """
        Create a new Git instance from a git.Repo instance

        Args:
            module(str): Name of module
            area(str): Area of module
            path(str): Path to repo

        Returns:
            Git repo instance

        """
        base_repo = git.Repo(path)
        return Git(module, area, self, base_repo)

    def get_clone_repo(self, server_repo_path, local_repo_path, origin='gitlab'):
        """
        Get Repo clone given server and local repository paths

        Args:
            server_repo_path(str): server repository path
            local_repo_path(str): local repository path
            origin(str): name to be assigned to remote on clone
        """
        repo = git.Repo.clone_from(
            os.path.join(self.clone_url,
                         self.get_clone_path(server_repo_path)),
            os.path.join("./", local_repo_path), origin=origin)

        return repo

    def clone(self, server_repo_path, local_repo_path):
        """
        Clones a repository on the server to a local directory.

        Args:
            server_repo_path(str): Suffix of URL for remote repo to clone
            local_repo_path(str): Name of module to clone

        Raises:
            :class:`~dls_ade.exceptions.VCSGitError`: Repository does not
            contain <source>
            :class:`~dls_ade.exceptions.VCSGitError`: <module> already exists
            in current directory
        """

        dls_util.remove_end_slash(server_repo_path)

        if not self.is_server_repo(server_repo_path):
            raise ValueError("Repository does not contain " +
                             server_repo_path)
        elif os.path.isdir(local_repo_path):
            raise ValueError(local_repo_path + " already exists in current "
                                               "directory")

        module = local_repo_path
        # Area is second section of path
        area = server_repo_path.split('/')[1]

        repo = self.get_clone_repo(server_repo_path, local_repo_path)

        git_inst = Git(module, area, self, repo)

        return git_inst

    def temp_clone(self, source):
        """
        Clones repo to /tmp directory and returns the relevant git.Repo object.

        Args:
            source(str): server repository path to clone

        Returns:
            :class:`~git.repo.base.Repo`: Repository instance
        """

        dls_util.remove_end_slash(source)

        if not self.is_server_repo(source):
            raise ValueError("Repository does not contain " + source)

        # Area is second section of path
        area = source.split('/')[1]
        # Module is everything after area
        module = source.split('/', 2)[-1]

        if module.endswith('.git'):
            module = module[:-4]

        repo_dir = tempfile.mkdtemp(suffix="_" + module.replace("/", "_"))
        repo = git.Repo.clone_from(os.path.join(self.clone_url,
                                                self.get_clone_path(source)),
                                   repo_dir)

        git_inst = Git(module, area, self, repo)

        return git_inst

    def clone_multi(self, source):
        """
        Checks if source is valid, then clones all repositories in source

        Args:
            source(str): Suffix of URL for remote repo area to clone

        Raises:
            :class:`~dls_ade.exceptions.VCSGitError`: Repository does not
                contain <source>
        """

        split_list = self.get_server_repo_list()
        for path in split_list:
            if path.startswith(source):

                # Remove controls/<area>/ from front of save path
                module = path.split('/', 2)[-1]
                log.debug("Module: {}".format(module))

                if module not in os.listdir("./"):
                    usermsg.info("Cloning: {}".format(path))
                    git.Repo.clone_from(
                        os.path.join(self.clone_url,
                                     self.get_clone_path(path)),
                        os.path.join("./", module))
                else:
                    usermsg.info(module + " already exists in current directory")

    def create_remote_repo(self, dest):
        """
        Create a git repository on the given server path.

        Args:
            dest(str): The server path for the git repository to be created.

        Raises:
            :class:`~dls_ade.exceptions.VCSGitError`: If a git repository
            already exists on the destination path.
        """

        raise NotImplementedError("Must be implemented in child classes")

    def dev_area_path(self, area="support"):
        """
        Return the full server path for the given area.

        Args:
            area(str): The area of the module.

        Returns:
            str: The full server path for the given area.
        """

        raise NotImplementedError("Must be implemented in child classes")

    def dev_module_path(self, module, area="support"):
        """
        Return the full server path for the given module and area.

        Args:
            area(str): The area of the module.
            module(str): The module name.

        Returns:
            str: The full server path for the given module.

        """
        return os.path.join(self.dev_area_path(area), module)

    @staticmethod
    def get_clone_path(path):
        """
        Generate path that can be used to clone repo

        Args:
            path(str): Full path to repo

        Returns:
            str: Path that can be use to clone repo
        """

        raise NotImplementedError("Must be implemented in child classes")
