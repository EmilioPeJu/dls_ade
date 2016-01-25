from pkg_resources import require
require('nose')

import systems_testing as st
import os
import shutil
import tempfile

COMPARISON_FILES = "comparison_files"


# TODO(Martin) Suggestion: Use exact same tests as local repo tests, but also
# TODO(Martin) use comparison to server repository.
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
