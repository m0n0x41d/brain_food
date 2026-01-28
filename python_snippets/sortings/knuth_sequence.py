# O(log n) by both time and space
def KnuthSequence(array_size: int) -> list[int]:
    sequence = []
    x = 1
    while x < array_size:
        sequence.append(x)
        x = 3 * x + 1

    sequence.reverse()
    return sequence
