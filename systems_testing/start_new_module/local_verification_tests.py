from pkg_resources import require
require('nose')

import systems_testing as st
import os
import shutil
import tempfile

COMPARISON_FILES = "comparison_files"

# NOTE: 'create_folder' used by this module to create conflicting folder names.
conflicting_settings_list = [
    {
        'description': "test_module_creation_fails_if_path_already_exists",

        'arguments': "test_module",

        'exception_type': "dls_ade.exceptions.VerificationError",

        'exception_string': "Directory test_module already exists, please move elsewhere and try again.",

        'create_folder': "test_module",
    },

    {
        'description': "test_module_creation_fails_if_nested_path_already_exists",

        'arguments': "-i testB21-EA-IOC-01",

        'exception_type': "dls_ade.exceptions.VerificationError",

        'exception_string': "Directory testB21/testB21-EA-IOC-01 already exists, please move elsewhere and try again.",

        'create_folder': "testB21/testB21-EA-IOC-01"
    },
]

def test_generator_conflicting_filepaths_expected():

    tempdir = tempfile.mkdtemp()
    cwd = os.getcwd()

    os.chdir(tempdir)

    for settings in conflicting_settings_list:
        os.makedirs(settings.pop('create_folder'))

    for test in st.generate_tests_from_dicts("dls-start-new-module.py -n",
                                             st.SystemsTest,
                                             conflicting_settings_list):
        yield test

    os.chdir(cwd)

    shutil.rmtree(tempdir)


git_root_dir_settings_list = [
    {
        'description': "test_module_creation_fails_if_located_inside_local_git_repository_root_directory",

        'arguments': "test_module_git_root_directory",

        'exception_type': "dls_ade.exceptions.VerificationError",

        'exception_string': "Currently in a git repository, please move elsewhere and try again.",
    },
]


def test_generator_local_git_repo_root_directory():

    tempdir = tempfile.mkdtemp()
    cwd = os.getcwd()

    os.chdir(tempdir)

    st.vcs_git.init_repo(".")

    for test in st.generate_tests_from_dicts("dls-start-new-module.py -n",
                                             st.SystemsTest,
                                             git_root_dir_settings_list):
        yield test

    os.chdir(cwd)

    shutil.rmtree(tempdir)


git_nested_dir_settings_list = [
    {
        'description': "test_module_creation_fails_if_located_inside_local_git_repository_nested_directory",

        'arguments': "test_module_git_nested_directory",

        'exception_type': "dls_ade.exceptions.VerificationError",

        'exception_string': "Currently in a git repository, please move elsewhere and try again.",
    },
]


def test_generator_local_git_repo_nested_directory():

    tempdir = tempfile.mkdtemp()
    cwd = os.getcwd()

    os.chdir(tempdir)

    st.vcs_git.init_repo(".")
    os.makedirs("nested_folder")
    os.chdir("nested_folder")

    for test in st.generate_tests_from_dicts("dls-start-new-module.py -n",
                                             st.SystemsTest,
                                             git_nested_dir_settings_list):
        yield test

    os.chdir(cwd)

    shutil.rmtree(tempdir)
