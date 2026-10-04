from __future__ import annotations

from dataclasses import dataclass

from cubic.cubical_inductive import CubicalCircle, CubicalSphere, CubicalTorus
from cubic.cubical_path import CubicalPath
from cubic.interval import Interval

DIFFERENT_SPACES = -1
DIFFERENT_ENDPOINTS = -2
OUTSIDE_INTERVAL = -3


@dataclass(frozen=True)
class HomotopyPath:
    space: Interval | CubicalCircle | CubicalSphere | CubicalTorus
    path: CubicalPath
    winding: tuple[int, ...]

    def then(self, other: HomotopyPath) -> HomotopyPath | int:
        if self.space is not other.space:
            return DIFFERENT_SPACES
        if self.path.end != other.path.start:
            return DIFFERENT_ENDPOINTS

        path = self.path * other.path
        pairs = zip(self.winding, other.winding)
        sums = map(sum, pairs)
        winding = tuple(sums)
        return HomotopyPath(self.space, path, winding)

    def inverse(self) -> HomotopyPath:
        path = self.path.inverse()
        negated = map(lambda turns: -turns, self.winding)
        winding = tuple(negated)
        return HomotopyPath(self.space, path, winding)

    def constant(self) -> HomotopyPath:
        start = self.path.start
        function = lambda t: start
        path = CubicalPath(function)
        dimensions = len(self.winding)
        winding = (0,) * dimensions
        return HomotopyPath(self.space, path, winding)


def interval_path(space: Interval, start: float, end: float) -> HomotopyPath | int:
    if not (0 <= start <= 1 and 0 <= end <= 1):
        return OUTSIDE_INTERVAL

    function = space.path(start, end)
    path = CubicalPath(function)
    return HomotopyPath(space, path, ())


def circle_loop(space: CubicalCircle) -> HomotopyPath:
    path = CubicalPath(space.loop)
    return HomotopyPath(space, path, (1,))


def sphere_meridian(space: CubicalSphere, position: float) -> HomotopyPath | int:
    if not 0 <= position <= 1:
        return OUTSIDE_INTERVAL

    path = space.merid(position)
    return HomotopyPath(space, path, ())


def torus_loop1(space: CubicalTorus) -> HomotopyPath:
    path = CubicalPath(space.loop1)
    return HomotopyPath(space, path, (1, 0))


def torus_loop2(space: CubicalTorus) -> HomotopyPath:
    path = CubicalPath(space.loop2)
    return HomotopyPath(space, path, (0, 1))


def compare_paths(first: HomotopyPath, second: HomotopyPath) -> bool | int:
    if first.space is not second.space:
        return DIFFERENT_SPACES

    same_start = first.path.start == second.path.start
    same_end = first.path.end == second.path.end
    if not (same_start and same_end):
        return DIFFERENT_ENDPOINTS

    return first.winding == second.winding


def test_interval_paths():
    space = Interval()
    direct = interval_path(space, 0, 1)
    first = interval_path(space, 0, 0.25)
    second = interval_path(space, 0.25, 1)
    joined = first.then(second)
    assert compare_paths(direct, joined) is True
    assert first.then(first) == DIFFERENT_ENDPOINTS
    assert interval_path(space, 0, 2) == OUTSIDE_INTERVAL


def test_circle_paths():
    space = CubicalCircle()
    loop = circle_loop(space)
    backward = loop.inverse()
    round_trip = loop.then(backward)
    rest = loop.constant()
    assert compare_paths(round_trip, rest) is True
    assert compare_paths(loop, rest) is False

    other_space = CubicalCircle()
    other = circle_loop(other_space)
    assert compare_paths(loop, other) == DIFFERENT_SPACES
    assert loop.then(other) == DIFFERENT_SPACES


def test_sphere_paths():
    space = CubicalSphere()
    first = sphere_meridian(space, 0)
    second = sphere_meridian(space, 0.5)
    rest = first.constant()
    assert compare_paths(first, second) is True
    assert compare_paths(first, rest) == DIFFERENT_ENDPOINTS
    assert sphere_meridian(space, 2) == OUTSIDE_INTERVAL


def test_torus_paths():
    space = CubicalTorus()
    horizontal = torus_loop1(space)
    vertical = torus_loop2(space)
    xy = horizontal.then(vertical)
    yx = vertical.then(horizontal)
    assert compare_paths(horizontal, vertical) is False
    assert compare_paths(xy, yx) is True


if __name__ == "__main__":
    test_interval_paths()
    test_circle_paths()
    test_sphere_paths()
    test_torus_paths()
