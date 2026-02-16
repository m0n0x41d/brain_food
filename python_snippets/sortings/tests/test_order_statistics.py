import pytest

from sortings.order_statistics import KthOrderStatisticsStep


def test_KthOrderStatisticsStep_uses_full_range_when_bounds_are_none(monkeypatch):
    captured: dict[str, tuple[int, int]] = {}

    def fake_array_chunk(_array: list[int], left: int, right: int) -> int:
        captured["bounds"] = (left, right)
        return 1

    monkeypatch.setattr("sortings.order_statistics.ArrayChunk", fake_array_chunk)

    array = [3, 1, 2]
    result = KthOrderStatisticsStep(array, None, None, 1)

    assert captured["bounds"] == (0, len(array) - 1)
    assert result == [1, 1]


def test_KthOrderStatisticsStep_keeps_zero_right_boundary(monkeypatch):
    captured: dict[str, tuple[int, int]] = {}

    def fake_array_chunk(_array: list[int], left: int, right: int) -> int:
        captured["bounds"] = (left, right)
        return 0

    monkeypatch.setattr("sortings.order_statistics.ArrayChunk", fake_array_chunk)

    result = KthOrderStatisticsStep([42], 0, 0, 0)

    assert captured["bounds"] == (0, 0)
    assert result == [0, 0]


@pytest.mark.parametrize(
    "n,k,left,right,expected",
    [
        (2, 5, 1, 6, [3, 6]),  # N < k => move left bound to N + 1
        (4, 2, 1, 6, [1, 3]),  # N > k => move right bound to N - 1
        (3, 3, 1, 6, [3, 3]),  # N == k => found
    ],
)
def test_KthOrderStatisticsStep_updates_boundaries(monkeypatch, n, k, left, right, expected):
    monkeypatch.setattr("sortings.order_statistics.ArrayChunk", lambda *_: n)
    array = [0, 1, 2, 3, 4, 5, 6]
    assert KthOrderStatisticsStep(array, left, right, k) == expected


@pytest.mark.parametrize(
    "k,expected",
    [
        (1, [0, 2]),
        (3, [3, 3]),
        (5, [4, 6]),
    ],
)
def test_KthOrderStatisticsStep_integration_with_real_partition(k: int, expected: list[int]):
    array = [7, 5, 6, 4, 3, 1, 2]
    assert KthOrderStatisticsStep(array, 0, len(array) - 1, k) == expected
