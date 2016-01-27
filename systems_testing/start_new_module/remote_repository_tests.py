import os

with open("repo_test_num.txt", "r") as f:
    test_number = f.readline()

if not test_number and not test_number.isdigit():
    raise Exception("The file repo_test_num.txt must contain the current test "
                    "number.")

test_number = int(test_number)
test_number += 1
test_number = str(test_number)

os.environ['GIT_ROOT_DIR'] = "controlstest/targetOS/creation" + test_number

with open("repo_test_num.txt", "w") as f:
    f.write(test_number)

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
        #
        # tempdir = tempfile.mkdtemp()
        # cwd = os.getcwd()
        #
        # os.chdir(tempdir)
        #
        # for test in st.generate_tests_from_dicts("./test_error_script.py",
        #                                          st.SystemsTest,
        #                                          settings_list):
        #     yield test
        #
        # os.chdir(cwd)
        #
        # shutil.rmtree(tempdir)

