from systems_testing import systems_testing as st

support_list = "Modules in support:\n\n" \
               "testsupportmod\n" \
               "testsupportmo\n"

python_list = "Modules in python:\n\n" \
              "dls_testpythonmod2\n" \
              "dls_testpythonmod\n"

ioc_list = "Modules in ioc:\n\n" \
           "BTEST2/TS\n" \
           "BTEST/BTEST-EB-IOC-03\n" \
           "BTEST/BTEST-EB-IOC-0\n" \
           "BTEST/BTEST-VA-IOC-04\n" \
           "BTEST/TS\n"

ioc_domain_list = "Modules in ioc:\n\n" \
                  "BTEST/BTEST-EB-IOC-03\n" \
                  "BTEST/BTEST-EB-IOC-0\n" \
                  "BTEST/BTEST-VA-IOC-04\n" \
                  "BTEST/TS\n"

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
