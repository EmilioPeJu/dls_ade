#! /bin/env dls-python

import os
import subprocess
import tempfile
import shutil


class Error(Exception):
    pass


# Make sure env var is set.(PYTHONPATH must also be set, but cannot
# easily test it is correct)
try:
    os.environ['GIT_ROOT_DIR']
except KeyError:
    raise Error("GIT_ROOT_DIR must be set")

try:
    from dls_ade import vcs_git
except ImportError:
    vcs_git = None
    raise ImportError("PYTHONPATH must contain the dls_ade package")


def call_script(script_name, arguments=""):

    call_args = (script_name + " " + arguments).split()

    out, err = process_call(call_args)

    return out, err


def process_call(call_args):

    process = subprocess.Popen(call_args, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    out, err = process.communicate()

    return out, err


def check_stderr_for_exception(exception_type, exception_string, stderr):
    expected_string = "\n{exc_t:s}: {exc_s:s}\n"
    expected_string = expected_string.format(exc_t=exception_type,
                                             exc_s=exception_string)

    exception_found = stderr.endswith(expected_string)

    return exception_found


def is_server_repo(server_repo_path):

    return vcs_git.is_repo_path(server_repo_path)


def check_git_attrs_exist(local_repo_path, attributes_dict):
    # This is very fragile. When the additional functions located in other
    # branches are pulled in, this can use the much more useful getattr stuff
    # in vcs_git. Just keep the functionality the same!
    file_handle = open(os.path.join(local_repo_path, ".gitattributes"), "r")

    contents = file_handle.readlines()

    for attr in attributes_dict:
        attr_line = "* {key:s}={val:s}\n"
        attr_line = attr_line.format(key=attr, val=attributes_dict[attr])

        if attr_line not in contents:
            return False

    return True


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
