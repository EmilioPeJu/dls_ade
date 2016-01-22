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


def dev_area_path(area_v="support"):
    """Return the path for the trunk section of a particular area_v"""
    return area(area_v)


def dev_module_path(module, area_v="support"):
    """Return the path for module in trunk section a particular area"""
    return os.path.join(dev_area_path(area_v), module)
