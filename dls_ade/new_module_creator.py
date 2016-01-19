from __future__ import print_function
import os
import path_functions as pathf
import shutil
import logging
import vcs_git
import module_template as mt
from exceptions import ParsingError, RemoteRepoError, VerificationError

logging.basicConfig(level=logging.DEBUG)


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
            raise ParsingError("Python module names must start with 'dls_' "
                               "and be valid python identifiers")

        return NewModuleCreator(module_name, area, mt.ModuleTemplatePython)

    elif area == "support":
        return NewModuleCreatorWithApps(module_name, area,
                                        mt.ModuleTemplateSupport,
                                        app_name=module_name)

    elif area == "tools":
        return NewModuleCreator(module_name, area, mt.ModuleTemplateTools)

    else:
        raise ParsingError("Don't know how to make a module of type: " + area)


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

    dash_separated, cols, domain, technical_area = parse_ioc_module_name(
            module_name)

    if technical_area == "BL":
        if dash_separated:
            app_name = module_name
            module_path = domain + "/" + app_name
        else:
            app_name = domain
            module_path = domain + "/" + technical_area

        return NewModuleCreatorWithApps(module_path, area,
                                        mt.ModuleTemplateIOCBL,
                                        app_name=app_name)

    module_template_cls = mt.ModuleTemplateIOC

    if dash_separated:
        app_name = module_name
        module_path = domain + "/" + app_name
        return NewModuleCreatorWithApps(module_path, area, module_template_cls,
                                        app_name=app_name)

    if len(cols) == 3 and cols[2]:
        ioc_number = cols[2]
    else:
        ioc_number = "01"

    app_name = "-".join([domain, technical_area, "IOC", ioc_number])

    if fullname:
        module_path = domain + "/" + app_name
        return NewModuleCreatorWithApps(module_path, area, module_template_cls,
                                        app_name=app_name)
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
                                                  app_name=app_name)
        else:
            # Otherwise, the behaviour is exactly the same as that given
            # by the ordinary IOC class as module_path is the only thing
            # that is different
            return NewModuleCreatorWithApps(module_path, area,
                                            module_template_cls,
                                            app_name=app_name)


# TODO(Martin) unit tests for function
def parse_ioc_module_name(module_name):
    """Parses the module name and returns relevant data.

    Args:
        module_name: The ioc module's name.

    Returns:
        bool: True if the string is dash-separated, false otherwise.
            Based on original svn implementation, if both slashes and dashes
            appear in the module name, it will default to slash-separated.
        list[str]: A list of strings that make up the module name.
        str: The domain of the module.
        str: The technical area of the module

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

    domain = cols[0]
    technical_area = cols[1]

    return dash_separated, cols, domain, technical_area


class NewModuleCreator(object):
    """Abstract base class for the management of the creation of new modules.

    Attributes:
        _area: The 'area' of the module to be created.
        _cwd: The current working directory upon initialisation.
        _module_name: The base name of the module path.
        _module_path: The relative module path.
            Used in messages and exceptions for user-friendliness.
        disk_dir: The absolute module path.
            Used for system and git commands.
        _server_repo_path: The git repository server path for module.
        _module_template: Object that handles file and user message creation.

    Raises:
        Error: All errors raised by this module inherit from this class
        VerificationError: Errors relating to the `verify_` methods.

    """

    def __init__(self, module_path, area, module_template_cls,
                 **kwargs):
        """Default initialisation of all object attributes.

        Args:
            module_path: The relative module path.
                Used in messages and exceptions for user-friendliness.
            area: The development area of the module to be created.
                In particular, this specifies the exact template files to be
                created as well as affecting the repository server path.
            module_template_cls: Class for module_template object.
                Must be a non-abstract subclass of ModuleTemplate.
           kwargs: Additional arguments for module creation.

        """
        self._area = area
        self._cwd = os.getcwd()

        self._module_path = module_path
        self._module_name = os.path.basename(os.path.normpath(
                                             self._module_path))

        self.disk_dir = os.path.join(self._cwd, self._module_path)
        self._server_repo_path = pathf.devModule(self._module_path, self._area)

        template_args = {'module_name': self._module_name,
                         'module_path': self._module_path,
                         'user_login': os.getlogin()}

        if kwargs:
            template_args.update(kwargs)

        self._module_template = module_template_cls(template_args)

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
        if self._remote_repo_valid:
            return

        if vcs_git.is_repo_path(self._server_repo_path):
            err_message = ("The path {dir:s} already exists on gitolite,"
                           " cannot continue")
            raise VerificationError(
                err_message.format(dir=self._server_repo_path)
            )

        self._remote_repo_valid = True

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
        if self._can_create_local_module:
            return

        err_list = []

        if os.path.exists(self.disk_dir):
            err_list.append("Directory {dir:s} already exists, "
                            "please move elsewhere and try again.")

        if vcs_git.is_git_dir(self._cwd):
            err_list.append("Currently in a git repository, "
                            "please move elsewhere and try again.")

        if err_list:
            err_message = "\n".join(err_list).format(dir=self._module_path)

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
        if self._can_push_repo_to_remote:
            return

        self._can_push_repo_to_remote = True

        err_list = []

        if not os.path.exists(self.disk_dir):
            err_list.append("Directory {dir:s} does not exist.")

        else:
            mod_dir_is_repo = vcs_git.is_git_root_dir(self.disk_dir)
            if not mod_dir_is_repo:
                err_list.append("Directory {dir:s} is not a git repository. "
                                "Unable to push to remote repository.")

        err_list = [err.format(dir=self._module_path) for err in err_list]

        # This allows us to retain the remote_repo_valid error message
        if not self._remote_repo_valid:
            try:
                self.verify_remote_repo()
            except VerificationError as e:
                err_list.append(str(e))

        if err_list:
            self._can_push_repo_to_remote = False
            raise VerificationError("\n".join(err_list))

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
            OSError: The disk_dir already exists (outside interference).

        """
        self.verify_can_create_local_module()

        self._can_create_local_module = False

        print("Making clean directory structure for " + self._module_path)

        os.makedirs(self.disk_dir)

        # The reason why we have to change directory into the folder where the
        # files are created is in order to remain compatible with
        # makeBaseApp.pl, used for IOC and Support modules
        os.chdir(self.disk_dir)

        self._module_template.create_files()

        os.chdir(self._cwd)

        vcs_git.init_repo(self.disk_dir)
        vcs_git.stage_all_files_and_commit(self.disk_dir)

    def print_message(self):
        """Prints a message to detail the user's next steps."""
        self._module_template.print_message()

    def push_repo_to_remote(self):
        """Pushes the local repo to the remote server.

        Note:
            This will set `_can_push_repo_to_remote` and `_remote_repo_valid`
            False in order to prevent the user calling this method twice in
            succession.

        Raises:
            VerificationError: Local repository cannot be pushed to remote.

        """
        self.verify_can_push_repo_to_remote()

        self._can_push_repo_to_remote = False
        self._remote_repo_valid = False

        vcs_git.add_new_remote_and_push(self._server_repo_path, self.disk_dir)


class NewModuleCreatorWithApps(NewModuleCreator):
    """Abstract class for the management of the creation of app-based modules.

    Attributes:
        _app_name: The name of the app for the new module.
            This is a separate folder in each git repository, corresponding to
            the newly created module.

    """

    def __init__(self, module_path, area, module_template, **kwargs):
        """Initialise variables.

        Args:
            kwargs: Must include app_name.
        """

        if 'app_name' not in kwargs:
            raise mt.ArgumentError("'app_name' must be provided as keyword "
                                   "argument.")

        super(NewModuleCreatorWithApps, self).__init__(
            module_path,
            area,
            module_template,
            **kwargs
        )

        self._app_name = kwargs['app_name']


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

        if self._remote_repo_valid:
            return

        if not vcs_git.is_repo_path(self._server_repo_path):
            err_message = ("The path {path:s} does not exist on gitolite, so "
                           "cannot clone from it")
            err_message = err_message.format(path=self._server_repo_path)
            raise VerificationError(err_message)

        conflicting_path = self._check_if_remote_repo_has_app(
            self._server_repo_path
        )

        if conflicting_path:
            err_message = ("The repository {path:s} has an app that conflicts "
                           "with app name: {app_name:s}")
            err_message = err_message.format(
                path=self._server_repo_path,
                app_name=self._app_name
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
                                             app_name=self._app_name)
            raise RemoteRepoError(err_message)

        temp_dir = ""
        exists = False
        try:
            repo = vcs_git.temp_clone(remote_repo_path)
            temp_dir = repo.working_tree_dir

            if os.path.exists(os.path.join(temp_dir, self._app_name + "App")):
                exists = True

        finally:
            try:
                if temp_dir:
                    shutil.rmtree(temp_dir)
            except OSError:
                pass

        return exists

    def create_local_module(self):
        """Creates the folder structure and files in a cloned git repository.

        This will use the file creation specified in :meth:`_create_files`.

        """
        self.verify_can_create_local_module()

        self._can_create_local_module = False

        print("Cloning module to " + self._module_path)

        vcs_git.clone(self._server_repo_path, self.disk_dir)

        os.chdir(self.disk_dir)
        self._module_template.create_files()
        os.chdir(self._cwd)

        vcs_git.stage_all_files_and_commit(self.disk_dir)

    def push_repo_to_remote(self):
        """Pushes the local repo to the remote server using remote 'origin'.

        This will push the master branch of the local repository to the remote
        server it was cloned from.

        Raises:
            Error: From :meth:`verify_can_push_repo_to_remote`.

        """
        self.verify_can_push_repo_to_remote()

        self._can_push_repo_to_remote = False

        vcs_git.push_to_remote(self.disk_dir)
