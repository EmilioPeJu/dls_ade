import logging
from dls_ade import Server
from dls_ade import module_template as mt
from dls_ade import module_creator as mc
from dls_ade.exceptions import ParsingError

base_ioc_name_err_message = (
    "IOC name should be of the form:\n"
    "  <Domain>/<Domain>-<Technical area>-IOC-<Number> or <Domain>/BL\n"
    "but the IOC name given was {name}. "
)

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

    elif area in ("python", "python3"):
        valid_name = (module_name.startswith("dls_") and
                      ("-" not in module_name) and
                      ("." not in module_name))
        if not valid_name:
            raise ParsingError("Python module names must start with 'dls_' "
                               "and be valid python identifiers")

        template = (mt.ModuleTemplatePython if area == "python"
                    else mt.ModuleTemplatePython3)
        return mc.ModuleCreator(module_name, area, template)

    elif area == "support":
        return mc.ModuleCreatorWithApps(module_name, area,
                                        mt.ModuleTemplateSupport,
                                        app_name=module_name)

    elif area == "tools":
        return mc.ModuleCreator(module_name, area, mt.ModuleTemplateTools)

    elif area == "matlab":
        return mc.ModuleCreator(module_name, area, mt.ModuleTemplateMatlab)

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
    module_template_cls = mt.ModuleTemplateIOC

    dash_separated, cols = split_ioc_module_name(module_name)

    domain = cols[0]
    technical_area = cols[1]
    template_args = {
        "domain": domain,
        "technical_area": technical_area,
        "ioc_number": "01"
    }

    # Regular IOC name
    # e.g. BL99P-TS-IOC-01 - use this for app name
    if dash_separated:
        app_name = "-".join(cols)
        module_path = domain + "/" + app_name

        # e.g. BLXXI/BLXXI-UI-IOC-01
        if technical_area == "UI":
            module_template_cls = mt.ModuleTemplateIOCUI
            module_path = domain + "/" + app_name

    # e.g. BLXXI/BL
    elif technical_area == "BL":
        module_template_cls = mt.ModuleTemplateIOCBL
        app_name = domain
        module_path = domain + "/" + "BL"

    else:
        raise ParsingError(base_ioc_name_err_message.format(name=module_name))

    template_args['app_name'] = app_name
    return mc.ModuleCreatorWithApps(module_path, area, module_template_cls,
                                    **template_args)


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
        ParsingError: If the name is not of the correct form

    """
    slash_tokens = module_name.split('/')

    # No slash present in name e.g. "BL99P-TS-IOC-01"
    if len(slash_tokens) <= 1:

        # Well-formed IOC name but domain omitted
        # e.g. "BL99P-TS-IOC-01
        if module_name.count("-") == 3:
            tokens = module_name.split("-")
            err_message = (base_ioc_name_err_message
                           + "\nDid you mean {technical_area}/{name} ?")
            raise ParsingError(err_message.format(technical_area=tokens[0],
                                                  name=module_name))

        # Malformed IOC name
        # e.g. BL99P-TS-
        raise ParsingError(base_ioc_name_err_message.format(name=module_name))

    # Trailing slash
    elif not slash_tokens[1]:
        raise ParsingError(base_ioc_name_err_message.format(name=module_name))

    # Slash present in name.
    # e.g. "test/module" or "test/module/02" or "BL99P/BL99P-TS-IOC-01"
    elif len(slash_tokens) == 2:
        domain = slash_tokens[0]
        dash_tokens = slash_tokens[1].split('-')

        # No dashes in second part
        # e.g. BL99P/BL
        if len(dash_tokens) == 1:
            return False, slash_tokens

        # Dashes in second part
        # e.g. BL99P/BL99P-TS-IOC-01
        else:
            return True, dash_tokens

    # More than one slash - not allowed
    else:
        raise ParsingError(base_ioc_name_err_message.format(name=module_name))
