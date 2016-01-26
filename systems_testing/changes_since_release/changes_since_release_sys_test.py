from systems_testing import systems_testing as st

changes = "Changes have been made to dls_testpythonmod since release 1-1\n"
no_changes = "No changes have been made to dls_testpythonmod2 since most recent release 2-1\n"

settings_list = [

    # List everything in python area
    {
        'description': "changes_made",

        'arguments': "-p dls_testpythonmod",

        'std_out_compare_string': python_changes,

    },

    # List everything in python area
    {
        'description': "no_changes_made",

        'arguments': "-p dls_testpythonmod2",

        'std_out_compare_string': python_no_changes,

    },

]


def test_generator():

    for test in st.generate_tests_from_dicts("dls-changes-since-release.py",
                                             st.SystemsTest,
                                             settings_list):
        yield test
