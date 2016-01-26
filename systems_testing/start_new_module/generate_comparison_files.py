import subprocess
import os
import tarfile

COMPARISON_FILES = "comparison_files"

SUBVERSION_SCRIPT_BASE = ("dls-python /dls_sw/prod/common/python/RHEL6-x86_64/"
                          "dls_scripts/3-21/prefix/lib/python2.7/"
                          "site-packages/dls_scripts-3.21-py2.7.egg/"
                          "py_scripts/dls_start_new_module.py -n ")


def call_start_new_module(call_args):

    call = (SUBVERSION_SCRIPT_BASE + call_args).split()

    subprocess.check_call(call)


# Expected module path in comment.
call_dict = {
    '--area=python dls_test_python_module': "dls_test_python_module",
    '--area=support test_support_module': "test_support_module",
    '--area=tools test_tools_module': "test_tools_module",
    '--area=ioc testB21/BL/01': "testB22",
    '--area=ioc testB22-BL-IOC-04': "testB22",
}

if __name__ == "__main__":

    os.mkdir(COMPARISON_FILES)

    cwd = os.getcwd()

    os.chdir(COMPARISON_FILES)
    tar_list = []

    for call_arg, folder in call_dict.iteritems():
        call_start_new_module(call_arg)
        tar_list.append(folder)

    user_login = os.getlogin()
    current_dir = os.getcwd()

    subprocess.check_call(("find " + current_dir + " -type f -exec sed -i s/" +
                          user_login + "/USER_LOGIN_NAME/g {} +").split())

    os.chdir(cwd)

    with tarfile.open("comparison_files.tar.gz", "w:gz") as tar:
        for file_name in tar_list:
            tar.add(os.path.join(COMPARISON_FILES, file_name))
