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


# O(log n) by both time and space
def KnuthSequence(array_size: int) -> list[int]:
    sequence = []
    x = 1
    while x < array_size:
        sequence.append(x)
        x = 3 * x + 1

    sequence.reverse()
    return sequence


# O(n * (log n)^2), because we do log n passes by the Knuth sequence,
# each ~O(n log n) due to partial ordering.
# Apparently, exact asymptotic analysis of shell sort is nontrivial math,
# and it seems that O(n * (log n)^2) is an empirically "proven" evaluation.
def ShellSort(array: list[int]):
    seq = KnuthSequence(len(array))

    for step in seq:
        for i in range(step):
            InsertionSortStep(array, step, i)
