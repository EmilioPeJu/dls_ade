from vcs import BaseVCS
import tempfile
import subprocess
import os

from pkg_resources import require
require('GitPython')
import git


GIT_ROOT = "dascgitolite@dasc-git.diamond.ac.uk"
GIT_SSH_ROOT = "ssh://dascgitolite@dasc-git.diamond.ac.uk/"
GIT_ROOT_DIR = os.getenv('GIT_ROOT_DIR', "controls")


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


def temp(area, module):
    # >>> This has been properly implemented on start-new-module branch

    # >>> adjust for technical area
    if area == "ioc":
        pass

    path = "./"
    target = os.path.join(GIT_SSH_ROOT, "controls", area, module)

    print("Initialising repo...")
    repo = git.Repo.init(path)
    print("Creating remote...")
    repo.clone_from(target, path + "dummy")
    os.rmdir(path + "dummy")
    print("Adding remote to repo...")
    origin = repo.create_remote("origin", target)
    repo.git.add('--all')
    print("Committing files to repo...")
    print(repo.git.commit(m=" 'Initial commit'"))
    print("Pushing repo to gitolite...")
    origin.push('master')


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

    path = os.path.join("/tmp", 'temp_module')

    repo = git.Repo.clone_from(os.path.join(GIT_SSH_ROOT, source), path)

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
            source_length = len(source) + 1
            target_path = path[source_length:]
            if target_path not in os.listdir("./"):
                print("Cloning: " + path + "...")
                git.Repo.clone_from(os.path.join(GIT_SSH_ROOT, path),
                                    os.path.join("./", target_path))
            else:
                print(target_path + " already exists in current directory")


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
