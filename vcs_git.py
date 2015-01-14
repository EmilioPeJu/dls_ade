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


    def check_epics_version(self, src_dir, build_epics, epics_version):
        ''' Compare epics version on machine and requested, confirm choice '''
        pass


    def next_release(self, module, area):
        ''' Work out the release number by checking source directory '''
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