import system_testing as st
import os

support_list = "Modules in support:\n\n" \
               "mock_repo/support/testsupportmod\n"

ioc_list = "Modules in ioc:\n\n" \
           "mock_repo/ioc/BTEST2/TS\n" \
           "mock_repo/ioc/BTEST/BTEST-EB-IOC-03\n" \
           "mock_repo/ioc/BTEST/TS\n"

ioc_domain_list = "Modules in BTEST:\n\n" \
                  "mock_repo/ioc/BTEST/BTEST-EB-IOC-03\n" \
                  "mock_repo/ioc/BTEST/TS\n"

settings_list = [

    {
        'description': "list_modules_in_support_area",

        'std_out_compare_string': support_list,

    },

    {
        'description': "list_modules_in_ioc_area",

        'arguments': "-i",

        'std_out_compare_string': ioc_list,

    },

    {
        'description': "list_modules_in_domain_in_ioc_area",

        'arguments': "-i BTEST",

        'std_out_compare_string': ioc_domain_list,

    },

]

ORIGINAL_GIT_ROOT_DIR = os.getenv('GIT_ROOT_DIR')
NEW_GIT_ROOT_DIR = ""


def setup_module():
    """Change environment variable and module variables.

    """
    global NEW_GIT_ROOT_DIR

    # The environment variable is set for the use of the script being tested.
    NEW_GIT_ROOT_DIR = "controlstest/targetOS/mock_repo"
    os.environ['GIT_ROOT_DIR'] = NEW_GIT_ROOT_DIR

    # Set so SystemTest object can use the new variable.
    st.vcs_git.GIT_ROOT_DIR = NEW_GIT_ROOT_DIR
    st.vcs_git.pathf.GIT_ROOT_DIR = NEW_GIT_ROOT_DIR


def teardown_module():
    """Change environment variable and module variables to the original values.

    """
    os.environ['GIT_ROOT_DIR'] = ORIGINAL_GIT_ROOT_DIR
    st.vcs_git.GIT_ROOT_DIR = ORIGINAL_GIT_ROOT_DIR
    st.vcs_git.pathf.GIT_ROOT_DIR = ORIGINAL_GIT_ROOT_DIR


def test_generator():

    for test in st.generate_tests_from_dicts("dls-list-modules.py",
                                             settings_list):
        yield test

