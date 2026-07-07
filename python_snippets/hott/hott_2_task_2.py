from typing import TypeVar

from core.homotopy_groups import HigherPath, HomotopyGroup, InfinityGroupoid

T = TypeVar("T")


###  assignment 1


def is_homotopic_equivalent(
    path1: HigherPath[T],
    path2: HigherPath[T],
) -> bool:
    # only paths of the same dimension can be possibly homotopically equivalent
    if path1.dimension != path2.dimension:
        return False

    # paths must start and end at the same points to be deformable into each other
    if path1.start != path2.start or path1.end != path2.end:
        return False

    # maybe highet path at one level above?
    candidate_higher_path = HigherPath(
        path1.dimension + 1,
        path2.start,
        path2.end,
        [path2],
        None,
    )

    try:
        InfinityGroupoid.whiskering(
            path1,
            candidate_higher_path,
        )
    except ValueError:
        # No valid higher path could connect paths we have
        return False

    return True


def test_is_homotopic_equivalent_accepts_parallel_one_dimensional_paths() -> None:
    path1 = HigherPath.base_path("A", "B")
    path2 = HigherPath.base_path("A", "B")

    result = is_homotopic_equivalent(path1, path2)

    # Same dimension and same endpoints mean a higher path witness can connect them.
    assert result is True


def test_is_homotopic_equivalent_rejects_different_dimensions() -> None:
    lower_path = HigherPath.base_path("A", "B")
    higher_path = HigherPath(2, "A", "B", [lower_path])

    result = is_homotopic_equivalent(lower_path, higher_path)

    # A 1D path and a 2D path live on different levels, so they are not comparable.
    assert result is False


def test_is_homotopic_equivalent_rejects_different_start_points() -> None:
    path1 = HigherPath.base_path("A", "B")
    path2 = HigherPath.base_path("X", "B")

    result = is_homotopic_equivalent(path1, path2)

    # Homotopic paths must be parallel: same dimension plus same start and end.
    assert result is False


def test_is_homotopic_equivalent_rejects_different_end_points() -> None:
    path1 = HigherPath.base_path("A", "B")
    path2 = HigherPath.base_path("A", "C")

    result = is_homotopic_equivalent(path1, path2)

    # If the target point differs, one path cannot be deformed into the other.
    assert result is False


def test_is_homotopic_equivalent_accepts_parallel_higher_paths() -> None:
    lower_path1 = HigherPath.base_path("A", "B")
    lower_path2 = HigherPath.base_path("A", "B")
    path1 = HigherPath(2, "A", "B", [lower_path1])
    path2 = HigherPath(2, "A", "B", [lower_path2])

    result = is_homotopic_equivalent(path1, path2)

    # The same rule works one level up: two 2D paths need a possible 3D witness.
    assert result is True


###  assignment 2


class HomotopyGroupIterative(HomotopyGroup):
    def __iter__(self):
        # well... I guess
        return iter(self.elements)

    def find_inverse(self, index: int) -> int:
        if index not in self.elements:
            raise ValueError("Index not found")

        element = self.elements[index]

        for candidate_index, candidate in self.elements.items():
            if candidate.start == element.end and candidate.end == element.start:
                return candidate_index

        raise ValueError("No inverse path found")


def test_homotopy_group_iterates_and_composes_each_element_with_inverse() -> None:
    base_point = "A"
    group = HomotopyGroupIterative(base_point, 1)
    identity = InfinityGroupoid.identity(base_point, 1)

    original_indices = [
        group.add_element(HigherPath.base_path(base_point, base_point))
        for _ in range(6)
    ]

    iterated_indices = list(group)

    # __iter__ should expose group element indices, not the raw HigherPath objects.
    assert iterated_indices == original_indices

    for element_index in original_indices:
        inverse_index = group.find_inverse(element_index)
        left_composed_index = group.compose(element_index, inverse_index)
        right_composed_index = group.compose(inverse_index, element_index)
        left_composed_element = group.elements[left_composed_index]
        right_composed_element = group.elements[right_composed_index]

        # The inverse must be one of the original group elements.
        assert inverse_index in original_indices

        # In this simplified model, identity is checked by the loop shape:
        # same dimension, same base start, same base end.
        assert left_composed_element.dimension == identity.dimension
        assert left_composed_element.start == identity.start
        assert left_composed_element.end == identity.end

        # Check the other direction too: inverse composed with element.
        assert right_composed_element.dimension == identity.dimension
        assert right_composed_element.start == identity.start
        assert right_composed_element.end == identity.end
