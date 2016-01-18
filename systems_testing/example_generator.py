from pkg_resources import require
require('nose')
import systems_testing as st


settings_list = [
    {
        'description': "example_test_name",
        'std_out_compare_string': "I am not the message?\n",

        'exception_type': "__main__.Error",

        'exception_string': "I am the message."


    }
]


def test_generator():
        for test in st.generate_tests_from_dicts("./test_error_script.py",
                                                 st.SystemsTest,
                                                 settings_list):
            yield test
