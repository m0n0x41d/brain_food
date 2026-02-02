import pytest

from sortings.array_chunking import ArrayChunk


def is_valid_partition(original: list[int], result: list[int], pivot_idx: int):
    pivot = result[pivot_idx]
    for i in range(pivot_idx):
        assert result[i] < pivot, f"Left side element {result[i]} at index {i} is not less than pivot {pivot}"
    for i in range(pivot_idx + 1, len(result)):
        assert result[i] > pivot, f"Right side element {result[i]} at index {i} is not greater than pivot {pivot}"
    assert sorted(original) == sorted(result)


@pytest.mark.parametrize(
    "array,expected_index,expected_array",
    [
        ([7, 5, 6, 4, 3, 1, 2], 3, [2, 1, 3, 4, 6, 5, 7]),
    ],
)
def test_ArrayChunk_task_example(array: list[int], expected_index: int, expected_array: list[int]):
    result = ArrayChunk(array)
    assert result == expected_index
    assert array == expected_array


@pytest.mark.parametrize(
    "array",
    [
        [3, 1, 2],
        [5, 3, 4, 2, 1],
        [1, 2, 3, 4, 5],
        [5, 4, 3, 2, 1],
        [2, 1],
        [1, 2],
        [1, 3, 4, 6, 5, 2, 8],
    ],
)
def test_ArrayChunk_valid_partition(array: list[int]):
    original = array[:]
    pivot_idx = ArrayChunk(array)
    is_valid_partition(original, array, pivot_idx)
