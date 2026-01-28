import pytest

from sortings.insertion_sort_step import InsertionSortStep
from sortings.shell_sort import ShellSort


@pytest.mark.parametrize(
    "array,step,i,expected",
    [
        ([7, 6, 5, 4, 3, 2, 1], 3, 0, [1, 6, 5, 4, 3, 2, 7]),
        ([1, 6, 5, 4, 3, 2, 7], 3, 1, [1, 3, 5, 4, 6, 2, 7]),
        ([1, 3, 5, 4, 6, 2, 7], 3, 2, [1, 3, 2, 4, 6, 5, 7]),
        ([4, 3, 1, 2], 1, 0, [1, 2, 3, 4]),
        ([1, 2, 3, 4], 1, 0, [1, 2, 3, 4]),
        ([4, 3, 2, 1], 1, 0, [1, 2, 3, 4]),
        ([5], 1, 0, [5]),
        ([2, 1], 1, 0, [1, 2]),
        ([1, 2], 1, 0, [1, 2]),
        ([3, 2, 1, 6, 5, 4], 3, 0, [3, 2, 1, 6, 5, 4]),
        ([3, 2, 1, 6, 5, 4], 3, 1, [3, 2, 1, 6, 5, 4]),
    ],
)
def test_InsertionSortStep(array: list[int], step: int, i: int, expected: list[int]):
    InsertionSortStep(array, step, i)
    assert array == expected


@pytest.mark.parametrize(
    "array,expected",
    [
        ([7, 6, 5, 4, 3, 2, 1], [1, 2, 3, 4, 5, 6, 7]),
        ([4, 3, 1, 2], [1, 2, 3, 4]),
        ([1, 2, 3, 4], [1, 2, 3, 4]),
        ([4, 3, 2, 1], [1, 2, 3, 4]),
        ([5], [5]),
        ([2, 1], [1, 2]),
        ([1, 2], [1, 2]),
        ([], []),
        ([3, 1, 4, 1, 5, 9, 2, 6], [1, 1, 2, 3, 4, 5, 6, 9]),
        ([5, 5, 5, 5], [5, 5, 5, 5]),
        ([1, 3, 2, 3, 1], [1, 1, 2, 3, 3]),
    ],
)
def test_ShellSort(array: list[int], expected: list[int]):
    ShellSort(array)
    assert array == expected
