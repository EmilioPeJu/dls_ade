import system_testing as st
import tempfile
import os
import shutil
import subprocess
import logging
from dls_ade import vcs_git
from dls_ade import Server
from nose.tools import assert_equal, assert_true, assert_false
import unittest

ORIGINAL_GIT_ROOT_DIR = os.getenv('GIT_ROOT_DIR')
NEW_GIT_ROOT_DIR = "controlstest/targetOS/mock_repo"

settings_list = [

    {
        'description': "test_checkout_a_single_module",

        'arguments': "-p dls_testpythonmod",

        'repo_comp_method': "server_comp",

        'local_comp_path_one': "dls_testpythonmod",

        'server_repo_path': "controlstest/python/dls_testpythonmod",

    },

    {
        'description': "test_checkout_a_single_module_and_change_branch",

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
                                             settings_list):

        tempdir = tempfile.mkdtemp()
        cwd = os.getcwd()
        os.chdir(tempdir)

        yield test

        os.chdir(cwd)
        shutil.rmtree(tempdir)


class MultiCheckoutTest(unittest.TestCase):

    def setUp(self):
        """Change environment variable and module variables.

        """
        # The environment variable is set for the use of the script being tested.
        os.environ['GIT_ROOT_DIR'] = NEW_GIT_ROOT_DIR

        # Set so SystemTest object can use the new variable.
        st.Server.GIT_ROOT_DIR = NEW_GIT_ROOT_DIR

    def tearDown(self):
        """Change environment variable and module variables to the original values.

        """
        os.environ['GIT_ROOT_DIR'] = ORIGINAL_GIT_ROOT_DIR
        st.Server.GIT_ROOT_DIR = ORIGINAL_GIT_ROOT_DIR

    def test_checkout_entire_area(self):

        tempdir = tempfile.mkdtemp()
        cwd = os.getcwd()
        os.chdir(tempdir)

        modules = ["controlstest/targetOS/mock_repo/ioc/BTEST/BTEST-EB-IOC-03",
                   "controlstest/targetOS/mock_repo/ioc/BTEST/TS",
                   "controlstest/targetOS/mock_repo/ioc/BTEST2/TS"]
        
        should_not_clone = ["controlstest/targetOS/mock_repo/python/dls_testpythonmod",
                            "controlstest/targetOS/mock_repo/support/testsupportmod"]

        process = subprocess.Popen("dls-checkout-module.py -i".split(),
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   stdin=subprocess.PIPE)

        std_out, std_err = process.communicate('Y')

        logging.debug("Standard out:\n" + std_out)
        logging.debug("Standard error:\n" + std_err)

        # Check correct folders have been created
        for path in modules:
            assert_true(os.path.isdir(path.split('/', 2)[-1]))
        for path in should_not_clone:
            assert_false(os.path.isdir(path.split('/', 2)[-1]))

        # Check modules have been cloned correctly
        for path in modules:
            repo = path.split('/', 2)[-1]
            clone = Server().temp_clone(path).repo
            comp_repo = clone.working_tree_dir

            assert_true(st.check_if_repos_equal(repo, comp_repo))

        os.chdir(cwd)
        shutil.rmtree(tempdir)

    def test_checkout_entire_ioc_domain(self):

        tempdir = tempfile.mkdtemp()
        cwd = os.getcwd()
        os.chdir(tempdir)

        modules = ["controlstest/targetOS/mock_repo/ioc/BTEST/BTEST-EB-IOC-03",
                   "controlstest/targetOS/mock_repo/ioc/BTEST/TS"]

        should_not_clone = ["controlstest/targetOS/mock_repo/ioc/BTEST2/TS",
                            "controlstest/targetOS/mock_repo/python/dls_testpythonmod",
                            "controlstest/targetOS/mock_repo/support/testsupportmod"]

        process = subprocess.Popen("dls-checkout-module.py -i BTEST/".split(),
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   stdin=subprocess.PIPE)

        std_out, std_err = process.communicate()

        logging.debug("Standard out:\n" + std_out)
        logging.debug("Standard error:\n" + std_err)

        # Check correct folders have been created
        for path in modules:
            assert_true(os.path.isdir(path.split('/', 2)[-1]))
        for path in should_not_clone:
            assert_false(os.path.isdir(path.split('/', 2)[-1]))

        # Check modules have been cloned correctly
        for path in modules:
            repo = path.split('/', 2)[-1]
            clone = Server().temp_clone(path).repo
            comp_repo = clone.working_tree_dir

            assert_true(st.check_if_repos_equal(repo, comp_repo))

        os.chdir(cwd)
        shutil.rmtree(tempdir)
