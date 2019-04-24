import mock
import unittest
from dls_ade.dls_python3_check import compare_requirements, get_tags_on_head


class CompareRequirements(unittest.TestCase):

    def test_compare_requirements_accepts_identical_lists(self):
        requirements = ['a==1', 'b>=1.3', 'c~=3.4']
        self.assertTrue(compare_requirements(requirements, requirements))

    def test_compare_requirements_refuses_different_length_lists(self):
        req1 = ['a', 'b']
        req2 = ['a']
        self.assertFalse(compare_requirements(req1, req2))

    def test_compare_requirements_accepts_unordered_lists(self):
        req1 = ['a==1', 'b<=3.4']
        req2 = ['b<=3.4', 'a==1']
        self.assertTrue(compare_requirements(req1, req2))

    def test_compare_requirements_refuses_different_specifiers(self):
        req1 = ['b<=3.4']
        req2 = ['b==3.4']
        self.assertFalse(compare_requirements(req1, req2))


class GetTagsOnHead(unittest.TestCase):

    def test_get_tags_on_head_returns_True_if_matching_tag(self):
        DUMMY_COMMIT = 'abcdef'
        TAG_NAME = '1.0'
        repo = mock.MagicMock()
        repo.head.commit = DUMMY_COMMIT
        head_tag = mock.MagicMock()
        head_tag.name = TAG_NAME
        head_tag.commit = DUMMY_COMMIT
        repo.tags = [head_tag, mock.MagicMock()]
        self.assertEqual(get_tags_on_head(repo), [TAG_NAME])
