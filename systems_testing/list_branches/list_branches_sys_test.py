from systems_testing import systems_testing as st

support_list = "Branches of testsupportmod:\n\nbug-fix\nmaster\nnew-feature\n\n"

settings_list = [

    # List releases for support module on repo
    {
        'description': "list_support_branches",

        'arguments': "testsupportmod",

        'std_out_compare_string': support_list,

    },

    # # List everything in python area
    # {
    #     'description': "list_python",
    #
    #     'arguments': "-p",
    #
    #     'std_out_compare_string': python_list,
    #
    # },
    #
    # # List everything in ioc area
    # {
    #     'description': "list_ioc",
    #
    #     'arguments': "-i",
    #
    #     'std_out_compare_string': ioc_list,
    #
    # },
    #
    # # List everything in an ioc domain
    # {
    #     'description': "list_ioc_domain",
    #
    #     'arguments': "-i -d BTEST",
    #
    #     'std_out_compare_string': ioc_domain_list,
    #
    # },

]


def test_generator():

    for test in st.generate_tests_from_dicts("dls-list-branches.py",
                                             st.SystemsTest,
                                             settings_list):
        yield test
