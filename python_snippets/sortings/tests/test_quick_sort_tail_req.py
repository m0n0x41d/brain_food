import pytest

from sortings.quick_sort_tail_req import QuickSortTailOptimization


@pytest.mark.parametrize(
    "array",
    [
        [7, 5, 6, 4, 3, 1, 2],
        [3, 1, 2],
        [5, 3, 4, 2, 1],
        [1, 2, 3, 4, 5],
        [5, 4, 3, 2, 1],
        [2, 1],
        [1, 2],
        [1],
        [1, 3, 4, 6, 5, 2, 8],
        [10, -1, 0, 3, -5, 7],
    ],
)
def test_QuickSortTailOptimization(array: list[int]):
    expected = sorted(array)
    QuickSortTailOptimization(array, 0, len(array) - 1)
    assert array == expected
