from dls_ade import dls_utilities
import unittest

from dls_ade.exceptions import ParsingError

from dls_ade.dls_utilities import check_tag_is_valid


class TagFormatTest(unittest.TestCase):

    def test_approves_correct_tags(self):
        ex_valid_tags = ['2-51', '21-5-3', '2-5dls1', '2-5dls2-3']
        for ex_valid_tag in ex_valid_tags:
            self.assertTrue(check_tag_is_valid(ex_valid_tag))

    def test_rejects_incorrect_tags(self):
        ex_invalid_tags = ['2-5a', 'abcdef']
        for ex_invalid_tag in ex_invalid_tags:
            self.assertFalse(check_tag_is_valid(ex_invalid_tag))

    def test_approves_correct_python3_tags(self):
        valid_python3_tags = ['1.2', '1.2.3rc4', '1.2+dls3']
        for tag in valid_python3_tags:
            self.assertTrue(check_tag_is_valid(tag, 'python3'))

    def test_rejects_incorrect_python3_tags(self):
        invalid_python3_tags = ['aaa', '1.2.3xrc4', '1.2dls3']
        for tag in invalid_python3_tags:
            print(tag)
            self.assertFalse(check_tag_is_valid(tag, 'python3'))


class RemoveEndSlash(unittest.TestCase):

    def test_given_empty_string_then_return(self):
        test_string = ""

        new_string = dls_utilities.remove_end_slash(test_string)

        self.assertEqual(new_string, "")

    def test_given_path_slash_then_removed_and_returned(self):
        path = "controls/area/module/"

        new_path = dls_utilities.remove_end_slash(path)

        self.assertEqual(new_path, "controls/area/module")

    def test_given_path_no_slash_then_returned(self):
        path = "controls/area/module"

        new_path = dls_utilities.remove_end_slash(path)

        self.assertEqual(new_path, path)


class CheckTechnicalAreaValidTest(unittest.TestCase):

    def test_given_area_not_ioc_then_no_error_raised(self):
        area = "support"
        module = "test_module"

        dls_utilities.check_technical_area(area, module)

    def test_given_area_ioc_module_split_two_then_no_error_raised(self):
        area = "ioc"
        module = "modules/test_module"

        dls_utilities.check_technical_area(area, module)

    def test_given_area_ioc_module_split_less_than_two_then_no_error_raised(self):
        area = "ioc"
        module = "test_module"
        expected_error_msg = "Missing technical area under beamline"

        try:
            dls_utilities.check_technical_area(area, module)
        except ParsingError as error:
            self.assertEqual(str(error), expected_error_msg)
