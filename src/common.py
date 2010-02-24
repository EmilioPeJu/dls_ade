#!/bin/env python2.4

# import the version of pysvn that matches with the version of subversion installed
from subprocess import Popen, PIPE
version = Popen(["svn","--quiet","--version"], stdout = PIPE, stderr = PIPE)
(stdout, stderr) = version.communicate()
if version.returncode != 0:
    raise Exception(stderr)
svn_version = stdout.strip()
if "release 5" in open("/etc/redhat-release").read():
	svn_version += ".RHEL5"

from pkg_resources import require
require("dls.pysvn=="+svn_version)
import dls.pysvn
import os
from optparse import OptionParser

def doc(usage):
    "decorator that documents function with usage string"
    def decorator(f):
        f.__doc__ = usage.replace("%prog",f.__name__)
        return f
    return decorator

class svnClient:
    "Wrapper for pysvn Client with dls functions"
    
    def __init__(self):
        self.client = dls.pysvn.Client()
        # hack to make svnClient look like it has all the methods of pysvn.Client and pysvn
        for ob in [self.client,dls.pysvn]:
            for method in dir(ob):
                if not hasattr(self,method):
                    setattr(self,method,getattr(ob,method))
                
    def pathcheck(self, path):
        """Returns True if path exists in self, False if it doesn't"""
        try:        
            junk = self.client.ls(path)
            ret    = True
        except dls.pysvn._pysvn.ClientError:
            ret    = False
        return ret
        
    def workingCopy(self,directory="."):
        """If directory is a working copy, return its pysvn.info dict, otherwise
        return ''"""
        try:
            ret = self.client.info(directory)
        except dls.pysvn._pysvn.ClientError:
            ret = ''
        return ret
        
    def setLogMessage(self,log_message):
        """Create a default log message for the client to use"""
        def getLogMessage():
            return True, log_message
        self.client.callback_get_log_message = getLogMessage
        
    def mkdir(self,name):
        """Makes name and all parent directories on the way"""
        dirs = name.replace(self.root(),"").split("/")
        dirs[0] = self.root()
        for i in range(1,len(dirs)+1):
            # make sure all directories exist
            path = os.path.join(*dirs[:i])
            if not self.pathcheck(path):
                self.client.mkdir(path,'Created: '+path)
        
    def root(self):
        """Return the root for subversion (SVN_ROOT variable in the environment)"""
        root = os.environ["SVN_ROOT"]
        assert os.environ["SVN_ROOT"], "'SVN_ROOT' environment variable must be set"
        return root
                
    def devArea(self,area = "support"):
        """Return the path for the trunk section of a particular area"""
        return self.__area("trunk",area)
    
    def devModule(self,module,area = "support"):
        """Return the path for module in trunk section a particular area"""
        return os.path.join(self.devArea(area),module)

    def prodArea(self,area = "support"):
        """Return the path for the release section of a particular area"""
        return self.__area("release",area)
    
    def prodModule(self,module,area = "support"):
        """Return the path for module in release section a particular area"""
        return os.path.join(self.prodArea(area),module)

    def branchArea(self,area = "support"):
        """Return the path for the branch section of a particular area"""  
        return self.__area("branches",area)
    
    def branchModule(self,module,area = "support"):
        """Return the path for module in branch section a particular area"""
        return os.path.join(self.branchArea(area),module)

    def vendorArea(self,area = "support"):
        """Return the path for the vendor section of a particular area"""   
        return self.__area("vendor",area)
    
    def vendorModule(self,module,area = "support"):
        """Return the path for module in vendor section a particular area"""
        return os.path.join(self.vendorArea(area),module)

    def __area(self,type,area):
        if area == "init":
            return os.path.join(self.root(),"etc",type,"prod",area)
        else:
            return os.path.join(self.root(),"diamond",type,area)        

class svnOptionParser(OptionParser):
    "options parser with default options for dls svn environment"
    def __init__(self,usage):
        OptionParser.__init__(self,usage)    
        self.add_option("-a", "--area", action="store", type="string", dest="area", help="set <area>=AREA, e.g. support, ioc, python, matlab")
        self.add_option("-p", "--python", action="store_true", dest="python", help="set <area>='python'")
        self.add_option("-i", "--ioc", action="store_true", dest="ioc", help="set <area>='ioc'")
    
    def parse_args(self):
        (options, args) = OptionParser.parse_args(self)
        # setup area
        if options.ioc:
            options.area = "ioc"
        elif options.python:
            options.area = "python"
        elif not options.area:
            options.area = "support"
        return (options,args)
        

if __name__=="__main__":
    a = svnClient()
    print a.ls(a.root())
