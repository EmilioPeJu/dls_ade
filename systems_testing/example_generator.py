from pkg_resources import require
require('nose')
import systems_testing as st


settings_list = [
    {
        'description': "example_test_name",
        'std_out_compare_string': ("I am not the message?\n"),
        'exception_type': "__main__.Error",

        'exception_string': "I am the message.",

        'arguments': "message",

        'local_repo_path': "test_repo",

        'attributes_dict': {'module-contact': "lkz95212"}

    },

    {
        'description': "example_test_name",
        'std_out_compare_string': ("I am not the wine?\n"),

        'exception_type': "__main__.Error",

        'exception_string': "I am the message.",

        'arguments': "wine",

        'local_repo_path': "test_repo",

        'attributes_dict': {'module-contact': "lkz95212"}

    },

    {
        'description': "example_test_name",
        'std_out_compare_string': ("I am not the wine?\n"),

        'exception_type': "__main__.Error",

        'exception_string': "I am the message.",

        'arguments': "wine",

        'repo_comp_method': "local_comp",

        'local_comp_path_one': "test_repo",

        'local_comp_path_two': "test_repo_2",

    },

    {
        'description': "example_test_name",
        'std_out_compare_string': ("I am not the wine?\n"),

        'exception_type': "__main__.Error",

        'exception_string': "I am the message.",

        'arguments': "wine",

        'repo_comp_method': "server_comp",

        'local_comp_path_one': "test_repo",

        'server_repo_path': "controlstest/ioc/BTEST/BTEST-EB-IOC-03",

    },

    {
        'description': "example_test_name",
        'std_out_compare_string': ("I am not the wine?\n"),

        'exception_type': "__main__.Error",

        'exception_string': "I am the message.",

        'arguments': "wine",

        'repo_comp_method': "all_comp",

        'local_comp_path_one': "server_already_cloned",

        'local_comp_path_two': "server_clone_2",

        'server_repo_path': "controlstest/ioc/BTEST/BTEST-EB-IOC-03",

    }
]


def test_generator():
        for test in st.generate_tests_from_dicts("./test_error_script.py",
                                                 st.SystemsTest,
                                                 settings_list):
            yield test
