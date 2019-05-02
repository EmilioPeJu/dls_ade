#!/bin/env dls-python

import unittest
from dls_ade import dls_pipfilelock_to_venv
import mock
import os
import shutil
from tempfile import mkdtemp


class PipfilelockToVenv(unittest.TestCase):

    def setUp(self):
        self.starting_dir = os.getcwd()
        self.test_folder = mkdtemp()

    def tearDown(self):
        os.chdir(self.starting_dir)
        shutil.rmtree(self.test_folder)

    def test_system_exits_when_venv_is_already_present(self):
        os.chdir(self.test_folder)
        os.mkdir('lightweight-venv')
        with self.assertRaises(SystemExit) as cm:
            dls_pipfilelock_to_venv.create_venv([], False, False)
        self.assertEqual(cm.exception.args[0], 'lightweight-venv already present!')

    def test_venv_is_created_when_all_deps_are_installed(self):
        os.chdir(self.test_folder)
        path_list = ['/dls_sw/prod/python3/RHEL7-x86_64/numpy/1.16.2/prefix/lib/python3.7/site-packages']
        dls_pipfilelock_to_venv.create_venv(path_list, False, False)
        self.assertTrue(os.path.isdir('lightweight-venv'))

    def test_paths_file_created(self):
        os.chdir(self.test_folder)
        path_list = ['/dls_sw/prod/python3/RHEL7-x86_64/numpy/1.16.2/prefix/lib/python3.7/site-packages']
        dls_pipfilelock_to_venv.create_venv(path_list, False, False)
        file = 'lightweight-venv/lib/python3.7/site-packages/dls-installed-packages.pth'
        self.assertTrue(os.path.isfile(file))


class ConstructPkgPath(unittest.TestCase):

    @mock.patch('dls_ade.dls_pipfilelock_to_venv.python3_module_path')
    def test_path_list_includes_installed_package(self, mock_module_path):
        packages = {
            'pkg1': {'version': '==2.3'}
        }
        mock_module_path.return_value = '/tmp/dummy'
        path_list, missing_packages = dls_pipfilelock_to_venv.construct_pkg_path(packages)
        assert path_list == ['/tmp/dummy/prefix/lib/python3.7/site-packages']
        assert missing_packages == []

    @mock.patch('dls_ade.dls_pipfilelock_to_venv.python3_module_path')
    def test_missing_pkgs_includes_missing_package(self, mock_module_path):
        packages = {
            'pkg1': {'version': '==2.3'}
        }
        mock_module_path.return_value = None
        path_list, missing_packages = dls_pipfilelock_to_venv.construct_pkg_path(packages)
        assert path_list == []
        assert missing_packages == ['pkg1 2.3']
