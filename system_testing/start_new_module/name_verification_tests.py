from pkg_resources import require
require('nose')

import system_testing as st
import os
import shutil
import tempfile
from nose.tools import assert_false


settings_list = [
    {
        'description': "test_python_creation_fails_with_no_prepending_dls_in_name",

        'arguments': "-p test_python_module",

        'exception_type': "dls_ade.exceptions.ParsingError",

        'exception_string': "Python module names must start with 'dls_' and be valid python identifiers",
    },

    {
        'description': "test_python_creation_fails_with_full_stop_in_name",

        'arguments': "-p dls_test_python.module",

        'exception_type': "dls_ade.exceptions.ParsingError",

        'exception_string': "Python module names must start with 'dls_' and be valid python identifiers",
    },

    {
        'description': "test_python_creation_fails_with_hyphen_in_name",

        'arguments': "-p dls_test_python-module",

        'exception_type': "dls_ade.exceptions.ParsingError",

        'exception_string': "Python module names must start with 'dls_' and be valid python identifiers",
    },

    {
        'description': "test_ioc_creation_fails_with_neither_hyphen_nor_slash_in_name",

        'arguments': "-i test_ioc_module",

        'exception_type': "dls_ade.exceptions.ParsingError",

        'exception_string': "Need a name with '-' or '/' in it, got test_ioc_module",
    },

    {
        'description': "test_ioc_creation_fails_with_empty_second_part_of_slash_separated_name",

        'arguments': "-i test/",

        'exception_type': "dls_ade.exceptions.ParsingError",

        'exception_string': "Need a name with '-' or '/' in it, got test/",
    },

    {
        'description': "test_ioc_creation_fails_with_empty_second_part_of_slash_separated_name_but_third_exists",

        'arguments': "-i test//ioc",

        'exception_type': "dls_ade.exceptions.ParsingError",

        'exception_string': "Need a name with '-' or '/' in it, got test//ioc",
    },
]


# NOTE: All tests run the script with '-n' in order to prevent creating
# remote repository files if the tests fail
def test_generator_parsing_errors_expected():
    """Generator for tests relating to name verification.

    This will move into a temporary directory before returning the tests with
    the given script and settings list.

    When called by nosetests, nosetests will run every yielded test function.

    Yields:
        A :class:`system_testing.SystemTest` instance.

    """
    tempdir = tempfile.mkdtemp()
    cwd = os.getcwd()

    os.chdir(tempdir)

    for test in st.generate_tests_from_dicts("dls-start-new-module.py -n",
                                             settings_list):
        yield test

    # checks that no module folders have been created
    assert_false(os.listdir("."))

    os.chdir(cwd)

    shutil.rmtree(tempdir)
