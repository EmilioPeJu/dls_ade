from systems_testing import systems_testing as st
import tempfile
import os
import shutil

settings_list = [

    # Checkout one module from support area and check it is correctly cloned
    {
        'description': "checkout_from_support",

        'arguments': "testsupportmod",

        'repo_comp_method': "server_comp",

        'local_comp_path_one': "testsupportmod",

        'server_repo_path': "controlstest/support/testsupportmod",

    },

    # Checkout one module from support area, change branch and check it is correctly cloned
    {
        'description': "checkout_from_support_and_change_branch",

        'arguments': "testsupportmod -b bug-fix",

        'local_repo_path': "testsupportmod",

        'branch_name': "bug-fix",

        'repo_comp_method': "server_comp",

        'local_comp_path_one': "testsupportmod",

        'server_repo_path': "controlstest/support/testsupportmod",

    },

    # Checkout one module from python area and check it is correctly cloned
    {
        'description': "checkout_from_python",

        'arguments': "-p dls_testpythonmod",

        'repo_comp_method': "server_comp",

        'local_comp_path_one': "dls_testpythonmod",

        'server_repo_path': "controlstest/python/dls_testpythonmod",

    },

    # # Checkout one module from python area, change branch and check it is correctly cloned
    # {
    #     'description': "checkout_from_python_and_change_branch",
    #
    #     'arguments': "-p dls_testpythonmod -b bug-fix",
    #
    #     'local_repo_path': "dls_testpythonmod",
    #
    #     'branch_name': "bug-fix",
    #
    #     'repo_comp_method': "server_comp",
    #
    #     'local_comp_path_one': "dls_testpythonmod",
    #
    #     'server_repo_path': "controlstest/python/dls_testpythonmod",
    #
    # },

    # Checkout one module from ioc area and check it is correctly cloned
    {
        'description': "checkout_from_ioc",

        'arguments': "-i BTEST/TS",

        'repo_comp_method': "server_comp",

        'local_comp_path_one': "BTEST/TS",

        'server_repo_path': "controlstest/ioc/BTEST/TS",

    },

    # # Checkout one module from ioc area, change branch and check it is correctly cloned
    # {
    #     'description': "checkout_from_ioc_and_change_branch",
    #
    #     'arguments': "-i BTEST/TS -b bug-fix",
    #
    #     'local_repo_path': "BTEST/TS",
    #
    #     'branch_name': "bug-fix",
    #
    #     'repo_comp_method': "server_comp",
    #
    #     'local_comp_path_one': "BTEST/TS",
    #
    #     'server_repo_path': "controlstest/ioc/BTEST/TS",
    #
    # },

    # Checkout everything from support area and check one of them is correctly cloned
    {
        'description': "checkout_all_support (Enter 'Y')",

        'arguments': "everything",

        'repo_comp_method': "server_comp",

        'local_comp_path_one': "testsupportmod",

        'server_repo_path': "controlstest/support/testsupportmod",

    },

    # Checkout everything from python area and check one of them is correctly cloned
    {
        'description': "checkout_all_python (Enter 'Y')",

        'arguments': "-p everything",

        'repo_comp_method': "server_comp",

        'local_comp_path_one': "dls_testpythonmod",

        'server_repo_path': "controlstest/python/dls_testpythonmod",

    },

    # Checkout everything from ioc area and check one of them is correctly cloned
    {
        'description': "checkout_all_ioc (Enter 'Y')",

        'arguments': "-i everything",

        'repo_comp_method': "server_comp",

        'local_comp_path_one': "BTEST/TS",

        'server_repo_path': "controlstest/ioc/BTEST/TS",

    },

]


def test_generator():

    tempdir = tempfile.mkdtemp()
    cwd = os.getcwd()
    os.chdir(tempdir)

    for test in st.generate_tests_from_dicts("dls-checkout-module.py",
                                             st.SystemsTest,
                                             settings_list):
        yield test

    os.chdir(cwd)
    shutil.rmtree(tempdir)

