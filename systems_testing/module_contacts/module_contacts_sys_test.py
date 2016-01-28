import systems_testing as st
import os

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

    # Set one contact of python module
    {
        'description': "set_contact_not_cc",

        'arguments': "-p dls_testpythonmod -c mef65357",

        'attributes_dict': {'module-contact': 'mef65357',
                            'module-cc': 'mef65357'},

        'server_repo_path': "controlstest/python/dls_testpythonmod",

    },

    # Set contacts of python module
    {
        'description': "set_contacts",

        'arguments': "-p dls_testpythonmod -c mef65357 -d lkz95212",

        'attributes_dict': {'module-contact': 'mef65357',
                            'module-cc': 'lkz95212'},

        'server_repo_path': "controlstest/python/dls_testpythonmod",

    },

    # Set contacts of python module with CSV
    {
        'description': "set_contacts_CSV",

        'arguments': "-p dls_testpythonmod -m python_test_csv.txt",

        'attributes_dict': {'module-contact': 'lkz95212',
                            'module-cc': 'mef65357'},

        'server_repo_path': "controlstest/python/dls_testpythonmod",

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
