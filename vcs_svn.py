import abc
from vcs import BaseVCS


class vcs_svn(BaseVCS):


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


    _LogMessage = ''

    def getLogMessage(self):
        return self._LogMessage

    def setLogMessage(self, message):
        self._LogMessage = message

    LogMessage = property(getLogMessage,setLogMessage)


# sanity check: ensure class fully implements the interface (abc)
assert issubclass(vcs_svn,BaseVCS)
