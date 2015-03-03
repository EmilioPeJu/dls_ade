import abc


class BaseVCS(object):
    ''' Abstract interface to a version control system class '''
    __metaclass__ = abc.ABCMeta


    # @abc.abstractmethod
    # def cat(self,filename):
    #     ''' Fetch contents of particular file in remote repository '''
    #     raise NotImplementedError


    @abc.abstractmethod
    def list_releases(self):
        ''' Return list of releases/tags of module '''
        raise NotImplementedError


    # @abc.abstractmethod
    # def path_check(self, path):
    #     ''' search for path. '''
    #     raise NotImplementedError


    # @abc.abstractmethod
    # def checkout_module(self):
    #     ''' Create release/tag of module. '''
    #     raise NotImplementedError


    # @abc.abstractmethod
    # def set_log_message(self, message):
    #     '''
    #     Abstraction for callback function to return message string for log.
    #     '''
    #     raise NotImplementedError


    # @abc.abstractmethod
    # def get_src_dir(self, module, options):
    #     '''
    #     Find/create the source directory from which to release the module.
    #     '''
    #     raise NotImplementedError


    # @abc.abstractmethod
    # def get_rel_dir(self, module, options):
    #     '''
    #     Create the release directory the module will be released into.
    #     '''
    #     raise NotImplementedError
