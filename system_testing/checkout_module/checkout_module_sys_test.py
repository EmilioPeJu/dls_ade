import system_testing as st
import tempfile
import os
import shutil
import subprocess
import logging
from dls_ade import vcs_git
from nose.tools import assert_equal, assert_true, assert_false
import unittest

settings_list = [

    {
        'description': "checkout_a_single_module",

        'arguments': "-p dls_testpythonmod",

        'repo_comp_method': "server_comp",

        'local_comp_path_one': "dls_testpythonmod",

        'server_repo_path': "controlstest/python/dls_testpythonmod",

    },

    {
        'description': "checkout_a_single_module_and_change_branch",

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


class CheckoutEntireAreaTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(CheckoutEntireAreaTest, self).__init__()
        self.ORIGINAL_GIT_ROOT_DIR = os.getenv('GIT_ROOT_DIR')
        self.NEW_GIT_ROOT_DIR = ""

    def runTest(self):
        self.test_checkout_entire_area()

    def setup_module(self):
        """Change environment variable and module variables.

        """

        # The environment variable is set for the use of the script being tested.
        self.NEW_GIT_ROOT_DIR = "controlstest/targetOS/mock_repo"
        os.environ['GIT_ROOT_DIR'] = self.NEW_GIT_ROOT_DIR

        # Set so SystemTest object can use the new variable.
        st.vcs_git.GIT_ROOT_DIR = self.NEW_GIT_ROOT_DIR
        st.vcs_git.pathf.GIT_ROOT_DIR = self.NEW_GIT_ROOT_DIR

    def teardown_module(self):
        """Change environment variable and module variables to the original values.

        """
        os.environ['GIT_ROOT_DIR'] = self.ORIGINAL_GIT_ROOT_DIR
        st.vcs_git.GIT_ROOT_DIR = self.ORIGINAL_GIT_ROOT_DIR
        st.vcs_git.pathf.GIT_ROOT_DIR = self.ORIGINAL_GIT_ROOT_DIR

    def test_checkout_entire_area(self):

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


class CheckoutEntireIOCTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(CheckoutEntireIOCTest, self).__init__()
        self.ORIGINAL_GIT_ROOT_DIR = os.getenv('GIT_ROOT_DIR')
        self.NEW_GIT_ROOT_DIR = ""

    def runTest(self):
        self.test_checkout_entire_ioc_domain()

    def setup_module(self):
        """Change environment variable and module variables.

        """

        # The environment variable is set for the use of the script being tested.
        self.NEW_GIT_ROOT_DIR = "controlstest/targetOS/mock_repo"
        os.environ['GIT_ROOT_DIR'] = self.NEW_GIT_ROOT_DIR

        # Set so SystemTest object can use the new variable.
        st.vcs_git.GIT_ROOT_DIR = self.NEW_GIT_ROOT_DIR
        st.vcs_git.pathf.GIT_ROOT_DIR = self.NEW_GIT_ROOT_DIR

    def teardown_module(self):
        """Change environment variable and module variables to the original values.

        """
        os.environ['GIT_ROOT_DIR'] = self.ORIGINAL_GIT_ROOT_DIR
        st.vcs_git.GIT_ROOT_DIR = self.ORIGINAL_GIT_ROOT_DIR
        st.vcs_git.pathf.GIT_ROOT_DIR = self.ORIGINAL_GIT_ROOT_DIR

    def test_checkout_entire_ioc_domain(self):

        tempdir = tempfile.mkdtemp()
        cwd = os.getcwd()
        os.chdir(tempdir)

        modules = ["controlstest/ioc/BTEST/BTEST-EB-IOC-03",
                   "controlstest/ioc/BTEST/TS"]

        should_not_clone = "controlstest/ioc/BTEST2/TS"

        process = subprocess.Popen("dls-checkout-module.py -i BTEST/".split(),
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   stdin=subprocess.PIPE)

        std_out, std_err = process.communicate()

        logging.debug("Standard out:\n" + std_out)
        logging.debug("Standard error:\n" + std_err)

        for path in modules:
            assert_true(os.path.isdir(path.split('/', 2)[-1]))
            assert_false(os.path.isdir(should_not_clone))

        for path in modules:
            repo = path.split('/', 2)[-1]
            clone = vcs_git.temp_clone(path)
            comp_repo = clone.working_tree_dir

            assert_true(st.check_if_repos_equal(repo, comp_repo))

        os.chdir(cwd)
        shutil.rmtree(tempdir)
