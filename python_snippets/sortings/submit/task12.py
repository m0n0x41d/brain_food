from enum import IntEnum

# All interfaces are "pythonic unconventional" due to the request of the laboratory server.


class SearchStatus(IntEnum):
    IN_PROGRESS = 0
    FOUND = 1
    NOT_FOUND = -1


class BinarySearch:
    Left: int
    Right: int
    sorted_array: list[int]
    search_status: SearchStatus
    current_checking_index: int

    def __init__(self, sorted_array: list[int]):
        self.Left = 0
        self.Right = len(sorted_array) - 1
        self.sorted_array = sorted_array
        self.search_status = SearchStatus.IN_PROGRESS

    def Step(self, N: int):
        if self.search_status != SearchStatus.IN_PROGRESS:
            return

        if self.Left > self.Right:
            self.search_status = SearchStatus.NOT_FOUND
            return

        center_item_idx = (self.Right + self.Left) // 2
        self.current_checking_index = center_item_idx
        center_item = self.sorted_array[center_item_idx]

        if center_item == N:
            self.search_status = SearchStatus.FOUND
        elif center_item > N:
            self.Right = center_item_idx - 1
        else:
            self.Left = center_item_idx + 1

        remaining = self.Right - self.Left

        if remaining < 0:
            self.search_status = SearchStatus.NOT_FOUND
        elif remaining <= 1:
            left_ok = self.sorted_array[self.Left] == N
            right_ok = remaining == 1 and self.sorted_array[self.Right] == N
            self.search_status = (
                SearchStatus.FOUND if left_ok or right_ok else SearchStatus.NOT_FOUND
            )

    def GetResult(self) -> int:
        return int(self.search_status)

    @staticmethod
    def GallopingSearch(sorted_array: list[int], N: int) -> bool:
        if not sorted_array:
            return False

        def calc_current_index(x: int) -> int:
            return (2**x) - 2

        def run_binary_search(left: int, right: int) -> bool:
            bs = BinarySearch(sorted_array)
            bs.Left = left
            bs.Right = right

            while bs.GetResult() == SearchStatus.IN_PROGRESS:
                bs.Step(N)

            return bs.GetResult() == SearchStatus.FOUND

        i = 1
        last_index = len(sorted_array) - 1

        while True:
            current_index = min(calc_current_index(i), last_index)
            check_value = sorted_array[current_index]

            if check_value == N:
                return True

            if check_value > N:
                left = (2 ** (i - 1) - 2) + 1
                right = current_index
                return run_binary_search(left, right)

            if current_index == last_index:
                return False

            i += 1


def GallopingSearch(sorted_array: list[int], N: int) -> bool:
    return BinarySearch.GallopingSearch(sorted_array, N)
