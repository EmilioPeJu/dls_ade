from pkg_resources import require
require('nose')

import systems_testing as st
import os
import shutil
import tempfile
import start_new_module_util as snm_util

COMPARISON_FILES = "comparison_files"

printed_messages = {
    'python':
        ("\nPlease add your python files to the dls_test_python_module"
         "\ndirectory and edit dls_test_python_module/setup.py appropriately."
         "\n"),

    'tools':
        ("\nPlease add your patch files to the test_tools_module\ndirectory "
         "and edit test_tools_module/build script appropriately.\n"),

    'support':
        ("\nPlease now edit test_support_module/configure/RELEASE to put in "
         "correct paths for dependencies.\nYou can also add dependencies to "
         "test_support_module/test_support_moduleApp/src/Makefile"
         "\nand test_support_module/test_support_moduleApp/Db/Makefile if "
         "appropriate.\n"),

    'IOC-BL-slash':
        ("\nPlease now edit testB21/BL/configure/RELEASE to put in correct "
         "paths for the ioc's other technical areas and path to scripts."
         "\nAlso edit testB21/BL/testB21App/src/Makefile to add all database "
         "files from these technical areas.\nAn example set of screens has "
         "been placed in testB21/BL/testB21App/opi/edl. Please modify these."
         "\n"),

    'IOC-BL-dash':
        ("\nPlease now edit testB22/testB22-BL-IOC-01/configure/RELEASE to put"
         " in correct paths for the ioc's other technical areas and path to "
         "scripts.\nAlso edit "
         "testB22/testB22-BL-IOC-01/testB22-BL-IOC-01App/src/Makefile to add "
         "all database files from these technical areas.\nAn example set of "
         "screens has been placed in "
         "testB22/testB22-BL-IOC-01/testB22-BL-IOC-01App/opi/edl. Please "
         "modify these.\n"),

    'IOC-B01':
        ("\nPlease now edit testB01/TS/configure/RELEASE to put in correct "
         "paths for dependencies.\nYou can also add dependencies to "
         "testB01/TS/testB01-TS-IOC-01App/src/Makefile\nand "
         "testB01/TS/testB01-TS-IOC-01App/Db/Makefile if appropriate.\n"),

    'IOC-B02':
        ("\nPlease now edit testB02/TS/configure/RELEASE to put in correct "
         "paths for dependencies.\nYou can also add dependencies to "
         "testB02/TS/testB02-TS-IOC-03App/src/Makefile\nand "
         "testB02/TS/testB02-TS-IOC-03App/Db/Makefile if appropriate.\n"),

    'IOC-B03':
        ("\nPlease now edit testB03/testB03-TS-IOC-01/configure/RELEASE to put "
         "in correct paths for dependencies.\nYou can also add dependencies "
         "to testB03/testB03-TS-IOC-01/testB03-TS-IOC-01App/src/Makefile\nand "
         "testB03/testB03-TS-IOC-01/testB03-TS-IOC-01App/Db/Makefile if "
         "appropriate.\n"),

    'IOC-B04':
        ("\nPlease now edit testB04/testB04-TS-IOC-04/configure/RELEASE to put "
         "in correct paths for dependencies.\nYou can also add dependencies "
         "to testB04/testB04-TS-IOC-04/testB04-TS-IOC-04App/src/Makefile\nand "
         "testB04/testB04-TS-IOC-04/testB04-TS-IOC-04App/Db/Makefile if "
         "appropriate.\n"),

    'IOC-B05':
        ("\nPlease now edit testB05/testB05-TS-IOC-02/configure/RELEASE to put "
         "in correct paths for dependencies.\nYou can also add dependencies "
         "to testB05/testB05-TS-IOC-02/testB05-TS-IOC-02App/src/Makefile\nand "
         "testB05/testB05-TS-IOC-02/testB05-TS-IOC-02App/Db/Makefile if "
         "appropriate.\n"),

    'IOC-B06':
        ("\nPlease now edit testB06/TS/configure/RELEASE to put "
         "in correct paths for dependencies.\nYou can also add dependencies "
         "to testB06/TS/testB06-TS-IOC-02App/src/Makefile\nand "
         "testB06/TS/testB06-TS-IOC-02App/Db/Makefile if "
         "appropriate.\n"),
}

settings_list = [
    {
        'description': "test_local_python_module_created_with_correct_files",

        'arguments': "-p dls_test_python_module",

        'std_out_ends_with_string': printed_messages['python'],

        'attributes_dict': {'module-contact': os.getlogin()},

        'local_repo_path': "dls_test_python_module",

        'repo_comp_method': "local_comp",

        'local_comp_path_one': "dls_test_python_module",

        'local_comp_path_two': "dls_test_python_module",
    },

    {
        'description': "test_local_tools_module_created_with_correct_files",

        'arguments': "-a tools test_tools_module",

        'std_out_ends_with_string': printed_messages['tools'],

        'attributes_dict': {'module-contact': os.getlogin()},

        'local_repo_path': "test_tools_module",

        'repo_comp_method': "local_comp",

        'local_comp_path_one': "test_tools_module",

        'local_comp_path_two': "test_tools_module",
    },

    {
        'description': "test_local_support_module_created_with_correct_files",

        'arguments': "-a support test_support_module",

        'std_out_ends_with_string': printed_messages['support'],

        'attributes_dict': {'module-contact': os.getlogin()},

        'local_repo_path': "test_support_module",

        'repo_comp_method': "local_comp",

        'local_comp_path_one': "test_support_module",

        'local_comp_path_two': "test_support_module",
    },

    {
        'description': "test_local_IOC_BL_slash_form_module_created_with_correct_files",

        'arguments': "-i testB21/BL",

        'std_out_ends_with_string': printed_messages['IOC-BL-slash'],

        'attributes_dict': {'module-contact': os.getlogin()},

        'local_repo_path': "testB21/BL",

        'repo_comp_method': "local_comp",

        'local_comp_path_one': "testB21/BL",

        'local_comp_path_two': "testB21/BL",
    },

    {
        'description': "test_local_IOC_BL_dash_form_module_created_with_correct_files",

        'arguments': "-i testB22-BL-IOC-01",

        'std_out_ends_with_string': printed_messages['IOC-BL-dash'],

        'attributes_dict': {'module-contact': os.getlogin()},

        'local_repo_path': "testB22/testB22-BL-IOC-01",

        'repo_comp_method': "local_comp",

        'local_comp_path_one': "testB22/testB22-BL-IOC-01",

        'local_comp_path_two': "testB22/testB22-BL-IOC-01",
    },

    {
        'description': "test_local_IOC_module_slash_form_without_ioc_number_created_with_correct_ioc_number_and_module_name_and_files",

        'arguments': "-i testB01/TS",

        'input': "",

        'std_out_ends_with_string': printed_messages['IOC-B01'],

        'attributes_dict': {'module-contact': os.getlogin()},

        'local_repo_path': "testB01/TS",

        'repo_comp_method': "local_comp",

        'local_comp_path_one': "testB01/TS",

        'local_comp_path_two': "testB01/TS",
    },

    {
        'description': "test_local_IOC_module_slash_form_with_ioc_number_created_with_correct_ioc_number_and_module_name_and_files",

        'arguments': "-i testB02/TS/03",

        'input': "",

        'std_out_ends_with_string': printed_messages['IOC-B02'],

        'attributes_dict': {'module-contact': os.getlogin()},

        'local_repo_path': "testB02/TS",

        'repo_comp_method': "local_comp",

        'local_comp_path_one': "testB02/TS",

        'local_comp_path_two': "testB02/TS",
    },

    {
        'description': "test_local_IOC_module_slash_form_with_no_ioc_number_and_fullname_created_with_correct_module_name_and_files",

        'arguments': "-i testB03/TS/ --fullname",

        'input': "",

        'std_out_ends_with_string': printed_messages['IOC-B03'],

        'attributes_dict': {'module-contact': os.getlogin()},

        'local_repo_path': "testB03/testB03-TS-IOC-01",

        'repo_comp_method': "local_comp",

        'local_comp_path_one': "testB03/testB03-TS-IOC-01",

        'local_comp_path_two': "testB03/testB03-TS-IOC-01",
    },

    {
        'description': "test_local_IOC_module_slash_form_with_ioc_number_and_fullname_created_with_correct_module_name_and_files",

        'arguments': "-i testB04/TS/04 --fullname",

        'input': "",

        'std_out_ends_with_string': printed_messages['IOC-B04'],

        'attributes_dict': {'module-contact': os.getlogin()},

        'local_repo_path': "testB04/testB04-TS-IOC-04",

        'repo_comp_method': "local_comp",

        'local_comp_path_one': "testB04/testB04-TS-IOC-04",

        'local_comp_path_two': "testB04/testB04-TS-IOC-04",
    },

    {
        'description': "test_local_IOC_module_dash_form_created_with_correct_module_name_and_files",

        'arguments': "-i testB05-TS-IOC-02 --fullname",

        'input': "",

        'std_out_ends_with_string': printed_messages['IOC-B05'],

        'attributes_dict': {'module-contact': os.getlogin()},

        'local_repo_path': "testB05/testB05-TS-IOC-02",

        'repo_comp_method': "local_comp",

        'local_comp_path_one': "testB05/testB05-TS-IOC-02",

        'local_comp_path_two': "testB05/testB05-TS-IOC-02",
    },

    {
        'description': "test_local_IOC_module_slash_form_that_needs_to_add_app_created_with_correct_module_name_and_app_name_and_files",

        'arguments': "-i testB06/TS/02",

        'input': "",

        'std_out_ends_with_string': printed_messages['IOC-B06'],

        'attributes_dict': {'module-contact': os.getlogin()},

        'local_repo_path': "testB06/TS",

        'repo_comp_method': "local_comp",

        'local_comp_path_one': "testB06/TS",

        'local_comp_path_two': "testB06/TS",
    },
]


def test_generator_local():

        # Search the COMPARISON_FILES folder for folders to compare with.
        for settings_dict in settings_list:
            comparison_path = settings_dict['local_comp_path_two']
            settings_dict['local_comp_path_two'] = os.path.join(
                    COMPARISON_FILES,
                    comparison_path
            )

        tempdir = tempfile.mkdtemp()
        cwd = os.getcwd()

        # Unpack tar in tempdir and change to match currently logged in user.
        snm_util.untar_comparison_files_and_insert_user_login(
                COMPARISON_FILES + ".tar.gz", tempdir
        )

        os.chdir(tempdir)

        for test in st.generate_tests_from_dicts("dls-start-new-module.py -n",
                                                 st.SystemsTest,
                                                 settings_list):
            yield test

        os.chdir(cwd)

        shutil.rmtree(tempdir)

