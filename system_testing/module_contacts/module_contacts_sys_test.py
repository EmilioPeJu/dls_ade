import system_testing as st
import os

sys_test_dir_path = os.path.realpath(os.path.dirname(__file__))

csv_output = 'Performing search for lkz95212...\n' \
             'Performing search for mef65357...\n' \
             'Module,Contact,Contact Name,CC,CC Name\n' \
             'dls_testpythonmod,lkz95212,Martin Gaughran,mef65357,Gary Yendell\n'

default_contact = 'lkz95212'
default_cc = 'mef65357'
new_contact = 'up45'
new_cc = 'tmc43'

settings_list = [

    {
        'description': "print_module_contacts",

        'arguments': "-p dls_testpythonmod",

        'std_out_compare_string': "Contact: lkz95212 (CC: mef65357)\n",

    },

    {
        'description': "print_module_contacts_in_CSV_format",

        'arguments': "-p dls_testpythonmod -s",

        'std_out_compare_string': csv_output,

    },

    {
        'description': "set_both_contacts",

        'arguments': "-p dls_testpythonmod3 -c up45 -d tmc43",

        'attributes_dict': {'module-contact': new_contact,
                            'module-cc': new_cc},

        'default_server_repo_path': "controlstest/python/dls_testpythonmod",

        'server_repo_path': "controlstest/python/dls_testpythonmod3",

    },

    {
        'description': "set_contact_leaving_cc_unchanged",

        'arguments': "-p dls_testpythonmod3 -c up45",

        'attributes_dict': {'module-contact': new_contact,
                            'module-cc': default_cc},

        'default_server_repo_path': "controlstest/python/dls_testpythonmod",

        'server_repo_path': "controlstest/python/dls_testpythonmod3",

    },

    {
        'description': "set_cc_leaving_contact_unchanged",

        'arguments': "-p dls_testpythonmod3 -d tmc43",

        'attributes_dict': {'module-contact': default_contact,
                            'module-cc': new_cc},

        'default_server_repo_path': "controlstest/python/dls_testpythonmod",

        'server_repo_path': "controlstest/python/dls_testpythonmod3",

    },

    {
        'description': "set_both_contacts_using_CSV_file",

        'arguments': "-p dls_testpythonmod3 -m python_test_csv.txt",

        'attributes_dict': {'module-contact': new_contact,
                            'module-cc': new_cc},

        'default_server_repo_path': "controlstest/python/dls_testpythonmod",

        'server_repo_path': "controlstest/python/dls_testpythonmod3",

    },

    {
        'description': "set_contact_using_CSV_file_leaving_cc_unchanged",

        'arguments': "-p dls_testpythonmod3 -m contact_python_test_csv.txt",

        'attributes_dict': {'module-contact': new_contact,
                            'module-cc': default_cc},

        'default_server_repo_path': "controlstest/python/dls_testpythonmod",

        'server_repo_path': "controlstest/python/dls_testpythonmod3",

    },

    {
        'description': "set_cc_using_CSV_file_leaving_contact_unchanged",

        'arguments': "-p dls_testpythonmod3 -m cc_python_test_csv.txt",

        'attributes_dict': {'module-contact': default_contact,
                            'module-cc': new_cc},

        'default_server_repo_path': "controlstest/python/dls_testpythonmod",

        'server_repo_path': "controlstest/python/dls_testpythonmod3",

    },

]


def test_generator():

    cwd = os.getcwd()
    os.chdir(sys_test_dir_path)

    for test in st.generate_tests_from_dicts("dls-module-contacts.py",
                                             settings_list):

        yield test

    os.chdir(cwd)
