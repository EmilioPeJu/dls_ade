import system_testing as st
import os
import shutil
import tempfile

settings_list = [
    {
        'description': "test_module_creation_fails_if_repository_already_on_server",

        'arguments': "testsupportmod",

        'exception_type': "VerificationError",

        'exception_string': "The path controlstest/support/testsupportmod already exists on server, cannot continue",
    },

    {
        'description': "test_module_creation_fails_if_app_already_exists_for_old_style_ioc_module",

        'arguments': "-i BTEST/TS/05",

        'exception_type': "VerificationError",

        'exception_string': "The repository controlstest/ioc/BTEST/TS has an app that conflicts with app name: BTEST-TS-IOC-05",
    },
]


def test_generator_remote_verification():
    """Generator for tests relating to remote server verification.

    This will move into a temporary directory before returning the tests with
    the given script and settings list.

    When called by nosetests, nosetests will run every yielded test function.

    Yields:
        A :class:`system_testing.SystemTest` instance.

    """
    tempdir = tempfile.mkdtemp()
    cwd = os.getcwd()

    os.chdir(tempdir)

    for test in st.generate_tests_from_dicts("dls-start-new-module.py",
                                             settings_list):
        yield test

    os.chdir(cwd)

    shutil.rmtree(tempdir)
