#!/bin/env dls-python

import unittest
from dls_ade import dls_populate_dist
import os
from tempfile import mkdtemp

class PopulateDist(unittest.TestCase):

    lockfile = '''{
    "_meta": {
        "hash": {
            "sha256": "bc7e66f6a26742e21d302e533ffeb1e4665a7a5e43d6d51b4f3be34fab2cfc5e"
        },
        "pipfile-spec": 6,
        "requires": {
            "python_version": "3.7"
        },
        "sources": [
            {
                "name": "pypi",
                "url": "https://pypi.org/simple",
                "verify_ssl": true
            }
        ]
    },
    "default": {
        "numpy": {
            "hashes": [
                "sha256:1980f8d84548d74921685f68096911585fee393975f53797614b34d4f409b6da"
            ],
            "index": "pypi",
            "version": "==1.16.2"
        }
    },
    "develop": {}
}'''

    def setUp(self):
        self.test_folder = mkdtemp()
        os.environ['TESTING_ROOT'] = self.test_folder

    def tearDown(self):
        pass

    def test_ensure_script_exits_when_no_lockfile_present(self):
        os.chdir(self.test_folder)
        with self.assertRaises(SystemExit) as cm:
            dls_populate_dist.populate_dist(self.test_folder)
        self.assertEqual(cm.exception.args[0], 'Job aborted: Pipfile.lock was not found!')

    def test_ensure_wheel_is_downloaded(self):
        os.chdir(self.test_folder)
        with open('Pipfile.lock', 'w') as f:
            f.write(PopulateDist.lockfile)
        dls_populate_dist.populate_dist(self.test_folder)
        myfiles = os.listdir(self.test_folder)
        target_wheel = 'numpy-1.16.2-cp37-cp37m-manylinux1_x86_64.whl'
        assert target_wheel in myfiles

    def test_populate_dist_returns_item(self):
        os.chdir(self.test_folder)
        with open('Pipfile.lock', 'w') as f:
            f.write(PopulateDist.lockfile)
        item = dls_populate_dist.populate_dist(self.test_folder)
        self.assertEqual(item[0], 'numpy 1.16.2')
