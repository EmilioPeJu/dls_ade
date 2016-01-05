from __future__ import print_function
import os
import re
import path_functions as pathf
import shutil
import tempfile
import logging
from new_module_templates import py_files, tools_files, default_files
import vcs_git

logging.basicConfig(level=logging.DEBUG)


class Error(Exception):
    """Class for exceptions relating to new_module_creator module"""
    pass


def get_new_module_creator(module_name, area="support", fullname=False):
    """Returns a :class:`NewModuleCreator` subclass object.

    Returns an object of a subclass of :class:`NewModuleCreator`, depending on
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
        NewModuleCreator: An object of a :class:`NewModuleCreator` subclass

    Raises:
        Error: If invalid arguments are provided.

    """
    # Use arguments to determine which new module creator to use, and return it
    if area == "ioc":
        return get_new_module_creator_ioc(module_name, fullname)

    elif area == "python":
        valid_name = (module_name.startswith("dls_") and
                      ("-" not in module_name) and
                      ("." not in module_name))
        if not valid_name:
            raise Error("Python module names must start with 'dls_' and be"
                        " valid python identifiers")

        module_template_cls = ModuleTemplatePython

        return NewModuleCreator(module_name, area, module_template_cls)

    elif area == "support":
        module_template_cls = ModuleTemplateSupport
        return NewModuleCreatorWithApps(module_name, area, module_template_cls)

    elif area == "tools":
        module_template_cls = ModuleTemplateTools
        return NewModuleCreator(module_name, area, module_template_cls)

    else:
        raise Error("Don't know how to make a module of type: " + area)


def get_new_module_creator_ioc(module_name, fullname=False):
    """Returns a :class:`NewModuleCreatorIOC` subclass object.

    Returns an object of a subclass of :class:`NewModuleCreatorIOC`, depending
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
        NewModuleCreatorIOC: :class:`NewModuleCreatorIOC` subclass object

    Raises:
        Error: Using an invalid name

    """
    area = "ioc"
    cols = re.split(r'[-/]', module_name)

    if len(cols) <= 1 or not cols[1]:
        err_message = ("Need a name with dashes or hyphens in it, got "
                       "{module:s}")
        raise Error(err_message.format(module=module_name))

    domain = cols[0]
    technical_area = cols[1]
    dash_separated = "/" not in module_name

    # TODO(Martin) - should I add extra validation checks on the input?
    if technical_area == "BL":
        module_template_cls = ModuleTemplateIOCBL
        if dash_separated:
            app_name = module_name
            module_path = domain + "/" + app_name
        else:
            app_name = domain
            module_path = domain + "/" + technical_area

        return NewModuleCreatorWithApps(module_path, area, module_template_cls,
                                        app_name)

    module_template_cls = ModuleTemplateIOC

    if dash_separated:
        app_name = module_name
        module_path = domain + "/" + app_name
        return NewModuleCreatorWithApps(module_path, area, module_template_cls,
                                        app_name)

    if len(cols) == 3 and cols[2]:
        ioc_number = cols[2]
    else:
        ioc_number = "01"

    app_name = domain + "-" + technical_area + "-IOC-" + ioc_number

    if fullname:
        module_path = domain + "/" + app_name
        return NewModuleCreatorWithApps(module_path, area, module_template_cls,
                                        app_name)
    else:
        # This part is here to retain compatibility with "old-style" modules,
        # in which a single repo (or module) named "domain/technical_area"
        # contains multiple domain-technical_area-IOC-xxApp's. This code is
        # included in here to retain compatibility with the older svn scripts.
        # The naming is ambiguous, however. I will continue to use the name
        # 'module' to refer to the repo, but be aware that start_new_module and
        # new_module_creator don't have to actually create new modules (repos)
        # on the server in this instance.
        module_path = domain + "/" + technical_area
        server_repo_path = pathf.devModule(module_path, area)
        if vcs_git.is_repo_path(server_repo_path):
            # Adding new App to old style "domain/tech_area" module that
            # already exists on the remote server.
            return NewModuleCreatorAddAppToModule(module_path, area,
                                                  module_template_cls,
                                                  app_name)
        else:
            # Otherwise, the behaviour is exactly the same as that given
            # by the ordinary IOC class as module_path is the only thing
            # that is different
            return NewModuleCreatorWithApps(module_path, area,
                                            module_template_cls, app_name)


def obtain_template_files(area):
    """Returns the default template_files dictionary for the given area.

    Args:
        area: The area of the module to be created.

    Returns:
        dict: The dictionary mapping file paths to document text.

    """
    if area in ["default", "ioc", "support"]:
        return default_files
    elif area == "python":
        return py_files
    elif area == "tools":
        return tools_files
    else:
        return {}


class VerificationError(Error):
    """Class for exceptions relating to the `verify_` methods.

    This allows us to handle and concatenate internal verification errors.

    """
    pass


class NewModuleCreator(object):
    """Abstract base class for the management of the creation of new modules.

    Attributes:
        cwd: The current working directory upon initialisation.
        module_name: The base name of the module path.
        module_path: The relative module path.
            Used in messages and exceptions for user-friendliness.
        disk_dir: The absolute module path.
            Used for system and git commands.
        server_repo_path: The git repository server path for module.

    Raises:
        Error: All errors raised by this module inherit from this class
        VerificationError: Errors relating to the `verify_` methods.

    """

    def __init__(self, module_path, area, module_template_cls,
                 extra_placeholders=None):
        """Default initialisation of all object attributes.

        Args:
            module_path: The relative module path.
                Used in messages and exceptions for user-friendliness.
            area: The development area of the module to be created.
                In particular, this specifies the exact template files to be
                created as well as affecting the repository server path.

        """
        self._area = area  #: The 'area' of the module to be created.
        self.cwd = os.getcwd()

        self.module_path = ""
        self.module_name = ""
        self.module_path = module_path
        self.module_name = os.path.basename(
            os.path.normpath(self.module_path))

        self.disk_dir = ""
        self.server_repo_path = ""
        self.disk_dir = os.path.join(self.cwd, self.module_path)
        self.server_repo_path = pathf.devModule(self.module_path, self._area)

        placeholders = {'module_name': self.module_name,
                        'module_path': self.module_path,
                        'getlogin': os.getlogin()}

        self.module_template = module_template_cls()

        self.module_template.set_placeholders(placeholders)

        self._remote_repo_valid = False
        """bool: Specifies whether there are conflicting server file paths.
        This is separate from `_can_push_repo_to_remote` as the latter
        considers local issues as well. This flag is separated as the user
        needs to call this towards the beginning to avoid unnecessary file
        creation"""

        # These boolean values allow us to call the methods in any order
        self._can_create_local_module = False
        """bool: Specifies whether create_local_module can be called"""

        self._can_push_repo_to_remote = False
        """bool: Specifies whether push_repo_to_remote can be called"""

    def set_template_files_from_folder(self, template_folder, update=False):
        """Sets `template_files` from a folder passed to it.

        If update is 'True', then the dictionary is updated, not overwritten.

        Note:
            All hidden files and folders (apart from '.' and '..') will be
            included.

        Args:
            template_folder: The relative or absolute path to template folder.
                Inside, all files and folders can use {value:s} placeholders
                to allow completion using `template_args` attribute.
            update: If True, `template_files` will be updated

        """

        self.module_template.set_template_files_from_folder(template_folder,
                                                            update)

    def verify_remote_repo(self):
        """Verifies there are no name conflicts with the remote repository.

        This checks whether or not there are any name conflicts between the
        intended module name and the modules that already exist on the remote
        repository.

        Sets the `_remote_repo_valid` boolean value to True if there are no
        conflicts.

        Raises:
            VerificationError: If there is a name conflict with the server.

        """
        existing_remote_repo_paths = self._get_existing_remote_repo_paths()

        if existing_remote_repo_paths:
            err_message = ("The paths {dirs:s} already exist on gitolite,"
                           " cannot continue")
            raise VerificationError(
                err_message.format(
                    dirs=", ".join(existing_remote_repo_paths))
            )

        self._remote_repo_valid = True

    def _get_existing_remote_repo_paths(self):
        """Gets a list of existing remote repository paths relating to module.

        This checks whether any paths relating to the new module exist on
        gitolite, returning a list of all of them.

        Returns:
            List[str]: A list of all existing remote repository paths

        """
        dir_list = self._get_remote_dir_list()
        existing_dir_paths = []

        for d in dir_list:
            if vcs_git.is_repo_path(d):
                existing_dir_paths.append(d)

        return existing_dir_paths

    def _get_remote_dir_list(self):
        """Returns a list of paths with which to check for naming collisions.

        Aside from the intended server destination for the module, there should
        be no conflicts with eg. vendor module paths.

        Returns:
            List[str]: A list of all potentially conflicting paths.

        """
        # Intended initial destination for module
        server_repo_path = self.server_repo_path

        # Vendor location for module
        vendor_path = pathf.vendorModule(self.module_path, self._area)

        # Production location for module
        prod_path = pathf.prodModule(self.module_path, self._area)

        dir_list = [server_repo_path, vendor_path, prod_path]

        return dir_list

    def verify_can_create_local_module(self):
        """Verifies that conditions are suitable for creating a local module.

        When :meth:`create_local_module` is called, if the boolean value
        `_can_create_local_module` is False, this method is run to make sure
        that :meth:`create_local_module` can operate completely.

        This method also sets the `_can_create_local_module` attribute to True
        so it can be run separately before :meth:`create_local_module`.

        This method will fail (raise a VerificationError) if:
            - The intended local directory for creation already exists
            - The user is currently inside a git repository

        Raises:
            VerificationError: Local module cannot be created.

        """

        mod_dir_exists = os.path.exists(self.disk_dir)
        cwd_is_repo = vcs_git.is_git_dir()

        if mod_dir_exists or cwd_is_repo:
            err_list = []

            if mod_dir_exists:
                err_list.append("Directory {dir:s} already exists, "
                                "please move elsewhere and try again.")

            if cwd_is_repo:
                err_list.append("Currently in a git repository, "
                                "please move elsewhere and try again.")

            err_message = "\n".join(err_list).format(dir=self.module_path)

            self._can_create_local_module = False
            raise VerificationError(err_message)

        self._can_create_local_module = True

    def verify_can_push_repo_to_remote(self):
        """Verifies that one can push the local module to the remote server.

        When :meth:`push_repo_to_remote` is called, if the boolean value
        `_can_push_repo_to_remote` is False, this method is run to make sure
        that :meth:`push_repo_to_remote` can operate completely.

        This method also sets the `_can_push_repo_to_remote` attribute to True
        so it can be run separately before :meth:`push_repo_to_remote`.

        This method will fail (raise a VerificationError) if:
            - The local module does not exist
            - The local module is not a git repository
            - There is a naming conflict with the remote server

        Raises:
            VerificationError: Local repository cannot be pushed to remote.

        """
        valid = True

        mod_dir_exists = os.path.exists(self.disk_dir)

        err_list = []

        if not mod_dir_exists:
            err_list.append("Directory {dir:s} does not exist.")
            valid = False

        else:
            mod_dir_is_repo = vcs_git.is_git_root_dir(self.disk_dir)
            if not mod_dir_is_repo:
                err_list.append("Directory {dir:s} is not a git repository. "
                                "Unable to push to remote repository.")
                valid = False

        err_list = [err.format(dir=self.module_path) for err in err_list]

        # This allows us to retain the remote_repo_valid error message
        if not self._remote_repo_valid:
            try:
                self.verify_remote_repo()
            except VerificationError as e:
                err_list.append(str(e))
                valid = False

        if not valid:
            self._can_push_repo_to_remote = False
            raise VerificationError("\n".join(err_list))

        self._can_push_repo_to_remote = True

    def create_local_module(self):
        """Creates the folder structure and files in a new git repository.

        This will use the file creation specified in :meth:`create_files`.
        It will also stage and commit these files to a git repository located
        in the same directory

        Note:
            This will set `_can_create_local_module` False in order to prevent
            the user calling this method twice in succession.

        Raises:
            VerificationError: Local module cannot be created.

        """
        if not self._can_create_local_module:
            self.verify_can_create_local_module()

        self._can_create_local_module = False

        print("Making clean directory structure for " + self.module_path)

        if not os.path.isdir(self.disk_dir):
            os.makedirs(self.disk_dir)

        # The reason why we have to change directory into the folder where the
        # files are created is in order to remain compatible with
        # makeBaseApp.pl, used for IOC and Support modules
        os.chdir(self.disk_dir)
        self.module_template.create_files()
        os.chdir(self.cwd)

        vcs_git.init_repo(self.disk_dir)
        vcs_git.stage_all_files_and_commit(self.disk_dir)

    def print_message(self):
        """Prints a message to detail the user's next steps."""
        self.module_template.print_message()

    def add_contact(self):
        """Add the current user as primary module contact"""
        # TODO(Martin) Will have to work out how this works
        # What checks should this method perform?
        raise NotImplementedError

    def push_repo_to_remote(self):
        """Pushes the local repo to the remote server.

        Note:
            This will set `_can_push_repo_to_remote` and `_remote_repo_valid`
            False in order to prevent the user calling this method twice in
            succession.

        Raises:
            VerificationError: Local repository cannot be pushed to remote.

        """
        if not self._can_push_repo_to_remote:
            self.verify_can_push_repo_to_remote()

        self._can_push_repo_to_remote = False
        self._remote_repo_valid = False

        vcs_git.add_new_remote_and_push(self.server_repo_path, self.disk_dir)


class NewModuleCreatorWithApps(NewModuleCreator):
    """Abstract class for the management of the creation of app-based modules.

    Attributes:
        app_name: The name of the app for the new module.
            This is a separate folder in each git repository, corresponding to
            the newly created module.

    """

    def __init__(self, module_path, area, module_template, app_name=None):
        """Initialise variables.

        Args:
            app_name: The name of the app for the new module.
        """
        super(NewModuleCreatorWithApps, self).__init__(module_path, area,
                                                       module_template)
        if app_name:
            self.app_name = app_name
        else:  # Sensible default - used by support
            self.app_name = self.module_name

        self.module_template.set_placeholders({'app_name': self.app_name},
                                              True)


class NewModuleCreatorAddAppToModule(NewModuleCreatorWithApps):
    """Class for the management of adding a new App to an existing IOC module.

    In an old-style module, a single module repository contains multiple IOC
    apps. To maintain compatibility, this class exists for the creation of new
    apps inside existing modules.

    Note:
        While the script is called dls_start_new_module, the original svn
        script similarly created the new 'app_nameApp' folders in existing
        svn 'modules'.

        In keeping with the rest of the :class:`NewModuleCreator` code, I
        continue to use the word 'module' to refer to the git repository (local
        or remote) in the documentation, and the 'app' to be the new IOC folder
        'app_nameApp' created inside.

        From the point of view of the user, however, the 'app_nameApp' folder
        itself was considered the 'module', hence the confusing use of eg.
        dls_start_new_module for the main script's name.

    """

    def verify_remote_repo(self):
        """Verifies there are no name conflicts with the remote repository.

        This checks whether or not there are any name conflicts between the
        intended module and app names, and the modules that already exist on
        the remote repository.

        Sets the `_remote_repo_valid` boolean value to True if there are no
        conflicts.

        This method will fail (raise a VerificationError) if:
            - There is no remote repository to clone from
            - There is an app_name conflict with one of the remote
              paths

        Raises:
            VerificationError: If there is an issue with the remote repository.
            Error: From :meth:`_check_if_remote_repo_has_app`.
                This should never be raised. There is a bug if it is!

        """
        existing_remote_repo_paths = self._get_existing_remote_repo_paths()

        if self.server_repo_path not in existing_remote_repo_paths:
            err_message = ("The path {path:s} does not exist on gitolite, so "
                           "cannot clone from it")
            err_message = err_message.format(path=self.server_repo_path)
            raise VerificationError(err_message)

        conflicting_paths = []

        for path in existing_remote_repo_paths:
            if self._check_if_remote_repo_has_app(path):
                conflicting_paths.append(path)

        if conflicting_paths:
            err_message = ("The repositories {paths:s} have apps that"
                           " conflict with {app_name:s}")
            err_message = err_message.format(
                paths=", ".join(conflicting_paths),
                app_name=self.app_name
            )
            raise VerificationError(err_message)

        self._remote_repo_valid = True

    def _check_if_remote_repo_has_app(self, remote_repo_path):
        """Checks if the remote repository contains an app_nameApp folder.

        This checks whether or not there is already a folder with the name
        "app_nameApp" on the remote repository with the given gitolite
        repository path.

        Sets the `_remote_repo_valid` boolean value to True if there are no
        conflicts.

        Returns:
            bool: True if app exists, False otherwise.

        Raises:
            Error: If given repo path does not exist on gitolite.
                This should never be raised. There is a bug if it is!

        """
        if not vcs_git.is_repo_path(remote_repo_path):
            # This should never get raised!
            err_message = ("Remote repo {repo:s} does not exist. Cannot "
                           "clone to determine if there is an app_name "
                           "conflict with {app_name:s}")
            err_message = err_message.format(repo=remote_repo_path,
                                             app_name=self.app_name)
            raise Error(err_message)

        temp_dir = ""
        exists = False
        try:
            temp_dir = tempfile.mkdtemp()
            vcs_git.clone(remote_repo_path, temp_dir)

            if os.path.exists(os.path.join(temp_dir, self.app_name + "App")):
                exists = True

        finally:
            if temp_dir:  # If mkdtemp worked
                shutil.rmtree(temp_dir)

        return exists

    def create_local_module(self):
        """Creates the folder structure and files in a cloned git repository.

        This will use the file creation specified in :meth:`_create_files`. It
        will call this function directly inside the cloned repository; as a
        result, any files you wish to insert in the app folder using
        :meth:`_create_files_from_template_dict` will require `template_files`
        keys to begin with "{app_name:s}App/" before the usual file path.

        """
        if not self._can_create_local_module:
            self.verify_can_create_local_module()

        self._can_create_local_module = False

        print("Cloning module to " + self.module_path)

        vcs_git.clone(self.server_repo_path, self.disk_dir)

        os.chdir(self.disk_dir)
        self.module_template.create_files()
        os.chdir(self.cwd)

        vcs_git.stage_all_files_and_commit(self.disk_dir)

    def push_repo_to_remote(self):
        """Pushes the local repo to the remote server using remote 'origin'.

        This will push the master branch of the local repository to the remote
        server it was cloned from.

        Raises:
            Error: From :meth:`verify_can_push_repo_to_remote`.

        """
        if not self._can_push_repo_to_remote:
            self.verify_can_push_repo_to_remote()

        self._can_push_repo_to_remote = False

        vcs_git.push_to_remote(self.disk_dir)


class ModuleTemplate(object):
    """Class for the creation of new module contents.

    Raises:
        Error: All errors raised by this module inherit from this class

    """

    def __init__(self):
        """Default initialisation of all object attributes.

        """
        self.template_files = {}
        """dict: Dictionary containing file templates.
        Each entry has the (relative) file-path as the key, and the file
        contents as the value. Either may contain placeholders in the form of
        {template_arg:s} for use with the string .format() method, each
        evaluated using the `template_args` attribute."""

        # TODO(Martin) Sort out
        self.required_placeholders = [
            'module_name', 'module_path', 'getlogin'
        ]
        """dict: List of all placeholders used by default.
        These are the placeholders used either in the printed message, or as
        part of the file creation process."""

        self.placeholders = {}
        """dict: Dictionary for module-specific phrases in template_files
        Used for including module-specific phrases such as `module_name`"""

    def set_placeholders(self, extra_placeholders, update=False):
        if update:
            self.placeholders.update(extra_placeholders)
        else:
            self.placeholders = extra_placeholders

    def set_template_files(self, extra_template_files, update=False):
        if update:
            self.template_files.update(extra_template_files)
        else:
            self.template_files = extra_template_files

    def set_template_files_from_folder(self, template_folder, update=False):
        """Sets `template_files` from a folder passed to it.

        If update is 'True', then the dictionary is updated, not overwritten.

        Note:
            All hidden files and folders (apart from '.' and '..') will be
            included.

        Args:
            template_folder: The relative or absolute path to template folder.
                Inside, all files and folders can use {value:s} placeholders
                to allow completion using `template_args` attribute.
            update: If True, `template_files` will be updated

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
        """Creates files from `template_files` and `template_args`

        This uses the `template_files` and `template_args` attributes for file
        creation by default.

        Raises:
            Error: If key in `template_files` is a directory, not a file.

        """
        # dictionary keys are the relative file paths for the documents
        for path in self.template_files:
            # Using template_args allows us to insert eg. module_name
            rel_path = path.format(**self.placeholders)
            logging.debug("rel_path: " + rel_path)

            dir_path = os.path.dirname(rel_path)

            # Stops us from overwriting files in folder (eg .gitignore when
            # adding to Old-Style IOC modules (IOCAddToModule)
            if os.path.isfile(rel_path):
                logging.debug("File already exists: " + rel_path)
                continue

            if os.path.normpath(dir_path) == os.path.normpath(rel_path):
                # If folder given instead of file (ie. rel_path ends with a
                # slash or folder already exists)
                err_message = ("{dir:s} in template dictionary "
                               "is not a valid file name")
                raise Error(err_message.format(dir=dir_path))
            else:
                # dir_path = '' (dir_path = False) if eg. "file.txt" given
                if dir_path and not os.path.isdir(dir_path):
                    os.makedirs(dir_path)

                open(rel_path, "w").write(self.template_files[path].format(
                    **self.placeholders))

    def print_message(self):
        """Prints a message to detail the user's next steps."""
        raise NotImplementedError


class ModuleTemplateTools(ModuleTemplate):
    """Class for the management of the creation of new Tools modules."""

    def __init__(self):
        """Initialise placeholders and default template files."""
        super(ModuleTemplateTools, self).__init__()

        # TODO(Martin) Sort out
        self.required_placeholders = {'module_name': "module_name",
                                      'module_path': "module_path",
                                      'getlogin': "user_login"}

        initial_template_files = obtain_template_files("tools")

        self.set_template_files(initial_template_files)

    def print_message(self):
        message_dict = {'module_path': self.placeholders['module_path']}

        message = ("\nPlease add your patch files to the {module_path:s} "
                   "\ndirectory and edit {module_path:s}/build script "
                   "appropriately")
        message = message.format(**message_dict)

        print(message)


class ModuleTemplatePython(ModuleTemplate):
    """Class for the management of the creation of new Python modules."""

    def __init__(self):
        """Initialise placeholders and default template files."""
        super(ModuleTemplatePython, self).__init__()

        # TODO(Martin) Sort out
        self.required_placeholders = {'module_name': "module_name",
                                 'module_path': "module_path",
                                 'getlogin': "user_login"}

        initial_template_files = obtain_template_files("python")

        self.set_template_files(initial_template_files)

    def print_message(self):
        module_path = self.placeholders['module_path']
        message_dict = {'module_path': module_path,
                        'setup_path': os.path.join(module_path, "setup.py")
                        }

        message = ("\nPlease add your python files to the {module_path:s} "
                   "\ndirectory and edit {setup_path} appropriately.")
        message = message.format(**message_dict)

        print(message)


class ModuleTemplateSupportAndIOC(ModuleTemplate):
    """Abstract class to implement the shared user message for Support and IOC.

    Ensure you use this with :mod:`NewModuleCreatorWithApps`, in order to
    ensure that the app_name value exists

    """

    def __init__(self):
        """Initialise placeholders and default template files."""
        super(ModuleTemplateSupportAndIOC, self).__init__()

        # TODO(Martin) Sort out
        self.required_placeholders.append('app_name')

        # TODO(Martin) Sort out
        # self.set_placeholders(self.required_placeholders)

    def print_message(self):
        # This message is shared between support and IOC
        module_path = self.placeholders['module_path']
        app_name = self.placeholders['app_name']

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

    def __init__(self):
        """Initialise placeholders and default template files."""
        super(ModuleTemplateSupport, self).__init__()

        initial_template_files = obtain_template_files("support")

        self.set_template_files(initial_template_files)

    def create_files(self):
        """Creates the folder structure and files in the current directory.

        This uses makeBaseApp.pl program alongside the
        :meth:`_create_files_from_template_dict` method for file creation.

        """
        os.system('makeBaseApp.pl -t dls {app_name:s}'.format(
            app_name=self.placeholders['app_name']))
        os.system('dls-make-etc-dir.py && make clean uninstall')
        self._create_files_from_template_dict()


class ModuleTemplateIOC(ModuleTemplateSupportAndIOC):
    """Class for the management of the creation of new IOC modules.

    These have apps with a different name to the module.

    """

    def __init__(self):
        """Initialise placeholders and default template files."""
        super(ModuleTemplateIOC, self).__init__()

        initial_template_files = obtain_template_files("ioc")

        self.set_template_files(initial_template_files)

    def create_files(self):
        """Creates the folder structure and files in the current directory.

        This uses makeBaseApp.pl program alongside the
        _create_files_from_template_dict method for file creation.

        """
        os.system('makeBaseApp.pl -t dls {app_name:s}'.format(
            **self.placeholders))
        os.system('makeBaseApp.pl -i -t dls {app_name:s}'.format(
            **self.placeholders))
        shutil.rmtree(os.path.join(self.placeholders['app_name'] + 'App',
                                   'opi'))
        self._create_files_from_template_dict()


class ModuleTemplateIOCBL(ModuleTemplateIOC):
    """Class for the management of the creation of new IOC BL modules."""

    def print_message(self):
        module_path = self.placeholders['module_path']
        app_name = self.placeholders['app_name']
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
        os.system('makeBaseApp.pl -t dlsBL ' + self.placeholders['app_name'])
        self._create_files_from_template_dict()

