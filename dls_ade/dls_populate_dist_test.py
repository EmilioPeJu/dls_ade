#!/bin/env dls-python

import unittest
from dls_ade import dls_populate_dist as pdist
import os

class PopulateDist(unittest.TestCase):

    def setUp(self):
        pass

    def test_conversion_from_dash_to_underscore_is_ok(self):
        package, version = 'module-name', '1-2-3'
        test_list = pdist.format_pkg_name(package, version)
        test_module_name = test_list.split()[0]
        self.assertEqual(test_module_name, 'module_name')

    def test_ensure_missing_pkgs_list_correctly_filled_with_items(self):
        package, version = 'module-name', '==1-2-3'
        test_item = pdist.format_pkg_name(package, version)
        self.assertEqual(test_item, 'module_name 1-2-3')

    def test_ensure_wheel_is_downloaded(self):
        test_lockfile_path = '/dls_sw/work/python3/unit-testing'
        os.chdir(test_lockfile_path)
        pdist.populate_dist()
        myfiles = os.listdir('/dls_sw/work/python3/distributions')
        target_wheel = 'numpy-1.16.2-cp37-cp37m-manylinux1_x86_64.whl'
        assert target_wheel in myfiles

    def test_populate_dist_returns_item(self):
        test_lockfile_path = '/dls_sw/work/python3/unit-testing'
        os.chdir(test_lockfile_path)
        commands = pdist.populate_dist()
        assert commands[0] == 'numpy 1.16.2'
