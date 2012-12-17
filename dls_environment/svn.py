#!/bin/env python2.6

# import the version of pysvn that matches with the version of subversion installed
from subprocess import Popen, PIPE
version = Popen(["svn","--quiet","--version"], stdout = PIPE, stderr = PIPE)
(stdout, stderr) = version.communicate()
if version.returncode != 0:
    raise Exception(stderr)
svn_version = stdout.strip()

#if "release 5" in open("/etc/redhat-release").read():
#    svn_version += ".RHEL5"

from pkg_resources import require
try:
    require("pysvn=="+svn_version)
except:
    # pysvn is not an egg on RHEL6
    pass
import pysvn, os

class svnClient:
    "Wrapper for pysvn Client with dls functions"
    
    def __init__(self):
        self.client = pysvn.Client()
        # hack to make svnClient look like it has all the methods of pysvn.Client and pysvn
        for ob in [self.client,pysvn]:
            for method in dir(ob):
                if not hasattr(self,method):
                    try:
                        setattr(self,method,getattr(ob,method))
                    except AttributeError:
                        pass

    def pathcheck(self, path):
        """Returns True if path exists in self, False if it doesn't"""
        try:        
            junk = self.client.ls(path)
            ret    = True
        except pysvn._pysvn.ClientError:
            ret    = False
        return ret
        
    def workingCopy(self,directory="."):
        """If directory is a working copy, return its pysvn.info dict, otherwise
        return ''"""
        try:
            ret = self.client.info(directory)
        except pysvn._pysvn.ClientError:
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
        assert type in ("branches","release","tags","trunk","vendor"), "Subversion type must be branches, release, tags, trunk or vendor"
        if area in ["etc"]:
            return os.path.join(self.root(),area,type,"prod")
        elif area in ["epics"]:
            return os.path.join(self.root(),area,type)
        elif area in ["tools"]:
            return os.path.join(self.root(),"diamond",type,"build_scripts")
        else:
            return os.path.join(self.root(),"diamond",type,area)        
       
if __name__=="__main__":
    a = svnClient()
    print a.ls(a.root())

    for area in ["support", "ioc", "matlab", "python","etc","epics","tools"]:
        print "Production  directory for area %s is %s"%(area,a.prodArea(area))
        print "Development directory for area %s is %s"%(area,a.devArea(area))

    for module in ["init","Launcher","build","redirector"]:
        print "Production  directory for module %s is %s"%(module,a.prodModule(module,"etc"))
        print "Development directory for module %s is %s"%(module,a.devModule(module,"etc"))
       
        print
