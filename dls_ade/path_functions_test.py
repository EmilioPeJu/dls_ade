from dls_ade import path_functions
import unittest

GIT_SSH_ROOT = "ssh://dascgitolite@dasc-git.diamond.ac.uk/"


class RootTest(unittest.TestCase):

    def test_return_value(self):
        self.assertEqual(path_functions.root(), GIT_SSH_ROOT)


class AreaTest(unittest.TestCase):

    def test_given_area_etc_then_path_to_prod(self):
        area = "etc"

        path = path_functions.area(area)

        self.assertEqual(path, GIT_SSH_ROOT + area + "/prod")

    def test_given_area_epics_then_path_to_type(self):
        area = "epics"

        path = path_functions.area(area)

        self.assertEqual(path, GIT_SSH_ROOT + area)

    def test_given_area_other_then_path_to_area(self):
        area = "other"

        path = path_functions.area(area)

        self.assertEqual(path, "controlstest/" + area)


class ModuleAreaTests(unittest.TestCase):

    def test_devModule(self):

        area = "etc"
        module = "test_module"

        path = path_functions.devModule(module, area)

        self.assertEqual(path, GIT_SSH_ROOT + area + "/prod/" + module)

    def test_prodModule(self):

        area = "epics"
        module = "test_module"

        path = path_functions.prodModule(module, area)

        self.assertEqual(path, GIT_SSH_ROOT + area + "/" + module)

    def test_branchModule(self):

        area = "tools"
        module = "test_module"

        path = path_functions.branchModule(module, area)

        self.assertEqual(path, "controlstest/" + area + "/" + module)
