import os
from pkg_resources import require
require('GitPython')
import git

GIT_ROOT = "ssh://dascgitolite@dasc-git.diamond.ac.uk/"

# Lots of Git functions in here /dls_sw/prod/tools/RHEL6-x86_64/defaults/lib/python2.7/site-packages/all_eggs/GitPython-0.3.2.RC1-py2.7.egg/git/refs/head.py
# and here /dls_sw/prod/tools/RHEL6-x86_64/defaults/lib/python2.7/site-packages/all_eggs/GitPython-0.3.2.RC1-py2.7.egg/git/refs/base.py


def root():
    """Return the root for subversion (SVN_ROOT variable in the environment)"""
    rootV = GIT_ROOT
    # assert os.environ["SVN_ROOT"], "'SVN_ROOT' environment variable must be set"
    return rootV


def area(typeV, areaV):
    assert typeV in ("branches", "release", "tags", "trunk", "vendor"),\
        "Type must be: branches, release, tags, trunk or vendor"
    if areaV is "etc":
        return os.path.join(root(), areaV, typeV, "prod")
    elif areaV is "epics":
        return os.path.join(root(), areaV, typeV)
    elif areaV is "tools":
        return os.path.join(root(), "diamond", typeV, "build_scripts")
    else:
        return os.path.join(root(), "diamond", typeV, areaV)


def devArea(areaV="support"):
    """Return the path for the trunk section of a particular area"""
    return area("trunk", areaV)


def devModule(module, areaV="support"):
    """Return the path for module in trunk section a particular area"""
    return os.path.join(devArea(areaV), module)


def prodArea(areaV="support"):
    """Return the path for the release section of a particular area"""
    return area("release", areaV)


def prodModule(module, areaV="support"):
    """Return the path for module in release section a particular area"""
    return os.path.join(prodArea(areaV), module)


def branchArea(areaV="support"):
    """Return the path for the branch section of a particular area"""
    return area("branches", areaV)


def branchModule(module, areaV="support"):
    """Return the path for module in branch section a particular area"""
    return os.path.join(branchArea(areaV), module)


def vendorArea(areaV="support"):
    """Return the path for the vendor section of a particular area"""
    return area("vendor", areaV)


def vendorModule(module, areaV="support"):
    """Return the path for module in vendor section a particular area"""
    return os.path.join(vendorArea(areaV), module)


def pathcheck(path):
    """Returns True if path exists in self, False if it doesn't"""
    try:
        junk = self.client.ls(path)
        ret = True
    except pysvn._pysvn.ClientError:
        ret = False
    return ret


def setLogMessage(log_message):
    """Create a default log message for the client to use"""
    def getLogMessage():
        return True, log_message
    self.client.callback_get_log_message = getLogMessage


def mkdir(name):
    """Makes name and all parent directories on the way"""
    dirs = name.replace(root(), "").split("/")
    dirs[0] = root()
    for i in range(1, len(dirs)+1):
        # make sure all directories exist
        path = os.path.join(*dirs[:i])
        if not self.pathcheck(path):
            self.client.mkdir(path, 'Created: ' + path)
