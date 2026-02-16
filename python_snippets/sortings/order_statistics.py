from sortings.array_chunking import ArrayChunk


# This implementation follows the function signature
# required by the laboratory test server interface.
# However, this return type feels weak here:
# a typed two-value record/tuple would be clearer.
def KthOrderStatisticsStep(
    Array: list[int],
    L: int | None,
    R: int | None,
    k: int,
) -> list[int]:
    left = 0 if L is None else L
    right = len(Array) - 1 if R is None else R

    n = ArrayChunk(Array, left, right)

    if n < k:
        new_left = n + 1
        new_right = right
    elif n > k:
        new_left = left
        new_right = n - 1
    else:
        # The k-th order statistic has been found.
        new_left = n
        new_right = n

    return [new_left, new_right]
