from systems_testing import systems_testing as st

releases_list = "Previous releases for dls_testpythonmod2 in the repository:\n1-0\n1-1\n2-0\n2-1\n"
latest_release = "The latest release for dls_testpythonmod2 in the repository is: 2-1\n"

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

]


def test_generator():

    for test in st.generate_tests_from_dicts("dls-list-releases.py",
                                             st.SystemsTest,
                                             settings_list):
        yield test
