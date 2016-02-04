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

    {
        'description': "check_contacts",

        'arguments': "-p dls_testpythonmod",

        'std_out_compare_string': "Contact: lkz95212 (CC: mef65357)\n",

    },

    {
        'description': "check_contacts_with_CSV_format",

        'arguments': "-p dls_testpythonmod -s",

        'std_out_compare_string': csv_output,

    },

    {
        'description': "set_both_contacts",

        'arguments': "-p dls_testpythonmod3 -c up45 -d tmc43",

        'attributes_dict': {'module-contact': new_contact,
                            'module-cc': new_cc},

        'server_repo_path': "controlstest/python/dls_testpythonmod3",

    },

    {
        'description': "set_contact_leave_cc_unchanged",

        'arguments': "-p dls_testpythonmod3 -c up45",

        'attributes_dict': {'module-contact': new_contact,
                            'module-cc': default_cc},

        'server_repo_path': "controlstest/python/dls_testpythonmod3",

    },

    {
        'description': "set_cc_leave_contact_unchanged",

        'arguments': "-p dls_testpythonmod3 -d tmc43",

        'attributes_dict': {'module-contact': default_contact,
                            'module-cc': new_cc},

        'server_repo_path': "controlstest/python/dls_testpythonmod3",

    },

    {
        'description': "set_both_contacts_using_CSV_file",

        'arguments': "-p dls_testpythonmod3 -m python_test_csv.txt",

        'attributes_dict': {'module-contact': new_contact,
                            'module-cc': new_cc},

        'server_repo_path': "controlstest/python/dls_testpythonmod3",

    },

    {
        'description': "set_contact_using_CSV_file_leave_cc_unchanged",

        'arguments': "-p dls_testpythonmod3 -m contact_python_test_csv.txt",

        'attributes_dict': {'module-contact': new_contact,
                            'module-cc': default_cc},

        'server_repo_path': "controlstest/python/dls_testpythonmod3",

    },

    {
        'description': "set_cc_using_CSV_file_leave_contact_unchanged",

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
