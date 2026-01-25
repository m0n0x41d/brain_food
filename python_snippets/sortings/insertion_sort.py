# O(1) by space – no new slices.
# O(n^2) by time, where n is the length of an array.
def InsertionSortStep(
    array: list[int],
    step: int,
    i: int,
):
    for insert_pos in range(i + step, len(array), step):
        value = array[insert_pos]
        check_pos = insert_pos - step
        while check_pos >= i and array[check_pos] > value:
            array[check_pos + step] = array[check_pos]
            check_pos -= step
        array[check_pos + step] = value
