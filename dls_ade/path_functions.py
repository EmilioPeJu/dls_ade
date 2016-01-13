import os

GIT_ROOT_DIR = os.getenv('GIT_ROOT_DIR', "controls")


def area(area_v):
    """Return the full file path for the given area."""
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
