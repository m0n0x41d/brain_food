import pytest

from sortings.selection_and_bubble import BubbleSortStep, SelectionSortStep


@pytest.mark.parametrize(
    "array,i,expected",
    [
        ([4, 3, 1, 2], 0, [1, 3, 4, 2]),
        ([1, 3, 4, 2], 1, [1, 2, 4, 3]),
        ([1, 2, 4, 3], 2, [1, 2, 3, 4]),
        ([1, 2, 3, 4], 3, [1, 2, 3, 4]),
        ([5], 0, [5]),
        ([2, 1], 0, [1, 2]),
        ([1, 2], 0, [1, 2]),
    ],
)
def test_SelectionSortStep(array: list[int], i: int, expected: list[int]):
    SelectionSortStep(array, i)
    assert array == expected


def test_BubbleSortStep():
    array = [4, 3, 1, 2]
    assert BubbleSortStep(array) is True
    assert array == [3, 1, 2, 4]

    assert BubbleSortStep(array) is True
    assert array == [1, 2, 3, 4]

    assert BubbleSortStep(array) is False
