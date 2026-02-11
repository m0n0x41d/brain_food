from sortings.array_chunking import ArrayChunk


def QuickSort(array: list[int], left: int, right: int):
    # We need to check if left >= right because there might be cases when
    # left will jump over to the right in some chunking scenarios;
    # thus, this will lead to endless recursions.
    if left >= right:
        return

    N = ArrayChunk(array, left, right)
    QuickSort(array, left, N - 1)
    QuickSort(array, N + 1, right)
