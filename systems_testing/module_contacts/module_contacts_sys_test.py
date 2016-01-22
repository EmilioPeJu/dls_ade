from systems_testing import systems_testing as st
import tempfile
import os
import shutil

sys_test_dir_path = os.path.realpath(os.path.dirname(__file__))

support_csv_output = 'Module,Contact,Contact Name,CC,CC Name\n' \
                     'Performing search for lkz95212...\n' \
                     'Performing search for mef65357...\n' \
                     'testsupportmod,lkz95212,Martin Gaughran,mef65357,Gary Yendell\n'

python_csv_output = 'Module,Contact,Contact Name,CC,CC Name\n' \
                     'Performing search for lkz95212...\n' \
                     'Performing search for mef65357...\n' \
                     'dls_testpythonmod,lkz95212,Martin Gaughran,mef65357,Gary Yendell\n'

ioc_csv_output = 'Module,Contact,Contact Name,CC,CC Name\n' \
                     'Performing search for lkz95212...\n' \
                     'Performing search for mef65357...\n' \
                     'BTEST/TS,lkz95212,Martin Gaughran,mef65357,Gary Yendell\n'


settings_list = [

    # Check contacts of support module
    {
        'description': "check_support_contacts",

        'arguments': "testsupportmod",

        'std_out_compare_string': "Contact: lkz95212 (CC: mef65357)\n",

    },

    # Check contacts of support module in CSV format
    {
        'description': "check_support_contacts_CSV",

        'arguments': "testsupportmod -s",

        'std_out_compare_string': support_csv_output,

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

        'arguments': "testsupportmod -m test_csv.txt",

        'attributes_dict': {'module-contact': 'lkz95212',
                            'module-cc': 'mef65357'},

        'server_repo_path': "controlstest/support/testsupportmod",

    },

    # Check contacts of python module
    {
        'description': "check_python_contacts",

        'arguments': "-p dls_testpythonmod",

        'std_out_compare_string': "Contact: lkz95212 (CC: mef65357)\n",

    },

    # Check contacts of python module in CSV format
    {
        'description': "check_python_contacts_CSV",

        'arguments': "-p dls_testpythonmod -s",

        'std_out_compare_string': python_csv_output,

    },

    # Set contacts of python module
    {
        'description': "set_python_contacts",

        'arguments': "-p dls_testpythonmod -c mef65357 -d lkz95212",

        'attributes_dict': {'module-contact': 'mef65357',
                            'module-cc': 'lkz95212'},

        'server_repo_path': "controlstest/python/dls_testpythonmod",

    },

    # Set contacts of python module with CSV
    {
        'description': "set_python_contacts_CSV",

        'arguments': "-p dls_testpythonmod -m python_test_csv.txt",

        'attributes_dict': {'module-contact': 'lkz95212',
                            'module-cc': 'mef65357'},

        'server_repo_path': "controlstest/python/dls_testpythonmod",

    },

    # Check contacts of ioc module
    {
        'description': "check_ioc_contacts",

        'arguments': "-i BTEST/TS",

        'std_out_compare_string': "Contact: lkz95212 (CC: mef65357)\n",

    },

    # Check contacts of ioc module CSV format
    {
        'description': "check_ioc_contacts",

        'arguments': "-i BTEST/TS -s",

        'std_out_compare_string': ioc_csv_output,

    },

    # Set contacts of ioc module
    {
        'description': "set_ioc_contacts",

        'arguments': "-i BTEST/TS -c mef65357 -d lkz95212",

        'attributes_dict': {'module-contact': 'mef65357',
                            'module-cc': 'lkz95212'},

        'server_repo_path': "controlstest/ioc/BTEST/TS",

    },

    # Set contacts of ioc module with CSV
    {
        'description': "set_ioc_contacts_CSV",

        'arguments': "-i BTEST/TS -m ioc_test_csv.txt",

        'attributes_dict': {'module-contact': 'lkz95212',
                            'module-cc': 'mef65357'},

        'server_repo_path': "controlstest/ioc/BTEST/TS",

    },

]


def test_generator():

    cwd = os.getcwd()
    os.chdir(sys_test_dir_path)

    for test in st.generate_tests_from_dicts("dls-module-contacts.py",
                                             st.SystemsTest,
                                             settings_list):
        yield test

    os.chdir(cwd)
