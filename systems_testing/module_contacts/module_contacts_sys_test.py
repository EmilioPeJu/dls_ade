from systems_testing import systems_testing as st
import tempfile
import os
import shutil

settings_list = [

    # Check contacts of support module
    {
        'description': "check_support_contacts",

        'arguments': "testsupportmod",

        'std_out_compare_string': "Contact: lkz95212 (CC: mef65357)\n",

    },

    # Set contacts of support module
    {
        'description': "set_support_contacts",

        'arguments': "testsupportmod -c mef65357 -d lkz95212",

        'attributes_dict': {'module-contact': 'mef65357',
                            'module-cc': 'lkz95212'},

        'server_repo_path': "controlstest/support/testsupportmod",

    },

    # Set contacts of support module with CSV
    {
        'description': "set_support_contacts_CSV",

        'arguments': "testsupportmod -m module_contacts/test_csv.txt",

        'attributes_dict': {'module-contact': 'lkz95212',
                            'module-cc': 'mef65357'},

        'server_repo_path': "controlstest/support/testsupportmod",

    },

    # # Checkout one module from python area and check it is correctly cloned
    # {
    #     'description': "checkout_from_python",
    #
    #     'arguments': "-p dls_testpythonmod",
    #
    #     'repo_comp_method': "server_comp",
    #
    #     'local_comp_path_one': "dls_testpythonmod",
    #
    #     'server_repo_path': "controlstest/python/dls_testpythonmod",
    #
    # },
    #
    # # Checkout one module from ioc area and check it is correctly cloned
    # {
    #     'description': "checkout_from_ioc",
    #
    #     'arguments': "-i BTEST/TS",
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

    for test in st.generate_tests_from_dicts("dls-module-contacts.py",
                                             st.SystemsTest,
                                             settings_list):
        yield test

