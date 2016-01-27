from dls_ade import path_functions
import unittest

GIT_SSH_ROOT = "ssh://dascgitolite@dasc-git.diamond.ac.uk/"


class RemoveEndSlash(unittest.TestCase):

    def test_given_empty_string_then_return(self):
        test_string = ""

        new_string = path_functions.remove_end_slash(test_string)

        self.assertEqual(new_string, "")

    def test_given_path_slash_then_removed_and_returned(self):
        path = "controls/area/module/"

        new_path = path_functions.remove_end_slash(path)

        self.assertEqual(new_path, "controls/area/module")

    def test_given_path_no_slash_then_returned(self):
        path = "controls/area/module"

        new_path = path_functions.remove_end_slash(path)

        self.assertEqual(new_path, path)


class CheckTechnicalAreaTest(unittest.TestCase):

    def test_given_area_not_ioc_then_no_error_raised(self):
        area = "support"
        module = "test_module"

        path_functions.check_technical_area_valid(area, module)

    def test_given_area_ioc_module_split_two_then_no_error_raised(self):
        area = "ioc"
        module = "modules/test_module"

        path_functions.check_technical_area_valid(area, module)

    def test_given_area_ioc_module_split_less_than_two_then_no_error_raised(self):
        area = "ioc"
        module = "test_module"
        expected_error_msg = "Missing Technical Area Under Beamline"

        try:
            path_functions.check_technical_area_valid(area, module)
        except Exception as error:
            self.assertEqual(error.message, expected_error_msg)


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
