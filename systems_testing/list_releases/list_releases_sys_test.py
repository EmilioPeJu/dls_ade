import systems_testing as st

releases_list = "Previous releases for dls_testpythonmod2 in the repository:\n1-0\n1-1\n2-0\n2-1\n"
latest_release = "The latest release for dls_testpythonmod2 in the repository is: 2-1\n"
prod_releases_list = "Previous releases for dummy in prod:\n0-3\n0-5\n0-6\n0-7\n0-8\n"
latest_prod_release = "The latest release for dummy in prod is: 0-8\n"
e_release_list = "Previous releases for symbols in prod:\n1-9\n1-10\n"
e_latest_release = "The latest release for symbols in prod is: 1-10\n"

settings_list = [

    # List releases for python module on repo
    {
        'description': "list_repo_releases",

        'arguments': "-p dls_testpythonmod2 -g",

        'std_out_compare_string': releases_list,

    },

    # List last release for python module on repo
    {
        'description': "list_last_repo_release",

        'arguments': "-p dls_testpythonmod2 -g -l",

        'std_out_compare_string': latest_release,

    },

    # List releases for support module in prod
    {
        'description': "list_prod_releases",

        'arguments': "dummy",

        'std_out_compare_string': prod_releases_list,

    },

    # List releases for support module in prod
    {
        'description': "list_latest_prod_release",

        'arguments': "dummy -l",

        'std_out_compare_string': latest_prod_release,

    },

    # List releases for support module in prod
    {
        'description': "list_prod_releases_other_epics",

        'arguments': "symbols -e R3.14.8.2",

        'std_out_compare_string': e_release_list,

    },

    # List releases for support module in prod
    {
        'description': "list_latest_prod_release_other_epics",

        'arguments': "symbols -e R3.14.8.2 -l",

        'std_out_compare_string': e_latest_release,

    },

]


def test_generator():

    for test in st.generate_tests_from_dicts("dls-list-releases.py",
                                             st.SystemsTest,
                                             settings_list):
        yield test
