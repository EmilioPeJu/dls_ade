import abc

class BaseVCS(object):
    ''' Abstract interface to a version control system class '''
    __metaclass__ = abc.ABCMeta


    @abc.abstractmethod
    def check_epics_version(self, build_epics, epics_version):
        ''' Compare epics version on machine and requested, confirm choice '''
        raise NotImplementedError


    @abc.abstractmethod
    def next_release(self, module, area):
        ''' Work out the release number by checking source directory '''
        raise NotImplementedError

    
    @abc.abstractmethod
    def pathcheck(self, path):
        ''' search for path '''
        raise NotImplementedError


    @abc.abstractmethod
    def create_release(self):
        ''' create release/tag of module '''
        raise NotImplementedError


    @abc.abstractmethod
    def setLogMessage(self, message):
        '''
        abstraction for callback function to return message string for log
        '''
        raise NotImplementedError


    # read/write-able attribute
    # LogMessage = abc.abstractproperty(getLogMessage,setLogMessage)