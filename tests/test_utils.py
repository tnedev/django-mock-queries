from mock import patch, MagicMock
from unittest import TestCase

from django_mock_queries import utils, constants


class TestUtils(TestCase):
    def test_merge_concatenates_lists(self):
        l1 = [1, 2, 3]
        l2 = [4, 5, 6]
        result = utils.merge(l1, l2)
        for x in (l1 + l2):
            assert x in result

    def test_merge_eliminates_duplicate_entries(self):
        l1 = [1, 2]
        l2 = [2, 3]
        result = utils.merge(l1, l2)
        for x in (l1 + l2):
            assert result.count(x) == 1

    def test_intersect_creates_list_with_common_elements(self):
        l1 = [1, 2]
        l2 = [2, 3]
        result = utils.intersect(l1, l2)
        for x in (l1 + l2):
            if x in l1 and x in l2:
                assert x in result
            else:
                assert x not in result

    def test_get_attribute_returns_value_with_default_comparison(self):
        obj = MagicMock(foo='test')
        value, comparison = utils.get_attribute(obj, 'foo')
        assert value == 'test'
        assert comparison is None

    def test_get_attribute_returns_value_with_defined_comparison(self):
        obj = MagicMock(foo='test')
        value, comparison = utils.get_attribute(obj, 'foo__' + constants.COMPARISON_IEXACT)
        assert value == 'test'
        assert comparison == constants.COMPARISON_IEXACT

    def test_get_attribute_returns_nested_object_value(self):
        obj = MagicMock(child=MagicMock(foo='test'))
        value, comparison = utils.get_attribute(obj, 'child__foo__' + constants.COMPARISON_IEXACT)
        assert value == 'test'
        assert comparison == constants.COMPARISON_IEXACT

    def test_get_attribute_returns_default_value_when_object_is_none(self):
        obj = None
        default_value = ''
        value, comparison = utils.get_attribute(obj, 'foo', default_value)
        assert value == default_value
        assert comparison is None

    def test_is_match_equality_check_when_comparison_none(self):
        result = utils.is_match(1, 1)
        assert result is True

        result = utils.is_match('a', 'a')
        assert result is True

        result = utils.is_match(1, '1')
        assert result is False

    def test_is_match_case_insensitive_equality_check(self):
        result = utils.is_match('a', 'A', constants.COMPARISON_IEXACT)
        assert result is True

    def test_is_match_greater_than_value_check(self):
        result = utils.is_match(5, 3, constants.COMPARISON_GT)
        assert result is True

        result = utils.is_match(3, 5, constants.COMPARISON_GT)
        assert result is False

    def test_is_match_greater_than_equal_to_value_check(self):
        result = utils.is_match(5, 3, constants.COMPARISON_GTE)
        assert result is True

        result = utils.is_match(5, 5, constants.COMPARISON_GTE)
        assert result is True

        result = utils.is_match(3, 5, constants.COMPARISON_GTE)
        assert result is False

    def test_is_match_less_than_value_check(self):
        result = utils.is_match(1, 2, constants.COMPARISON_LT)
        assert result is True

        result = utils.is_match(2, 2, constants.COMPARISON_LT)
        assert result is False

    def test_is_match_less_than_equal_to_value_check(self):
        result = utils.is_match(1, 2, constants.COMPARISON_LTE)
        assert result is True

        result = utils.is_match(1, 1, constants.COMPARISON_LTE)
        assert result is True

        result = utils.is_match(2, 1, constants.COMPARISON_LTE)
        assert result is False

    @patch('django_mock_queries.utils.get_attribute')
    @patch('django_mock_queries.utils.is_match', MagicMock(return_value=True))
    def test_matches_includes_object_in_results_when_match(self, get_attr_mock):
        source = [
            MagicMock(foo=1),
            MagicMock(foo=2),
        ]

        get_attr_mock.return_value = None, None
        results = utils.matches(*source, foo__gt=0)

        for x in source:
            assert x in results

    @patch('django_mock_queries.utils.get_attribute')
    @patch('django_mock_queries.utils.is_match', MagicMock(return_value=False))
    def test_matches_excludes_object_from_results_when_not_match(self, get_attr_mock):
        source = [
            MagicMock(foo=1),
            MagicMock(foo=2),
        ]

        get_attr_mock.return_value = None, None
        results = utils.matches(*source, foo__gt=5)

        for x in source:
            assert x not in results