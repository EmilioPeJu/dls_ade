import os
import vcs_git

GIT_SSH_ROOT = vcs_git.GIT_SSH_ROOT
GIT_ROOT_DIR = vcs_git.GIT_ROOT_DIR


def root():
    """Return the root for subversion (SVN_ROOT variable in the environment)"""
    root_v = GIT_SSH_ROOT
    # assert os.environ["SVN_ROOT"], "'SVN_ROOT' environment variable must be set"
    return root_v


# TODO Sort out paths for etc, epics (root() replaced with GIT_ROOT_DIR)
def area(area_v):

    if area_v is "etc":
        return os.path.join(root(), area_v, "prod")
    elif area_v is "epics":
        return os.path.join(root(), area_v)
    else:
        return os.path.join(GIT_ROOT_DIR, area_v)


def devArea(area_v="support"):
    """Return the path for the trunk section of a particular area_v"""
    return area(area_v)


def devModule(module, area_v="support"):
    """Return the path for module in trunk section a particular area"""
    return os.path.join(devArea(area_v), module)


def prodArea(area_v="support"):
    """Return the path for the release section of a particular area"""
    return area(area_v)


def prodModule(module, area_v="support"):
    """Return the path for module in release section a particular area"""
    return os.path.join(prodArea(area_v), module)


def branchArea(area_v="support"):
    """Return the path for the branch section of a particular area"""
    return area(area_v)


def branchModule(module, area_v="support"):
    """Return the path for module in branch section a particular area"""
    return os.path.join(branchArea(area_v), module)
