from systems_testing import systems_testing as st
import tempfile
import os
import shutil

settings_list = [

    # Checkout one module from python area and check it is correctly cloned
    {
        'description': "checkout_module",

        'arguments': "-p dls_testpythonmod",

        'repo_comp_method': "server_comp",

        'local_comp_path_one': "dls_testpythonmod",

        'server_repo_path': "controlstest/python/dls_testpythonmod",

    },

    # Checkout one module from python area, change branch and check it is correctly cloned
    {
        'description': "checkout_and_change_branch",

        'arguments': "-p dls_testpythonmod -b bug-fix",

        'local_repo_path': "dls_testpythonmod",

        'branch_name': "bug-fix",

        'repo_comp_method': "server_comp",

        'local_comp_path_one': "dls_testpythonmod",

        'server_repo_path': "controlstest/python/dls_testpythonmod",

    },

    # Checkout everything from python area and check one of them is correctly cloned
    {
        'description': "checkout_all_area (Enter 'Y')",

        'arguments': "-p everything",

        'repo_comp_method': "server_comp",

        'local_comp_path_one': "dls_testpythonmod",

        'server_repo_path': "controlstest/python/dls_testpythonmod",

    },

    # # Checkout everything from ioc area/domain and check one of them is correctly cloned
    # {
    #     'description': "checkout_ioc_domain",
    #
    #     'arguments': "-i ...",
    #
    #     'repo_comp_method': "server_comp",
    #
    #     'local_comp_path_one': "BTEST/TS",
    #
    #     'server_repo_path': "controlstest/ioc/BTEST/TS",
    #
    # },

]


def test_generator():

    for test in st.generate_tests_from_dicts("dls-checkout-module.py",
                                             st.SystemsTest,
                                             settings_list):

        tempdir = tempfile.mkdtemp()
        cwd = os.getcwd()
        os.chdir(tempdir)

        yield test

        os.chdir(cwd)
        shutil.rmtree(tempdir)

