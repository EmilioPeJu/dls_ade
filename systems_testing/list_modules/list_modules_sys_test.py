from systems_testing import systems_testing as st

support_list = "Modules in support:\n\ntestsupportmod\ntestsupportmo\n"
python_list = "Modules in python:\n\ndls_testpythonmod2\ndls_testpythonmod\n"
ioc_list = "Modules in ioc:\n\nBTEST2/TS\nBTEST/BTEST-EB-IOC-03\nBTEST/BTEST-EB-IOC-0\nBTEST/BTEST-VA-IOC-04\nBTEST/TS\n"
ioc_domain_list = "Modules in ioc:\n\nBTEST/BTEST-EB-IOC-03\nBTEST/BTEST-EB-IOC-0\nBTEST/BTEST-VA-IOC-04\nBTEST/TS\n"

settings_list = [

    # List everything in support area
    {
        'description': "list_support",

        'std_out_compare_string': support_list,

    },

    # List everything in python area
    {
        'description': "list_python",

        'arguments': "-p",

        'std_out_compare_string': python_list,

    },

    # List everything in ioc area
    {
        'description': "list_ioc",

        'arguments': "-i",

        'std_out_compare_string': ioc_list,

    },

    # List everything in an ioc domain
    {
        'description': "list_ioc_domain",

        'arguments': "-i -d BTEST",

        'std_out_compare_string': ioc_domain_list,

    },

]


def test_generator():

        for test in st.generate_tests_from_dicts("dls-list-modules.py",
                                                 st.SystemsTest,
                                                 settings_list):
            yield test
