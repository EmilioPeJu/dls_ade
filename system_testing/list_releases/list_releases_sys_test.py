import system_testing as st

releases_list = "Previous releases for dls_testpythonmod2 in the repository:\n1-0\n1-1\n2-0\n2-1\n"
latest_release = "The latest release for dls_testpythonmod2 in the repository is: 2-1\n"
no_git_release = "testB06/TS: No releases made in git\n"
module_does_not_exist = "Repository does not contain controlstest/python/testpythonmod"
no_prod_release = "dummy2: No releases made for R3.14.12.3\n"
prod_releases_list = "Previous releases for dummy in prod:\n0-3\n0-5\n0-6\n0-7\n0-8\n"
python_prod_releases_list = "Previous releases for dls_pilatus in prod:\n1-0\n1-1\n"
latest_prod_release = "The latest release for dummy in prod is: 0-8\n"
e_release_list = "Previous releases for symbols in prod:\n1-9\n1-10\n"
e_latest_release = "The latest release for symbols in prod is: 1-10\n"

settings_list = [

    {
        'description': "list_releases_for_a_module_on_the_repository",

        'arguments': "-p dls_testpythonmod2 -g",

        'std_out_compare_string': releases_list,

    },

    {
        'description': "list_the_latest_release_for_a_module_on_the_repository",

        'arguments': "-p dls_testpythonmod2 -g -l",

        'std_out_compare_string': latest_release,

    },

    {
        'description': "print_no_releases_made_for_a_module_on_the_repository",

        'arguments': "-i testB06/TS -g",

        'std_out_compare_string': no_git_release,

    },

    {
        'description': "raise_exception_for_a_non_existent_module_on_repository",

        'arguments': "-p testpythonmod -g",

        'exception_type': "dls_ade.exceptions.VCSGitError",

        'exception_string': module_does_not_exist,

    },

    {
        'description': "list_releases_for_a_module_in_prod_python",

        'arguments': "-p dls_pilatus",

        'std_out_compare_string': python_prod_releases_list,

    },

    {
        'description': "list_releases_for_a_module_in_prod",

        'arguments': "dummy",

        'std_out_compare_string': prod_releases_list,

    },

    {
        'description': "list_the_latest_release_for_a_module_in_prod",

        'arguments': "dummy -l",

        'std_out_compare_string': latest_prod_release,

    },

    {
        'description': "raise_exception_for_non_existent_module_in_prod",

        'arguments': "dummy2",

        'std_out_compare_string': no_prod_release,

    },

    {
        'description': "list_the_latest_release_for_a_module_in_prod_with_another_epics_version",

        'arguments': "symbols -e R3.14.8.2",

        'std_out_compare_string': e_release_list,

    },

    {
        'description': "list_the_latest_release_for_a_module_in_prod_with_another_epics_version",

        'arguments': "symbols -e R3.14.8.2 -l",

        'std_out_compare_string': e_latest_release,

    },

]


def test_generator():

    for test in st.generate_tests_from_dicts("dls-list-releases.py",
                                             settings_list):
        yield test
