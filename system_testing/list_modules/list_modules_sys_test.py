import system_testing as st

support_list = "Modules in support:\n\n" \
               "testsupportmod\n" \
               "testsupportmo\n"

ioc_list = "Modules in ioc:\n\n" \
           "BTEST2/TS\n" \
           "BTEST/BTEST-EB-IOC-03\n" \
           "BTEST/BTEST-EB-IOC-0\n" \
           "BTEST/BTEST-VA-IOC-04\n" \
           "BTEST/TS\n" \
           "testB06/TS\n" \
           "testB07/TS\n"

ioc_domain_list = "Modules in BTEST:\n\n" \
                  "BTEST/BTEST-EB-IOC-03\n" \
                  "BTEST/BTEST-EB-IOC-0\n" \
                  "BTEST/BTEST-VA-IOC-04\n" \
                  "BTEST/TS\n"

settings_list = [

    {
        'description': "list_modules_in_support_area",

        'std_out_compare_string': support_list,

    },

    {
        'description': "list_modules_in_ioc_area",

        'arguments': "-i",

        'std_out_compare_string': ioc_list,

    },

    {
        'description': "list_modules_in_domain_in_ioc_area",

        'arguments': "-i BTEST",

        'std_out_compare_string': ioc_domain_list,

    },

]


def test_generator():

    for test in st.generate_tests_from_dicts("dls-list-modules.py",
                                             settings_list):
        yield test
