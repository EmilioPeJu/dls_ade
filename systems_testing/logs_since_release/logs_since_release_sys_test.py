from systems_testing import systems_testing as st
import logs

settings_list = [

    # Print logs for module in support area
    {
        'description': "print_support_logs",

        'arguments': "testsupportmod 1-0 1-1",

        'std_out_compare_string': logs.support,

    },

    # Print verbose logs for module in support area
    {
        'description': "print_verbose_support_logs",

        'arguments': "testsupportmod 1-0 1-1 -v",

        'std_out_compare_string': logs.verbose_support,

    },

    # Print logs for module in python area
    {
        'description': "print_python_logs",

        'arguments': "-p dls_testpythonmod 1-0 1-1",

        'std_out_compare_string': logs.python,

    },

    # Print verbose logs for module in python area
    {
        'description': "print_verbose_python_logs",

        'arguments': "-p dls_testpythonmod 1-0 1-1 -v",

        'std_out_compare_string': logs.verbose_python,

    },

    # Print logs for module in ioc area
    {
        'description': "print_ioc_logs",

        'arguments': "-i BTEST/TS 1-0 1-1",

        'std_out_compare_string': logs.ioc,

    },

    # Print verbose logs for module in ioc area
    {
        'description': "print_verbose_ioc_logs",

        'arguments': "-i BTEST/TS 1-0 1-1 -v",

        'std_out_compare_string': logs.verbose_ioc,

    },

]


def test_generator():

    for test in st.generate_tests_from_dicts("dls-logs-since-release.py",
                                             st.SystemsTest,
                                             settings_list):
        yield test
