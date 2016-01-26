from systems_testing import systems_testing as st

support_output = "Branches of testsupportmod:\n\nbug-fix\nmaster\nnew-feature\n\n"
python_output = "Branches of dls_testpythonmod:\n\nbug-fix\nmaster\nnew-feature\n\n"
ioc_output = "Branches of BTEST/TS:\n\nbug-fix\nmaster\nnew-feature\n\n"

settings_list = [

    # # Tar up module in prod support
    # {
    #     'description': "list_support_branches",
    #
    #     'arguments': "dummy",
    #
    #     'std_out_compare_string': support_output,
    #
    # },
    #
    # # Untar module in prod support
    # {
    #     'description': "list_support_branches",
    #
    #     'arguments': "dummy -u",
    #
    #     'std_out_compare_string': support_output,
    #
    # },

]


def test_generator():

    for test in st.generate_tests_from_dicts("dls-tar-module.py",
                                             st.SystemsTest,
                                             settings_list):
        yield test
