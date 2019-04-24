#!/bin/env dls-python

import unittest
from dls_ade import dls_populate_dist
import mock
import os
import shutil
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
        self.starting_dir = os.getcwd()
        self.test_folder = mkdtemp()
        os.chdir(self.test_folder)
        os.environ['TESTING_ROOT'] = self.test_folder
        self.os_dir = os.path.join(self.test_folder, 'dls_sw/prod/python3/RHEL7-x86_64')
        os.makedirs(self.os_dir)

    def tearDown(self):
        os.chdir(self.starting_dir)
        shutil.rmtree(self.test_folder)

    def test_ensure_script_exits_when_no_lockfile_present(self):
        with self.assertRaises(SystemExit) as cm:
            dls_populate_dist.populate_dist(self.test_folder)
        self.assertEqual(cm.exception.args[0], 'Job aborted: Pipfile.lock was not found!')

    @mock.patch('subprocess.check_call')
    def test_ensure_pip_command_is_called(self, mock_check_call):
        with open('Pipfile.lock', 'w') as f:
            f.write(PopulateDist.lockfile)
        dls_populate_dist.populate_dist(self.test_folder)
        wheel_dir = '--wheel-dir={}'.format(self.test_folder)
        specifier = 'numpy==1.16.2'
        expected_pip_command = dls_populate_dist.PIP_COMMAND + [
            wheel_dir, specifier
        ]
        mock_check_call.assert_called_once_with(expected_pip_command)

    @mock.patch('subprocess.check_call')
    def test_populate_dist_returns_item(self, _):
        with open('Pipfile.lock', 'w') as f:
            f.write(PopulateDist.lockfile)
        item = dls_populate_dist.populate_dist(self.test_folder)
        self.assertEqual(item[0], 'numpy 1.16.2')

    def test_populate_dist_returns_nothing_when_package_installed(self):
        with open('Pipfile.lock', 'w') as f:
            f.write(PopulateDist.lockfile)
        os.makedirs('dls_sw/prod/python3/RHEL7-x86_64/numpy/1.16.2/prefix')
        item = dls_populate_dist.populate_dist(self.test_folder)
        self.assertFalse(item)
