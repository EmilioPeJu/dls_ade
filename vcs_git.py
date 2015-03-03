from vcs import BaseVCS
from pkg_resources import require
require('GitPython')
import git
import tempfile
import subprocess


class Git(BaseVCS):

    def __init__(self, module, options):

        list_cmd = 'ssh dascgitolite@dasc-git.diamond.ac.uk expand controls'
        list_cmd_output = subprocess.check_output(list_cmd.split())

        server_repo_path = 'controls/'+options.area+'/'+module
        if server_repo_path not in list_cmd_output:
            raise Exception('repo not found on gitolite server')

        self.repo_dir = tempfile.mkdtemp(suffix="_"+module)
        remote_repo = 'ssh://dascgitolite@dasc-git.diamond.ac.uk/'
        remote_repo += server_repo_path

        self.client = git.Repo.clone_from(remote_repo, self.repo_dir)

    # def cat(self, filename):
    #     ''' Fetch contents of file in remote repository '''
    #     return self.client.git.cat_file('-p',filename)

    def list_releases(self, module, area):
        ''' Return list of release tags of module '''
        release_paths = []
        for tag in self.client.tags:
            release_paths.append(tag.name)
        return release_paths

    # def path_check(self, path):
    #     ''' search for path '''
    #     pass

    # def checkout_module(self, module, area, not_src_dir, rel_dir):
    #     pass

    def set_log_message(self, message):
        ''' Git support will not do a commit, so log message not needed. '''
        return None

    # def get_src_dir(self, module, options):
    #     '''
    #     Find/create the source directory from which to release the module.
    #     '''
    #     pass

    # def get_rel_dir(self, module, options, version):
    #     '''
    #     Create the release directory the module will be released into.
    #     '''
    #     pass


# sanity check: ensure class fully implements the interface (abc)
assert issubclass(Git, BaseVCS)
