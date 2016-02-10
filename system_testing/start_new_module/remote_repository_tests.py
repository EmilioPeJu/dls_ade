import system_testing as st
import os
import shutil
import tempfile
import start_new_module_util as snm_util

COMPARISON_FILES = snm_util.COMPARISON_FILES

ORIGINAL_GIT_ROOT_DIR = os.getenv('GIT_ROOT_DIR')
NEW_GIT_ROOT_DIR = ""

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

    'IOC-B07':
        ("\nPlease now edit testB07/TS/configure/RELEASE to put "
         "in correct paths for dependencies.\nYou can also add dependencies "
         "to testB07/TS/testB07-TS-IOC-02App/src/Makefile\nand "
         "testB07/TS/testB07-TS-IOC-02App/Db/Makefile if "
         "appropriate.\n"),
}

# NOTE: These are (or ought to be) the exact same tests as from local
# repository tests. The only addition is the addition of a server path used for
# comparisons. I have copied over all the text, though, in order to make these
# tests self contained. The commented out tests are superfluous.
settings_list = [
    {
        'description': "test_exported_python_module_is_created_with_correct_files",

        'arguments': "-p dls_test_python_module",

        'std_out_ends_with_string': printed_messages['python'],

        'attributes_dict': {'module-contact': os.getlogin()},

        'repo_comp_method': "all_comp",

        'path': "dls_test_python_module",

        'module_area': "python",
    },

    {
        'description': "test_exported_tools_module_is_created_with_correct_files",

        'arguments': "-a tools test_tools_module",

        'std_out_ends_with_string': printed_messages['tools'],

        'attributes_dict': {'module-contact': os.getlogin()},

        'repo_comp_method': "all_comp",

        'path': "test_tools_module",

        'module_area': "tools",

    },

    {
        'description': "test_exported_support_module_is_created_with_correct_files",

        'arguments': "-a support test_support_module",

        'std_out_ends_with_string': printed_messages['support'],

        'attributes_dict': {'module-contact': os.getlogin()},

        'repo_comp_method': "all_comp",

        'path': "test_support_module",

        'module_area': "support",
    },

    {
        'description': "test_exported_IOC_BL_slash_form_module_is_created_with_correct_files",

        'arguments': "-i testB21/BL",

        'std_out_ends_with_string': printed_messages['IOC-BL-slash'],

        'attributes_dict': {'module-contact': os.getlogin()},

        'repo_comp_method': "all_comp",

        'path': "testB21/BL",

        'module_area': "ioc",
    },
    #
    # {
    #     'description': "test_exported_IOC_BL_dash_form_module_is_created_with_correct_files",
    #
    #     'arguments': "-i testB22-BL-IOC-01",
    #
    #     'std_out_ends_with_string': printed_messages['IOC-BL-dash'],
    #
    #     'attributes_dict': {'module-contact': os.getlogin()},
    #
    #     'repo_comp_method': "all_comp",
    #
    #     'path': "testB22/testB22-BL-IOC-01",
    #
    #     'module_area': "ioc",
    # },
    #
    # {
    #     'description': "test_exported_IOC_module_slash_form_without_ioc_number_is_created_with_correct_ioc_number_and_module_name_and_files",
    #
    #     'arguments': "-i testB01/TS",
    #
    #     'input': "",
    #
    #     'std_out_ends_with_string': printed_messages['IOC-B01'],
    #
    #     'attributes_dict': {'module-contact': os.getlogin()},
    #
    #     'repo_comp_method': "all_comp",
    #
    #     'path': "testB01/TS",
    #
    #     'module_area': "ioc",
    # },
    #
    # {
    #     'description': "test_exported_IOC_module_slash_form_with_ioc_number_is_created_with_correct_ioc_number_and_module_name_and_files",
    #
    #     'arguments': "-i testB02/TS/03",
    #
    #     'input': "",
    #
    #     'std_out_ends_with_string': printed_messages['IOC-B02'],
    #
    #     'attributes_dict': {'module-contact': os.getlogin()},
    #
    #     'repo_comp_method': "all_comp",
    #
    #     'path': "testB02/TS",
    #
    #     'module_area': "ioc",
    # },
    #
    # {
    #     'description': "test_exported_IOC_module_slash_form_with_no_ioc_number_and_fullname_is_created_with_correct_module_name_and_files",
    #
    #     'arguments': "-i testB03/TS/ --fullname",
    #
    #     'input': "",
    #
    #     'std_out_ends_with_string': printed_messages['IOC-B03'],
    #
    #     'attributes_dict': {'module-contact': os.getlogin()},
    #
    #     'repo_comp_method': "all_comp",
    #
    #     'path': "testB03/testB03-TS-IOC-01",
    #
    #     'module_area': "ioc",
    # },
    #
    # {
    #     'description': "test_exported_IOC_module_slash_form_with_ioc_number_and_fullname_is_created_with_correct_module_name_and_files",
    #
    #     'arguments': "-i testB04/TS/04 --fullname",
    #
    #     'input': "",
    #
    #     'std_out_ends_with_string': printed_messages['IOC-B04'],
    #
    #     'attributes_dict': {'module-contact': os.getlogin()},
    #
    #     'repo_comp_method': "all_comp",
    #
    #     'path': "testB04/testB04-TS-IOC-04",
    #
    #     'module_area': "ioc",
    # },

    {
        'description': "test_exported_IOC_module_dash_form_is_created_with_correct_module_name_and_files",

        'arguments': "-i testB05-TS-IOC-02 --fullname",

        'input': "",

        'std_out_ends_with_string': printed_messages['IOC-B05'],

        'attributes_dict': {'module-contact': os.getlogin()},

        'repo_comp_method': "all_comp",

        'path': "testB05/testB05-TS-IOC-02",

        'module_area': "ioc",
    },
]


def setup_module():
    """Change environment variable and module variables to numbered values.

    This allows us to perform tests without them impacting each other. The file
    `repo_test_num.txt` contains a single number that indicates the previous
    GIT_ROOT_DIR used.

    """
    global NEW_GIT_ROOT_DIR

    with open("repo_test_num.txt", "r") as f:
        test_number = f.readline()

    if not test_number and not test_number.isdigit():
        raise Exception("The file repo_test_num.txt must contain the current "
                        "test number.")

    test_number = str(int(test_number) + 1)
    
    # The environment variable is set for the use of the script being tested.
    NEW_GIT_ROOT_DIR = "controlstest/targetOS/creation" + test_number
    os.environ['GIT_ROOT_DIR'] = NEW_GIT_ROOT_DIR

    with open("repo_test_num.txt", "w") as f:
        f.write(test_number)

    # Set so SystemTest object can use the new variable.
    st.vcs_git.GIT_ROOT_DIR = NEW_GIT_ROOT_DIR
    st.vcs_git.pathf.GIT_ROOT_DIR = NEW_GIT_ROOT_DIR


def test_generator_export_to_server():
    """Generator for tests relating to remote server repository creation.

    This will move into a temporary directory before returning the tests with
    the given script and settings list.

    When called by nosetests, nosetests will run every yielded test function.

    Yields:
        A :class:`system_testing.SystemTest` instance.

    """
    alter_settings_dictionaries(settings_list)

    tempdir = tempfile.mkdtemp()
    cwd = os.getcwd()

    # Unpack tar in tempdir and change to match currently logged in user.
    snm_util.untar_comparison_files_and_insert_user_login(
            COMPARISON_FILES + ".tar.gz", tempdir
    )

    os.chdir(tempdir)

    for test in st.generate_tests_from_dicts("dls-start-new-module.py",
                                             settings_list):
        yield test

    os.chdir(cwd)

    shutil.rmtree(tempdir)


add_app_settings_list = [
    {
        'description': "test_exported_IOC_module_that_needs_to_add_app_without_conflict_is_created_with_correct_module_name_and_app_name_and_files",

        'arguments': "-i testB06/TS/02",

        'input': "",

        'std_out_ends_with_string': printed_messages['IOC-B06'],

        'attributes_dict': {'module-contact': "ORIGINAL_USER_NAME"},

        'repo_comp_method': "all_comp",

        'path': "testB06/TS",

        'module_area': "ioc",
    },
]


def test_generator_export_add_app_to_server():
    """Generator for tests where an app is added to a pre-existing repository.

    This will move into a temporary directory to run the tests with the given
    script and settings list.

    When called by nosetests, nosetests will run every yielded test function.

    Yields:
        A :class:`system_testing.SystemTest` instance.

    """
    for settings_dict in add_app_settings_list:
        # Set the server repository to the default to start with.

        settings_dict['default_server_repo_path'] = os.path.join(
                ORIGINAL_GIT_ROOT_DIR,
                settings_dict['module_area'],
                settings_dict['path'],
        )

    alter_settings_dictionaries(add_app_settings_list)

    tempdir = tempfile.mkdtemp()
    cwd = os.getcwd()

    # Unpack tar in tempdir and change to match currently logged in user.
    snm_util.untar_comparison_files_and_insert_user_login(
            COMPARISON_FILES + ".tar.gz", tempdir
    )

    os.chdir(tempdir)

    for test in st.generate_tests_from_dicts("dls-start-new-module.py",
                                             add_app_settings_list):
        yield test

    os.chdir(cwd)

    shutil.rmtree(tempdir)


def alter_settings_dictionaries(simplified_settings_list):
    """Changes the simplified settings list into the SystemTest compliant form.

    Args:
        simplified_settings_list: A settings list.

    """
    for settings_dict in simplified_settings_list:
        # `path` is used by four separate keys.
        path = settings_dict['path']

        settings_dict['local_repo_path'] = path
        settings_dict['local_comp_path_one'] = path

        # Search the COMPARISON_FILES folder for folders to compare with.
        settings_dict['local_comp_path_two'] = os.path.join(
                COMPARISON_FILES,
                path,
        )

        # Create the full server repo path from the given simplified version.
        settings_dict['server_repo_path'] = st.vcs_git.pathf.dev_module_path(
            path,
            settings_dict['module_area'],
        )


def teardown_module():
    """Change environment variable and module variables to the original values.

    """
    os.environ['GIT_ROOT_DIR'] = ORIGINAL_GIT_ROOT_DIR
    st.vcs_git.GIT_ROOT_DIR = ORIGINAL_GIT_ROOT_DIR
    st.vcs_git.pathf.GIT_ROOT_DIR = ORIGINAL_GIT_ROOT_DIR
