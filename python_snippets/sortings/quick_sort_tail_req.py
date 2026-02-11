from sortings.array_chunking import ArrayChunk


# Quick sort with tail recursive optimization works with the same efficiency
# as the two-rec-calls implementation (O(N log N) approximately and O(N^2 in the worst case)),
# but with tail recursion optimization, we are winning in stack size.
def QuickSortTailOptimization(array: list[int], left: int, right: int):
    oritiginal_right = right

    if left >= right:
        return

    # Here we replace one of the two recursive calls with a while loop
    # to process the right part of the array iteratively.
    # This way the call stack grows ~2x slower: only the left branch
    # adds stack frames, while the right branch is handled in-place by the loop.
    while left < right:
        N = ArrayChunk(array, left, right)
        right = N - 1
    QuickSortTailOptimization(array, N + 1, oritiginal_right)
