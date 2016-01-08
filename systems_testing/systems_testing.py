#! /bin/env dls-python

import subprocess
import imp

vcs_git = None


def setup_testing_environment(path):
    pass
    # set GIT_ROOT_DIR to "controlstest"
    # Include path at beginning of PATH

    global vcs_git
    vcs_git = imp.load_source('vcs_git', 'vcs_git.py')  # Requires PATH set


def call_script(script_name, arguments=""):

    call_args = (script_name + " " + arguments).split()

    out = ""
    err = ""

    process = subprocess.Popen(call_args, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    out, err = process.communicate()

    return out, err


def check_stderror_for_exception(exception_type, exception_string, stderr):
    expected_string = "\n{exc_t:s}: {exc_s:s}\n"
    expected_string = expected_string.format(exc_t=exception_type,
                                             exc_s=exception_string)

    exception_found = stderr.endswith(expected_string)

    return exception_found


def check_repository(server_repo_path):

    if not vcs_git:
        raise Exception("The testing environment must be set up first.")

    if not vcs_git.is_repo_path(server_repo_path):
        raise Exception("The given repository does not exist.")

    # clone repository to temporary dir
    # allow user to access file (hold open until user presses enter key?)
    # close and delete the temporary dir


if __name__ == "__main__":
    stdout, stderr = call_script("./test.py")
    type = "test2.MyError"
    string = "This is the expected message\nfor the test\ning"

    print(check_stderror_for_exception(type, string, stderr))
