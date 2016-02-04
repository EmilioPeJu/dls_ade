import system_testing as st

settings_list = [

    # {
    #     'description': "tar_a_module_in_prod",
    #
    #     'arguments': "dummy",
    #
    # },
    #
    # {
    #     'description': "untar_a_module_in_prod",
    #
    #     'arguments': "dummy -u",
    #
    # },

]


def test_generator():

    for test in st.generate_tests_from_dicts("dls-tar-module.py",
                                             settings_list):
        yield test
