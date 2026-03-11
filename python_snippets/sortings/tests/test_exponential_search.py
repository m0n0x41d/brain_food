import pytest

from sortings.exponential_search import BinarySearch, GallopingSearch


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
    ("array", "target"),
    [
        ([1], 1),
        ([1, 3, 5, 7], 1),
        ([1, 3, 5, 7], 3),
        ([1, 3, 5, 7], 5),
        ([1, 3, 5, 7], 7),
        ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 10),
    ],
)
def test_GallopingSearch_finds_existing_values(array: list[int], target: int):
    searcher = BinarySearch(array)

    assert searcher.GallopingSearch(array, target) is True


def test_GallopingSearch_can_be_called_autonomously_from_class():
    assert BinarySearch.GallopingSearch([1, 3, 5, 7], 5) is True
    assert BinarySearch.GallopingSearch([1, 3, 5, 7], 6) is False


def test_GallopingSearch_can_be_called_as_module_function():
    assert GallopingSearch([1, 3, 5, 7], 5) is True
    assert GallopingSearch([1, 3, 5, 7], 6) is False
