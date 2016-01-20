from __future__ import print_function
import path_functions as pathf
import logging
import vcs_git
import module_template as mt
import module_creator as mc
from exceptions import ParsingError

logging.basicConfig(level=logging.DEBUG)


def get_module_creator(module_name, area="support", fullname=False):
    """Returns a :class:`ModuleCreator` subclass object.

    Returns an object of a subclass of :class:`ModuleCreator`, depending on
    the arguments given.

    Supported areas are:
        - Python
        - Support
        - Tools
        - IOC

    Python module name format:
        - Must begin with `dls_`
        - Must not have any hyphens ("-") or full stops (".")

    IOC module name format:
        New-Style module (preferred):
            Format: "BL02I-VA-IOC-03"
                "<beamline>-<technical_area>-IOC-<ioc_number>"
            Alternative: "BL02I/VA/03", with fullname = True
                "<beamline>/<technical_area>/<ioc_number>", fullname = True

            If the alternative is used, if the IOC number is omitted
            (eg. <beamline>/<technical_area>) it defaults to "01"

        Old-Style module (deprecated, except for BL modules):
            Format: "BL02I/VA/03", with fullname = False (or omitted)
                "<beamline>/<technical_area>/<ioc_number>"

    Args:
        module_name: The name of the module.
        area: The area of the module.
        fullname: Create new-style module from old-style input.
            If True and module_name given in old-style format, then a
            new-style module is created.

    Returns:
        ModuleCreator: An object of a :class:`ModuleCreator` subclass

    Raises:
        ParsingError: If an IOC module name cannot be split by '-' or '/'.
        ParsingError: If the Python module name is not properly constructed.
        ParsingError: If the area given is not supported.

    """
    if area == "ioc":
        return get_module_creator_ioc(module_name, fullname)

    elif area == "python":
        valid_name = (module_name.startswith("dls_") and
                      ("-" not in module_name) and
                      ("." not in module_name))
        if not valid_name:
            raise ParsingError("Python module names must start with 'dls_' "
                               "and be valid python identifiers")

        return mc.ModuleCreator(module_name, area, mt.ModuleTemplatePython)

    elif area == "support":
        return mc.ModuleCreatorWithApps(module_name, area,
                                        mt.ModuleTemplateSupport,
                                        app_name=module_name)

    elif area == "tools":
        return mc.ModuleCreator(module_name, area, mt.ModuleTemplateTools)

    else:
        raise ParsingError("Don't know how to make a module of type: " + area)


def get_module_creator_ioc(module_name, fullname=False):
    """Returns a :class:`ModuleCreatorIOC` subclass object.

    Returns an object of a subclass of :class:`ModuleCreatorIOC`, depending
    on the arguments given.

    IOC module name format:
        New-Style module (preferred):
            Format: "BL02I-VA-IOC-03"
                "<beamline>-<technical_area>-IOC-<ioc_number>"
            Alternative: "BL02I/VA/03", with fullname = True
                "<beamline>/<technical_area>/<ioc_number>", fullname = True

            If the alternative is used, if the IOC number is omitted
            (eg. <beamline>/<technical_area>) it defaults to "01"

        Old-Style module (deprecated, except for BL modules):
            Format: "BL02I/VA/03", with fullname = False (or omitted)
                "<beamline>/<technical_area>/<ioc_number>"

    Args:
        module_name: The name of the module.
        fullname: Create new-style module from old-style input.
            If True and module_name given in old-style format, then a
            new-style module is created.

    Returns:
        ModuleCreatorIOC: :class:`ModuleCreatorIOC` subclass object

    Raises:
        ParsingError: If the module cannot be split by '-' or '/'.

    """
    area = "ioc"

    dash_separated, cols = split_ioc_module_name(module_name)

    domain = cols[0]
    technical_area = cols[1]

    if technical_area == "BL":
        if dash_separated:
            app_name = module_name
            module_path = domain + "/" + app_name
        else:
            app_name = domain
            module_path = domain + "/" + technical_area

        return mc.ModuleCreatorWithApps(module_path, area,
                                        mt.ModuleTemplateIOCBL,
                                        app_name=app_name)

    module_template_cls = mt.ModuleTemplateIOC

    if dash_separated:
        app_name = module_name
        module_path = domain + "/" + app_name
        return mc.ModuleCreatorWithApps(module_path, area, module_template_cls,
                                        app_name=app_name)

    if len(cols) == 3 and cols[2]:
        ioc_number = cols[2]
    else:
        ioc_number = "01"

    app_name = "-".join([domain, technical_area, "IOC", ioc_number])

    if fullname:
        module_path = domain + "/" + app_name
        return mc.ModuleCreatorWithApps(module_path, area, module_template_cls,
                                        app_name=app_name)
    else:
        # This part is here to retain compatibility with "old-style" modules,
        # in which a single repo (or module) named "domain/technical_area"
        # contains multiple domain-technical_area-IOC-xxApp's. This code is
        # included in here to retain compatibility with the older svn scripts.
        # The naming is ambiguous, however. I will continue to use the name
        # 'module' to refer to the repo, but be aware that start_new_module and
        # module_creator don't have to actually create new modules (repos)
        # on the server in this instance.
        module_path = domain + "/" + technical_area
        server_repo_path = pathf.devModule(module_path, area)
        if vcs_git.is_repo_path(server_repo_path):
            # Adding new App to old style "domain/tech_area" module that
            # already exists on the remote server.
            return mc.ModuleCreatorAddAppToModule(module_path, area,
                                                  module_template_cls,
                                                  app_name=app_name)
        else:
            # Otherwise, the behaviour is exactly the same as that given
            # by the ordinary IOC class as module_path is the only thing
            # that is different
            return mc.ModuleCreatorWithApps(module_path, area,
                                            module_template_cls,
                                            app_name=app_name)


def split_ioc_module_name(module_name):
    """Parses the module name and returns split module_name and split type.

    Args:
        module_name: The ioc module's name.

    Returns:
        bool: True if the string is dash-separated, false otherwise.
            Based on original svn implementation, if both slashes and dashes
            appear in the module name, it will default to slash-separated.
        list[str]: A list of strings that make up the module name.
            These are the components separated by a '/' or '-' in the module
            name.

    Raises:
        ParsingError: If the module cannot be split by '-' or '/'.

    """
    cols = module_name.split('/')
    dash_separated = False

    if len(cols) <= 1 or not cols[1]:
        cols = module_name.split('-')
        dash_separated = True

        # This has different check to retain compatibility with old svn script.
        if len(cols) <= 1:
            err_message = ("Need a name with dashes or hyphens in it, got "
                           "{module:s}")
            raise ParsingError(err_message.format(module=module_name))

    return dash_separated, cols
