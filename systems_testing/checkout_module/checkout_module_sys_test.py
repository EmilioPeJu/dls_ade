from systems_testing import systems_testing as st
import tempfile
import os
import shutil

settings_list = [

    {
        'description': "checkout_from_support",

        'arguments': "testsupportmod",

        'repo_comp_method': "server_comp",

        'local_comp_path_one': "testsupportmod",

        'server_repo_path': "controlstest/support/testsupportmod",

    },

    {
        'description': "checkout_from_python",

        'arguments': "-p dls_testpythonmod",

        'repo_comp_method': "server_comp",

        'local_comp_path_one': "dls_testpythonmod",

        'server_repo_path': "controlstest/python/dls_testpythonmod",

    },

    {
        'description': "checkout_from_ioc",

        'arguments': "-i BTEST/TS",

        'repo_comp_method': "server_comp",

        'local_comp_path_one': "BTEST/TS",

        'server_repo_path': "controlstest/ioc/BTEST/TS",

    },

    {
        'description': "checkout_all_support",

        'repo_comp_method': "server_comp",

        'local_comp_path_one': "testsupportmod",

        'server_repo_path': "controlstest/support/testsupportmod",

    },

    {
        'description': "checkout_all_python",

        'arguments': "-p",

        'repo_comp_method': "server_comp",

        'local_comp_path_one': "dls_testpythonmod",

        'server_repo_path': "controlstest/python/dls_testpythonmod",

    },

    {
        'description': "checkout_all_ioc",

        'arguments': "-i",

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

