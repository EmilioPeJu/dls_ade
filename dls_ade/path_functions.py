import os

GIT_ROOT_DIR = os.getenv('GIT_ROOT_DIR', "controls")


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


def area(area_v):
    """Return the full file path for the given area."""
    return os.path.join(GIT_ROOT_DIR, area_v)


# TODO(Martin): Rename to dev_area_path
def devArea(area_v="support"):
    """Return the path for the trunk section of a particular area_v"""
    return area(area_v)


# TODO(Martin): Rename to dev_module_path
def devModule(module, area_v="support"):
    """Return the path for module in trunk section a particular area"""
    return os.path.join(devArea(area_v), module)


# TODO(Martin): Delete the below functions, (check for usage and change to
# TODO(Martin): dev_module_path or dev_area_path). Note: dlsbuild uses entirely
# TODO(Martin): different set of devArea and prodArea functions.
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
