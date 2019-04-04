#!/bin/env dls-python

import unittest
from dls_ade import dls_populate_dist
import os
from tempfile import mkdtemp

class PopulateDist(unittest.TestCase):

    lockfile = '{\n    "_meta": {\n        "hash": {\n            "sha256": "bc7e66f6a26742e21d302e533ffeb1e4665a7a5e43d6d51b4f3be34fab2cfc5e"\n        },\n        "pipfile-spec": 6,\n        "requires": {\n            "python_version": "3.7"\n        },\n        "sources": [\n            {\n                "name": "pypi",\n                "url": "https://pypi.org/simple",\n                "verify_ssl": true\n            }\n        ]\n    },\n    "default": {\n        "numpy": {\n            "hashes": [\n                "sha256:1980f8d84548d74921685f68096911585fee393975f53797614b34d4f409b6da",\n                "sha256:22752cd809272671b273bb86df0f505f505a12368a3a5fc0aa811c7ece4dfd5c",\n                "sha256:23cc40313036cffd5d1873ef3ce2e949bdee0646c5d6f375bf7ee4f368db2511",\n                "sha256:2b0b118ff547fecabc247a2668f48f48b3b1f7d63676ebc5be7352a5fd9e85a5",\n                "sha256:3a0bd1edf64f6a911427b608a894111f9fcdb25284f724016f34a84c9a3a6ea9",\n                "sha256:3f25f6c7b0d000017e5ac55977a3999b0b1a74491eacb3c1aa716f0e01f6dcd1",\n                "sha256:4061c79ac2230594a7419151028e808239450e676c39e58302ad296232e3c2e8",\n                "sha256:560ceaa24f971ab37dede7ba030fc5d8fa173305d94365f814d9523ffd5d5916",\n                "sha256:62be044cd58da2a947b7e7b2252a10b42920df9520fc3d39f5c4c70d5460b8ba",\n                "sha256:6c692e3879dde0b67a9dc78f9bfb6f61c666b4562fd8619632d7043fb5b691b0",\n                "sha256:6f65e37b5a331df950ef6ff03bd4136b3c0bbcf44d4b8e99135d68a537711b5a",\n                "sha256:7a78cc4ddb253a55971115f8320a7ce28fd23a065fc33166d601f51760eecfa9",\n                "sha256:80a41edf64a3626e729a62df7dd278474fc1726836552b67a8c6396fd7e86760",\n                "sha256:893f4d75255f25a7b8516feb5766c6b63c54780323b9bd4bc51cdd7efc943c73",\n                "sha256:972ea92f9c1b54cc1c1a3d8508e326c0114aaf0f34996772a30f3f52b73b942f",\n                "sha256:9f1d4865436f794accdabadc57a8395bd3faa755449b4f65b88b7df65ae05f89",\n                "sha256:9f4cd7832b35e736b739be03b55875706c8c3e5fe334a06210f1a61e5c2c8ca5",\n                "sha256:adab43bf657488300d3aeeb8030d7f024fcc86e3a9b8848741ea2ea903e56610",\n                "sha256:bd2834d496ba9b1bdda3a6cf3de4dc0d4a0e7be306335940402ec95132ad063d",\n                "sha256:d20c0360940f30003a23c0adae2fe50a0a04f3e48dc05c298493b51fd6280197",\n                "sha256:d3b3ed87061d2314ff3659bb73896e622252da52558f2380f12c421fbdee3d89",\n                "sha256:dc235bf29a406dfda5790d01b998a1c01d7d37f449128c0b1b7d1c89a84fae8b",\n                "sha256:fb3c83554f39f48f3fa3123b9c24aecf681b1c289f9334f8215c1d3c8e2f6e5b"\n            ],\n            "index": "pypi",\n            "version": "==1.16.2"\n        }\n    },\n    "develop": {}\n}\n'

    def setUp(self):
        self.test_folder = mkdtemp()
        dls_populate_dist.WORK_DIST_DIR = self.test_folder
        dls_populate_dist.CENTRAL_LOCATION = self.test_folder

    def tearDown(self):
        pass

    def test_conversion_from_dash_to_underscore_is_ok(self):
        package, version = 'module-name', '1-2-3'
        test_list = dls_populate_dist.format_pkg_name(package, version)
        test_module_name = test_list.split()[0]
        self.assertEqual(test_module_name, 'module_name')

    def test_ensure_missing_pkgs_list_correctly_filled_with_items(self):
        package, version = 'module-name', '==1-2-3'
        test_item = dls_populate_dist.format_pkg_name(package, version)
        self.assertEqual(test_item, 'module_name 1-2-3')

    def test_ensure_script_exits_when_no_lockfile_present(self):
        os.chdir(self.test_folder)
        with self.assertRaises(SystemExit) as cm:
            dls_populate_dist.populate_dist(self.test_folder, self.test_folder)
        self.assertEqual(cm.exception.args[0], 'Job aborted: Pipfile.lock was not found!')

    def test_ensure_wheel_is_downloaded(self):
        os.chdir(self.test_folder)
        with open('Pipfile.lock', 'w') as f:
            f.write(PopulateDist.lockfile)
        dls_populate_dist.populate_dist(self.test_folder, self.test_folder)
        myfiles = os.listdir(self.test_folder)
        target_wheel = 'numpy-1.16.2-cp37-cp37m-manylinux1_x86_64.whl'
        assert target_wheel in myfiles

    def test_populate_dist_returns_item(self):
        os.chdir(self.test_folder)
        with open('Pipfile.lock', 'w') as f:
            f.write(PopulateDist.lockfile)
        item = dls_populate_dist.populate_dist(self.test_folder, self.test_folder)
        self.assertEqual(item[0], 'numpy 1.16.2')
