import pytest

from sortings.ksort import ksort


def test_ksort_initializes_fixed_items_storage():
    sorter = ksort()

    assert len(sorter.items) == 800
    assert all(item is None for item in sorter.items)


@pytest.mark.parametrize(
    "value,expected",
    [
        ("a00", 0),
        ("a01", 1),
        ("a99", 99),
        ("b00", 100),
        ("g09", 609),
        ("h99", 799),
    ],
)
def test_ksort_index_for_valid_values(value: str, expected: int):
    sorter = ksort()
    assert sorter.index(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        "",
        "a0",
        "a000",
        "a1",
        "a9a",
        "A01",
        "i00",
        "h100",
        "a-1",
    ],
)
def test_ksort_index_returns_minus_one_for_invalid_values(value: str):
    sorter = ksort()
    assert sorter.index(value) == -1


def test_ksort_add_places_value_by_computed_index():
    sorter = ksort()

    assert sorter.add("c42") is True
    assert sorter.items[242] == "c42"


def test_ksort_add_returns_false_for_invalid_value():
    sorter = ksort()

    assert sorter.add("x42") is False
    assert all(item is None for item in sorter.items)
