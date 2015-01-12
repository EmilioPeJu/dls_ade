import abc

class BaseVCS(object):
    '''
    Abstract interface to a version control system class
    '''
    __metaclass__ = abc.ABCMeta


    @abc.abstractmethod
    def check_epics_version(self, build_epics, epics_version):
        '''
        Compare epics version on machine and requested, confirm choice
        '''
        raise NotImplementedError


    @abc.abstractmethod
    def next_release(self, module, area):
        '''
        Work out the release number by checking source directory
        '''
        raise NotImplementedError

    
    @abc.abstractmethod
    def pathcheck(self, path):
        '''
        search for path
        '''
        raise NotImplementedError


    @abc.abstractmethod
    def mkdir(self, directory):
        '''
        create a new directory
        '''
        raise NotImplementedError


    @abc.abstractmethod
    def copy(self, src_dir, rel_dir):
        '''
        move the contents of one directory to another
        '''
        raise NotImplementedError

    
    def getLogMessage(self):
        return "Should never see this"

    def setLogMessage(self,newmessage):
        return

    # read/write-able attribute
    LogMessage = abc.abstractproperty(getLogMessage,setLogMessage)