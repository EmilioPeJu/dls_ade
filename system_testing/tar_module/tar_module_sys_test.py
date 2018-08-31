import system_testing as st

settings_list = [

    # {
    #     'description': "tar_a_module_in_prod",
    #
    #     'arguments': "-e R3.14.12.3 dummy 0-8",
    #
    # },
    #
    # {
    #     'description': "untar_a_module_in_prod",
    #
    #     'arguments': "-e R3.14.12.3 -u dummy 0-8",
    #
    # },

]


def test_generator():

    for test in st.generate_tests_from_dicts("dls-tar-module.py",
                                             settings_list):
        yield test
