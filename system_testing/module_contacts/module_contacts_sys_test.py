import system_testing as st
import os
import shutil
from dls_ade import vcs_git

GIT_SSH_ROOT = "ssh://dascgitolite@dasc-git.diamond.ac.uk/"

sys_test_dir_path = os.path.realpath(os.path.dirname(__file__))

csv_output = 'Module,Contact,Contact Name,CC,CC Name\n' \
             'Performing search for lkz95212...\n' \
             'Performing search for mef65357...\n' \
             'dls_testpythonmod,lkz95212,Martin Gaughran,mef65357,Gary Yendell\n'

default_contact = 'lkz95212'
default_cc = 'mef65357'
new_contact = 'up45'
new_cc = 'tmc43'

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

        'arguments': "-p dls_testpythonmod3 -c up45 -d tmc43",

        'attributes_dict': {'module-contact': new_contact,
                            'module-cc': new_cc},

        'server_repo_path': "controlstest/python/dls_testpythonmod3",

    },

    # Set contact of python module
    {
        'description': "set_contact_not_cc",

        'arguments': "-p dls_testpythonmod3 -c up45",

        'attributes_dict': {'module-contact': new_contact,
                            'module-cc': default_cc},

        'server_repo_path': "controlstest/python/dls_testpythonmod3",

    },

    # Set cc of python module
    {
        'description': "set_cc_not_contact",

        'arguments': "-p dls_testpythonmod3 -d tmc43",

        'attributes_dict': {'module-contact': default_contact,
                            'module-cc': new_cc},

        'server_repo_path': "controlstest/python/dls_testpythonmod3",

    },

    # Set contacts of python module with CSV
    {
        'description': "set_contacts_CSV",

        'arguments': "-p dls_testpythonmod3 -m python_test_csv.txt",

        'attributes_dict': {'module-contact': new_contact,
                            'module-cc': new_cc},

        'server_repo_path': "controlstest/python/dls_testpythonmod3",

    },

    # Set contact of python module with CSV
    {
        'description': "set_contact_not_cc_CSV",

        'arguments': "-p dls_testpythonmod3 -m contact_python_test_csv.txt",

        'attributes_dict': {'module-contact': new_contact,
                            'module-cc': default_cc},

        'server_repo_path': "controlstest/python/dls_testpythonmod3",

    },

    # Set cc of python module with CSV
    {
        'description': "set_cc_not_contact_CSV",

        'arguments': "-p dls_testpythonmod3 -m cc_python_test_csv.txt",

        'attributes_dict': {'module-contact': default_contact,
                            'module-cc': new_cc},

        'server_repo_path': "controlstest/python/dls_testpythonmod3",

    },

]


def test_generator():

    cwd = os.getcwd()
    os.chdir(sys_test_dir_path)

    repo = vcs_git.temp_clone("controlstest/python/dls_testpythonmod")
    repo.create_remote("dummy_repo",
                       os.path.join(GIT_SSH_ROOT,
                                    "controlstest/python/dls_testpythonmod3"))

    for test in st.generate_tests_from_dicts("dls-module-contacts.py",
                                             settings_list):
        yield test

        # Reset repo to initial state
        repo.git.push("dummy_repo", repo.active_branch, "-f")

    os.chdir(cwd)
    shutil.rmtree(repo.working_tree_dir)
