
from typing import Any, Protocol, TypeVar


class Comparable(Protocol):
    def __lt__(self, other: Any, /) -> bool: ...


T = TypeVar("T", bound=Comparable)


# This algorithm is for demonstration and training purposes.
# Due to using an additional internal buffer and array, its effectiveness is low.
# The key point of merge sort is the merging of arrays, not the sorting of subranges that have other effective implementations
# when merge sort is implemented in practice.
def MergeSort(array: list[T]) -> list[T]:

    if len(array) <= 1:
        return array

    def _divide(x: list[T]) -> tuple[list[T], list[T]]:
        middle = len(x) // 2
        return x[:middle], x[middle:]

    def _conquer(x: list[T], y: list[T]) -> list[T]:
        i, j = 0, 0
        result: list[T] = []

        while i < len(x) and j < len(y):
            if y[j] < x[i]:
                result.append(y[j])
                j += 1
            else:
                result.append(x[i])
                i += 1

        while i < len(x):
            result.append(x[i])
            i += 1

        while j < len(y):
            result.append(y[j])
            j += 1

        return result


    left, right = _divide(array)
    left_sorted = MergeSort(left)
    right_sorted = MergeSort(right)

    return _conquer(left_sorted, right_sorted)
