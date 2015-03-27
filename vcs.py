import abc


class BaseVCS(object):
    '''Abstract interface to a version control system class'''
    __metaclass__ = abc.ABCMeta


    @abc.abstractproperty
    def vcs_type(self):
        raise NotImplementedError


    @abc.abstractproperty
    def module(self):
        raise NotImplementedError


    @abc.abstractproperty
    def source_repo(self):
        ''' Fetch repo url for use by build server '''
        raise NotImplementedError


    @abc.abstractmethod
    def cat(self, filename):
        ''' Fetch contents of particular file in remote repository '''
        raise NotImplementedError


    @abc.abstractmethod
    def list_releases(self):
        ''' Return list of releases/tags of module '''
        raise NotImplementedError


    @abc.abstractmethod
    def set_log_message(self, message):
        '''
        Abstraction for callback function to return message string for log.
        '''
        raise NotImplementedError


    @abc.abstractmethod
    def check_version_exists(self, version):
        ''' True/False for existence of release/tag in repository '''
        raise NotImplementedError


    @abc.abstractmethod
    def set_branch(self, branch):
        ''' Specify a branch of the repo to use '''
        raise NotImplementedError