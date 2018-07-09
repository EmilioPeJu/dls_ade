import unittest
from contextlib import contextmanager
from dls_ade.exceptions import ParsingError
from dls_ade.tag_utility import check_tag_is_valid


class TagFormatTest(unittest.TestCase):

    @contextmanager
    def assertNotRaises(self, exc_type):
        try:
            yield None
        except exc_type:
            raise self.failureException('{} raised'.format(exc_type.__name__))

    def test_approves_correct_tags(self):

        ex_valid_tags = ['2-51', '21-5-3', '2-5dls1', '2-5dls2-3']
        for ex_valid_tag in ex_valid_tags:
            with self.assertNotRaises(ParsingError):
                check_tag_is_valid(ex_valid_tag)

    def test_rejects_incorrect_tags(self):

        ex_invalid_tags = ['2-5a', 'abcdef']
        for ex_invalid_tag in ex_invalid_tags:
            with self.assertRaises(ParsingError):
                check_tag_is_valid(ex_invalid_tag)