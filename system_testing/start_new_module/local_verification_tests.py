import system_testing as st
import os
import shutil
import tempfile


# NOTE: 'create_folder' used by this module to create conflicting folder names.
folder_conflict_settings_list = [
    {
        'description': "test_module_creation_fails_if_path_already_exists",

        'arguments': "test_module",

        'exception_type': "VerificationError",

        'exception_string': "Directory test_module already exists, please move elsewhere and try again.",

        'create_folder': "test_module",
    },

    {
        'description': "test_module_creation_fails_if_nested_path_already_exists",

        'arguments': "-i testB21-EA-IOC-01",

        'exception_type': "VerificationError",

        'exception_string': "Directory testB21/testB21-EA-IOC-01 already exists, please move elsewhere and try again.",

        'create_folder': "testB21/testB21-EA-IOC-01"
    },
]


def test_generator_conflicting_filepaths_expected():
    """Generator for tests involving a conflict of filepaths.

    This will move into a temporary directory which already has a number of
    folders that will conflict with the file creation process. It
    will then return the tests with the given script and settings list.

    When called by nosetests, nosetests will run every yielded test function.

    Yields:
        A :class:`system_testing.SystemTest` instance.

    """
    tempdir = tempfile.mkdtemp()
    cwd = os.getcwd()

    os.chdir(tempdir)

    for settings in folder_conflict_settings_list:
        os.makedirs(settings.pop('create_folder'))

    for test in st.generate_tests_from_dicts("dls-start-new-module.py -n",
                                             folder_conflict_settings_list):
        yield test

    os.chdir(cwd)

    shutil.rmtree(tempdir)


git_root_dir_settings_list = [
    {
        'description': "test_module_creation_fails_if_located_inside_local_git_repository_root_directory",

        'arguments': "test_module_git_root_directory",

        'exception_type': "VerificationError",

        'exception_string': "Currently in a git repository, please move elsewhere and try again.",
    },
]


def test_generator_local_git_repo_root_directory():
    """Generator for tests requiring operation in a git repository.

    This will move into a temporary directory which is a git repository. It
    will then return the tests with the given script and settings list.

    When called by nosetests, nosetests will run every yielded test function.

    Yields:
        A :class:`system_testing.SystemTest` instance.

    """
    tempdir = tempfile.mkdtemp()
    cwd = os.getcwd()

    os.chdir(tempdir)

    st.vcs_git.init_repo(".")

    for test in st.generate_tests_from_dicts("dls-start-new-module.py -n",
                                             git_root_dir_settings_list):
        yield test

    os.chdir(cwd)

    shutil.rmtree(tempdir)


git_nested_dir_settings_list = [
    {
        'description': "test_module_creation_fails_if_located_inside_local_git_repository_nested_directory",

        'arguments': "test_module_git_nested_directory",

        'exception_type': "VerificationError",

        'exception_string': "Currently in a git repository, please move elsewhere and try again.",
    },
]


def test_generator_local_git_repo_nested_directory():
    """Generator for tests requiring a nested directory in a git repository.

    This will move into a temporary directory which is nested inside a git
    repository. It will then return the tests with the given script and
    settings list.

    When called by nosetests, nosetests will run every yielded test function.

    Yields:
        A :class:`system_testing.SystemTest` instance.

    """
    tempdir = tempfile.mkdtemp()
    cwd = os.getcwd()

    os.chdir(tempdir)

    st.vcs_git.init_repo(".")
    os.makedirs("nested_folder")
    os.chdir("nested_folder")

    for test in st.generate_tests_from_dicts("dls-start-new-module.py -n",
                                             git_nested_dir_settings_list):
        yield test

    os.chdir(cwd)

    shutil.rmtree(tempdir)
