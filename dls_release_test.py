#!/bin/env dls-python

import unittest
import dls_release
# from pkg_resources import require
# require("mock")
# from mock import patch, ANY


class ParserTest(unittest.TestCase):

    def setUp(self):
        self.parser = dls_release.make_parser()

    def tearDown(self):
        pass

    def test_contains_branch_option(self):
        option = self.parser.get_option('-b')
        self.assertEqual(option.action,"store")
        self.assertEqual(option.type,"string")
        self.assertEqual(option.dest,"branch")
        self.assertEqual(option._long_opts[0],"--branch")
        self.assertEqual(option._short_opts[0],"-b")

    def test_contains_force_option(self):
        option = self.parser.get_option('-f')
        self.assertEqual(option.action,"store_true")
        self.assertEqual(option.dest,"force")
        self.assertEqual(option._long_opts[0],"--force")
        self.assertEqual(option._short_opts[0],"-f")

    def test_contains_no_test_build_option(self):
        option = self.parser.get_option('-t')
        self.assertEqual(option.action,"store_true")
        self.assertEqual(option.dest,"skip_test")
        self.assertEqual(option._long_opts[0],"--no-test-build")
        self.assertEqual(option._short_opts[0],"-t")

    def test_contains_local_build_option(self):
        option = self.parser.get_option('-l')
        self.assertEqual(option.action,"store_true")
        self.assertEqual(option.dest,"local_build")
        self.assertEqual(option._long_opts[0],"--local-build-only")
        self.assertEqual(option._short_opts[0],"-l")

    def test_contains_test_build_only_option(self):
        option = self.parser.get_option('-T')
        self.assertEqual(option.action,"store_true")
        self.assertEqual(option.dest,"test_only")
        self.assertEqual(option._long_opts[0],"--test_build-only")
        self.assertEqual(option._short_opts[0],"-T")

    def test_contains_work_build_option(self):
        option = self.parser.get_option("-W")
        self.assertEqual(option.action,"store_true")
        self.assertEqual(option.dest,"work_build")
        self.assertEqual(option._long_opts[0],"--work_build")
        self.assertEqual(option._short_opts[0],"-W")

    def test_contains_epics_version_option(self):
        option = self.parser.get_option('-e')
        self.assertEqual(option.action,"store")
        self.assertEqual(option.type,"string")
        self.assertEqual(option.dest,"epics_version")
        self.assertEqual(option._long_opts[0],'--epics_version')
        self.assertEqual(option._short_opts[0],"-e")

    def test_contains_message_option(self):
        option = self.parser.get_option('-m')
        self.assertEqual(option.action,"store")
        self.assertEqual(option.type,"string")
        self.assertEqual(option.default,"")
        self.assertEqual(option.dest,"message")
        self.assertEqual(option._long_opts[0],'--message')
        self.assertEqual(option._short_opts[0],"-m")

    def test_contains_next_version_option(self):
        option = self.parser.get_option('-n')
        self.assertEqual(option.action,"store_true")
        self.assertEqual(option.dest,"next_version")
        self.assertEqual(option._long_opts[0],'--next_version')
        self.assertEqual(option._short_opts[0],"-n")

    def test_contains_git_option(self):
        option = self.parser.get_option('-g')
        self.assertEqual(option.action,"store_true")
        self.assertEqual(option.dest,"git")
        self.assertEqual(option._long_opts[0],'--git')
        self.assertEqual(option._short_opts[0],"-g")

    def test_contains_rhel_version_option(self):
        option = self.parser.get_option('-r')
        self.assertEqual(option.action,"store")
        self.assertEqual(option.type,"string")
        self.assertEqual(option.dest,"rhel_version")
        self.assertEqual(option._short_opts[0],'-r')
        self.assertEqual(option._long_opts[0],'--rhel_version')

    def test_contains_windows_option(self):
        option = self.parser.get_option('-w')
        self.assertEqual(option.action,"store")
        self.assertEqual(option.type,"string")
        self.assertEqual(option.dest,"windows")
        self.assertEqual(option._short_opts[0],'-w')
        self.assertEqual(option._long_opts[0],'--windows')


class TestCreateBuildObject(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @patch('dls_release.dlsbuild.default_build')
    def test_given_default_args_then_default_build(self, mock_default):
            something_that_would_call_it()

            self.assertTrue(mock_default.called)
            mock_default.assertCalledOnceWith("3.14.12.3") # can be 'ANY' in argument (not in quotes) 

# class TestDLSRelease(unittest.TestCase):

#     def setUp(self):
#         pass

#     def tearDown(self):
#         pass

    # variable = 5
    # def setUp(self):
    #     with patch('moduleb.Class1') as mock_class1:
    #         self.b_to_test = b()
    #         self.x.boo = MagicMock(return_value=10)
    #         self..y = stub_class2()

    #     self.object = 5

    # def test_svn_commit_is_called(self):
    #     with patch('vcs_svn.commit') as mock_commit:
    #         do_somthing_that_should_commit(...)

    #         self.assetTrue(mock_commit.called)
    #         mock_commit.assertCalledOnceWith('root', ANY)


    # def test_sanity(self):
    #     self.assertTrue(self.variable==5)

    # def test_release_dry_run_with_test_build(self):
    #     assert(MockFoo().submit('1','2','3'))


    # @patch('dls_releas.ls')
    # @patch('vcs_svn.update')
    # @patch('vcs_svn.commit')
    # def  test_svn_commit_is_called_with_BRIAN(self, mock_commit, _, mock_ls):

    #         do_somthing_that_should_commit(...)

    #         self.assetTrue(mock_commit.called)
    #         mock_commit.assertCalledOnceWith('root', 'BRIAN')


# class MockFoo(object):
#     def submit(self, rel_dir, module, version, test=None):
#         try:
#             assert("svn" in rel_dir.lower())
#             assert(module == "dummy")
#             assert(version[:2] == "1-")
#             assert(test)
#         except AssertionError:
#             return False
#         return True

    # def test(self, src_dir, module, version):
    #     try:
    #         assert("svn" in rel_dir.lower())
    #         assert()


if __name__ == '__main__':

    unittest.main()


    # class b(object)
    #  def __init__(self)
    #     self.x = Class1()
    #     self.y = Class2()
    #     ...

    # class stub_class2(object)
    #     def thismethd():
    #         counter++
    #         return counter