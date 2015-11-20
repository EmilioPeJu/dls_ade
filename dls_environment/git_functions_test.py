import git_functions as gitf
import unittest

GIT_ROOT = "ssh://dascgitolite@dasc-git.diamond.ac.uk/"


class GitRootAreaTest(unittest.TestCase):

    def test_given_area_etc_then_path_to_prod(self):
        type = "branches"
        area = "etc"

        path = gitf.area(type, area)

        self.assertEqual(path, GIT_ROOT + area + "/" + type + "/prod")

    def test_given_area_epics_then_path_to_type(self):
        type = "branches"
        area = "epics"

        path = gitf.area(type, area)

        self.assertEqual(path, GIT_ROOT + area + "/" + type)

    def test_given_area_tools_then_path_to_build_scripts(self):
        type = "branches"
        area = "tools"

        path = gitf.area(type, area)

        self.assertEqual(path, GIT_ROOT + "diamond/" + type + "/build_scripts")

    def test_given_area_tools_then_path_to_area(self):
        type = "branches"
        area = "other"

        path = gitf.area(type, area)

        self.assertEqual(path, GIT_ROOT + "diamond/" + type + "/" + area)


class GitAreaModuleTest(unittest.TestCase):

    def test_devModule(self):

        area = "etc"
        module = "test_module"

        path = gitf.devModule(module, area)

        self.assertEqual(path, GIT_ROOT + area + "/trunk/prod/" + module)

    def test_prodModule(self):

        area = "epics"
        module = "test_module"

        path = gitf.prodModule(module, area)

        self.assertEqual(path, GIT_ROOT + area + "/release/" + module)

    def test_branchModule(self):

        area = "tools"
        module = "test_module"

        path = gitf.branchModule(module, area)

        self.assertEqual(path, GIT_ROOT + "diamond/branches/build_scripts/" + module)

    def test_vendorModule(self):

        area = "other"
        module = "test_module"

        path = gitf.vendorModule(module, area)

        self.assertEqual(path, GIT_ROOT + "diamond/vendor/" + area + "/" + module)