#! /bin/env dls-python
from __future__ import print_function
import os
import subprocess
import tempfile
import shutil
from pkg_resources import require
require('nose')
from nose.tools import assert_equal, assert_true, assert_false


# Make sure env var is set.(PYTHONPATH must also be set, but cannot
# easily test it is correct)
try:
    os.environ['GIT_ROOT_DIR']
except KeyError:
    raise EnvironmentError("GIT_ROOT_DIR must be set")

try:
    from dls_ade import vcs_git
except ImportError:
    vcs_git = None
    raise ImportError("PYTHONPATH must contain the dls_ade package")


class Error(Exception):
    pass


def get_input(message):
    return raw_input(message)


def is_server_repo(server_repo_path):

    return vcs_git.is_repo_path(server_repo_path)


def get_local_temp_clone(server_repo_path):

    repo = vcs_git.temp_clone(server_repo_path)

    tempdir = repo.working_tree_dir

    return tempdir


def delete_temp_repo(local_repo_path):

    if not os.path.realpath(local_repo_path).startswith(tempfile.gettempdir()):
        err_message = ("{local_repo_path:s} is not a temporary folder, cannot "
                       "delete.")
        raise Error(err_message.format(local_repo_path=local_repo_path))

    if not vcs_git.is_git_root_dir(local_repo_path):
        err_message = ("{local_repo_path:s} is not a git root directory, "
                       "cannot delete.")
        raise Error(err_message.format(local_repo_path=local_repo_path))

    shutil.rmtree(local_repo_path)


# TODO(Martin) Add testing for initial exception
def check_if_folders_equal(path_1, path_2):
    # Returns True if filesystems equal, False otherwise.
    if not (path_1 and path_2):
        err_message = ("Two paths must be given to compare folders.\n"
                       "path 1: {path_1:s}, path 2: {path_2:s}.")
        raise Error(err_message.format(path_1=path_1, path_2=path_2))

    command_format = "diff -rq {path1:s} {path2:s}"
    call_args = command_format.format(path1=path_1, path2=path_2).split()

    out = subprocess.check_output(call_args)

    return not out


class SystemsTest(object):
    def __init__(self, script, description):
        self.script = script
        self.description = description

        self.std_out = ""
        self.std_err = ""
        self.return_code = None

        # Used for attribute checking and comparisons
        self.server_clone_path = ""

        self.exception_type = ""
        self.exception_string = ""
        self.std_out_compare_method = ""  # Set to: manual_comp or string_comp
        self.std_out_compare_string = ""
        self.arguments = ""
        self.attributes_dict = {}

        # Used for attribute checking
        self.local_repo_path = ""

        # Used for comparisons
        self.repo_comp_method = ""  # Set to: local_comp, server_comp, all_comp

        self.local_comp_path_one = ""
        self.local_comp_path_two = ""

        # Used for attribute checking and comparisons
        self.server_repo_path = ""

        self.settings_list = [  # List of valid variables to update.
            'exception_type',
            'exception_string',
            'std_out_compare_method',
            'std_out_compare_string',
            'arguments',
            'attributes_dict',
            'server_repo_path'
            'local_repo_path'
            'repo_comp_method'
            'local_comp_path_one'
            'local_comp_path_two'
        ]

    def load_settings(self, settings):
        self.__dict__.update({key: value for (key, value) in settings.items()
                              if key in self.settings_list})

    def setup(self):
        # Add anything that needs to be completed before class is run.
        pass

    def call_script(self):
        # Call the script and return the output and error
        call_args = (self.script + " " + self.arguments).split()

        # It appears that we cannot use 'higher-level' subprocess functions,
        # eg. check_output here. This is because stderr cannot be obtained
        # separately to stdout in these functions.
        process = subprocess.Popen(call_args, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

        self.std_out, self.std_err = process.communicate()

        self.return_code = process.returncode

    def check_std_err_for_exception(self):

        if not self.exception_type or not self.exception_string:
            if not self.exception_type and not self.exception_string:
                return
            raise Error("Both exception_type and exception_string must "
                        "be provided.")

        if self.return_code == 0:
            # Function must have succeeded:
            raise Error("Function succeeded, no exception raised.")

        expected_string = "\n{exc_t:s}: {exc_s:s}\n"
        expected_string = expected_string.format(exc_t=self.exception_type,
                                                 exc_s=self.exception_string)

        assert_true(self.std_err.endswith(expected_string))

    def compare_std_out_to_string(self):
        if not self.std_out_compare_string:
            raise Error("A std_out comparison string must be provided.")

        assert_equal(self.std_out, self.std_out_compare_string)

    def compare_std_out_manually(self):
        print("The following content is the direct output of the script:\n")
        print(self.std_out)
        response = get_input("Does this match the expected output? (y/n)")

        assert_true(response.lower() == "y")

    # TODO(Martin) Docs and unit tests
    def check_remote_repo_exists(self):
        if not self.server_repo_path:
            return

        assert_true(is_server_repo(self.server_repo_path))

    # TODO(Martin) Docs and unit tests
    def clone_server_repo(self):
        repo = vcs_git.temp_clone(self.server_repo_path)
        self.server_clone_path = repo.working_tree_dir

    # TODO(Martin) Docs and unit tests
    def run_git_attributes_tests(self):
        if not self.attributes_dict:
            return

        if self.server_clone_path:
            return_value = vcs_git.check_git_attributes(self.server_clone_path,
                                                        self.attributes_dict)
            assert_true(return_value)

        if self.local_repo_path:
            return_value = vcs_git.check_git_attributes(self.local_repo_path,
                                                        self.attributes_dict)
            assert_true(return_value)

    # TODO(Martin) Docs and unit tests, put bottom error in docstring
    def run_comparison_tests(self):
        if not self.repo_comp_method:
            return

        if self.repo_comp_method == "local_comp":
            equal = check_if_folders_equal(self.local_comp_path_one,
                                           self.local_comp_path_two)
            assert_true(equal)

        elif self.repo_comp_method == "server_comp":
            equal = check_if_folders_equal(self.local_comp_path_one,
                                           self.server_clone_path)
            assert_true(equal)

        elif self.repo_comp_method == "all_comp":
            equal_1 = check_if_folders_equal(self.local_comp_path_one,
                                             self.local_comp_path_two)
            equal_2 = check_if_folders_equal(self.local_comp_path_two,
                                             self.server_clone_path)
            assert_true(equal_1 and equal_2)

        else:
            raise Error("The repo_comp_method key must have a value of:\n"
                        "local_comp: compares the two local paths, named with "
                        "local_comp_path_one and local_comp_path_two.\n"
                        "server_comp: compares local_comp_path_one with the "
                        "repo pointed to by server_repo_path.\n"
                        "all_comp: compares all three paths against one "
                        "another.")

    # TODO(Martin) docs and unit tests
    def check_std_out_and_exceptions(self):
        self.check_std_err_for_exception()

        if self.std_out_compare_method == "string_comp":
            self.compare_std_out_to_string()
        elif self.std_out_compare_method == "manual_comp":
            self.compare_std_out_manually()

    # TODO(Martin) docs and unit tests
    def perform_tests(self):

        self.check_std_out_and_exceptions()

        self.check_remote_repo_exists()
        # Skips if server_repo_path does not exist

        self.clone_server_repo()
        # And adds path to server_clone_path. Skips if server_repo_path does
        # not exist

        self.run_git_attributes_tests()
        # This should check local_repo and server_repo_path for attributes_dict

        self.run_comparison_tests()
        # Filesystem equality checks

    def __call__(self):
        raise Error("Remove when script fully tested")
        self.setup()
        self.call_script()
        self.perform_tests()


def generate_tests_from_dicts(script, systems_test_cls, test_settings):

    for settings in test_settings:
        if 'script' in settings:
            script = settings.pop('script')
        description = settings.pop('description')
        systems_test = systems_test_cls(script, description)
        systems_test.load_settings(settings)
        yield systems_test
