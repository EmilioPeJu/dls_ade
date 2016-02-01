import os
import shutil
import subprocess
import tarfile

import start_new_module_util

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
    '--area=ioc testB21/BL': "testB21",
    '--area=ioc testB22-BL-IOC-01': "testB22",
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

    # Swap instances of user login to USER_LOGIN_NAME
    start_new_module_util.find_and_replace_characters_in_folder(
            user_login,
            "USER_LOGIN_NAME",
            current_dir
    )
    os.chdir(cwd)
    tar_name = COMPARISON_FILES + ".tar.gz"

    # Tarball the resultant folder
    with tarfile.open(tar_name, "w:gz") as tar:
        for file_name in tar_list:
            tar.add(os.path.join(COMPARISON_FILES, file_name))

    shutil.rmtree(COMPARISON_FILES)
