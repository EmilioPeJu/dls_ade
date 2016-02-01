import os
from exceptions import ParsingError

GIT_ROOT_DIR = os.getenv('GIT_ROOT_DIR', "controls")


def remove_end_slash(path_string):

    if path_string and isinstance(path_string, str) and path_string.endswith('/'):
        path_string = path_string[:-1]

    return path_string


def check_technical_area(area, module):
    """
    Checks if given area is IOC and if so, checks that the technical area is also provided.

    Args:
        area: Area of repository
        module: Module to check

    Raises:
        ValueError: "Missing technical area under beamline"
    """

    if area == "ioc" and len(module.split('/')) < 2:
        raise ParsingError("Missing technical area under beamline")


def dev_area_path(area="support"):
    """Return the full server path for the given area.

    Args:
        area: The area of the module.

    Returns:
        str: The full server path for the given area.

    """
    return os.path.join(GIT_ROOT_DIR, area)


def dev_module_path(module, area="support"):
    """Return the full server path for the given module and area.

    Args:
        area: The area of the module.
        module: The module name.

    Returns:
        str: The full server path for the given module.

    """
    return os.path.join(dev_area_path(area), module)
