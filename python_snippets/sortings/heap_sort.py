# simple int heap implementation for the sake of HeatSort task
class Heap:
    def __init__(self):
        self.HeapArray: list[int | None] = []
        self._size = 0

    @staticmethod
    def _parent(index: int) -> int:
        return (index - 1) // 2

    @staticmethod
    def _left(index: int) -> int:
        return 2 * index + 1

    @staticmethod
    def _right(index: int) -> int:
        return 2 * index + 2

    def MakeHeap(self, array: list[int], depth: int):
        # capacity of a complete binary tree with the given depth.
        capacity = 0 if depth < 0 else (1 << (depth + 1)) - 1
        self.HeapArray = [None] * capacity
        self._size = 0

        for key in array:
            if not self.Add(key):
                break

    def GetMax(self):
        if self._size == 0:
            return -1

        max_key = self.HeapArray[0]
        assert max_key is not None

        last_index = self._size - 1
        self.HeapArray[0] = self.HeapArray[last_index]
        self.HeapArray[last_index] = None
        self._size -= 1

        if self._size > 0:
            self._sift_down(0)

        return max_key

    def Add(self, key: int):
        if self._size >= len(self.HeapArray):
            return False

        index = self._size
        self.HeapArray[index] = key
        self._size += 1
        self._sift_up(index)
        return True

    def _sift_up(self, index: int):
        while index > 0:
            parent = self._parent(index)
            current_value = self.HeapArray[index]
            parent_value = self.HeapArray[parent]
            assert current_value is not None
            assert parent_value is not None

            if parent_value >= current_value:
                break

            self.HeapArray[parent], self.HeapArray[index] = (
                self.HeapArray[index],
                self.HeapArray[parent],
            )
            index = parent

    def _sift_down(self, index: int):
        while True:
            left = self._left(index)
            if left >= self._size:
                return

            right = self._right(index)
            largest = left

            left_value = self.HeapArray[left]
            assert left_value is not None

            if right < self._size:
                right_value = self.HeapArray[right]
                assert right_value is not None
                if right_value > left_value:
                    largest = right

            current_value = self.HeapArray[index]
            largest_value = self.HeapArray[largest]
            assert current_value is not None
            assert largest_value is not None

            if current_value >= largest_value:
                return

            self.HeapArray[index], self.HeapArray[largest] = (
                self.HeapArray[largest],
                self.HeapArray[index],
            )
            index = largest


# due to the heap nature the average complexity of HeapSort is O(n log n)
class HeapSort:
    HeapObject: Heap

    def __init__(self, array: list[int]):
        self.HeapObject = Heap()
        # Laboratory task requires loading through Add() one element at a time
        # so MakeHeap is called with empty list ¯\_(ツ)_/¯
        self.HeapObject.MakeHeap([], self._depth_for_size(len(array)))
        for value in array:
            self.HeapObject.Add(value)

    def GetNextMax(self):
        return self.HeapObject.GetMax()

    @staticmethod
    def _depth_for_size(size: int) -> int:
        if size == 0:
            return -1
        if size == 1:
            return 0

        depth = 0
        while (1 << (depth + 1)) - 1 < size:
            depth += 1
        return depth
