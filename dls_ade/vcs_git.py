#from dls_ade.vcs import BaseVCS
from vcs import BaseVCS
import subprocess
import os
import tempfile
import shutil

from pkg_resources import require
require('GitPython')
import git


GIT_ROOT = "dascgitolite@dasc-git.diamond.ac.uk"
GIT_SSH_ROOT = "ssh://dascgitolite@dasc-git.diamond.ac.uk/"


def new_is_git_dir(path="./"):
    if os.path.isdir(path):
        try:
            git.Repo(path)
        except git.exc.InvalidGitRepositoryError:
            return False
        else:
            return True
    else:
        raise Exception("Path is not valid")


def is_git_dir(path="."):
    if not os.path.isdir(path):
        # Check if local folder actually exists - below command will return True for non-existent folder that is a
        # subdirectory of a git repository (eg. git_repo/fake_name)
        return False

    return subprocess.call(
        ['git', 'status', path], stderr=subprocess.STDOUT, stdout=open(os.devnull, 'w')) == 0


def is_git_root_dir(path="."):
    if is_git_dir(path):
        git_repo = git.Repo(path)
        top_level_path = os.path.normpath(git_repo.git.rev_parse("--show-toplevel"))
        full_path = os.path.abspath(path)
        if full_path == top_level_path:
            return True
        else:
            return False
    else:
        return False


def is_repo_path(server_repo_path):

    list_cmd = "ssh " + GIT_ROOT + " expand controls"
    list_cmd_output = subprocess.check_output(list_cmd.split())

    return server_repo_path in list_cmd_output


def get_repository_list():

    list_cmd = "ssh " + GIT_ROOT + " expand controls"
    list_cmd_output = subprocess.check_output(list_cmd.split())
    split_list = list_cmd_output.split()

    return split_list


def init_repo(path="./"):

    if os.path.isdir(path):
        print("Initialising repo...")
        repo = git.Repo.init(path)
        print("Repository created.")
    else:
        raise Exception("Specified path does not exist")


def stage_all_files_and_commit(path="./"):

    if os.path.isdir(path):
        repo = git.Repo(path)
        print("Staging files...")
        repo.git.add('--all')
        print("Committing files to repo...")
        print(repo.git.commit(m="Initial commit"))
    else:
        raise Exception("Specified path does not exist")


def add_new_remote_and_push(dest, path="./", remote_name="origin", branch_name="master", ):
    '''
    This will push the given repository to the URL given by dest. If the repository already has a remote called
    <remote_name>, then it will return an exception - use push_to_remote_repo. Pushes only branch <branch_name>.
    '''

    if not is_git_root_dir(path):
        raise Exception("Path {path:s} is not a git repository".format(path=path))

    repo = git.Repo(path)

    if remote_name in [x.name for x in repo.remotes]:
        # <remote_name> remote already exists - use push_to_remote_repo instead!
        err_message = "Cannot push local repository to destination as remote {remote:s} is already defined"
        raise Exception(err_message.format(remote=remote_name))

    if is_repo_path(dest):
        raise Exception("{dest:s} already exists".format(dest=dest))

    create_remote_repo(dest)
    print("Adding remote to repo...")
    remote = repo.create_remote(remote_name, dest)
    print("Pushing repo to destination...")
    remote.push(branch_name)


def create_remote_repo(dest):
    pass
    # Change to make use of temporary directories
    # print("Creating remote...")
    # temp_dir = tempfile.mkdtemp()

    # try:
    #     #git.Repo.clone_from(dest, temp_dir)  # Cloning from gitolite server with non-existent repo creates it
    # finally:
    #     shutil.rmtree(temp_dir)


def push_to_remote(path="./", remote_name="origin", branch_name="master"):
    '''
    This will push the given local repository to its remote <remote_name> on branch <branch_name>. If this remote does
    not exist, the program will exit
    '''

    if not is_git_root_dir(path):
        raise Exception("Path given is not a git repository")

    repo = git.Repo(path)

    if remote_name not in [x.name for x in repo.remotes]:  # Remote "origin" does not already exists
        raise Exception("Local repository does not have remote " + remote_name)

    remote = repo.remotes[remote_name]
    if not is_repo_path(remote.url):
        raise Exception("Remote repository URL " + remote.url + " does not currently exist")

    if branch_name not in [x.name for x in repo.branches]:
        raise Exception("Local repository branch " + branch_name + " does not currently exist.")

    print("Pushing repo to destination...")
    remote.push(branch_name)


def clone(source, module):

    if not is_repo_path(source):
        raise Exception("Repository does not contain " + source)
    elif os.path.isdir(module):
        raise Exception(module + " already exists in current directory")

    if source[-1] == '/':
        source = source[:-1]

    git.Repo.clone_from(os.path.join(GIT_SSH_ROOT, source),
                        os.path.join("./", module))


def clone_multi(source, module):

    if not is_repo_path(source):
        raise Exception("Repository does not contain " + source)
    elif os.path.isdir(module):
        raise Exception(module + " already exists in current directory")

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
        '''
        Fetch contents of file in repository, if version not set then uses
        master.
        '''
        tag = 'master'
        if self._version:
            if self.check_version_exists(self._version):
                tag = self._version
        return self.client.git.cat_file('-p', tag + ':' + filename)

    def list_releases(self):
        '''Return list of release tags of module.'''
        if not hasattr(self, 'releases'):
            self.releases = []
            for tag in self.client.tags:
                self.releases.append(tag.name)
        return self.releases

    def set_log_message(self, message):
        '''Git support will not do a commit, so log message not needed.'''
        return None

    def check_version_exists(self, version):
        return version in self.list_releases()

    def set_branch(self, branch):
        raise NotImplementedError('branch handling for git not implemented')

    def set_version(self, version):
        if not self.check_version_exists(version):
            raise Exception('version does not exist')
        self._version = version

    def release_version(self, version):
        raise NotImplementedError('version release for git not implemented')

# sanity check: ensure class fully implements the interface (abc)
assert issubclass(Git, BaseVCS), "Git is not a base class of BaseVCS"
