@dataclass
class CartesianPoint:
    x: float
    y: float


@dataclass
class PolarPoint:
    r: float
    theta: float


def cartesian_to_polar(point: CartesianPoint) -> PolarPoint:
    radius = hypot(point.x, point.y)
    angle = atan2(point.y, point.x)
    return PolarPoint(radius, angle)


def polar_to_cartesian(point: PolarPoint) -> CartesianPoint:
    x = point.r * cos(point.theta)
    y = point.r * sin(point.theta)
    return CartesianPoint(x, y)


def test_coordinate_glue() -> None:
    # same constant witnesses as in the lesson; check the round trips below
    qinv = CubicalQInv(
        forward=cartesian_to_polar,
        backward=polar_to_cartesian,
        forward_backward=lambda point: CubicalPath(lambda t: point),
        backward_forward=lambda point: CubicalPath(lambda t: point),
    )
    equiv = CubicalEquivalence(cartesian_to_polar, qinv)
    type_path = cubical_uni_axi(CartesianPoint, PolarPoint, equiv)
    transport = CubicalTransport(type_path)

    forward = Direction(1)
    backward = Direction(0)

    # take (3, 4) on a polar path, then bring it to the start
    cartesian = CartesianPoint(3.0, 4.0)
    polar = transport.transport(cartesian, forward)
    restored_cartesian = transport.transport(polar, backward)

    assert isclose(polar.r, 5.0, abs_tol=1e-9)
    assert isclose(polar.theta, 0.9272952180016122, abs_tol=1e-9)
    assert isclose(restored_cartesian.x, cartesian.x, abs_tol=1e-9)
    assert isclose(restored_cartesian.y, cartesian.y, abs_tol=1e-9)

    # regular polar coordinates
    polar = PolarPoint(2.0, pi / 2)
    cartesian = transport.transport(polar, backward)
    restored_polar = transport.transport(cartesian, forward)

    # cos(pi / 2) is almost zero, floats have their quirks
    assert isclose(cartesian.x, 0.0, abs_tol=1e-9)
    assert isclose(cartesian.y, 2.0, abs_tol=1e-9)
    assert isclose(restored_polar.r, polar.r, abs_tol=1e-9)
    assert isclose(restored_polar.theta, polar.theta, abs_tol=1e-9)
