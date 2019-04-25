#!/bin/env dls-python

import unittest
from dls_ade import dls_pipfilelock_to_venv
from collections import OrderedDict
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
