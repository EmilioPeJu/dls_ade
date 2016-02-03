from dls_ade import path_functions
import unittest
from exceptions import ParsingError

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


def setUpModule():
    path_functions.GIT_ROOT_DIR = "controlstest"


class CheckTechnicalAreaValidTest(unittest.TestCase):

    def test_given_area_not_ioc_then_no_error_raised(self):
        area = "support"
        module = "test_module"

        path_functions.check_technical_area(area, module)

    def test_given_area_ioc_module_split_two_then_no_error_raised(self):
        area = "ioc"
        module = "modules/test_module"

        path_functions.check_technical_area(area, module)

    def test_given_area_ioc_module_split_less_than_two_then_no_error_raised(self):
        area = "ioc"
        module = "test_module"
        expected_error_msg = "Missing technical area under beamline"

        try:
            path_functions.check_technical_area(area, module)
        except ParsingError as error:
            self.assertEqual(error.message, expected_error_msg)


class ModuleAreaTests(unittest.TestCase):

    def test_dev_module(self):

        area = "etc"
        module = "test_module"

        path = path_functions.dev_module_path(module, area)

        self.assertEqual(path, "controlstest/" + area + "/" + module)
