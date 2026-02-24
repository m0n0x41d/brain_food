import pytest

from sortings.heap_sort import Heap, HeapSort


@pytest.mark.parametrize(
    "array",
    [
        [],
        [0],
        [3, 1, 2],
        [9, 7, 5, 3, 1],
        [1, 3, 5, 7, 9],
        [4, 1, 4, 2, 4, 3],
        [10, 2, 8, 6, 4, 0],
    ],
)
def test_HeapSort_GetNextMax(array: list[int]):
    sorter = HeapSort(array)

    extracted = [sorter.GetNextMax() for _ in range(len(array))]

    assert extracted == sorted(array, reverse=True)
    assert sorter.GetNextMax() == -1


def test_Heap_Add_and_GetMax():
    heap = Heap()
    heap.MakeHeap([], 2)  # capacity is 7

    for value in [3, 10, 1, 7, 5]:
        assert heap.Add(value) is True

    assert heap.GetMax() == 10
    assert heap.GetMax() == 7
    assert heap.GetMax() == 5
    assert heap.GetMax() == 3
    assert heap.GetMax() == 1
    assert heap.GetMax() == -1


def test_Heap_Add_returns_false_when_heap_is_full():
    heap = Heap()
    heap.MakeHeap([], 1)  # capacity is 3

    assert heap.Add(4) is True
    assert heap.Add(2) is True
    assert heap.Add(3) is True
    assert heap.Add(1) is False
