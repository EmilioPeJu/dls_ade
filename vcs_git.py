from vcs import BaseVCS
from pkg_resources import require
require('GitPython')
import git
import tempfile
import subprocess


class Git(BaseVCS):


    def __init__(self, module, options):

        self._module = module
        self.area = options.area
        self.init_client()
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


    def init_client(self):
        list_cmd = 'ssh dascgitolite@dasc-git.diamond.ac.uk expand controls'
        list_cmd_output = subprocess.check_output(list_cmd.split())

        server_repo_path = 'controls/' + self.area + '/' + self._module
        if server_repo_path not in list_cmd_output:
            raise Exception('repo not found on gitolite server')

        repo_dir = tempfile.mkdtemp(suffix="_" + self._module)
        self._remote_repo = 'ssh://dascgitolite@dasc-git.diamond.ac.uk/'
        self._remote_repo += server_repo_path

        self.client = git.Repo.clone_from(self._remote_repo, repo_dir)


    def cat(self, filename):
        '''
        Fetch contents of file in repository, if version not set then uses
        master.
        '''
        tag = 'master'
        if self._version:
            if self.check_version_exists(self._version):
                tag = self._version
        return self.client.git.cat_file('-p', tag+':'+filename)


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
