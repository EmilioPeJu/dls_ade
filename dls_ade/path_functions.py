import os
from exceptions import ParsingError

GIT_ROOT_DIR = os.getenv('GIT_ROOT_DIR', "controls")


def check_technical_area_valid(area, module):
    """
    Checks if given area is IOC and if so, checks that the technical area is also provided.

    Args:
        area(str): Area of repository
        module(str): Module to check

    Raises:
        :class:`exceptions.ValueError`: Missing technical area under beamline

    """

    if area == "ioc" and len(module.split('/')) < 2:
        raise ParsingError("Missing technical area under beamline")


def dev_area_path(area="support"):
    """
    Return the full server path for the given area.

    Args:
        area(str): The area of the module.

    Returns:
        str: The full server path for the given area.

    """
    return os.path.join(GIT_ROOT_DIR, area)


def dev_module_path(module, area="support"):
    """
    Return the full server path for the given module and area.

    Args:
        area(str): The area of the module.
        module(str): The module name.

    Returns:
        str: The full server path for the given module.

    """
    return os.path.join(dev_area_path(area), module)
