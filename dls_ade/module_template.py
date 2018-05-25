import os
import shutil
import logging

from cookiecutter.main import cookiecutter

from dls_ade.exceptions import ArgumentError, TemplateFolderError

logging.getLogger(__name__).addHandler(logging.NullHandler())
log = logging.getLogger(__name__)

TEMPLATES_FOLDER = "module_templates"
COOKIECUTTER_TEMPLATES_FOLDER = "cookiecutter_templates"


class ModuleTemplate(object):
    """Class for the creation of new module contents.

    Attributes:
        _template_files(dict): Dictionary containing file templates.
            Each entry has the (relative) file-path as the key, and the file
            contents as the value. Either may contain placeholders in the form
            of {template_arg:s} for use with the string .format() method, each
            evaluated using the `template_args` attribute.
        _required_template_args(List[str]): List of all required template_args.
        _template_args(dict): Dictionary for module-specific phrases. Used for
         including module-specific phrases such as `module_name`.

    Raises:
        :class:`~dls_ade.exceptions.ModuleTemplateError`: Base class for this \
        module's exceptions

    """

    def __init__(self, template_args, extra_required_args=None):
        """Default initialisation of all object attributes.

        Args:
            template_args: Dictionary for module-specific phrases.
                Used to replace {} tags in template files.
            extra_required_args: Additional required template arguments.

        """
        self._template_files = {}

        self._required_template_args = set()

        if extra_required_args is not None:
            self._required_template_args.update(extra_required_args)

        self._template_args = template_args

        # The following code ought to be used in subclasses to ensure that the
        # template_args given contain the required ones.
        self._verify_template_args()

        self._cookiecutter_template_path = ""

    def _verify_template_args(self):
        """Verify that the template_args fulfill the template requirements.

        Raises:
            :class:`~dls_ade.exceptions.VerificationError`: If a required \
                placeholder is missing.

        """
        if not all(key in self._template_args
                   for key in self._required_template_args):
            raise ArgumentError(
                "All required template arguments must be supplied: " +
                str(", ".join(self._required_template_args))
            )

    def _set_template_files_from_area(self, template_area):
        """Sets `template_files` from the templates folder in dls_ade.

        Uses the module_templates folder to set the `template_files`.

        Note:
            "default" template contains a basic .gitignore file that can be
            used by all modules.

        Args:
            template_area: The module area for obtaining the templates.

        Raises:
            :class:`~dls_ade.exceptions.TemplateFolderError`: If template \
                folder does not exist.

        """
        template_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            TEMPLATES_FOLDER,
            template_area
        )

        if not os.path.isdir(template_path):
            raise TemplateFolderError(template_path)

        self._template_files = self._get_template_files_from_folder(
                template_path)

    def _get_template_files_from_folder(self, template_folder):
        """Sets `template_files` from a folder passed to it.

        Note:
            All hidden files and folders (apart from '.' and '..') will be
            included.

        Args:
            template_folder: The relative or absolute path to template folder.
                Inside, all files and folders can use {value:s} template_args
                to allow completion using `template_args` attribute.

        Raises:
            :class:`~dls_ade.exceptions.TemplateFolderError`: If \
                `template_folder` does not exist.

        """
        log.debug("About to get template files from folder.")

        if not os.path.isdir(template_folder):
            raise TemplateFolderError(template_folder)

        log.debug("Template files to add (relative paths):")

        template_files = {}
        for dir_path, _, files in os.walk(template_folder):
            for file_name in files:
                file_path = os.path.join(dir_path, file_name)
                with open(file_path, "r") as f:
                    contents = f.read()
                rel_path = os.path.relpath(file_path, template_folder)

                log.debug("        " + rel_path)

                # This stops the installer from compiling the .py files.
                if rel_path.endswith(".py_template"):
                    rel_path = rel_path[:-9]

                template_files[rel_path] = contents

        return template_files

    def create_files(self):
        """Creates the folder structure and files in the current directory.

        This uses the :meth:`._create_files_from_template_dict` method for file
        creation by default.

        Raises:
            :class:`~dls_ade.exceptions.ArgumentError`: From \
                :meth:`_create_files_from_template_dict`
            OSError: From :meth:`_create_files_from_template_dict`

        """
        self._create_custom_files()
        self._run_cookiecutter()
        self._create_files_from_template_dict()

    def _create_custom_files(self):
        """Creates files specific to the application using external scripts.

        This does not use the template files or args.

        """
        pass

    def _create_files_from_template_dict(self):
        """Creates files from `_template_files` and `_template_args`

        This uses the `_template_files` and `_template_args` attributes for
        file creation by default.

        Raises:
            :class:`~dls_ade.exceptions.ArgumentError`: If dictionary key is \
                a directory, not a file.
            OSError: From :func:`os.makedirs`

        """
        # dictionary keys are the relative file paths for the documents
        log.debug("About to create files from template.")
        log.debug("Template files to create (relative paths):")
        for path, contents in self._template_files.iteritems():
            # Using template_args allows us to insert eg. module_name
            rel_path = path.format(**self._template_args)

            dir_path = os.path.dirname(rel_path)

            log.debug("        " + rel_path)

            # Stops us from overwriting files in folder (eg .gitignore and
            # .gitattributes when adding to Old-Style IOC modules
            # (ModuleCreatorAddAppToModule))
            if os.path.isfile(rel_path):
                log.debug("File already exists: " + rel_path)
                continue

            if os.path.normpath(dir_path) == os.path.normpath(rel_path):
                # If folder given instead of file (ie. rel_path ends with a
                # slash or folder already exists)
                err_message = ("{dir:s} in template dictionary "
                               "is not a valid file name")
                raise ArgumentError(err_message.format(dir=dir_path))

            # dir_path = '' (dir_path = False) if eg. "file.txt" given
            if dir_path and not os.path.isdir(dir_path):
                os.makedirs(dir_path)

            with open(rel_path, "w") as f:
                f.write(contents.format(**self._template_args))

    def _run_cookiecutter(self):
        """ Run CookieCutter to populate the module folder

        It uses the template specified by propety cookiecutter_template.

        The template project folder is expected to be
        {{cookiecutter.project_name}}, this name will be set to one of the
        template args, firstly it tries using module_name if it does not exits, it
        uses app_name otherwise CookieCutter's defaults
        """
        if self._cookiecutter_template_path:
            log.info("Running CookieCutter using template: %s",
                     self.cookiecutter_template)
            _cwd = os.getcwd()
            # ModuleCreator enters the module directory, but CookieCutters
            # expects to be in the parent folder
            os.chdir('..')

            project_name = self._template_args.get('module_name') \
                or self._template_args.get('app_name')

            if project_name:
                self._template_args['project_name'] = project_name

            project_path = cookiecutter(
                template=self._cookiecutter_template_path, no_input=True,
                overwrite_if_exists=True,
                extra_context=self._template_args)

            project_basename = os.path.basename(project_path)
            if project_basename != project_name:
                log.warning("The cookiecutter template was not applied over "
                            "the module folder, %s was used instead",
                            project_basename)
            os.chdir(_cwd)

    @property
    def cookiecutter_template(self):
        """Get CookieCutter template used

        if none is used, it returns an empty string
        """
        return os.path.basename(self._cookiecutter_template_path)

    @cookiecutter_template.setter
    def cookiecutter_template(self, template_name):
        """Set this property to defined the CookieCutter template used"""
        template_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            COOKIECUTTER_TEMPLATES_FOLDER,
            template_name
        )

        if not os.path.isdir(template_path):
            raise TemplateFolderError(template_path)

        self._cookiecutter_template_path = template_path

    def get_print_message(self):
        """Return a string with a message to detail the user's next steps."""
        raise NotImplementedError


class ModuleTemplateTools(ModuleTemplate):
    """Class for the management of the creation of new Tools modules.

    For this class to work properly, the following template arguments must be\
    specified upon initialisation:

        - module_name
        - module_path
        - user_login

    """

    def __init__(self, template_args, additional_required_args=None):
        """Initialise template args and default template files."""

        required_args = ['module_name', 'module_path', 'user_login']

        if additional_required_args is not None:
            required_args += additional_required_args

        super(ModuleTemplateTools, self).__init__(
                template_args,
                required_args
        )

        self._set_template_files_from_area("tools")

    def get_print_message(self):
        message_dict = {'module_path': self._template_args['module_path']}

        message = ("\nPlease add your patch files to the {module_path:s}"
                   "\ndirectory and edit {module_path:s}/build script "
                   "appropriately.")
        message = message.format(**message_dict)
        return message


class ModuleTemplatePython(ModuleTemplate):
    """Class for the management of the creation of new Python modules."""

    def __init__(self, template_args, additional_required_args=None):
        """Initialise template args and default template files."""

        required_args = ['module_name', 'module_path', 'user_login']

        if additional_required_args is not None:
            required_args += additional_required_args

        super(ModuleTemplatePython, self).__init__(
                template_args,
                required_args
        )

        self._set_template_files_from_area("python")

    def get_print_message(self):
        module_path = self._template_args['module_path']
        message_dict = {'module_path': module_path,
                        'setup_path': os.path.join(module_path, "setup.py")
                        }

        message = ("\nPlease add your python files to the {module_path:s}"
                   "\ndirectory and edit {setup_path:s} appropriately.")
        message = message.format(**message_dict)

        return message


class ModuleTemplateWithApps(ModuleTemplate):
    """Abstract class to implement the 'app_name' attribute.

    This also includes the app-dependent print message, used by IOC and\
    Support ModuleTemplate subclasses

    Ensure you use this with :class:`ModuleCreatorWithApps`, in order to\
    ensure that the `app_name` value exists.

    For this class to work properly, the following template arguments must be\
    specified upon initialisation:

        - module_path
        - user_login
        - app_name

    """

    def __init__(self, template_args, additional_required_args=None):

        required_args = ['module_path', 'app_name', 'user_login']

        if additional_required_args is not None:
            required_args += additional_required_args

        super(ModuleTemplateWithApps, self).__init__(
                template_args,
                required_args
        )

        self._set_template_files_from_area("default")

    def get_print_message(self):
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

        return message


class ModuleTemplateSupport(ModuleTemplateWithApps):
    """Class for the management of the creation of new Support modules.

    These have apps with the same name as the module.

    """
    def __init__(self, template_args, additional_required_args=None):

        if additional_required_args is None:
            additional_required_args = []

        super(ModuleTemplateSupport, self).__init__(
                template_args,
                additional_required_args
        )

        # The difference between this and WithApps' template_files, is that a
        # number of '.keep' files are included in otherwise empty repositories
        # created by MakeBaseApp.pl so the folders are included in the git
        # repository.
        self._set_template_files_from_area("support")

    def _create_custom_files(self):
        """Creates the folder structure and files in the current directory.

        This uses the makeBaseApp.pl program for file creation.

        Raises:
            OSError: If system call fails.

        """
        os.system('makeBaseApp.pl -t dls {app_name:s}'.format(
            app_name=self._template_args['app_name']))
        os.system('dls-make-etc-dir.py && make clean uninstall')


class ModuleTemplateIOC(ModuleTemplateWithApps):
    """Class for the management of the creation of new IOC modules.

    These have apps with a different name to the module.

    """

    def _create_custom_files(self):
        """Creates the folder structure and files in the current directory.

        This uses the makeBaseApp.pl program for file creation.

        Note:
            When using `ModuleCreatorAddAppToModule`, an IOC app is added to a
            previously existing module. As a result, if only a local module is
            being created, and the app name conflicts with one on the server,
            the previously existing app has to be deleted (along with boot
            files) in order for the app to be created properly. Due to the
            checks in place, this cannot be pushed to the remote repository
            using the `ModuleCreatorAddAppToModule` class.

        Raises:
            OSError: If system call fails.

        """
        # If there is already an app of the given name, delete it.
        app_folder = "{app_name:s}App".format(**self._template_args)
        if os.path.exists(app_folder):
            shutil.rmtree(app_folder)

        # We need to delete the ioc boot file as well.
        boot_file = "ioc_boot/ioc{app_name:s}".format(**self._template_args)
        if os.path.exists(boot_file):
            shutil.rmtree(boot_file)

        os.system('makeBaseApp.pl -t dls {app_name:s}'.format(
            **self._template_args))
        os.system('makeBaseApp.pl -i -t dls {app_name:s}'.format(
            **self._template_args))

        shutil.rmtree(os.path.join(app_folder, 'opi'))


class ModuleTemplateIOCBL(ModuleTemplateWithApps):
    """Class for the management of the creation of new IOC BL modules."""

    def _create_custom_files(self):
        """Creates the folder structure and files in the current directory.

        This uses the makeBaseApp.pl program for file creation.

        Raises:
            OSError: If system call fails.

        """
        os.system('makeBaseApp.pl -t dlsBL ' + self._template_args['app_name'])

    def get_print_message(self):
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
                   " has been placed in {opi/edl:s}. Please modify these.")
        message = message.format(**message_dict)

        return message


class ModuleTemplateMatlab(ModuleTemplate):
    """Class for the management of the creation of new Matlab modules.

    For this class to work properly, the following template arguments must be\
    specified upon initialisation:

        - module_name
        - module_path
        - user_login

    """

    def __init__(self, template_args, additional_required_args=None):
        """Initialise template args and default template files."""

        required_args = ['module_name', 'module_path', 'user_login']

        if additional_required_args is not None:
            required_args += additional_required_args

        super(ModuleTemplateMatlab, self).__init__(
                template_args,
                required_args
        )

        self._set_template_files_from_area("default")

    def get_print_message(self):
        message_dict = {'module_path': self._template_args['module_path']}

        message = ("\nPlease add your matlab files to the {module_path:s}"
                   "\ndirectory and commit them before releasing.")
        message = message.format(**message_dict)

        return message


class ModuleTemplateIOCUI(ModuleTemplateWithApps):

    def __init__(self, template_args, additional_required_args=None):
        super(ModuleTemplateIOCUI, self).__init__(
                template_args,
                additional_required_args
        )

        self.cookiecutter_template = "CSS_IOC"

    def get_print_message(self):
        module_path = self._template_args['module_path']
        app_name = self._template_args['app_name']
        message_dict = {
            'RELEASE': os.path.join(module_path, "configure/RELEASE"),
            'DbMakefile': os.path.join(
                module_path,
                app_name + "App/Db/Makefile"
            ),
            'create_gui': os.path.join(
                module_path,
                app_name + "App/op/opi/create_gui"
            ),
            'synoptic': os.path.join(
                module_path,
                app_name + "App/op/opi/synoptic.opi"
            )
        }

        message = ("\nPlease now edit {RELEASE:s} to put in correct paths "
                   "for the ioc's other technical areas and path to scripts."
                   "\nAlso edit {DbMakefile:s} to add all database files "
                   "from these technical areas.\nAn example set of screens"
                   " has been created in {create_gui:s}. Please modify these."
                   "\nThe synoptic opi in {synoptic:s} will need to be "
                   "expanded as needed.")
        message = message.format(**message_dict)

        return message
