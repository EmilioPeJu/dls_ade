from __future__ import print_function
import os
import shutil
import logging

logging.basicConfig(level=logging.DEBUG)


class Error(Exception):
    """Class for exceptions relating to module_template module."""
    pass


class ModuleTemplate(object):
    """Class for the creation of new module contents.

    Raises:
        Error: All errors raised by this module inherit from this class

    """

    def __init__(self, template_args):
        """Default initialisation of all object attributes.

        """
        self._template_files = {}
        """dict: Dictionary containing file templates.
        Each entry has the (relative) file-path as the key, and the file
        contents as the value. Either may contain placeholders in the form of
        {template_arg:s} for use with the string .format() method, each
        evaluated using the `template_args` attribute."""

        self._required_template_args = []
        """List[str]: List of all required template_args."""

        self._template_args = {}
        """dict: Dictionary for module-specific phrases in template_files.
        Used for including module-specific phrases such as `module_name`"""

        # The following code ought to be used in subclasses to ensure that the
        # template_args given contain the required ones.
        self.set_template_args(template_args)

    def set_template_args(self, extra_template_args, update=False):
        """Set the template args using the given dictionary.

        Args:
            extra_template_args: List of additional template_args to include.
            update: If True, the dictionary should be updated, not overwritten.

        """
        if update:
            self._template_args.update(extra_template_args)
        else:
            self._template_args = extra_template_args
            self._verify_template_args()

    def set_template_files(self, extra_template_files, update=False):
        """Set the template files using the given dictionary.

        Args:
            extra_template_files: List of additional template_args to include.
            update: If True, the dictionary should be updated, not overwritten.

        """
        if update:
            self._template_files.update(extra_template_files)
        else:
            self._template_files = extra_template_files

    def _verify_template_args(self):
        """Verify that the template_args fulfill the template requirements.

        Raises:
            VerificationError: If a required placeholder is missing.

        """
        if not all(key in self._template_args
                   for key in self._required_template_args):
            raise Error(
                "All required template arguments must be supplied: " +
                str(", ".join(self._required_template_args))
            )

    def _set_template_files_from_area(self, template_area):
        """Sets `template_files` from the templates folder in dls_ade.

        Uses the new_module_templates folder to set the `template_files`.

        Note:
            "default" template contains a basic .gitignore file that can be
            used by all modules.

        Args:
            template_area: The module area for obtaining the templates.

        Raises:
            Error: If template folder does not exist.

        """
        templates_folder = "new_module_templates"
        template_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            templates_folder,
            template_area
        )

        if not os.path.isdir(template_path):
            err_message = ("Template folder {template_path:s} does not exist. "
                           "\nNote: This exception means there is a bug in "
                           "the ModuleTemplate subclass code.")

            raise Error(err_message.format(template_path=template_path))

        self._set_template_files_from_folder(template_path)

    def _set_template_files_from_folder(self, template_folder, update=False):
        """Sets `template_files` from a folder passed to it.

        If update is 'True', then the dictionary is updated, not overwritten.

        Note:
            All hidden files and folders (apart from '.' and '..') will be
            included.

        Args:
            template_folder: The relative or absolute path to template folder.
                Inside, all files and folders can use {value:s} template_args
                to allow completion using `template_args` attribute.
            update: If True, `_template_files` will be updated

        Raises:
            Error: If `template_folder` does not exist.

        """
        if not os.path.isdir(template_folder):
            err_message = ("The template folder {template_folder:s} "
                           "does not exist")
            raise Error(err_message.format(template_folder=template_folder))

        template_files = {}
        for dir_path, _, files in os.walk(template_folder):
            for file_name in files:
                file_path = os.path.join(dir_path, file_name)
                with open(file_path, "r") as f:
                    contents = f.read()
                rel_path = os.path.relpath(file_path, template_folder)
                logging.debug("rel path: " + rel_path)
                template_files.update({rel_path: contents})

        self.set_template_files(template_files, update)

    def create_files(self):
        """Creates the folder structure and files in the current directory.

        This uses the :meth:`_create_files_from_template_dict` method for file
        creation by default.

        Raises:
            Error: From :meth:`_create_files_from_template_dict`

        """
        self._create_files_from_template_dict()

    def _create_files_from_template_dict(self):
        """Creates files from `_template_files` and `_template_args`

        This uses the `_template_files` and `_template_args` attributes for
        file creation by default.

        Raises:
            Error: If key in `_template_files` is a directory, not a file.

        """
        # dictionary keys are the relative file paths for the documents
        for path in self._template_files:
            # Using template_args allows us to insert eg. module_name
            rel_path = path.format(**self._template_args)
            logging.debug("rel_path: " + rel_path)

            dir_path = os.path.dirname(rel_path)

            # Stops us from overwriting files in folder (eg .gitignore and
            # .gitattributes when adding to Old-Style IOC modules
            # (NewModuleCreatorAddAppToModule))
            if os.path.isfile(rel_path):
                logging.debug("File already exists: " + rel_path)
                continue

            if os.path.normpath(dir_path) == os.path.normpath(rel_path):
                # If folder given instead of file (ie. rel_path ends with a
                # slash or folder already exists)
                err_message = ("{dir:s} in template dictionary "
                               "is not a valid file name")
                raise Error(err_message.format(dir=dir_path))

            # dir_path = '' (dir_path = False) if eg. "file.txt" given
            if dir_path and not os.path.isdir(dir_path):
                os.makedirs(dir_path)

            with open(rel_path, "w") as f:
                f.write(self._template_files[path].format(
                        **self._template_args))

    def print_message(self):
        """Prints a message to detail the user's next steps."""
        raise NotImplementedError


class ModuleTemplateTools(ModuleTemplate):
    """Class for the management of the creation of new Tools modules.

    For this class to work properly, the following template arguments must be
    specified upon initialisation:
        - module_name
        - module_path
        - user_login

    """

    def __init__(self, template_args):
        """Initialise template args and default template files."""
        super(ModuleTemplateTools, self).__init__(template_args)

        self._required_template_args = [
            'module_name', 'module_path', 'user_login'
        ]

        self._verify_template_args()

        self._set_template_files_from_area("tools")

    def print_message(self):
        message_dict = {'module_path': self._template_args['module_path']}

        message = ("\nPlease add your patch files to the {module_path:s} "
                   "\ndirectory and edit {module_path:s}/build script "
                   "appropriately")
        message = message.format(**message_dict)

        print(message)


class ModuleTemplatePython(ModuleTemplate):
    """Class for the management of the creation of new Python modules."""

    def __init__(self, template_args):
        """Initialise template args and default template files."""
        super(ModuleTemplatePython, self).__init__(template_args)

        self._required_template_args = [
            'module_name', 'module_path', 'user_login'
        ]

        self._verify_template_args()

        self._set_template_files_from_area("python")

    def print_message(self):
        module_path = self._template_args['module_path']
        message_dict = {'module_path': module_path,
                        'setup_path': os.path.join(module_path, "setup.py")
                        }

        message = ("\nPlease add your python files to the {module_path:s} "
                   "\ndirectory and edit {setup_path} appropriately.")
        message = message.format(**message_dict)

        print(message)


class ModuleTemplateSupportAndIOC(ModuleTemplate):
    """Abstract class to implement the shared user message for Support and IOC.

    Ensure you use this with :class:`NewModuleCreatorWithApps`, in order to
    ensure that the `app_name` value exists.

    For this class to work properly, the following template arguments must be
    specified upon initialisation:
        - module_path
        - user_login
        - app_name

    """

    def __init__(self, template_args):
        super(ModuleTemplateSupportAndIOC, self).__init__(template_args)

        self._required_template_args = [
            'module_path', 'app_name', 'user_login'
        ]

        self._verify_template_args()

        self._set_template_files_from_area("default")

    def print_message(self):
        # This message is shared between support and IOC
        module_path = self._template_args['module_path']
        app_name = self._template_args['app_name']

        message_dict = {
            'RELEASE': os.path.join(module_path, 'configure/RELEASE'),
            'srcMakefile': os.path.join(
                module_path,
                app_name + 'App/src/Makefile'
            ),
            'DbMakefile': os.path.join(
                module_path,
                app_name + 'App/Db/Makefile'
            )
        }

        message = ("\nPlease now edit {RELEASE:s} to put in correct paths "
                   "for dependencies.\nYou can also add dependencies to "
                   "{srcMakefile:s}\nand {DbMakefile:s} if appropriate.")
        message = message.format(**message_dict)

        print(message)


class ModuleTemplateSupport(ModuleTemplateSupportAndIOC):
    """Class for the management of the creation of new Support modules.

    These have apps with the same name as the module.

    """

    def create_files(self):
        """Creates the folder structure and files in the current directory.

        This uses makeBaseApp.pl program alongside the
        :meth:`_create_files_from_template_dict` method for file creation.

        """
        os.system('makeBaseApp.pl -t dls {app_name:s}'.format(
            app_name=self._template_args['app_name']))
        os.system('dls-make-etc-dir.py && make clean uninstall')
        self._create_files_from_template_dict()


class ModuleTemplateIOC(ModuleTemplateSupportAndIOC):
    """Class for the management of the creation of new IOC modules.

    These have apps with a different name to the module.

    """

    def create_files(self):
        """Creates the folder structure and files in the current directory.

        This uses makeBaseApp.pl program alongside the
        _create_files_from_template_dict method for file creation.

        """
        os.system('makeBaseApp.pl -t dls {app_name:s}'.format(
            **self._template_args))
        os.system('makeBaseApp.pl -i -t dls {app_name:s}'.format(
            **self._template_args))
        shutil.rmtree(os.path.join(self._template_args['app_name'] + 'App',
                                   'opi'))
        self._create_files_from_template_dict()


class ModuleTemplateIOCBL(ModuleTemplateSupportAndIOC):
    """Class for the management of the creation of new IOC BL modules."""

    def print_message(self):
        module_path = self._template_args['module_path']
        app_name = self._template_args['app_name']
        message_dict = {
            'RELEASE': os.path.join(module_path, "configure/RELEASE"),
            'srcMakefile': os.path.join(
                module_path,
                app_name + "App/src/Makefile"
            ),
            'opi/edl': os.path.join(
                module_path,
                app_name + "App/opi/edl"
            )
        }

        message = ("\nPlease now edit {RELEASE:s} to put in correct paths "
                   "for the ioc's other technical areas and path to scripts."
                   "\nAlso edit {srcMakefile:s} to add all database files "
                   "from these technical areas.\nAn example set of screens"
                   " has been placed in {opi/edl} . Please modify these.\n")
        message = message.format(**message_dict)

        print(message)

    def create_files(self):
        """Creates the folder structure and files in the current directory.

        This uses makeBaseApp.pl program alongside the
        _create_files_from_template_dict method for file creation.

        """
        os.system('makeBaseApp.pl -t dlsBL ' + self._template_args['app_name'])
        self._create_files_from_template_dict()
