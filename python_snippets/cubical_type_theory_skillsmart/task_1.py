import pytest
from cubic.direction import Direction
from cubic.face import Face
from cubic.interval import Interval


@pytest.mark.parametrize("direction_index", (0, 1, 2), ids=("x", "y", "z"))
@pytest.mark.parametrize(
    "start_value, end_value, expected_values",
    (
        (0, 1, (0, 0.25, 0.5, 0.75, 1)),
        (1, 0, (1, 0.75, 0.5, 0.25, 0)),
    ),
    ids=("forward", "backward"),
)
def test_paths_between_opposite_faces(
    direction_index: int,
    start_value: int,
    end_value: int,
    expected_values: tuple[float, ...],
) -> None:
    # pick face and two coordinates
    interval = Interval()
    direction = Direction(direction_index)
    start_face = Face(direction, start_value)
    end_face = Face(direction, end_value)

    assert interval.endpoints == (0, 1)
    assert direction.index == direction_index
    assert start_face.direction == direction
    assert end_face.direction == direction
    assert start_face.value == start_value
    assert end_face.value == end_value
    assert start_face != end_face

    start_is_endpoint = interval.is_endpoint(start_face.value)
    end_is_endpoint = interval.is_endpoint(end_face.value)
    assert start_is_endpoint
    assert end_is_endpoint

    # opposite face changes side but keeps axis
    opposite_face = start_face.opposite()
    restored_face = opposite_face.opposite()
    assert opposite_face == end_face
    assert opposite_face.direction == direction
    assert restored_face == start_face
    assert start_face.value == start_value

    # build an integer "path" between faces coordinates
    path = interval.path(start_face.value, end_face.value)
    at_start = path(0)
    at_end = path(1)
    assert at_start == start_face.value
    assert at_end == end_face.value

    sample_points = (0, 0.25, 0.5, 0.75, 1)
    path_samples = map(path, sample_points)
    path_values = tuple(path_samples)
    assert path_values == expected_values

    # degenerated path must remain on one of the boundary coordinate
    constant_path = interval.degeneracy(start_face.value)
    constant_samples = map(constant_path, sample_points)
    constant_values = tuple(constant_samples)
    sample_count = len(sample_points)
    expected_constant_values = (start_value,) * sample_count
    assert constant_values == expected_constant_values

    # identical endpoints give the same result due to linear interpolation or something...
    same_endpoint_path = interval.path(start_face.value, start_face.value)
    same_endpoint_samples = map(same_endpoint_path, sample_points)
    same_endpoint_values = tuple(same_endpoint_samples)
    assert same_endpoint_values == constant_values


@pytest.mark.parametrize(
    "direction_index, axis_name",
    ((0, "x"), (1, "y"), (2, "z")),
)
@pytest.mark.parametrize("side", (0, 1))
def test_each_direction_and_side_selects_its_own_face(
    direction_index: int,
    axis_name: str,
    side: int,
) -> None:
    # 3d cube has 6 faces
    x = Direction(0)
    y = Direction(1)
    z = Direction(2)
    x_start = Face(x, 0)
    x_end = Face(x, 1)
    y_start = Face(y, 0)
    y_end = Face(y, 1)
    z_start = Face(z, 0)
    z_end = Face(z, 1)
    face_names = {
        x_start: "x=0",
        x_end: "x=1",
        y_start: "y=0",
        y_end: "y=1",
        z_start: "z=0",
        z_end: "z=1",
    }
    face_count = len(face_names)
    assert face_count == 6

    # new 'object' with the same index must land up to the same edge
    equivalent_direction = Direction(direction_index)
    equivalent_face = Face(equivalent_direction, side)
    actual_name = face_names[equivalent_face]
    expected_name = f"{axis_name}={side}"
    assert actual_name == expected_name
