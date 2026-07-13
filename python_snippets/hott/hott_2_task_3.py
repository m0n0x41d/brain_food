from typing import Callable, Final, TypeVar

import pytest
from core.truncation import SetTruncation as BaseSetTruncation
from core.truncation import TruncationLevel

T = TypeVar("T")


class PrecisionCalculator:
    _DECIMAL_PLACES: Final[dict[int, int]] = {
        TruncationLevel.ZERO: 1,
        TruncationLevel.ONE: 2,
        TruncationLevel.TWO: 3,
    }

    @staticmethod
    def truncate(number: float, level: int) -> int | float:
        if level == TruncationLevel.MINUS_TWO:
            if number > 0:
                return 1
            if number < 0:
                return -1
            return 0

        if level == TruncationLevel.MINUS_ONE:
            return round(number)

        if level in PrecisionCalculator._DECIMAL_PLACES:
            decimal_places = PrecisionCalculator._DECIMAL_PLACES[level]
            return round(number, decimal_places)

        raise ValueError(f"Unsupported truncation level: {level}")


class SetTruncation(BaseSetTruncation[T]):
    @staticmethod
    def verify_equivalence_relation(
        relation: Callable[[T, T], bool], elements: list[T]
    ) -> bool:

        # check reflexivity
        for element in elements:
            if not relation(element, element):
                return False

        # check symmetry
        for first in elements:
            for second in elements:
                if relation(first, second) and not relation(second, first):
                    return False

        # check transitivity
        for first in elements:
            for second in elements:
                for third in elements:
                    if (
                        relation(first, second)
                        and relation(second, third)
                        and not relation(first, third)
                    ):
                        return False

        return True

    @classmethod
    def create_quotient_set(
        cls, elements: list[T], relation: Callable[[T, T], bool]
    ) -> dict[T, list[T]]:
        if not cls.verify_equivalence_relation(relation, elements):
            raise ValueError("The relation must be an equivalence relation")

        quotient_classes: dict[T, list[T]] = {}

        for element in elements:
            for representative, equivalence_class in quotient_classes.items():
                if relation(element, representative):
                    equivalence_class.append(element)
                    break
            else:
                quotient_classes[element] = [element]

        return quotient_classes

    @staticmethod
    def find_representative(element: T, quotient_classes: dict[T, list[T]]) -> T:
        for representative, equivalence_class in quotient_classes.items():
            if element in equivalence_class:
                return representative

        raise ValueError(f"Element {element!r} is not in the quotient set")


def test_precision_calculator_supports_every_truncation_level() -> None:
    calculator = PrecisionCalculator()
    number = 3.14159

    assert calculator.truncate(number, TruncationLevel.MINUS_TWO) == 1
    assert calculator.truncate(number, TruncationLevel.MINUS_ONE) == 3
    assert calculator.truncate(number, TruncationLevel.ZERO) == 3.1
    assert calculator.truncate(number, TruncationLevel.ONE) == 3.14
    assert calculator.truncate(number, TruncationLevel.TWO) == 3.142


@pytest.mark.parametrize(
    ("number", "expected_sign"),
    [(12.5, 1), (-12.5, -1), (0.0, 0)],
)
def test_minus_two_truncation_keeps_only_the_sign(
    number: float, expected_sign: int
) -> None:
    assert (
        PrecisionCalculator.truncate(number, TruncationLevel.MINUS_TWO) == expected_sign
    )


def test_equivalence_relation_by_remainder() -> None:
    elements = [0, 1, 2, 3, 4, 5]

    def same_remainder_modulo_three(first: int, second: int) -> bool:
        return first % 3 == second % 3

    assert SetTruncation.verify_equivalence_relation(
        same_remainder_modulo_three, elements
    )
    assert SetTruncation.create_quotient_set(elements, same_remainder_modulo_three) == {
        0: [0, 3],
        1: [1, 4],
        2: [2, 5],
    }


def test_quotient_set_groups_strings_by_length() -> None:
    elements = ["a", "to", "I", "cat", "be"]

    def same_length(first: str, second: str) -> bool:
        return len(first) == len(second)

    quotient_classes = SetTruncation.create_quotient_set(elements, same_length)

    assert quotient_classes == {
        "a": ["a", "I"],
        "to": ["to", "be"],
        "cat": ["cat"],
    }
    assert SetTruncation.find_representative("be", quotient_classes) == "to"


def test_quotient_set_groups_points_by_distance_from_origin() -> None:
    points = [(1, 0), (0, 1), (2, 0), (0, -2)]

    def same_distance(first: tuple[int, int], second: tuple[int, int]) -> bool:
        return first[0] ** 2 + first[1] ** 2 == second[0] ** 2 + second[1] ** 2

    quotient_classes = SetTruncation.create_quotient_set(points, same_distance)

    assert quotient_classes == {
        (1, 0): [(1, 0), (0, 1)],
        (2, 0): [(2, 0), (0, -2)],
    }


def test_verification_rejects_non_transitive_closeness_relation() -> None:
    elements = [1, 2, 3]

    def are_close(first: int, second: int) -> bool:
        return abs(first - second) <= 1

    assert not SetTruncation.verify_equivalence_relation(are_close, elements)

    with pytest.raises(ValueError, match="equivalence relation"):
        SetTruncation.create_quotient_set(elements, are_close)


def test_find_representative_rejects_unknown_element() -> None:
    with pytest.raises(ValueError, match="is not in the quotient set"):
        SetTruncation.find_representative(10, {0: [0, 2, 4]})
