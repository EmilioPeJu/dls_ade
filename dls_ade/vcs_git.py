#from dls_ade.vcs import BaseVCS
from vcs import BaseVCS
import subprocess
import os
import tempfile
import shutil
import logging

from pkg_resources import require
require('GitPython')
import git

logging.basicConfig(level=logging.DEBUG)

GIT_ROOT = "dascgitolite@dasc-git.diamond.ac.uk"
GIT_SSH_ROOT = "ssh://dascgitolite@dasc-git.diamond.ac.uk/"
GIT_ROOT_DIR = os.getenv('GIT_ROOT_DIR', "controls")


class Error(Exception):
    """Class for exceptions relating to vcs_git module"""
    pass


def is_git_dir(path="./"):
    if os.path.isdir(path):
        try:
            git.Repo(path)
        except git.exc.InvalidGitRepositoryError:
            return False
        else:
            return True
    else:
        raise Exception("Path is not valid")


def is_git_root_dir(path="."):
    if is_git_dir(path):
        git_repo = git.Repo(path)
        top_level_path = os.path.normpath(
            git_repo.git.rev_parse("--show-toplevel")
        )
        full_path = os.path.abspath(path)
        if full_path == top_level_path:
            return True
        else:
            return False
    else:
        return False


def is_repo_path(server_repo_path):
    """
    Checks if path exists on repository

    Args:
        server_repo_path(str): Path to module to check for

    Returns:
        bool: True if path does exist False if not
    """

    list_cmd = "ssh {git_root:s} expand {git_root_dir:s}/"
    list_cmd = list_cmd.format(git_root=GIT_ROOT, git_root_dir=GIT_ROOT_DIR)

    list_cmd_output = subprocess.check_output(list_cmd.split())

    return server_repo_path in list_cmd_output


def get_repository_list():
    """
    Returns formatted list of entries from 'ssh dascgitolite@dasc-git.diamond.ac.uk expand controls' command

    Returns:
        list: Reduced 'expand controls' output
    """
    list_cmd = "ssh " + GIT_ROOT + " expand controls"
    list_cmd_output = subprocess.check_output(list_cmd.split())
    # list_cmd_output is some heading text followed by a module list in the form:
    # R   W 	(alan.greer)	controls/support/ADAndor
    # R   W 	(ronaldo.mercado)	controls/support/ethercat
    # This is split and entries with a '/' are added to a list of the module file paths
    split_list = []
    for entry in list_cmd_output.split():
        if '/' in entry:
            split_list.append(entry)

    return split_list


def init_repo(path="./"):
    """Initialise a local git repository.

    Args:
        path: The relative or absolute path for the local git repository.

    Raises:
        Error: If the path is not a directory, or is already a git repository.

    """
    if not os.path.isdir(path):
        raise Error("Path {path:s} is not a directory".format(path=path))

    if is_git_root_dir(path):
        err_message = "Path {path:s} is already a git repository"
        raise Error(err_message.format(path=path))

    print("Initialising repo...")
    git.Repo.init(path)
    print("Repository created.")


def stage_all_files_and_commit(path="./"):
    """Stage and commit all files in a local git repository.

    Args:
        path: The relative or absolute path of the local git repository.

    Raises:
        Error: If the path is not a git repository.

    """

    if not os.path.isdir(path):
        raise Error("Path {path:s} is not a directory".format(path=path))

    if not is_git_root_dir(path):
        err_message = "Path {path:s} is not a git repository"
        raise Error(err_message.format(path=path))

    repo = git.Repo(path)
    print("Staging files...")
    repo.git.add('--all')
    print("Committing files to repo...")
    msg = repo.git.commit(m="Initial commit")
    print(msg)


def add_new_remote_and_push(dest, path="./", remote_name="origin",
                            branch_name="master"):
    """Adds a remote to a git repository, and pushes to the gitolite server.

    This will fail if:
        - The path given is not a git repository.
        - The local repository does not have the given branch name.
        - The remote name already exists for the local repository.
        - A git repository already exists on the destination path.

    Note:
        If the local repository already has the given remote name defined, use
        :func:`push_to_remote` to push to its defined server path.

    Args:
        dest: The server path for the git repository.
        path: The relative or absolute path for the local git repository.
        remote_name: The git repository's alias for the destination path.
        branch_name: The name of the branch to push from / to.

    Raises:
        Error: If there is an issue with the operation.

    """

    if not is_git_root_dir(path):
        err_message = "Path {path:s} is not a git repository"
        raise Error(err_message.format(path=path))

    repo = git.Repo(path)

    if branch_name not in [x.name for x in repo.branches]:
        err_message = ("Local repository branch {branch:s} does not currently "
                       "exist.")
        raise Error(err_message.format(branch=branch_name))

    if remote_name in [x.name for x in repo.remotes]:
        # <remote_name> already exists - use push_to_remote_repo instead!
        err_message = ("Cannot push local repository to destination as remote "
                       "{remote:s} is already defined")
        raise Error(err_message.format(remote=remote_name))

    create_remote_repo(dest)
    print("Adding remote to repo...")
    remote = repo.create_remote(remote_name, os.path.join(GIT_SSH_ROOT, dest))
    print("Pushing repo to destination...")
    remote.push(branch_name)


def create_remote_repo(dest):
    """Create a git repository on the given gitolite server path.

    Args:
        dest: The server path for the git repository to be created.

    Raises:
        Error: If a git repository already exists on the destination path.

    """

    if is_repo_path(dest):
        raise Error("{dest:s} already exists".format(dest=dest))

    git_dest = os.path.join(GIT_SSH_ROOT, dest)

    print("Creating remote...")
    temp_dir = tempfile.mkdtemp()

    try:
        # Cloning from gitolite server with non-existent repo creates it
        git.Repo.clone_from(git_dest, temp_dir)
    finally:
        shutil.rmtree(temp_dir)


def push_to_remote(path="./", remote_name="origin", branch_name="master"):
    """Pushes to the server path given by its remote name, on the given branch.

    Args:
        path: The relative or absolute path for the local git repository.
        remote_name: The git repository's remote name to push to.
        branch_name: The name of the branch to push from / to.

    This will fail if:
        - The path given is not a git repository.
        - The local repository does not have the given branch name.
        - The local repository does not have the given remote name.
        - A git repository does not already exist on the destination path.

    Note:
        If the local repository does not have the given remote name defined,
        use :func:`add_new_remote_and_push` and give the gitolite server
        repository path.

    Raises:
        Error: If there is an issue with the operation.

    """
    if not is_git_root_dir(path):
        err_message = "Path {path:s} is not a git repository"
        raise Error(err_message.format(path=path))

    repo = git.Repo(path)

    if branch_name not in [x.name for x in repo.branches]:
        err_message = ("Local repository branch {branch:s} does not currently "
                       "exist.")
        raise Error(err_message.format(branch=branch_name))

    if remote_name not in [x.name for x in repo.remotes]:
        # Remote "origin" does not already exist
        err_message = "Local repository does not have remote {remote:s}"
        raise Error(err_message.format(remote=remote_name))

    # They have overloaded the dictionary lookup to compare string with .name
    remote = repo.remotes[remote_name]

    if not remote.url.startswith(GIT_SSH_ROOT):
        err_message = ("Remote repository URL {remoteURL:s} does not "
                       "begin with the gitolite server path")
        raise Error(err_message.format(remoteURL=remote.url))

    # Removes initial GIT_SSH_ROOT (with slash at end)
    server_repo_path = remote.url[len(GIT_SSH_ROOT):]

    if not is_repo_path(server_repo_path):
        err_message = ("Server repo path {s_repo_path:s} does not "
                       "currently exist")
        raise Error(err_message.format(s_repo_path=server_repo_path))

    print("Pushing repo to destination...")
    remote.push(branch_name)


def clone(source, module):
    """
    Checks if source is valid and that module doesn't already exist locally, then clones repo

    Args:
        source(str): Suffix of URL for remote repo to clone
        module(str): Name of module to clone

    Raises:
        Exception: Repository does not contain <source>
        Exception: <module> already exists in current directory
    """
    if not is_repo_path(source):
        raise Exception("Repository does not contain " + source)
    elif os.path.isdir(module):
        raise Exception(module + " already exists in current directory")

    if source[-1] == '/':
        source = source[:-1]

    repo = git.Repo.clone_from(os.path.join(GIT_SSH_ROOT, source),
                               os.path.join("./", module))

    return repo


def temp_clone(source):
    """
    Clones repo to /tmp directory and returns the path to the repo instance to access information

    Args:
        source: URL of remote repo to clone

    Returns:
        Path to repo
    """
    if not is_repo_path(source):
        raise Exception("Repository does not contain " + source)

    if source[-1] == '/':
        source = source[:-1]

    tempdir = tempfile.mkdtemp()

    repo = git.Repo.clone_from(os.path.join(GIT_SSH_ROOT, source), tempdir)

    return repo


def clone_multi(source):
    """
    Checks if source is valid, then clones all repositories in source

    Args:
        source(str): Suffix of URL for remote repo area to clone

    Raises:
        Exception: Repository does not contain <source>
    """
    if not is_repo_path(source):
        raise Exception("Repository does not contain " + source)

    if source[-1] == '/':
        source = source[:-1]

    split_list = get_repository_list()
    for path in split_list:
        if source in path:
            module = path.split('/')[-1]
            if module not in os.listdir("./"):
                print("Cloning: " + path + "...")
                git.Repo.clone_from(os.path.join(GIT_SSH_ROOT, path),
                                    os.path.join("./", module))
            else:
                print(module + " already exists in current directory")


def list_module_releases(repo):
    """
    Return list of release tags of module.

    Args:
        repo: Git repository instance

    Returns:
        Release tags of module corresponding to repo
    """

    releases = []
    for tag in repo.tags:
        releases.append(tag.name)
    return releases


def list_remote_branches(repo):
    """
    Lists remote branches of current git repository

    Args:
        repo: Repository instance

    Returns:
        list: Branches of current git repository

    """
    branches = []
    for ref in repo.references:
        if ref not in repo.branches + repo.tags:
            remote = str(ref).split('/')[1]
            if remote not in ['HEAD']:
                branches.append(remote)

    return branches


def checkout_remote_branch(branch, repo):
    """
    Creates a new local branch and links it to a remote of the current repo

    Args:
        branch(str): Remote branch to create locally
        repo: Repository instance
    """
    if branch in list_remote_branches(repo):
        print("Checking out " + branch + " branch.")
        repo.git.checkout("-b", branch, "origin/" + branch)


class Git(BaseVCS):

    def __init__(self, module, options):

        self._module = module
        self.area = options.area

        server_repo_path = 'controls/' + self.area + '/' + self._module

        if not is_repo_path(server_repo_path):
            raise Exception('repo not found on gitolite server')

        repo_dir = tempfile.mkdtemp(suffix="_" + self._module.replace("/", "_"))
        self._remote_repo = os.path.join(GIT_SSH_ROOT, server_repo_path)

        self.client = git.Repo.clone_from(self._remote_repo, repo_dir)
        self._version = None

    @property
    def vcs_type(self):
        return 'git'

    @property
    def module(self):
        return self._module

    @property
    def source_repo(self):
        return self._remote_repo

    @property
    def version(self):
        if not self._version:
            raise Exception('version not set')
        return self._version

    def cat(self, filename):
        """
        Fetch contents of file in repository, if version not set then uses master.

        :param filename: File to fetch from
        :return: Contents of file
        :rtype: str
        """
        tag = 'master'
        if self._version:
            if self.check_version_exists(self._version):
                tag = self._version
        return self.client.git.cat_file('-p', tag + ':' + filename)

    def list_releases(self):
        """
        Return list of release tags of module.

        :return: Release tags of module
        :rtype: list
        """
        if not hasattr(self, 'releases'):
            self.releases = []
            for tag in self.client.tags:
                self.releases.append(tag.name)
        return self.releases

    def set_log_message(self, message):
        """
        Git support will not do a commit, so log message not needed.

        :param message:
        :return:
        """
        return None

    def check_version_exists(self, version):
        """
        Check if version corresponds to a previous release.

        :param version: Release tag to check for
        :return: True or False for whether the version exists or not
        :rtype: bool
        """
        return version in self.list_releases()

    def set_branch(self, branch):
        raise NotImplementedError('branch handling for git not implemented')

    def set_version(self, version):
        """
        Set version release tag.

        :param version: Version release tag
        :type version: str
        :return: Null
        """
        if not self.check_version_exists(version):
            raise Exception('version does not exist')
        self._version = version

    def release_version(self, version):
        raise NotImplementedError('version release for git not implemented')

# sanity check: ensure class fully implements the interface (abc)
assert issubclass(Git, BaseVCS), "Git is not a base class of BaseVCS"
