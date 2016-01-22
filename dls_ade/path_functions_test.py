from dls_ade import path_functions
import unittest
from exceptions import ParsingError

GIT_SSH_ROOT = "ssh://dascgitolite@dasc-git.diamond.ac.uk/"


def setUpModule():
    path_functions.GIT_ROOT_DIR = "controlstest"


class CheckTechnicalAreaValidTest(unittest.TestCase):

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
        expected_error_msg = "Missing technical area under beamline"

        try:
            path_functions.check_technical_area_valid(area, module)
        except ParsingError as error:
            self.assertEqual(error.message, expected_error_msg)


class ModuleAreaTests(unittest.TestCase):

    def test_dev_module(self):

        area = "etc"
        module = "test_module"

        path = path_functions.dev_module_path(module, area)

        self.assertEqual(path, "controlstest/" + area + "/" + module)
