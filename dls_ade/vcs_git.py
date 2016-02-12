from dls_ade.vcs import BaseVCS
import subprocess
import os
import tempfile
import shutil
from dls_ade import path_functions as pathf
from pkg_resources import require
require('GitPython')
import git

from dls_ade.exceptions import VCSGitError

GIT_ROOT = "dascgitolite@dasc-git.diamond.ac.uk"
GIT_SSH_ROOT = "ssh://" + GIT_ROOT + "/"
GIT_ROOT_DIR = pathf.GIT_ROOT_DIR


def is_in_local_repo(path="./"):
    """
    Returns whether or not the local path is inside a git repository.

    Args:
        path(str): The path to check.
            This is the current working directory by default.

    Returns:
        bool: True if the path is inside a git repository, false otherwise.

    Raises:
        :class:`~dls_ade.exceptions.VCSGitError`: If the path given is not a \
            local directory.

    """
    if not os.path.isdir(path):
        raise VCSGitError("Path is not valid")

    try:
        git.Repo(path)
    except git.exc.InvalidGitRepositoryError:
        return False
    else:
        return True


def is_local_repo_root(path="."):
    """
    Returns whether or not the local path is the root of a git repository.

    Args:
        path(str): The path to check.
            This is the current working directory by default.

    Returns:
        bool: True if the path is inside a git repository, false otherwise.

    Raises:
        :class:`~dls_ade.exceptions.VCSGitError`: If path given is not a \
            local directory (from :func:`is_in_local_repo`).

    """
    if not is_in_local_repo(path):
        return False

    git_repo = git.Repo(path)
    top_level_path = os.path.normpath(
        git_repo.git.rev_parse("--show-toplevel")
    )
    full_path = os.path.abspath(path)

    return full_path == top_level_path


def is_server_repo(server_repo_path):
    """
    Checks if path exists on repository

    Args:
        server_repo_path(str): Path to module to check for

    Returns:
        bool: True if path does exist False if not

    """
    repo_list = get_server_repo_list()
    return server_repo_path in repo_list


def get_server_repo_list():
    """
    Returns list of module repository paths from the git server.

    Returns:
        List[str]: Repository paths on the server.

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
    """
    Initialise a local git repository.

    Args:
        path(str): The relative or absolute path for the local git repository.

    Raises:
        :class:`~dls_ade.exceptions.VCSGitError`: If the path is not a \
            directory, or is already a git repository.

    """
    if not os.path.isdir(path):
        raise VCSGitError("Path {path:s} is not a directory".format(path=path))

    if is_local_repo_root(path):
        err_message = "Path {path:s} is already a git repository"
        raise VCSGitError(err_message.format(path=path))

    print("Initialising repo...")
    git.Repo.init(path)
    print("Repository created.")


def stage_all_files_and_commit(path="./", message="Initial commit."):
    """Stage and commit all files in a local git repository.

    Args:
        path: The relative or absolute path of the local git repository.
        message: The commit message to use.

    Raises:
        :class:`~dls_ade.exceptions.VCSGitError`: If the path is not a git \
            repository.

    """
    if not os.path.isdir(path):
        raise VCSGitError("Path {path:s} is not a directory".format(path=path))

    if not is_local_repo_root(path):
        err_message = "Path {path:s} is not a git repository"
        raise VCSGitError(err_message.format(path=path))

    repo = git.Repo(path)
    print("Staging files...")
    repo.git.add('--all')
    print("Committing files to repo...")

    # If there are no changes to commit, then GitCommandError will be raised.
    # There is no reason to raise an exception for this.
    msg = ""
    try:
        msg = repo.git.commit(m=message)
    except git.exc.GitCommandError as e:
        pass
    print(msg)


def add_new_remote_and_push(dest, path="./", remote_name="origin",
                            branch_name="master"):
    """
    Adds a remote to a git repository, and pushes to the gitolite server.

    This will fail if:
        - The path given is not a git repository.
        - The local repository does not have the given branch name.
        - The remote name already exists for the local repository.
        - A git repository already exists on the destination path.

    Note:
        If the local repository already has the given remote name defined, use
        :func:`push_to_remote` to push to its defined server path.

    Args:
        dest(str): The server path for the git repository.
        path(str): The relative or absolute path for the local git repository.
        remote_name(str): The git repository's alias for the destination path.
        branch_name(str): The name of the branch to push from / to.

    Raises:
        :class:`~dls_ade.exceptions.VCSGitError`: If there is an issue with \
            the operation.

    """
    if not is_local_repo_root(path):
        err_message = "Path {path:s} is not a git repository"
        raise VCSGitError(err_message.format(path=path))

    repo = git.Repo(path)

    if branch_name not in [x.name for x in repo.branches]:
        err_message = ("Local repository branch {branch:s} does not currently "
                       "exist.")
        raise VCSGitError(err_message.format(branch=branch_name))

    if has_remote(repo, remote_name):
        # <remote_name> already exists - use push_to_remote_repo instead!
        err_message = ("Cannot push local repository to destination as remote "
                       "{remote:s} is already defined")
        raise VCSGitError(err_message.format(remote=remote_name))

    create_remote_repo(dest)
    print("Adding remote to repo...")
    remote = repo.create_remote(remote_name, os.path.join(GIT_SSH_ROOT, dest))
    print("Pushing repo to destination...")
    remote.push(branch_name)


def create_remote_repo(dest):
    """
    Create a git repository on the given gitolite server path.

    Args:
        dest(str): The server path for the git repository to be created.

    Raises:
        :class:`~dls_ade.exceptions.VCSGitError`: If a git repository already \
            exists on the destination path.

    """
    if is_server_repo(dest):
        raise VCSGitError("{dest:s} already exists".format(dest=dest))

    git_dest = os.path.join(GIT_SSH_ROOT, dest)

    print("Creating remote...")
    temp_dir = tempfile.mkdtemp()

    try:
        # Cloning from gitolite server with non-existent repo creates it
        git.Repo.clone_from(git_dest, temp_dir)
    finally:
        shutil.rmtree(temp_dir)


def push_to_remote(path="./", remote_name="origin", branch_name="master"):
    """
    Pushes to the server path given by its remote name, on the given branch.

    Args:
        path(str): The relative or absolute path for the local git repository.
        remote_name(str): The git repository's remote name to push to.
        branch_name(str): The name of the branch to push from / to.

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
        :class:`~dls_ade.exceptions.VCSGitError`: If there is an issue with \
            the operation.

    """
    if not is_local_repo_root(path):
        err_message = "Path {path:s} is not a git repository"
        raise VCSGitError(err_message.format(path=path))

    repo = git.Repo(path)

    if branch_name not in [x.name for x in repo.branches]:
        err_message = ("Local repository branch {branch:s} does not currently "
                       "exist.")
        raise VCSGitError(err_message.format(branch=branch_name))

    check_remote_exists(repo, remote_name)

    # They have overloaded the dictionary lookup to compare string with .name
    remote = repo.remotes[remote_name]

    if not remote.url.startswith(GIT_SSH_ROOT):
        err_message = ("Remote repository URL {remoteURL:s} does not "
                       "begin with the gitolite server path")
        raise VCSGitError(err_message.format(remoteURL=remote.url))

    # Removes initial GIT_SSH_ROOT (with slash at end)
    server_repo_path = remote.url[len(GIT_SSH_ROOT):]

    if not is_server_repo(server_repo_path):
        err_message = ("Server repo path {s_repo_path:s} does not "
                       "currently exist")
        raise VCSGitError(err_message.format(s_repo_path=server_repo_path))

    print("Pushing repo to destination...")
    remote.push(branch_name)


def check_remote_exists(repo, remote_name):
    """Raises exception if the given remote name does not exist in the repo.

    Args:
        repo: The git.Repo object representing the repository.
        remote_name: The remote name to be checked for.

    Raises:
        :class:`~dls_ade.exceptions.VCSGitError`: If the given remote name \
            does not exist.

    """
    if not has_remote(repo, remote_name):
        err_message = "Local repository does not have remote {remote:s}"
        raise VCSGitError(err_message.format(remote=remote_name))


def has_remote(repo, remote_name):
    """Returns true if the given repository already has the named remote.

    Args:
        repo: The git.Repo object representing the repository.
        remote_name: The remote name to be looked for.

    """
    return remote_name in [x.name for x in repo.remotes]


def clone(server_repo_path, local_repo_path):
    """
    Clones a repository on the server to a local directory.

    Args:
        server_repo_path(str): Suffix of URL for remote repo to clone
        local_repo_path(str): Name of module to clone

    Raises:
        :class:`~dls_ade.exceptions.VCSGitError`: Repository does not contain \
            <source>
        :class:`~dls_ade.exceptions.VCSGitError`: <module> already exists in \
            current directory

    """
    if not is_server_repo(server_repo_path):
        raise VCSGitError("Repository does not contain " + server_repo_path)
    elif os.path.isdir(local_repo_path):
        raise VCSGitError(local_repo_path + " already exists in current "
                                            "directory")

    pathf.remove_end_slash(server_repo_path)

    print(os.path.join(GIT_SSH_ROOT, server_repo_path))

    repo = git.Repo.clone_from(os.path.join(GIT_SSH_ROOT, server_repo_path),
                               os.path.join("./", local_repo_path))

    return repo


def temp_clone(source):
    """
    Clones repo to /tmp directory and returns the relevant git.Repo object.

    Args:
        source(str): server repository path to clone

    Returns:
        :class:`~git.repo.base.Repo`: Repository instance

    """
    if not is_server_repo(source):
        raise VCSGitError("Repository does not contain " + source)

    pathf.remove_end_slash(source)

    tempdir = tempfile.mkdtemp()

    repo = git.Repo.clone_from(os.path.join(GIT_SSH_ROOT, source), tempdir)

    return repo


def clone_multi(source):
    """
    Checks if source is valid, then clones all repositories in source

    Args:
        source(str): Suffix of URL for remote repo area to clone

    Raises:
        :class:`~dls_ade.exceptions.VCSGitError`: Repository does not contain \
            <source>
    """

    split_list = get_server_repo_list()
    for path in split_list:
        if path.startswith(source):

            # Remove controls/<area>/ from front of save path
            module = path.split('/', 2)[-1]
            print("Module: " + module)

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
        repo(:class:`~git.repo.base.Repo`): Git repository instance

    Returns:
        List[str]: Release tags of module corresponding to repo
    """

    releases = []
    for tag in repo.tags:
        releases.append(tag.name)
    return releases


def list_remote_branches(repo):
    """
    Lists remote branches of current git repository

    Args:
        repo(:class:`~git.repo.base.Repo`): Git repository instance

    Returns:
        List[str]: Branches of current git repository

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
        repo(:class:`~git.repo.base.Repo`): Git repository instance

    """
    if branch in list_remote_branches(repo):
        print("Checking out " + branch + " branch.")
        repo.git.checkout("-b", branch, "origin/" + branch)


def check_git_attributes(local_repo_path, attributes_dict):
    """Checks the given local repository for the attributes listed.

    Args:
        local_repo_path: The path to the local repository.
        attributes_dict(dict): A dictionary of key-value pairs for attributes.

    Returns:
        bool: True if all attributes present, False otherwise.

    """
    repo = git.Repo(local_repo_path)

    for attr in attributes_dict:
        output = repo.git.check_attr((attr + " -- .").split())
        exp_out = ".: {attr:s}: {value:s}"
        exp_out = exp_out.format(attr=attr, value=attributes_dict[attr])

        if not exp_out == output:
            return False

    return True


def get_active_branch(local_repo_path):
    """Returns the active branch of the given local repository.

    Args:
        local_repo_path: The path to the local repository.

    Returns:
        str: The name of the active branch.

    """
    repo = git.Repo(local_repo_path)

    return repo.active_branch.name


def delete_remote(local_repo_path, remote_name):
    """Deletes the remote for the given local repository.

    Args:
        local_repo_path: The path to the local repository.
        remote_name: The name of the remote to be deleted.

    Raises:
        :class:`~dls_ade.exceptions.VCSGitError`: If the given remote name \
            does not exist.

    """
    repo = git.Repo(local_repo_path)

    check_remote_exists(repo, remote_name)

    repo.git.remote("rm", remote_name)


def push_all_branches_and_tags(local_repo_path, server_repo_path, remote_name):
    """Push all branches a tags of a local repository to the given server path.

    Args:
        local_repo_path: The path to the local repository.
        server_repo_path: The path on the server for the repository.
        remote_name: The name of the remote to push with.
            This will be deleted if it already exists.

    Raises:
        :class:`~dls_ade.exceptions.VCSGitError`: From \
            :func:`.check_remote_exists`.

    """
    repo = git.Repo(local_repo_path)

    if has_remote(repo, remote_name):
        delete_remote(local_repo_path, remote_name)

    repo.create_remote(remote_name, os.path.join(GIT_SSH_ROOT,
                                                 server_repo_path))
    repo.git.push(remote_name, "*:*")
    repo.git.push(remote_name, "--tags")


class Git(BaseVCS):
    """
    A class to handle generic vcs operations in a git context.

    """

    def __init__(self, module, options):

        self._module = module
        self.area = options.area

        server_repo_path = pathf.dev_module_path(self._module, self.area)

        if not is_server_repo(server_repo_path):
            raise VCSGitError('repo not found on gitolite server')

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
            raise VCSGitError('version not set')
        return self._version

    def cat(self, filename):
        """
        Fetch contents of file in repository, if version not set then uses master.

        Args:
            filename(str): File to fetch from

        Returns:
            str: Contents of file

        """
        tag = 'master'
        if self._version:
            if self.check_version_exists(self._version):
                tag = self._version
        try:
            return self.client.git.cat_file('-p', tag+':'+filename)
        except git.GitCommandError:
            return str('')

    def list_releases(self):
        """
        Return list of release tags of module.

        Returns:
            list[str]: Release tags of module

        """

        releases = []
        for tag in self.client.tags:
            releases.append(tag.name)

        return releases

    def set_log_message(self, message):
        """
        Git support will not do a commit, so log message not needed.

        Args:
            message:

        Returns:
            None

        """
        return None

    def check_version_exists(self, version):
        """
        Check if version corresponds to a previous release.

        Args:
            version(str): Release tag to check for

        Returns:
            bool: True or False for whether the version exists or not

        """
        return version in self.list_releases()

    def set_branch(self, branch):
        raise NotImplementedError('branch handling for git not implemented')

    def set_version(self, version):
        """
        Set version release tag for self

        Args:
            version(str): Version release tag

        """
        if not self.check_version_exists(version):
            raise VCSGitError('version does not exist')
        self._version = version

    def release_version(self, version):
        raise NotImplementedError('version release for git not implemented')

# sanity check: ensure class fully implements the interface (abc)
assert issubclass(Git, BaseVCS), "Git is not a base class of BaseVCS"
