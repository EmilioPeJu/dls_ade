#!/bin/env dls-python

import unittest
from pkg_resources import require
require("mock")
from mock import patch, ANY
import vcs_git


class GitClassTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass
        

if __name__ == '__main__':

    unittest.main()