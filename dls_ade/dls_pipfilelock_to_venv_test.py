#!/bin/env dls-python

import unittest
from dls_ade import dls_pipfilelock_to_venv
from collections import OrderedDict
import os
import shutil
from tempfile import mkdtemp

class PipfilelockToVenv(unittest.TestCase):

    def setUp(self):
        self.test_folder = mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_folder)

    def test_path_list_is_constructed_correctly(self):
        test_dict = OrderedDict([(u'numpy', OrderedDict([(u'hashes', \
        [ u'sha256:d3b3ed87061d2314ff3659bb73896e622252da52558f2380f12c421f\
        bdee3d89', u'sha256:dc235bf29a406dfda5790d01b998a1c01d7d37f449128c0\
        b1b7d1c89a84fae8b', u'sha256:fb3c83554f39f48f3fa3123b9c24aecf681b1c\
        289f9334f8215c1d3c8e2f6e5b']), (u'index', u'pypi'), (u'version', u'==1.16.2')]))])
        path_list = dls_pipfilelock_to_venv.construct_pkg_path(test_dict)
        target_path = '/dls_sw/prod/python3/RHEL7-x86_64/numpy/1.16.2/prefix/lib/python3.7/site-packages'
        self.assertEqual(path_list[0], target_path)

    def test_system_exits_when_venv_is_already_present(self):
        os.chdir(self.test_folder)
        os.mkdir('lightweight-venv')
        with self.assertRaises(SystemExit) as cm:
            dls_pipfilelock_to_venv.create_venv([],[])
        self.assertEqual(cm.exception.args[0], 'lightweight-venv already present!')

    def test_venv_is_created_when_all_deps_are_installed(self):
        os.chdir(self.test_folder)
        absent_pkg_list = []
        path_list = ['/dls_sw/prod/python3/RHEL7-x86_64/numpy/1.16.2/prefix/lib/python3.7/site-packages']
        dls_pipfilelock_to_venv.create_venv(absent_pkg_list, path_list)
        self.assertTrue(os.path.isdir('lightweight-venv'))

    def test_paths_file_created_correctly(self):
        os.chdir(self.test_folder)
        absent_pkg_list = []
        path_list = ['/dls_sw/prod/python3/RHEL7-x86_64/numpy/1.16.2/prefix/lib/python3.7/site-packages']
        dls_pipfilelock_to_venv.create_venv(absent_pkg_list, path_list)
        file = 'lightweight-venv/lib/python3.7/site-packages/dls-installed-packages.pth'
        self.assertTrue(os.path.isfile(file))