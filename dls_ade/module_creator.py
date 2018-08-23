import os
import shutil
import logging
from getpass import getuser

from dls_ade import vcs_git, Server
from dls_ade.exceptions import (RemoteRepoError, VerificationError,
                                ArgumentError)


class ModuleCreator(object):
    """Abstract base class for the management of the creation of new modules.

    Attributes:
        _area: The 'area' of the module to be created.
        _cwd: The current working directory upon initialisation.
        _module_name: The base name of the module path.
        _module_path: The relative module path.
            Used in messages and exceptions for user-friendliness.
        abs_module_path: The absolute module path.
            Used for system and git commands.
        _server_repo_path: The git repository server path for module.
        _module_template: Object that handles file and user message creation.
        _remote_repo_valid(bool): True if conflicting paths exist on server.
            This flag is separated as the user needs to check this towards
            the beginning to avoid unnecessary file creation.
        _can_create_local_module(bool): True if can run create_local_module.
        _can_push_repo_to_remote(bool): True if can run push_repo_to_remote.

    Raises:
        :class:`~dls_ade.exceptions.ModuleCreatorError`: Base class for this \
            module's exceptions
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
        self._usermsg = logging.getLogger("usermessages")

        self._area = area
        self._cwd = os.getcwd()

        self._module_path = module_path
        self._module_name = os.path.basename(os.path.normpath(
                                             self._module_path))
        self.server = Server()

        self.abs_module_path = os.path.join(self._cwd, self._module_path)
        self._server_repo_path = self.server.dev_module_path(self._module_path,
                                                             self._area)

        template_args = {'module_name': self._module_name,
                         'module_path': self._module_path,
                         'user_login': getuser()}

        if kwargs:
            template_args.update(kwargs)

        self._module_template = module_template_cls(template_args)

        self._remote_repo_valid = False

        # These boolean values allow us to call the methods in any order
        self._can_create_local_module = False
        self._can_push_repo_to_remote = False

    def verify_remote_repo(self):
        """Verifies there are no name conflicts with the remote repository.

        This checks whether or not there are any name conflicts between the
        intended module name and the modules that already exist on the remote
        repository.

        Sets the `_remote_repo_valid` boolean value to True if there are no
        conflicts.

        Raises:
            :class:`~dls_ade.exceptions.VerificationError`: If there is a \
                name conflict with the server.
        """

        if self._remote_repo_valid:
            return

        if self.server.is_server_repo(self._server_repo_path):
            err_message = ("The path {dir:s} already exists on server,"
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
            :class:`~dls_ade.exceptions.VerificationError`: Local module \
                cannot be created.
        """

        if self._can_create_local_module:
            return

        err_list = []

        if os.path.exists(self.abs_module_path):
            err_list.append("Directory {dir:s} already exists, "
                            "please move elsewhere and try again.")

        if vcs_git.is_in_local_repo(self._cwd):
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
            :class:`~dls_ade.exceptions.VerificationError`: Local repository \
                cannot be pushed to remote.
        """

        if self._can_push_repo_to_remote:
            return

        self._can_push_repo_to_remote = True

        err_list = []

        if not os.path.exists(self.abs_module_path):
            err_list.append("Directory {dir:s} does not exist.")

        else:
            mod_dir_is_repo = vcs_git.is_local_repo_root(self.abs_module_path)
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

        This will use the file creation specified in
        :meth:`~dls_ade.module_template.ModuleTemplate.create_files`. It will
        also stage and commit these files to a git repository located in the
        same directory

        Note:
            This will set `_can_create_local_module` False in order to prevent
            the user calling this method twice in succession.

        Raises:
            :class:`~dls_ade.exceptions.VerificationError`: Local module \
                cannot be created.
            OSError: The abs_module_path already exists (outside interference).
        """

        self.verify_can_create_local_module()

        self._can_create_local_module = False

        self._usermsg.info("Making clean directory structure for %s",
                           self._module_path)

        os.makedirs(self.abs_module_path)

        # The reason why we have to change directory into the folder where the
        # files are created is in order to remain compatible with
        # makeBaseApp.pl, used for IOC and Support modules
        os.chdir(self.abs_module_path)

        self._module_template.create_files()

        os.chdir(self._cwd)

        repo = vcs_git.init_repo(self.abs_module_path)
        vcs_git.stage_all_files_and_commit(repo, "Initial commit")

    def get_print_message(self):
        """Prints a message to detail the user's next steps."""
        return self._module_template.get_print_message()

    def push_repo_to_remote(self):
        """Pushes the local repo to the remote server.

        Note:
            This will set `_can_push_repo_to_remote` and `_remote_repo_valid`
            False in order to prevent the user calling this method twice in
            succession.

        Raises:
            :class:`~dls_ade.exceptions.VerificationError`: Local repository \
                cannot be pushed to remote.
            :class:`~dls_ade.exceptions.VCSGitError`: If issue with adding a \
                new remote and pushing.
        """

        self.verify_can_push_repo_to_remote()

        self._can_push_repo_to_remote = False
        self._remote_repo_valid = False

        vcs = self.server.create_new_local_repo(self._module_name, self._area,
                                                self.abs_module_path)
        vcs.add_new_remote_and_push(self._server_repo_path)


class ModuleCreatorWithApps(ModuleCreator):
    """Abstract class for the management of the creation of app-based modules.

    Attributes:
        _app_name: The name of the app for the new module.
            This is a separate folder in each git repository, corresponding to
            the newly created module.

    Raises:
        :class:`~dls_ade.exceptions.ArgumentError`: If 'app_name' not given \
            as a keyword argument
    """

    def __init__(self, module_path, area, module_template, **kwargs):
        """Initialise variables.

        Args:
            kwargs: Must include app_name.
        """

        if 'app_name' not in kwargs:
            raise ArgumentError("'app_name' must be provided as keyword "
                                "argument.")

        super(ModuleCreatorWithApps, self).__init__(
            module_path,
            area,
            module_template,
            **kwargs
        )

        self._app_name = kwargs['app_name']


class ModuleCreatorAddAppToModule(ModuleCreatorWithApps):
    """Class for the management of adding a new App to an existing IOC module.

    In an old-style module, a single module repository contains multiple IOC
    apps. To maintain compatibility, this class exists for the creation of new
    apps inside existing modules.

    Note:
        While the script is called dls_start_new_module, the original svn
        script similarly created the new 'app_nameApp' folders in existing
        svn 'modules'.

        In keeping with the rest of the :class:`ModuleCreator` code, I
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
            :class:`~dls_ade.exceptions.VerificationError`: If there is an \
                issue with the remote repository.
            :class:`~dls_ade.exceptions.RemoteRepoError`: If the given server \
                path does not exist.
                This should never be raised. There is a bug if it is!
        """

        if self._remote_repo_valid:
            return

        if not self.server.is_server_repo(self._server_repo_path):
            err_message = ("The path {path:s} does not exist on server, so "
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
        "app_nameApp" on the remote repository with the given server
        repository path.

        Sets the `_remote_repo_valid` boolean value to True if there are no
        conflicts.

        Returns:
            bool: True if app exists, False otherwise.

        Raises:
            :class:`~dls_ade.exceptions.RemoteRepoError`: If given repo path \
                does not exist on server.
                This should never be raised. There is a bug if it is!
            :class:`~dls_ade.exceptions.VCSGitError`: Issue with the vcs_git \
                function calls.
        """

        if not self.server.is_server_repo(remote_repo_path):
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
            repo = self.server.temp_clone(remote_repo_path).repo
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

        This will use the file creation specified in
        :meth:`~dls_ade.module_template.ModuleTemplate.create_files`.

        Raises:
            :class:`~dls_ade.exceptions.ArgumentError`: From \
                :meth:`~dls_ade.module_template.ModuleTemplate.create_files`
            OSError: From \
                :meth:`~dls_ade.module_template.ModuleTemplate.create_files`
            :class:`~dls_ade.exceptions.VCSGitError`: From \
                :func:`~dls_ade.vcs_git.stage_all_files_and_commit`
        """

        self.verify_can_create_local_module()

        self._can_create_local_module = False

        self._usermsg.info("Cloning module to {}".format(self._module_path))

        vcs = self.server.clone(self._server_repo_path, self.abs_module_path)

        os.chdir(self.abs_module_path)
        self._module_template.create_files()
        os.chdir(self._cwd)

        commit_message = ("Added app, {app_name:s}, to module.".format(
            app_name=self._app_name
        ))

        vcs_git.stage_all_files_and_commit(vcs.repo, commit_message)

    def push_repo_to_remote(self):
        """Pushes the local repo to the remote server using remote 'origin'.
        :class:`~dls_ade.exceptions.VCSGitError`
        This will push the master branch of the local repository to the remote
        server it was cloned from.

        Raises:
            :class:`~dls_ade.exceptions.VerificationError`: From \
                :meth:`.verify_can_push_repo_to_remote`.
            :class:`~dls_ade.exceptions.VCSGitError`: From \
                :func:`~dls_ade.vcs_git.push_to_remote`

        """
        self.verify_can_push_repo_to_remote()

        self._can_push_repo_to_remote = False

        vcs = self.server.create_new_local_repo(self._module_name, self._area,
                                                self.abs_module_path)
        vcs.push_to_remote()
