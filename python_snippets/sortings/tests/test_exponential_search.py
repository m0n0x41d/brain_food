import pytest

from sortings.exponential_search import BinarySearch


@pytest.mark.parametrize(
    ("array", "target"),
    [
        ([], 1),
        ([1], 2),
        ([1, 3, 5, 7], 0),
        ([1, 3, 5, 7], 4),
        ([1, 3, 5, 7], 6),
        ([1, 3, 5, 7], 8),
    ],
)
def test_GallopingSearch_returns_false_for_missing_values(
    array: list[int], target: int
):
    searcher = BinarySearch(array)

    assert searcher.GallopingSearch(array, target) is False


@pytest.mark.parametrize(
    ("array", "target", "expected_index"),
    [
        ([1], 1, 0),
        ([1, 3, 5, 7], 1, 0),
        ([1, 3, 5, 7], 3, 1),
        ([1, 3, 5, 7], 5, 2),
        ([1, 3, 5, 7], 7, 3),
        ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 10, 9),
    ],
)
def test_GallopingSearch_finds_existing_values(
    array: list[int], target: int, expected_index: int
):
    searcher = BinarySearch(array)

    assert searcher.GallopingSearch(array, target) is True
    assert searcher.current_checking_index == expected_index
