import os
import vcs_git

GIT_SSH_ROOT = vcs_git.GIT_SSH_ROOT


def check_technical_area_valid(area, module):
    """
    Checks if <area> is 'ioc', if so checks if <module_name> is of the form 'tech_area/module' and
    raises a parser error if not

    Args:
        area: Area of repository
        module: Module to check

    Raises:
        "Missing Technical Area Under Beamline"
    """

    if area == "ioc" and len(module.split('/')) < 2:
        raise Exception("Missing Technical Area Under Beamline")


def root():
    """Return the root for subversion (SVN_ROOT variable in the environment)"""
    root_v = GIT_SSH_ROOT
    # assert os.environ["SVN_ROOT"], "'SVN_ROOT' environment variable must be set"
    return root_v


def area(area_v, type_v=None):

    if type_v and type_v not in ['release', 'vendor']:
        raise Exception("Type must be release or vendor")

    if area_v is "etc":
        raise NotImplementedError
        # return os.path.join(root(), area_v, "prod")
    elif area_v is "epics":
        raise NotImplementedError
        # return os.path.join(root(), area_v)
    elif area_v is "tools":
        raise NotImplementedError
        # return os.path.join(root(), "diamond", "build_scripts")
    else:
        if type_v is None:
            return os.path.join("controls", area_v)
        elif type_v is 'release':
            raise NotImplementedError
        elif type_v is 'vendor':
            raise NotImplementedError


def devArea(area_v="support"):
    """Return the path for the trunk section of a particular area_v"""
    return area(area_v)


def devModule(module, area_v="support"):
    """Return the path for module in trunk section a particular area"""
    return os.path.join(devArea(area_v), module)


def prodArea(area_v="support"):
    """Return the path for the release section of a particular area"""
    return area(area_v, type_v='release')


def prodModule(module, area_v="support"):
    """Return the path for module in release section a particular area"""
    return os.path.join(prodArea(area_v), module)


def branchArea(area_v="support"):
    """Return the path for the branch section of a particular area"""
    return area(area_v)


def branchModule(module, area_v="support"):
    """Return the path for module in branch section a particular area"""
    return os.path.join(branchArea(area_v), module)


def vendorArea(area_v="support"):
    """Return the path for the vendor section of a particular area"""
    return area(area_v)


def vendorModule(module, area_v="support"):
    """Return the path for module in vendor section a particular area"""
    return os.path.join(vendorArea(area_v), module)
