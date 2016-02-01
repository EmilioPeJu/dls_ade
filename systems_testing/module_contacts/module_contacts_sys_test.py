import system_testing as st
import os
import shutil
from dls_ade import vcs_git

sys_test_dir_path = os.path.realpath(os.path.dirname(__file__))

csv_output = 'Module,Contact,Contact Name,CC,CC Name\n' \
             'Performing search for lkz95212...\n' \
             'Performing search for mef65357...\n' \
             'dls_testpythonmod,lkz95212,Martin Gaughran,mef65357,Gary Yendell\n'


settings_list = [

    # Check contacts of python module
    {
        'description': "check_contacts",

        'arguments': "-p dls_testpythonmod",

        'std_out_compare_string': "Contact: lkz95212 (CC: mef65357)\n",

    },

    # Check contacts of python module in CSV format
    {
        'description': "check_contacts_CSV",

        'arguments': "-p dls_testpythonmod -s",

        'std_out_compare_string': csv_output,

    },

    # Set contacts of python module
    {
        'description': "set_contacts",

        'arguments': "-p dls_testpythonmod -c mef65357 -d lkz95212",

        'attributes_dict': {'module-contact': 'mef65357',
                            'module-cc': 'lkz95212'},

        'server_repo_path': "controlstest/python/dls_testpythonmod",

    },

    # Set contact of python module
    {
        'description': "set_contact_not_cc",

        'arguments': "-p dls_testpythonmod -c mef65357",

        'attributes_dict': {'module-contact': 'mef65357',
                            'module-cc': 'mef65357'},

        'server_repo_path': "controlstest/python/dls_testpythonmod",

    },

    # Set cc of python module
    {
        'description': "set_cc_not_contact",

        'arguments': "-p dls_testpythonmod -d lkz95212",

        'attributes_dict': {'module-contact': 'lkz95212',
                            'module-cc': 'lkz95212'},

        'server_repo_path': "controlstest/python/dls_testpythonmod",

    },

    # Set contacts of python module with CSV
    {
        'description': "set_contacts_CSV",

        'arguments': "-p dls_testpythonmod -m python_test_csv.txt",

        'attributes_dict': {'module-contact': 'mef65357',
                            'module-cc': 'lkz95212'},

        'server_repo_path': "controlstest/python/dls_testpythonmod",

    },

    # Set contact of python module with CSV
    {
        'description': "set_contact_not_cc_CSV",

        'arguments': "-p dls_testpythonmod -m contact_python_test_csv.txt",

        'attributes_dict': {'module-contact': 'mef65357',
                            'module-cc': 'mef65357'},

        'server_repo_path': "controlstest/python/dls_testpythonmod",

    },

    # Set cc of python module with CSV
    {
        'description': "set_cc_not_contact_CSV",

        'arguments': "-p dls_testpythonmod -m cc_python_test_csv.txt",

        'attributes_dict': {'module-contact': 'lkz95212',
                            'module-cc': 'lkz95212'},

        'server_repo_path': "controlstest/python/dls_testpythonmod",

    },

]


def test_generator():

    cwd = os.getcwd()
    os.chdir(sys_test_dir_path)

    repo = vcs_git.temp_clone("controlstest/python/dls_testpythonmod")

    for test in st.generate_tests_from_dicts("dls-module-contacts.py",
                                             settings_list):
        yield test

        # Reset repo to initial state
        repo.git.push("origin", repo.active_branch, "-f")

    os.chdir(cwd)
    shutil.rmtree(repo.working_tree_dir)
