from cubic.cube import Cube
from cubic.direction import Direction
from cubic.face import Face
from cubic.system import System


def compose_cubes_with_rules(
    cube1: Cube,
    system1: System,
    cube2: Cube,
    system2: System,
    direction: Direction,
    value: int,
) -> tuple[Cube, System]:
    # make sure there's something on both sides of the seam
    seam = Face(direction, value)
    other_seam = seam.opposite()

    if seam not in cube1.faces or other_seam not in cube2.faces:
        raise ValueError("both cubes must have an assigned face at the seam")

    # let each object do its bit; compose already checks the face values
    composed_cube = cube1.compose(cube2, direction, value)
    shared_faces = [seam]
    composed_system = system1.compose(system2, shared_faces)

    return composed_cube, composed_system
