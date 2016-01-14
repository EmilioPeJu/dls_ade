from pkg_resources import require
require('nose')
import systems_testing as st


settings_list = [
    {
        'test_name': "example_test_name"
    }
]


def test_generator():
        for test in st.generate_tests_from_dicts("myscript.py", st.SystemsTest,
                                                 settings_list):
            yield test
