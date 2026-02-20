import pytest

from sortings.merge_sort import MergeSort


@pytest.mark.parametrize(
    "array",
    [
        [],
        [1],
        [2, 1],
        [1, 2, 3, 4, 5],
        [5, 4, 3, 2, 1],
        [3, 1, 4, 1, 5, 9, 2, 6],
        [10, -1, 0, 3, -5, 7],
        [5, 5, 5, 5],
        [2, 3, 2, 1, 1, 4],
    ],
)
def test_MergeSort(array: list[int]):
    expected = sorted(array)
    original = array.copy()

    result = MergeSort(array)

    assert result == expected
    assert array == original
