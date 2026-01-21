# O(1) by memory due to not using things like slices for enumeration
# O(n) by time for this particular function.
# However, full selection sort will take (n^2)
def SelectionSortStep(array: list[int], i: int):
    min_idx = i
    for j in range(i + 1, len(array)):
        if array[j] < array[min_idx]:
            min_idx = j

    if min_idx != i:
        array[i], array[min_idx] = array[min_idx], array[i]


def BubbleSortStep(array: list[int]) -> bool:
    is_swapped = False

    for i in range(len(array) - 1):
        if array[i] > array[i + 1]:
            array[i], array[i + 1] = array[i + 1], array[i]
            is_swapped = True

    return is_swapped
