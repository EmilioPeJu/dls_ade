import system_testing as st

branches_list = "Branches of dls_testpythonmod:\n\nbug-fix\nmaster\nnew-feature\n\n"

settings_list = [

    # List releases for python module on repo
    {
        'description': "list_branches",

        'arguments': "-p dls_testpythonmod",

        'std_out_compare_string': branches_list,

    },

]


def test_generator():

    for test in st.generate_tests_from_dicts("dls-list-branches.py",
                                             settings_list):
        yield test
