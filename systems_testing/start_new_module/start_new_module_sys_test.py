from pkg_resources import require
require('nose')

import systems_testing as st
import os
import shutil
import tempfile

COMPARISON_FILES = "comparison_files"

settings_list = [
    {
        'description': "example_test_name_1",

        'std_out_compare_string': "I am not the message?\n",

        'exception_type': "__main__.Error",

        'exception_string': "I am the message.",

        'arguments': "message",

        'local_repo_path': "test_repo",

        'attributes_dict': {'module-contact': "lkz95212"}

    },

    {
        'description': "example_test_name_2",

        'std_out_compare_string': "I am not the wine?\n",

        'exception_type': "__main__.Error",

        'exception_string': "I am the message.",

        'arguments': "wine",

        'local_repo_path': "test_repo",

        'attributes_dict': {'module-contact': "lkz95212"}

    },

    {
        'description': "example_test_name_3",

        'std_out_compare_string': "I am not the wine?\n",

        'exception_type': "__main__.Error",

        'exception_string': "I am the message.",

        'arguments': "wine",

        'repo_comp_method': "local_comp",

        'local_comp_path_one': "test_repo",

        'local_comp_path_two': "test_repo_2",

    },

    {
        'description': "example_test_name_4",

        'std_out_compare_string': "I am not the wine?\n",

        'exception_type': "__main__.Error",

        'exception_string': "I am the message.",

        'arguments': "wine",

        'repo_comp_method': "server_comp",

        'local_comp_path_one': "test_repo",

        'server_repo_path': "controlstest/ioc/BTEST/BTEST-EB-IOC-03",

    },

    {
        'description': "example_test_name_5",

        'std_out_compare_string': "I am not the wine?\n",

        'exception_type': "__main__.Error",

        'exception_string': "I am the message.",

        'arguments': "wine",

        'repo_comp_method': "all_comp",

        'local_comp_path_one': "server_already_cloned",

        'local_comp_path_two': "server_clone_2",

        'server_repo_path': "controlstest/ioc/BTEST/BTEST-EB-IOC-03",

    }
]


def test_generator_local():

        tempdir = tempfile.mkdtemp()
        cwd = os.getcwd()

        # CREATE SCRIPT TO GENERATE EXPECTED FILES
        # - USE SVN SCRIPT THEN DEL .SVN FOLDER?
        # COPY COMPARISON_FILES TO TEMPDIR
        # CHANGE USERNAME_FIELD TO OS.GETLOGIN RETURN
        #

        os.chdir(tempdir)

        for test in st.generate_tests_from_dicts("./test_error_script.py",
                                                 st.SystemsTest,
                                                 settings_list):
            yield test

        os.chdir(cwd)


# TODO(Martin) Make this one for all the expected verification errors.
# TODO(Martin) Can check that no local folders exist at the end - job complete!
def test_generator_local_exceptions_expected():

        tempdir = tempfile.mkdtemp()
        cwd = os.getcwd()

        # CREATE SCRIPT TO GENERATE EXPECTED FILES
        # - USE SVN SCRIPT THEN DEL .SVN FOLDER?
        # COPY COMPARISON_FILES TO TEMPDIR
        # CHANGE USERNAME_FIELD TO OS.GETLOGIN RETURN
        #

        os.chdir(tempdir)

        for test in st.generate_tests_from_dicts("./test_error_script.py",
                                                 st.SystemsTest,
                                                 settings_list):
            yield test

        os.chdir(cwd)


# TODO(Martin) Make this one cd to git repo (tempfile) and test cwd in git
# TODO(Martin) repository check.
def test_generator_local_cd_to_git_repo():

        tempdir = tempfile.mkdtemp()
        cwd = os.getcwd()

        # CREATE SCRIPT TO GENERATE EXPECTED FILES
        # - USE SVN SCRIPT THEN DEL .SVN FOLDER?
        # COPY COMPARISON_FILES TO TEMPDIR
        # CHANGE USERNAME_FIELD TO OS.GETLOGIN RETURN
        #

        os.chdir(tempdir)

        for test in st.generate_tests_from_dicts("./test_error_script.py",
                                                 st.SystemsTest,
                                                 settings_list):
            yield test

        os.chdir(cwd)


def test_generator_export_to_server():

        tempdir = tempfile.mkdtemp()
        cwd = os.getcwd()

        os.chdir(tempdir)

        for test in st.generate_tests_from_dicts("./test_error_script.py",
                                                 st.SystemsTest,
                                                 settings_list):
            yield test

        os.chdir(cwd)

        shutil.rmtree(tempdir)

