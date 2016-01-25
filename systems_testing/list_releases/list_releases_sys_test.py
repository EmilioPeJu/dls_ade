from systems_testing import systems_testing as st

support_list = "Previous releases for testsupportmod in the repository:\n1-0\n1-1\n"
python_list = "Previous releases for dls_testpythonmod in the repository:\n1-0\n1-1\n"
ioc_list = "Previous releases for BTEST/TS in the repository:\n1-0\n1-1\n"

settings_list = [

    # List releases for support module on repo
    {
        'description': "list_support_repo_releases",

        'arguments': "testsupportmod -g",

        'std_out_compare_string': support_list,

    },

    # List releases for python module on repo
    {
        'description': "list_python_repo_releases",

        'arguments': "-p dls_testpythonmod -g",

        'std_out_compare_string': python_list,

    },

    # List everything in ioc area
    {
        'description': "list_ioc_repo_releases",

        'arguments': "-i BTEST/TS -g",

        'std_out_compare_string': ioc_list,

    },

]


def test_generator():

    for test in st.generate_tests_from_dicts("dls-list-releases.py",
                                             st.SystemsTest,
                                             settings_list):
        yield test
