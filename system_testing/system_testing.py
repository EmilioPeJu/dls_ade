from __future__ import print_function
import os
import subprocess
import tempfile
import shutil
import logging
from nose.tools import assert_equal, assert_true, assert_false


ENVIRONMENT_CORRECT = False


try:
    from dls_ade import vcs_git
    from dls_ade import Server
    from dls_ade import bytes_to_string
except ImportError as e:
    print(e)
    vcs_git = None
    Server = None
    raise ImportError("PYTHONPATH must contain the dls_ade package")


def check_environment():
    """Checks that the environment has been set up correctly for testing."""
    # Make sure env var is set.(PYTHONPATH must also be set, but cannot
    # easily test it is correct)

    global ENVIRONMENT_CORRECT

    if ENVIRONMENT_CORRECT:
        return

    try:
        os.environ['GIT_ROOT_DIR']
    except KeyError:
        raise EnvironmentError("GIT_ROOT_DIR must be set")

    ENVIRONMENT_CORRECT = True


class SystemTestingError(Exception):
    """Class for exceptions relating to system_testing module."""
    pass


class SettingsError(SystemTestingError):
    """Class for exceptions relating to invalid settings"""
    pass


class TempdirError(SystemTestingError):
    """Class for exceptions relating to issues with temporary directories."""
    pass


class GitRootDirError(SystemTestingError):
    """Class for exceptions raised when GIT_ROOT_DIR is not set."""
    def __init__(self):
        err_message = "Cannot call functions if GIT_ROOT_DIR not set."
        super(GitRootDirError, self).__init__(err_message)


def get_local_temp_clone(server_repo_path):
    """Obtain the root directory for a temporary clone of the given repository.

    Args:
        server_repo_path: The repository path for the server.

    Returns:
        str: The root directory of the cloned server repository.
            This will always be located in a temporary folder.

    Raises:
        :class:`~dls_ade.exceptions.VCSGitError`: From \
            :func:`dls_ade,vcs_git.temp_clone`.

    """
    logging.debug("Cloning server repo path: " + server_repo_path)

    server = Server()

    repo = server.temp_clone(server_repo_path).repo

    tempdir = repo.working_tree_dir

    logging.debug("Server repo path cloned to: " + tempdir)

    return tempdir


def delete_temp_repo(local_repo_path):
    """Delete a repository in a temporary directory.

    Args:
        local_repo_path: The path to the temporary directory.

    Raises:
        :class:`.TempdirError`: If the path given is not a temporary folder.
        :class:`.TempdirError`: If the path given is not for a git repository.

    """
    if not os.path.realpath(local_repo_path).startswith(tempfile.gettempdir()):
        err_message = ("{local_repo_path:s} is not a temporary folder, cannot "
                       "delete.")
        raise TempdirError(err_message.format(
                local_repo_path=local_repo_path))

    if not vcs_git.is_local_repo_root(local_repo_path):
        err_message = ("{local_repo_path:s} is not a git root directory, "
                       "cannot delete.")
        raise TempdirError(err_message.format(
                local_repo_path=local_repo_path))

    shutil.rmtree(local_repo_path)


def check_if_repos_equal(path_1, path_2):
    """Check if the two local paths given are equivalent.

    This involves all files and folders (plus names) being identical. The
    names of the folders themselves are ignored.

    The `.git` folder is ignored, as it is different even for a cloned
    repository. The `.gitattributes` file is also ignored.

    Args:
        path_1: The first path for comparison.
        path_2: The second path for comparison.

    Returns:
        bool: True if the directories are equal, False otherwise.

    Raises:
        :class:`.SettingsError`: If either of the two paths are blank.
        :class:`subprocess.CalledProcessError`: If there is an unexpected \
            error in :func:`subprocess.check_output`.

    """
    if not (path_1 and path_2):
        err_message = ("Two paths must be given to compare folders.\n"
                       "path 1: {path_1:s}, path 2: {path_2:s}.")
        raise SettingsError(err_message.format(path_1=path_1, path_2=path_2))

    # .keep files allow git to store otherwise empty folders.
    command_format = ("diff -rq --exclude=.git --exclude=.gitattributes "
                      "--exclude=.keep {path1:s} {path2:s}")
    call_args = command_format.format(path1=path_1, path2=path_2).split()

    logging.debug("Testing folders for equality.")
    logging.debug("Comparison path one: " + path_1)
    logging.debug("Comparison path two: " + path_2)
    try:
        subprocess.check_output(call_args)
    except subprocess.CalledProcessError as e:
        logging.debug(e.output)
        if e.returncode == 1:  # Indicates files are different.
            return False
        else:
            raise

    return True


class SystemTest(object):
    """Class for the automatic generation of system tests using nosetests.

    Attributes:
        _script: The script to be tested.
        description: The test description as used by nosetests.

        _std_out: The standard output of the script called.
        _std_err: The standard error of the script called.
        _return_code: The return code of the script called.

        _server_repo_clone_path: The path to a clone of `_server_repo_path`.

        _default_server_repo_path: A server path pointing to a default repo.
            This is used to set `_server_repo_path` to a default state.

        _exception_type: The exception type to test for in standard error.
        _exception_string: The exception string to test for in standard error.
        _std_out_compare_string: The string for standard output comparisons.
        _std_out_starts_with_string: Standard output 'startswith' check string.
        _std_out_ends_with_string: Standard output 'endswith' check string.
        _arguments: A string containing the arguments for the given script.
        _input: The input to be sent to the script while it's running.
        _attributes_dict: A dictionary of all git attributes to check for.

        _local_repo_path: A local path, used for attribute checking.

        _repo_comp_method: Specifies how standard output is tested.
            This can be: 'local_comp' to test `_local_comp_path_one` against
            `_local_comp_path_two`. 'server_comp' to test
            `_local_comp_path_one` against `_server_repo_clone_path` (cloned
            from `_server_repo_path`) or 'all_comp' to compare all three paths
            against each other.

        _local_comp_path_one: A local path used for directory comparisons.
        _local_comp_path_two: A local path used for directory comparisons.

        _server_repo_path: The remote repository path.
            This is used for both git attribute checking as well as directory
            comparisons (after being cloned to `_server_repo_clone_path`)

        _branch_name: The name of the repository branch.
            This is used for checking that the given `_local_repo_path` is on
            the given branch, as well as changing `_server_repo_clone_path`'s
            branch.

        _settings_list: A list of all attributes that may be changed.

    Raises:
        :class:`.SettingsError`: Indicates issues with given settings.
        :class:`.TempdirError`: Indicates problem when acting on a temporary \
            directory.
        :class:`dls_ade.exceptions.VCSGitError`: Indicates error in this \
            class or in the settings dict.
        :class:`AssertionError`: Indicates a failure of the script being \
            tested.
        :class:`.GitRootDirError`: Indicates if GIT_ROOT_DIR is not set.

    """

    def __init__(self, script, description):
        check_environment()

        self.server = Server()

        self._script = script
        self.description = description

        self._std_out = ""
        self._std_err = ""
        self._return_code = None

        # Used for attribute checking and comparisons
        self._server_repo_clone_path = ""

        # Used to initialise a server repo to a default state.
        self._default_server_repo_path = ""

        # Used to tests exceptions
        self._exception_type = ""
        self._exception_string = ""

        # Used to test output
        self._std_out_compare_string = None
        self._std_out_starts_with_string = None
        self._std_out_ends_with_string = None

        # Used to alter script interaction
        self._arguments = ""
        self._input = None

        # Used for attribute checking
        self._attributes_dict = {}
        self._local_repo_path = ""

        # Used for comparisons
        self._repo_comp_method = ""

        self._local_comp_path_one = ""
        self._local_comp_path_two = ""

        # Used for attribute checking and comparisons
        self._server_repo_path = ""

        # Used to check for branch names, and also changes the branch of the
        # local `_server_repo_clone_path` repo.
        self._branch_name = ""

        self._settings_list = [  # List of valid variables to update.
            'default_server_repo_path',
            'exception_type',
            'exception_string',
            'std_out_compare_string',
            'std_out_starts_with_string',
            'std_out_ends_with_string',
            'arguments',
            'input',
            'attributes_dict',
            'server_repo_path',
            'local_repo_path',
            'repo_comp_method',
            'local_comp_path_one',
            'local_comp_path_two',
            'branch_name',
        ]

    def load_settings(self, settings):
        """Loads the given settings dictionary into the relevant variables.

        Note: This will only load the following variables:
            - default_server_repo_path
            - exception_type
            - exception_string
            - std_out_compare_string
            - std_out_starts_with_string
            - std_out_ends_with_string
            - arguments
            - input
            - attributes_dict
            - server_repo_path
            - local_repo_path
            - repo_comp_method
            - local_comp_path_one
            - local_comp_path_two
            - branch_name

        Args:
            settings: The dictionary of settings used to set up the test.

        """
        self.__dict__.update({("_" + key): value for (key, value)
                              in settings.items()
                              if key in self._settings_list})

        logging.debug("The test's local variables are:")
        for key, value in self.__dict__.items():
            logging.debug(str(key) + ": " + str(value))

        logging.debug("End of local variables.")

    def __call__(self):
        """Defined for the use of nosetests.

        This is considered the test function.

        Raises:
            :class:`.SettingsError`: From :meth:`.run_tests`.
            :class:`.SettingsError`: From :meth:`.set_server_repo_to_default`.
            :class:`.TempdirError`: From :meth:`.run_tests`
            :class:`AssertionError`: From :meth:`.run_tests`.
            :class:`dls_ade.exceptions.VCSGitError`: From :meth:`.run_tests`.

        """
        self.set_server_repo_to_default()
        self.call_script()
        self.run_tests()

    def set_server_repo_to_default(self):
        """Sets the given server repository to a default state.

        Note:
            If used on an existing server repository, all commit history will
            be overwritten.

        Raises:
            :class:`.SettingsError`: If default given but no server repo.
            :class:`dls_ade.exceptions.VCSGitError`: From \
                :mod:`~dls_ade.vcs_git` functions.

        """
        if not self._default_server_repo_path:
            return

        if not self._server_repo_path:
            raise SettingsError("If 'default_server_repo_path is set, then "
                                "'server_repo_path' must also be set.")

        logging.debug("Setting server repo to default.")
        logging.debug("'Default' server repo path: " +
                      self._default_server_repo_path)

        vcs = self.server.temp_clone(self._default_server_repo_path)
        temp_repo = vcs.repo
        vcs_git.delete_remote(temp_repo, "origin")

        if self.server.is_server_repo(self._server_repo_path):
            temp_repo.create_remote(
                    "origin",
                    os.path.join(self.server.url, self._server_repo_path)
            )
            temp_repo.git.push("origin", temp_repo.active_branch, "-f")

        else:
            vcs.add_new_remote_and_push(self._server_repo_path)

    def call_script(self):
        """Call the script and store output, error and return code.

        If `input` is set, this will pass the input to the child process.

        Raises:
            :class:`ValueError`: From Popen().
        """
        call_args = (self._script + " " + self._arguments).split()

        logging.debug("About to call script with: " + " ".join(call_args))

        # If no input is given, this will prevent communicate() from sending
        # data to the child process.
        if self._input is not None:
            stdin_pipe = subprocess.PIPE
        else:
            stdin_pipe = None

        process = subprocess.Popen(call_args, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   stdin=stdin_pipe)

        self._std_out, self._std_err = process.communicate(self._input)
        self._std_out = bytes_to_string(self._std_out)
        self._std_err = bytes_to_string(self._std_err)
        logging.debug("standard out:\n" + self._std_out)
        logging.debug("standard error:\n" + self._std_err)
        self._return_code = process.returncode
        logging.debug("return code: " + str(self._return_code))

    def run_tests(self):
        """Performs the entire test suite.

        Raises:
            :class:`.SettingsError`: From the tests.
            :class:`.TempdirError`: From :meth:`delete_cloned_server_repo`
            :class:`AssertionError`: From the tests.
            :class:`dls_ade.exceptions.VCSGitError`: From the tests.

        """
        logging.debug("Performing tests.")

        self.check_std_out_and_exceptions()

        self.check_for_and_clone_remote_repo()

        self.run_git_repo_tests()

        self.run_comparison_tests()
        # Filesystem equality checks

        self.delete_cloned_server_repo()

    def check_std_out_and_exceptions(self):
        """Performs all the standard out and error comparisons.

        This includes exception testing.

        Raises:
            :class:`.SettingsError`: From the comparison tests.
            :class:`AssertionError`: From the comparison tests.
            :class:`dls_ade.exceptions.VCSGitError`: From the comparison tests.

        """
        self.check_std_out_for_exception_string()

        self.compare_std_out_to_string()
        self.check_std_out_starts_with_string()
        self.check_std_out_ends_with_string()

    def check_std_out_for_exception_string(self):
        """Check the standard out and error for the exception information.

        Raises:
            :class:`.SettingsError`: If either the exception type or string \
                is blank while the other is not.
            :class:`AssertionError`: If the test does not pass.

        """

        if not self._exception_type or not self._exception_string:
            if not self._exception_type and not self._exception_string:
                return
            raise SettingsError("Both exception_type and exception_string "
                                "must be provided.")

        if isinstance(self._exception_string, list):
            expected_string_components = self._exception_string
        else:
            expected_string_components = [self._exception_string]

        expected_string_components.append(self._exception_type)

        logging.debug("Expected error string components: " +
                      ",".join(expected_string_components))

        assert_true(all(elem in self._std_out for elem in expected_string_components) or
                    all(elem in self._std_err for elem in expected_string_components))

    def compare_std_out_to_string(self):
        """Compare the standard output to std_out_compare_string.

        Raises:
            :class:`AssertionError`: If the test does not pass.

        """
        if self._std_out_compare_string is None:
            return

        logging.debug("Comparing the standard output to comparison string.")

        if isinstance(self._std_out_compare_string, list):
            expected_string_components = self._std_out_compare_string
        else:
            expected_string_components = [self._std_out_compare_string]

        assert_true(all(elem in self._std_out
                        for elem in expected_string_components))

    def check_std_out_starts_with_string(self):
        """Check if the standard output starts with std_out_starts_with_string.

        Raises:
            :class:`AssertionError`: If the test does not pass.

        """
        if self._std_out_starts_with_string is None:
            return

        logging.debug("Checking if the standard output starts with the given "
                      "string.")

        assert_true(self._std_out.startswith(self._std_out_starts_with_string))

    def check_std_out_ends_with_string(self):
        """Check if the standard output ends with std_out_ends_with_string.

        Raises:
            :class:`AssertionError`: If the test does not pass.

        """
        if self._std_out_ends_with_string is None:
            return

        logging.debug("Checking if the standard output ends with the given "
                      "string.")

        assert_true(self._std_out.endswith(self._std_out_ends_with_string))

    def check_for_and_clone_remote_repo(self):
        """Checks server repo path exists and clones it.

        Raises:
            :class:`AssertionError`: From check_remote_repo_exists
            :class:`dls_ade.exceptions.VCSGitError`: from clone_server_repo

        """
        if not self._server_repo_path:
            return

        self.check_remote_repo_exists()

        self.clone_server_repo()

    def check_remote_repo_exists(self):
        """Check that the server_repo_path exists on the server.

        Raises:
            :class:`AssertionError`: If the test does not pass.

        """
        logging.debug("Checking server repo path given exists.")
        assert_true(self.server.is_server_repo(self._server_repo_path))

    def clone_server_repo(self):
        """Clone the server_repo_path to a temp dir and return the path.

        If a branch name is set, then the remote branch will be checked out.

        Raises:
            VCSGitError: From vcs_git.temp_clone()
        """
        logging.debug("Cloning the server repository to temporary directory.")
        repo = self.server.temp_clone(self._server_repo_path).repo

        if self._branch_name:
            vcs_git.checkout_remote_branch(self._branch_name, repo)

        self._server_repo_clone_path = repo.working_tree_dir
        logging.debug("The cloned directory is: " +
                      self._server_repo_clone_path)

    def run_git_repo_tests(self):
        """Perform all repository-related tests.

        These are the tests that require a git repository to be given.

        Raises:
            :class:`.SettingsError`: From :meth:`.run_git_attributes_tests`
            :class:`.AssertionError`: From :meth:`.run_git_attributes_tests`

        """
        self.check_local_repo_active_branch()

        self.run_git_attributes_tests()
        # This should check local_repo and server_repo_path for attributes_dict

    def check_local_repo_active_branch(self):
        """This checks if the local repository's active branch is correct."""
        if not self._branch_name:
            return

        if not self._local_repo_path:
            # The branch_name may still be used when cloning the server repo.
            return

        logging.debug("Checking that local repository active branch is "
                      "correct.")

        current_active_branch = vcs_git.get_active_branch(
            vcs_git.init_repo(self._local_repo_path))

        logging.debug("Actual branch: " + current_active_branch)
        assert_equal(self._branch_name, current_active_branch)

    def run_git_attributes_tests(self):
        """Perform the git attributes tests.

        Raises:
            :class:`.SettingsError`: If no path is provided given an \
                attributes dictionary.
            :class:`.AssertionError`: If the test does not pass.

        """
        if not self._attributes_dict:
            return

        if not (self._server_repo_clone_path or self._local_repo_path):
            raise SettingsError("As an attributes dict has been provided, "
                                "either the local_repo_path or "
                                "server_repo_clone_path must be provided.")

        if self._server_repo_clone_path:
            logging.debug("Testing server clone's attributes.")
            return_value = vcs_git.check_git_attributes(
                    vcs_git.init_repo(self._server_repo_clone_path),
                    self._attributes_dict
            )
            assert_true(return_value)

        if self._local_repo_path:
            logging.debug("Testing local repo's attributes.")

            return_value = vcs_git.check_git_attributes(
                vcs_git.init_repo(self._local_repo_path),
                self._attributes_dict)
            assert_true(return_value)

    def run_comparison_tests(self):
        """Run the local path comparison tests.

        The repo_comp_method must be one of the following:
            - `local_comp`: Compares the two local paths.
                Paths are local_comp_path_one and local_comp_path_two.
            - `server_comp`: Compares a local path with the cloned server repo.
                Paths are local_comp_path_one and server_repo_clone_path.
            - `all_comp`: Compares all three paths against one another.
                Paths are local_comp_path_one, local_comp_path_two and
                server_repo_clone_path.

        Raises:
            :class:`.SettingsError`: From :func:`.check_if_repos_equal`.
            :class:`.SettingsError`: If the `repo_comp_method` has an \
                unexpected value.
            :class:`AssertionError`: If the test does not pass.
            :class:`subprocess.CalledProcessError`: From \
                :func:`.check_if_repos_equal`.

        """
        if not self._repo_comp_method:
            return

        if self._repo_comp_method == "local_comp":
            logging.debug("Performing 'local' comparison.")

            equal = check_if_repos_equal(self._local_comp_path_one,
                                         self._local_comp_path_two)
            assert_true(equal)

        elif self._repo_comp_method == "server_comp":
            logging.debug("Performing 'server' comparison.")

            equal = check_if_repos_equal(self._local_comp_path_one,
                                         self._server_repo_clone_path)
            assert_true(equal)

        elif self._repo_comp_method == "all_comp":
            logging.debug("Performing 'all' comparison.")

            equal_1 = check_if_repos_equal(self._local_comp_path_one,
                                           self._local_comp_path_two)
            equal_2 = check_if_repos_equal(self._local_comp_path_one,
                                           self._server_repo_clone_path)
            assert_true(equal_1 and equal_2)

        else:
            err_message = ("The repo_comp_method must be called using one of "
                           "the following:"
                           "\nlocal_comp, server_comp, all_comp."
                           "\nGot: {repo_comp_method:s}")
            raise SettingsError(err_message.format(
                    repo_comp_method=self._repo_comp_method)
            )

    def delete_cloned_server_repo(self):
        """Deletes the clone of the server repository.

        Raises:
            :class:`.TempdirError`: If the clone path is not a directory.
            :class:`.TempdirError`: If the clone path is not a git repository.

        """
        if not self._server_repo_clone_path:
            return

        logging.debug("About to delete temporary repository: " +
                      self._server_repo_clone_path)

        delete_temp_repo(self._server_repo_clone_path)

        self._server_repo_clone_path = ""


def generate_tests_from_dicts(script, test_settings):
    """Generator for the automatic construction of system tests.

    Args:
        script: The script to be tested.
        test_settings: The settings for each individual test.

    Raises:
        :class:`.SettingsError`: From :class:`.SystemTest`
        :class:`.TempdirError`: From :class:`.SystemTest`
        :class:`dls_ade.exceptions.VCSGitError`: From :class:`.SystemTest`
        :class:`AssertionError`: From :class:`.SystemTest`
        :class:`.GitRootDirError`: Indicates if GIT_ROOT_DIR is not set.

    """
    check_environment()

    for settings in test_settings:
        if 'script' in settings:
            script = settings.pop('script')

        description = settings.pop('description')

        system_test = SystemTest(script, description)
        system_test.load_settings(settings)

        yield system_test
