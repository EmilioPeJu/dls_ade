import system_testing as st
import logs

settings_list = [

    {
        'description': "print_all_logs_for_module",

        'arguments': "-p dls_testpythonmod2",

        'std_out_compare_string': logs.all_logs,

    },

    {
        'description': "print_all_logs_for_module_with_verbose",

        'arguments': "-p dls_testpythonmod2 -v",

        'std_out_compare_string': logs.verbose_all,

    },

    {
        'description': "print_logs_in_given_range",

        'arguments': "-p dls_testpythonmod2 1-1 2-0",

        'std_out_compare_string': logs.release_range,

    },

    {
        'description': "print_logs_in_given_range_with_verbose",

        'arguments': "-p dls_testpythonmod2 1-1 2-0 -v",

        'std_out_compare_string': logs.verbose_range,

    },

    {
        'description': "print_logs_from_earlier_arg_to_HEAD",

        'arguments': "-p dls_testpythonmod2 -e 1-1",

        'std_out_compare_string': logs.earlier,

    },

    {
        'description': "print_logs_from_earlier_arg_to_HEAD_with_verbose",

        'arguments': "-p dls_testpythonmod2 -e 1-1 -v",

        'std_out_compare_string': logs.earlier_verbose,

    },

    {
        'description': "print_logs_from_start_to_later_arg",

        'arguments': "-p dls_testpythonmod2 -l 2-0",

        'std_out_compare_string': logs.later,

    },

    {
        'description': "print_logs_from_start_to_later_arg_with_verbose",

        'arguments': "-p dls_testpythonmod2 -l 2-0 -v",

        'std_out_compare_string': logs.later_verbose,

    },

]


def test_generator():

    for test in st.generate_tests_from_dicts("dls-logs-since-release.py",
                                             settings_list):
        yield test
