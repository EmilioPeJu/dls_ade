from pkg_resources import require
require('nose')

import systems_testing as st
import os
import shutil
import tempfile

COMPARISON_FILES = "comparison_files"


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