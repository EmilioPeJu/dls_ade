import abc
from vcs import BaseVCS
from dls_environment.svn import svnClient

class vcs_svn(BaseVCS):

    def __init__(self):
        # self._LogMessage = ''
        self.client = svnClient()


    def check_epics_version(self, build_epics, epics_version):
        ''' Compare epics version on machine and requested, confirm choice '''
        print build_epics, epics_version


    def next_release(self, module, area):
        ''' Work out the release number by checking source directory '''
        print module, area


    def pathcheck(self, path):
        ''' search for path '''
        print path


    def create_release(self):
        ''' create release of module using mkdir and copy '''
        print "create_release"

    def mkdir(self, directory):
        ''' svn specific; create new directory (used for creating release) '''
        print path


    def copy(self, src_dir, rel_dir):
        ''' svn specific; copy dir contents (used for creating release) '''
        print src_dir, rel_dir


    # _LogMessage = ''

    def setLogMessage(self, message):
        ''' callback function to return message string for log '''
        self.client.setLogMessage(message)

    # def setLogMessage(self, message):
    #     self.client.setLogMessage(message)
    #     self._LogMessage = message

    # LogMessage = property(getLogMessage,setLogMessage)


# sanity check: ensure class fully implements the interface (abc)
assert issubclass(vcs_svn,BaseVCS)
