import systems_testing as st

settings_list = [

    # # Tar up module in prod support
    # {
    #     'description': "tar_module",
    #
    #     'arguments': "dummy",
    #
    # },
    #
    # # Untar module in prod support
    # {
    #     'description': "untar_module",
    #
    #     'arguments': "dummy -u",
    #
    # },

]


def test_generator():

    for test in st.generate_tests_from_dicts("dls-tar-module.py",
                                             st.SystemsTest,
                                             settings_list):
        yield test
