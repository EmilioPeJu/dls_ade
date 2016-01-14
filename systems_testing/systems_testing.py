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


def process_call(call_args):

    process = subprocess.Popen(call_args, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    std_out, std_err = process.communicate()

    return_code = process.returncode

    return std_out, std_err, return_code


def is_server_repo(server_repo_path):

    return vcs_git.is_repo_path(server_repo_path)


def get_local_temp_clone(server_repo_path):

    repo = vcs_git.temp_clone(server_repo_path)

    tempdir = repo.working_tree_dir

    return tempdir


def delete_temp_repo(local_repo_path):

    if not os.path.realpath(local_repo_path).startswith(tempfile.gettempdir()):
        raise Error("This function will only delete a temporary folder.")

    # Replace with more appropriate vcs_git function - it is currently on
    # start_new_module!
    if not vcs_git.is_git_root_dir(local_repo_path):
        raise Error("This function will only delete a git repository.")

    shutil.rmtree(local_repo_path)


class SystemsTest(object):
    def __init__(self, script):
        self.script = script
        self.std_out = ""
        self.std_err = ""
        self.return_code = None
        self.local_repo_path = ""
        self.description = ""

        self.test_name = ""
        self.exception_type = ""
        self.exception_string = ""
        self.std_out_compare_method = "string_comp"
        self.std_out_compare_string = ""
        self.arguments = ""
        self.attributes_dict = {}
        self.server_repo_path = ""

        self.settings_list = [  # List of valid variables to update.
            'test_name',
            'exception_type',
            'exception_string',
            'std_out_compare_method',
            'std_out_compare_string',
            'arguments',
            'attributes_dict',
            'server_repo_path'
        ]

    def load_settings(self, settings):
        self.__dict__.update({key: value for (key, value) in settings.items()
                              if key in self.settings_list})
        if not self.test_name:
            raise Error("The test name must be set.")

        self.description = self.test_name

    def setup(self):
        # Add anything that needs to be completed before class is run.
        pass

    def call_script(self):
        # Call the script and return the output and error
        call_args = (self.script + " " + self.arguments).split()

        self.std_out, self.std_err, self.return_code = process_call(call_args)

    def check_std_err_for_exception(self):

        if not self.exception_type or not self.exception_string:
            if not self.exception_type and not self.exception_string:
                return
            raise Error("Both exception_type and exception_string must "
                        "be provided.")

        if self.return_code == 0:
            # Function must have succeeded:
            raise Error("Function succeeded, no exception to compare to.")


        expected_string = "\n{exc_t:s}: {exc_s:s}\n"
        expected_string = expected_string.format(exc_t=self.exception_type,
                                                 exc_s=self.exception_string)

        assert_true(self.std_err.endswith(expected_string))

    def compare_std_out_to_string(self):
        if not self.std_out_compare_string:
            return

        assert_equal(self.std_out, self.std_out_compare_string)

    def compare_std_out_manually(self):
        print("The following contents is the direct output of the script:\n")
        print(self.std_out)
        response = raw_input("Does this match the expected output? (y/n)")

        assert_true(response.lower() == "y")

    def perform_local_repo_tests(self):
        if not self.server_repo_path:
            return

        if not is_server_repo(self.server_repo_path):
            raise Error("The server_repo_path must point to an existing repo.")

        self.local_repo_path = get_local_temp_clone(self.server_repo_path)

        self.check_git_attributes_exist()

        delete_temp_repo(self.local_repo_path)
        self.local_repo_path = ""

    def check_git_attributes_exist(self):
        # This is very fragile. When the additional functions located in other
        # branches are pulled in, this can use the much more useful getattr
        # stuff in vcs_git. Just keep the functionality the same!
        if not self.attributes_dict:
            return

        file_handle = open(os.path.join(self.local_repo_path,
                                        ".gitattributes"), "r")

        contents = file_handle.readlines()

        for attr in self.attributes_dict:
            attr_line = "* {key:s}={val:s}\n"
            attr_line = attr_line.format(key=attr,
                                         val=self.attributes_dict[attr])

            if attr_line not in contents:
                return False

        return True

    def perform_tests(self):

        self.check_std_err_for_exception()

        if self.std_out_compare_method == "string_comp":
            self.compare_std_out_to_string()
        elif self.std_out_compare_method == "manual_comp":
            self.compare_std_out_manually()

        self.perform_local_repo_tests()

    def __call__(self):
        raise Error("Remove when script fully tested")
        self.setup()
        self.call_script()
        self.perform_tests()


def generate_tests_from_dicts(script, systems_test_cls, test_settings):

    for settings in test_settings:
        systems_test = systems_test_cls(script)
        systems_test.load_settings(settings)
        yield systems_test
