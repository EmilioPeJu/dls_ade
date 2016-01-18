from pkg_resources import require
require('nose')
import systems_testing as st


settings_list = [
    {
        'description': "example_test_name",
        'std_out_compare_string': ("I am not the message?\n"
                                   "Do you liek: mudkips?\n"),
        'exception_type': "__main__.Error",

        'exception_string': "I am the message.",

        'arguments': "mudkips",

        'local_repo_path': "test_repo",

        'attributes_dict': {'module-contact': "lkz95212"}

    },

    {
        'description': "example_test_name",
        'std_out_compare_string': ("I am not the message?\nDo you liek: wine?\n"),

        'exception_type': "__main__.Error",

        'exception_string': "I am the message.",

        'arguments': "wine",

        'local_repo_path': "test_repo",

        'attributes_dict': {'modue-contact': "bobsuruncle"}

    }
]


def test_generator():
        for test in st.generate_tests_from_dicts("./test_error_script.py",
                                                 st.SystemsTest,
                                                 settings_list):
            yield test
