# By the time it should be O(n) for every call of ArrayChunk
# The external loop in the typical case works O(1) times, because
# one scan almost always completes partitioning and thus
# ends up with chunking. A re-scan is needed only when
# pointers meet on neighboring elements in the wrong order.
# In a very worst case, if every re-scan makes minimal progress,
# we might face O(n^2); however, it seems like a very unlikely scenario.
def ArrayChunk(M: list[int], left=0, right=None) -> int:
    """
    Partition the array in-place into two groups around a pivot element
    (the middle element). Elements smaller than the pivot end up on the left,
    elements larger — on the right. Returns the final index of the pivot.
    """

    if right is None:
        right = len(M) - 1

    while True:
        pivot_element_index = (left + right) // 2
        pivot_element_value = M[pivot_element_index]

        i1 = left
        i2 = right

        # Scan and swap items until pointers meet
        while True:
            while M[i1] < pivot_element_value:
                i1 += 1

            while M[i2] > pivot_element_value:
                i2 -= 1

            # Pointers are adjacent and left item is greater than right.
            # Swap them, but this still might not be enough for
            # a complete partition, so break to outer loop
            # and pick a new pivot.
            if i1 == i2 - 1 and M[i1] > M[i2]:
                M[i1], M[i2] = M[i2], M[i1]
                if i1 == pivot_element_index:
                    pivot_element_index = i2
                elif i2 == pivot_element_index:
                    pivot_element_index = i1

                break

            # Pointers have met, and left item is less than right,
            # so the partition is complete.
            if i1 >= i2 or (i1 == i2 - 1 and M[i1] < M[i2]):
                return pivot_element_index

            # If we end up here it means the items at both
            # pointers are on the wrong sides, so we swap them,
            # update the pivot index if needed, and shift
            # pointers inward to continue scanning.
            M[i1], M[i2] = M[i2], M[i1]

            if i1 == pivot_element_index:
                pivot_element_index = i2
            elif i2 == pivot_element_index:
                pivot_element_index = i1
            i1 += 1
            i2 -= 1


def QuickSort(array: list[int], left: int, right: int):
    # We need to check if left >= right because there might be cases when
    # left will jump over to the right in some chunking scenarios;
    # thus, this will lead to endless recursions.
    if left >= right:
        return

    N = ArrayChunk(array, left, right)
    QuickSort(array, left, N - 1)
    QuickSort(array, N + 1, right)
