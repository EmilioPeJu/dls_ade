import subprocess
import os

SUBVERSION_SCRIPT_BASE = ("dls-python /dls_sw/prod/common/python/RHEL6-x86_64/"
                          "dls_scripts/3-21/prefix/lib/python2.7/"
                          "site-packages/dls_scripts-3.21-py2.7.egg/"
                          "py_scripts/dls_start_new_module.py -n ")


def call_start_new_module(call_args):

    call = (SUBVERSION_SCRIPT_BASE + call_args).split()

    subprocess.check_call(call)


# Expected module path in comment.
call_list = [
    "--area=python dls_test_python_module",  # dls_test_python_module
    "--area=support test_support_module",  # test_support_module
    "--area=tools test_tools_module",  # test_tools_module
    "--area=ioc testB22/BL/01",  # testB22/BL
    "--area=ioc testB22-BL-IOC-04",  # testB22-BL-IOC-04
]

if __name__ == "__main__":

    for call_arg in call_list:
        call_start_new_module(call_arg)

    user_login = os.getlogin()
    current_dir = os.getcwd()

    subprocess.check_call("find " + current_dir + " -type f -exec sed -i 's/" +
                          user_login + "/USER_LOGIN_NAME/g' {} +")

