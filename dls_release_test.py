#!/bin/env dls-python

import unittest
import dls_release
from pkg_resources import require
require("mock")
from mock import patch, ANY


class ParserTest(unittest.TestCase):

    def setUp(self):
        self.parser = dls_release.make_parser()

    def test_contains_branch_option(self):
        self.assertTrue(self.parser.has_option('-b'))
        self.assertTrue(self.parser.has_option('--branch'))


class TestDLSRelease(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

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