import system_testing as st

changes = "Changes have been made to dls_testpythonmod since release 1-1\n"
no_changes = "No changes have been made to dls_testpythonmod2 since most recent release 2-1\n"
exception_msg = "Repository does not contain controlstest/python/testpythonmod"

settings_list = [

    # List everything in python area
    {
        'description': "changes_made",

        'arguments': "-p dls_testpythonmod",

        'std_out_compare_string': changes,

    },

    # List everything in python area
    {
        'description': "no_changes_made",

        'arguments': "-p dls_testpythonmod2",

        'std_out_compare_string': no_changes,

    },

    {
        'description': "raise_exception_for_non_existent_module",

        'arguments': "-p testpythonmod",

        'exception_type': "Exception",

        'exception_string': exception_msg,

    },

    {
        'description': "no_releases_done",

        'arguments': "-i testB06/TS",

        'std_out_compare_string': "No release has been done for testB06/TS\n",

    },

]


def test_generator():

    for test in st.generate_tests_from_dicts("dls-changes-since-release.py",
                                             settings_list):
        yield test
