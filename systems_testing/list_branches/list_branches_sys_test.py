from systems_testing import systems_testing as st

support_list = "Branches of testsupportmod:\n\nbug-fix\nmaster\nnew-feature\n\n"
python_list = "Branches of dls_testpythonmod:\n\nbug-fix\nmaster\nnew-feature\n\n"
ioc_list = "Branches of BTEST/TS:\n\nbug-fix\nmaster\nnew-feature\n\n"

settings_list = [

    # List releases for support module on repo
    {
        'description': "list_support_branches",

        'arguments': "testsupportmod",

        'std_out_compare_string': support_list,

    },

    # List everything in python area
    {
        'description': "list_python_branches",

        'arguments': "-p dls_testpythonmod",

        'std_out_compare_string': python_list,

    },

    # List everything in ioc area
    {
        'description': "list_ioc_branches",

        'arguments': "-i BTEST/TS",

        'std_out_compare_string': ioc_list,

    },

]


def test_generator():

    for test in st.generate_tests_from_dicts("dls-list-branches.py",
                                             st.SystemsTest,
                                             settings_list):
        yield test
