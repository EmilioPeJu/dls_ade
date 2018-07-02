import system_testing as st

branches_list = "Branches of controlstest/python/dls_testpythonmod: bug-fix, master, new-feature\n"

settings_list = [

    {
        'description': "list_the_branches_for_a_module_on_the_repository",

        'arguments': "-p dls_testpythonmod",

        'std_out_compare_string': branches_list,

    },

]


def test_generator():

    for test in st.generate_tests_from_dicts("dls-list-branches.py",
                                             settings_list):
        yield test
