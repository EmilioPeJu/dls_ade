from systems_testing import systems_testing as st
import tempfile
import os
import shutil
import subprocess
import logging
from dls_ade import vcs_git
from nose.tools import assert_equal, assert_true, assert_false

settings_list = [

    # Checkout one module from python area and check it is correctly cloned
    {
        'description': "checkout_module",

        'arguments': "-p dls_testpythonmod",

        'repo_comp_method': "server_comp",

        'local_comp_path_one': "dls_testpythonmod",

        'server_repo_path': "controlstest/python/dls_testpythonmod",

    },

    # Checkout one module from python area, change branch and check it is correctly cloned
    {
        'description': "checkout_and_change_branch",

        'arguments': "-p dls_testpythonmod -b bug-fix",

        'local_repo_path': "dls_testpythonmod",

        'branch_name': "bug-fix",

        'repo_comp_method': "server_comp",

        'local_comp_path_one': "dls_testpythonmod",

        'server_repo_path': "controlstest/python/dls_testpythonmod",

    },

]


def test_generator():

    for test in st.generate_tests_from_dicts("dls-checkout-module.py",
                                             st.SystemsTest,
                                             settings_list):

        tempdir = tempfile.mkdtemp()
        cwd = os.getcwd()
        os.chdir(tempdir)

        yield test

        os.chdir(cwd)
        shutil.rmtree(tempdir)


def test_checkout_area():

    tempdir = tempfile.mkdtemp()
    cwd = os.getcwd()
    os.chdir(tempdir)

    modules = ["controlstest/python/dls_testpythonmod",
               "controlstest/python/dls_testpythonmod2"]

    process = subprocess.Popen("dls-checkout-module.py -p".split(),
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               stdin=subprocess.PIPE)

    std_out, std_err = process.communicate('Y')

    logging.debug("Standard out:\n" + std_out)
    logging.debug("Standard error:\n" + std_err)

    for path in modules:
        assert_true(os.path.isdir(path.split('/', 2)[-1]))

    for path in modules:
        repo = path.split('/', 2)[-1]
        clone = vcs_git.temp_clone(path)
        comp_repo = clone.working_tree_dir

        assert_true(st.check_if_repos_equal(repo, comp_repo))

    os.chdir(cwd)
    shutil.rmtree(tempdir)


def test_checkout_domain():

    tempdir = tempfile.mkdtemp()
    cwd = os.getcwd()
    os.chdir(tempdir)

    modules = ["controlstest/ioc/BTEST/BTEST-EB-IOC-03",
               "controlstest/ioc/BTEST/BTEST-EB-IOC-0",
               "controlstest/ioc/BTEST/BTEST-VA-IOC-04",
               "controlstest/ioc/BTEST/TS"]

    process = subprocess.Popen("dls-checkout-module.py -i BTEST/".split(),
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               stdin=subprocess.PIPE)

    std_out, std_err = process.communicate()

    logging.debug("Standard out:\n" + std_out)
    logging.debug("Standard error:\n" + std_err)

    for path in modules:
        assert_true(os.path.isdir(path.split('/', 2)[-1]))

    for path in modules:
        repo = path.split('/', 2)[-1]
        clone = vcs_git.temp_clone(path)
        comp_repo = clone.working_tree_dir

        assert_true(st.check_if_repos_equal(repo, comp_repo))

    os.chdir(cwd)
    shutil.rmtree(tempdir)
