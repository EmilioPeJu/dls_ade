#!/bin/env dls-python

import unittest
import dls_release
from pkg_resources import require
require("mock")
from mock import patch, ANY


class ParserTest(unittest.TestCase):

    def setUp(self):
        self.parser = dls_release.make_parser()

    def tearDown(self):
        pass

    def test_branch_option_has_correct_attributes(self):
        option = self.parser.get_option('-b')
        self.assertEqual(option.action,"store")
        self.assertEqual(option.type,"string")
        self.assertEqual(option.dest,"branch")
        self.assertEqual(option._long_opts[0],"--branch")

    def test_force_option_has_correct_attributes(self):
        option = self.parser.get_option('-f')
        self.assertEqual(option.action,"store_true")
        self.assertEqual(option.dest,"force")
        self.assertEqual(option._long_opts[0],"--force")

    def test_no_test_build_option_has_correct_attributes(self):
        option = self.parser.get_option('-t')
        self.assertEqual(option.action,"store_true")
        self.assertEqual(option.dest,"skip_test")
        self.assertEqual(option._long_opts[0],"--no-test-build")

    def test_local_build_option_has_correct_attributes(self):
        option = self.parser.get_option('-l')
        self.assertEqual(option.action,"store_true")
        self.assertEqual(option.dest,"local_build")
        self.assertEqual(option._long_opts[0],"--local-build-only")

    def test_test_build_only_option_has_correct_attributes(self):
        option = self.parser.get_option('-T')
        self.assertEqual(option.action,"store_true")
        self.assertEqual(option.dest,"test_only")
        self.assertEqual(option._long_opts[0],"--test_build-only")

    def test_work_build_option_has_correct_attributes(self):
        option = self.parser.get_option("-W")
        self.assertEqual(option.action,"store_true")
        self.assertEqual(option.dest,"work_build")
        self.assertEqual(option._long_opts[0],"--work_build")

    def test_epics_version_option_has_correct_attributes(self):
        option = self.parser.get_option('-e')
        self.assertEqual(option.action,"store")
        self.assertEqual(option.type,"string")
        self.assertEqual(option.dest,"epics_version")
        self.assertEqual(option._long_opts[0],'--epics_version')

    def test_message_option_has_correct_attributes(self):
        option = self.parser.get_option('-m')
        self.assertEqual(option.action,"store")
        self.assertEqual(option.type,"string")
        self.assertEqual(option.default,"")
        self.assertEqual(option.dest,"message")
        self.assertEqual(option._long_opts[0],'--message')

    def test_next_version_option_has_correct_attributes(self):
        option = self.parser.get_option('-n')
        self.assertEqual(option.action,"store_true")
        self.assertEqual(option.dest,"next_version")
        self.assertEqual(option._long_opts[0],'--next_version')

    def test_git_option_has_correct_attributes(self):
        option = self.parser.get_option('-g')
        self.assertEqual(option.action,"store_true")
        self.assertEqual(option.dest,"git")
        self.assertEqual(option._long_opts[0],'--git')

    def test_rhel_version_option_has_correct_attributes(self):
        option = self.parser.get_option('-r')
        self.assertEqual(option.action,"store")
        self.assertEqual(option.type,"string")
        self.assertEqual(option.dest,"rhel_version")
        self.assertEqual(option._long_opts[0],'--rhel_version')

    def test_windows_option_has_correct_attributes(self):
        option = self.parser.get_option('-w')
        self.assertEqual(option.action,"store")
        self.assertEqual(option.type,"string")
        self.assertEqual(option.dest,"windows")
        
    def test_has_windows_option_with_short_name_w_long_name_windows(self):
        option = self.parser.get_option('-w')
        self.assertIsNotNone(option)
        self.assertEqual(option._long_opts[0],'--windows')


class TestCreateBuildObject(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @patch('dls_release.dlsbuild.default_build')
    def test_given_empty_options_then_default_build_called_with_None(self, mock_default):

        options = FakeOptions()
        dls_release.create_build_object(options)

        self.assertTrue(mock_default.called)
        mock_default.assert_called_once_with(None)


    @patch('dls_release.dlsbuild.default_build')
    def test_given_epicsversion_then_default_build_called_with_epics_version(self, mock_default):
        version = "R3.14.12.3"

        options = FakeOptions(epics_version=version)

        dls_release.create_build_object(options)

        mock_default.assert_called_once_with(version)

    @patch('dls_release.dlsbuild.RedhatBuild')
    def test_given_rhel_version_then_RedhatBuild_called_with_rhel_and_epics_version(self, mock_default):
        rhel_version = "25"

        options = FakeOptions(rhel_version=rhel_version)

        dls_release.create_build_object(options)

        mock_default.assert_called_once_with(rhel_version,None)

    @patch('dls_release.dlsbuild.RedhatBuild')
    def test_given_rhel_version_then_RedhatBuild_called_with_rhel_and_epics_version(self, mock_build):
        rhel_version = "25"
        epics_version = "R3.14.12.3"

        options = FakeOptions(
            rhel_version=rhel_version,
            epics_version=epics_version)

        dls_release.create_build_object(options)

        mock_build.assert_called_once_with(rhel_version,epics_version)

    @patch('dls_release.dlsbuild.WindowsBuild')
    def test_given_windows_option_without_rhel_then_WindowsBuild_called_with_windows_and_epics_version(self, mock_build):
        windows = 'xp'

        options = FakeOptions(windows=windows)

        dls_release.create_build_object(options)

        mock_build.assert_called_once_with(windows,None)

    @patch('dls_release.dlsbuild.Builder.set_area')
    def test_given_any_option_then_set_area_called_with_default_area_option(self, mock_set):
        options = FakeOptions()

        dls_release.create_build_object(options)

        mock_set.assert_called_once_with(options.area)

    @patch('dls_release.dlsbuild.Builder.set_area')
    def test_given_area_option_then_set_area_called_with_given_area_option(self, mock_set):
        area = 'python'

        options = FakeOptions(area=area)

        dls_release.create_build_object(options)

        mock_set.assert_called_once_with(options.area)

    @patch('dls_release.dlsbuild.Builder.set_force')
    def test_given_any_option_then_set_force_called_with_default_force_option(self, mock_set):
        options = FakeOptions()

        dls_release.create_build_object(options)

        mock_set.assert_called_once_with(None)

    @patch('dls_release.dlsbuild.Builder.set_force')
    def test_given_force_option_then_set_force_called_with_given_force_option(self, mock_set):
        force = True    
        options = FakeOptions(force=force)

        dls_release.create_build_object(options)

        mock_set.assert_called_once_with(True)


class FakeOptions(object):
    def __init__(self,**kwargs):
        self.rhel_version = kwargs.get('rhel_version',None)
        self.epics_version = kwargs.get('epics_version',None)
        self.windows = kwargs.get('windows',None)
        self.area = kwargs.get('area','support')
        self.force = kwargs.get('force',None)

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
