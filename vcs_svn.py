import abc
from vcs import BaseVCS


class vcs_svn(BaseVCS):


    def check_epics_version(self, build_epics, epics_version):
        print build_epics, epics_version


    def next_release(self, module, area):
        print module, area


    def pathcheck(self, path):
        print path


    def mkdir(self, directory):
        print path


    def copy(self, src_dir, rel_dir):
        print src_dir, rel_dir


    _LogMessage = ''

    def getLogMessage(self):
        return self._LogMessage

    def setLogMessage(self, message):
        self._LogMessage = message

    LogMessage = property(getLogMessage,setLogMessage)