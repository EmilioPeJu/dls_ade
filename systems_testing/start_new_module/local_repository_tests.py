from pkg_resources import require
require('nose')

import systems_testing as st
import os
import shutil
import tempfile

COMPARISON_FILES = "comparison_files"


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
