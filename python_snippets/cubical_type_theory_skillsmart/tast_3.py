from cubic.cube import Cube
from cubic.cubical_path import CubicalPath, fill
from cubic.direction import Direction
from cubic.face import Face


def transform_segment() -> Cube:
    bottom = CubicalPath(lambda t: (t, 0))
    top = CubicalPath(lambda t: (t, 1))

    i = Direction(0)
    j = Direction(1)
    lower_face = Face(j, 0)
    upper_face = Face(j, 1)

    cube1 = Cube([i, j])
    cube2 = Cube([i, j])
    middle = fill({"bottom": bottom, "top": top})

    # same middle object on both sides, no seam drama
    cube1.set_face(lower_face, bottom)
    cube1.set_face(upper_face, middle)
    cube2.set_face(lower_face, middle)
    cube2.set_face(upper_face, top)

    result = cube1.compose(cube2, j, 1)

    # the outer paths should survive "gluing"
    result_bottom = result.get_face(lower_face)
    result_top = result.get_face(upper_face)
    assert result_bottom is bottom
    assert result_top is top

    # t runs along a path; s runs through bottom -> middle -> top
    def h(t: float, s: float) -> tuple[float, float]:
        seam = middle(t)
        if s <= 0.5:
            return t, 2 * s * seam[1]
        return t, seam[1] + (2 * s - 1) * (1 - seam[1])

    # middle(t) = (t, t), so both pieces are polynomial and continuous
    # at s = 0.5 both formulas give middle(t): no jump at the seam
    assert h(0.25, 0) == bottom(0.25)
    assert h(0.25, 0.25) == (0.25, 0.125)
    assert h(0.25, 0.5) == middle(0.25)
    assert h(0.25, 0.75) == (0.25, 0.625)
    assert h(0.25, 1) == top(0.25)

    return result


if __name__ == "__main__":
    transform_segment()
    print("segment transformation checks passed")
