import pytest

from core.infinity_groupoid import HigherPath
from hott_2_task_1 import higher_compose, pentagon_identity


def test_higher_compose_composes_one_dimensional_paths() -> None:
    p = HigherPath.base_path("A", "B")
    q = HigherPath.base_path("B", "C")

    composed = higher_compose(p, q)

    assert composed.dimension == 1
    assert composed.start == "A"
    assert composed.end == "C"
    assert composed.previous_paths == []


def test_higher_compose_recursively_composes_previous_paths() -> None:
    first_lower_path = HigherPath.base_path("A", "B")
    second_lower_path = HigherPath.base_path("B", "C")
    first_higher_path = HigherPath(2, "A", "B", [first_lower_path])
    second_higher_path = HigherPath(2, "B", "C", [second_lower_path])

    composed = higher_compose(first_higher_path, second_higher_path)
    composed_lower_path = composed.previous_paths[0]

    assert composed.dimension == 2
    assert composed.start == "A"
    assert composed.end == "C"
    assert len(composed.previous_paths) == 1
    assert composed_lower_path.dimension == 1
    assert composed_lower_path.start == "A"
    assert composed_lower_path.end == "C"


def test_higher_compose_rejects_different_dimensions() -> None:
    p = HigherPath.base_path("A", "B")
    q = HigherPath(2, "B", "C", [HigherPath.base_path("B", "C")])

    with pytest.raises(ValueError, match="different dimensions"):
        higher_compose(p, q)


def test_higher_compose_rejects_unconnected_paths() -> None:
    p = HigherPath.base_path("A", "B")
    q = HigherPath.base_path("X", "C")

    with pytest.raises(ValueError, match="Paths not composable"):
        higher_compose(p, q)


def test_higher_compose_rejects_different_previous_path_shapes() -> None:
    lower_path = HigherPath.base_path("A", "B")
    p = HigherPath(2, "A", "B", [lower_path])
    q = HigherPath(
        2,
        "B",
        "C",
        [
            HigherPath.base_path("B", "C"),
            HigherPath.base_path("B", "C"),
        ],
    )

    with pytest.raises(ValueError, match="matching previous path"):
        higher_compose(p, q)


def test_pentagon_identity_returns_three_dimensional_coherence_path() -> None:
    p = HigherPath.base_path("A", "B")
    q = HigherPath.base_path("B", "C")
    r = HigherPath.base_path("C", "D")
    s = HigherPath.base_path("D", "E")

    pentagon = pentagon_identity(p, q, r, s)

    assert pentagon.dimension == 3
    assert pentagon.start == "A"
    assert pentagon.end == "E"
    assert len(pentagon.previous_paths) == 5
    assert all(path.dimension == 2 for path in pentagon.previous_paths)
    assert all(len(path.previous_paths) == 2 for path in pentagon.previous_paths)


def test_pentagon_identity_builds_associativity_paths_for_four_inputs() -> None:
    p = HigherPath.base_path("A", "B")
    q = HigherPath.base_path("B", "C")
    r = HigherPath.base_path("C", "D")
    s = HigherPath.base_path("D", "E")

    pentagon = pentagon_identity(p, q, r, s)
    associativity_boundaries = [
        (path.start, path.end)
        for path in pentagon.previous_paths
    ]

    assert associativity_boundaries == [
        ("A", "D"),
        ("B", "E"),
        ("A", "E"),
        ("A", "E"),
        ("A", "E"),
    ]


def test_pentagon_identity_rejects_non_one_dimensional_path() -> None:
    p = HigherPath.base_path("A", "B")
    q = HigherPath.base_path("B", "C")
    r = HigherPath.base_path("C", "D")
    s = HigherPath(2, "D", "E", [HigherPath.base_path("D", "E")])

    with pytest.raises(ValueError, match="dimension 1"):
        pentagon_identity(p, q, r, s)


def test_pentagon_identity_rejects_non_sequential_paths() -> None:
    p = HigherPath.base_path("A", "B")
    q = HigherPath.base_path("B", "C")
    r = HigherPath.base_path("X", "D")
    s = HigherPath.base_path("D", "E")

    with pytest.raises(ValueError, match="Paths not composable"):
        pentagon_identity(p, q, r, s)
