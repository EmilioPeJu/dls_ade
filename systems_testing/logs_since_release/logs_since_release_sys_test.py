import systems_testing as st
import logs

settings_list = [

    # Print logs for module in python area
    {
        'description': "print_logs",

        'arguments': "-p dls_testpythonmod2",

        'std_out_compare_string': logs.all_logs,

    },

    # Print verbose logs for module in python area
    {
        'description': "print_verbose_logs",

        'arguments': "-p dls_testpythonmod2 -v",

        'std_out_compare_string': logs.verbose_all,

    },

    # Print range logs for module in python area
    {
        'description': "print_range_logs",

        'arguments': "-p dls_testpythonmod2 1-1 2-0",

        'std_out_compare_string': logs.release_range,

    },

    # Print verbose range logs for module in python area
    {
        'description': "print_verbose_range_logs",

        'arguments': "-p dls_testpythonmod2 1-1 2-0 -v",

        'std_out_compare_string': logs.verbose_range,

    },

    # Print earlier logs for module in python area
    {
        'description': "print_earlier_logs",

        'arguments': "-p dls_testpythonmod2 -e 1-1",

        'std_out_compare_string': logs.earlier,

    },

    # Print verbose earlier logs for module in python area
    {
        'description': "print_verbose_earlier_logs",

        'arguments': "-p dls_testpythonmod2 -e 1-1 -v",

        'std_out_compare_string': logs.earlier_verbose,

    },

    # Print later logs for module in python area
    {
        'description': "print_later_logs",

        'arguments': "-p dls_testpythonmod2 -l 2-0",

        'std_out_compare_string': logs.later,

    },

    # Print verbose later logs for module in python area
    {
        'description': "print_verbose_later_logs",

        'arguments': "-p dls_testpythonmod2 -l 2-0 -v",

        'std_out_compare_string': logs.later_verbose,

    },

]


def test_generator():

    for test in st.generate_tests_from_dicts("dls-logs-since-release.py",
                                             st.SystemsTest,
                                             settings_list):
        yield test
