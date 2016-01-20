class ArgumentError(Exception):
    """Class for exceptions relating to template arguments."""
    pass


class ModuleTemplateError(Exception):
    """Class for exceptions relating to the 'module_template' python module."""
    pass


class TemplateFolderError(ModuleTemplateError):
    """Class for exceptions relating to missing template folders."""
    def __init__(self, template_folder):
        err_message = ("Template folder {template_path:s} does not exist. "
                       "\nNote: This exception means there is a bug in the "
                       "ModuleTemplate subclass code.")
        Exception.__init__(self, err_message.format(
                template_path=template_folder))


class ModuleCreatorError(Exception):
    """Class for exceptions relating to the 'new_module_creator' python module.

    """
    pass


class ParsingError(ModuleCreatorError):
    """Class for errors relating to parsing the given arguments"""
    pass


class RemoteRepoError(ModuleCreatorError):
    """Class for errors relating to issues with the remote repository."""
    pass


class VerificationError(ModuleCreatorError):
    """Class for errors raised by the `verify_` methods of new_module_creator.

    This allows us to handle and concatenate internal verification errors.

    """
    pass