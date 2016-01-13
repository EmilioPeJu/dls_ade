from dls_ade import path_functions
import unittest

GIT_SSH_ROOT = "ssh://dascgitolite@dasc-git.diamond.ac.uk/"


def setUpModule():
    path_functions.GIT_ROOT_DIR = "controlstest"


class AreaTest(unittest.TestCase):

    def test_given_area_then_path_to_area_returned(self):

        area = "any"

        path = path_functions.area(area)

        self.assertEqual(path, "controlstest/" + area)


class ModuleAreaTests(unittest.TestCase):

    def test_devModule(self):

        area = "etc"
        module = "test_module"

        path = path_functions.devModule(module, area)

        self.assertEqual(path, "controlstest/" + area + "/" + module)

    def test_prodModule(self):

        area = "epics"
        module = "test_module"

        path = path_functions.prodModule(module, area)

        self.assertEqual(path, "controlstest/" + area + "/" + module)

    def test_branchModule(self):

        area = "tools"
        module = "test_module"

        path = path_functions.branchModule(module, area)

        self.assertEqual(path, "controlstest/" + area + "/" + module)
