from sortings.insertion_sort_step import InsertionSortStep
from sortings.knuth_sequence import KnuthSequence


# O(n * (log n)^2), because we do log n passes by the Knuth sequence,
# each ~O(n log n) due to partial ordering.
# Apparently, exact asymptotic analysis of shell sort is nontrivial math,
# and it seems that O(n * (log n)^2) is an empirically "proven" evaluation.
def ShellSort(array: list[int]):
    seq = KnuthSequence(len(array))

    for step in seq:
        for i in range(step):
            InsertionSortStep(array, step, i)
