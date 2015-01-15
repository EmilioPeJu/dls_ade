import abc
import os
import re
from vcs import BaseVCS
from pkg_resources import require
require('GitPython')
import git


class Git(BaseVCS):

    def __init__(self):
        pass


    def cat(self, filename):
        ''' Fetch contents of file in remote repository '''
        pass


    def list_releases(self, module, area):
        ''' Return list of release tags of module '''
        pass


    def path_check(self, path):
        ''' search for path '''
        pass


    def checkout_module(self, module, area, not_src_dir, rel_dir):
        pass


    def set_log_message(self, message):
        ''' Git support will not do a commit, so log message not needed. '''
        return None


    def get_src_dir(self, module, options):
        '''
        Find/create the source directory from which to release the module.
        '''
        pass


    def get_rel_dir(self, module, options, version):
        '''
        Create the release directory the module will be released into.
        '''
        pass


# sanity check: ensure class fully implements the interface (abc)
assert issubclass(Git, BaseVCS)