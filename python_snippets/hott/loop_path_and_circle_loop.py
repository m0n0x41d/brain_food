from core.base_types import Path
from core.hits import Circle


class LoopPath(Path):
    __slots__ = ("turns",)

    def __init__(self, base_point, turns: int):
        super().__init__(base_point, base_point)
        self.turns = turns

    def trans(self, other):
        if self.end != other.start:
            raise ValueError(
                "Cannot compose paths: end of first path must equal start of second path"
            )

        if isinstance(other, LoopPath):
            total_turns = self.turns + other.turns
            result = LoopPath(self.start, total_turns)

            return result

        result = super().trans(other)

        return result

    def sym(self):
        result = LoopPath(self.start, -self.turns)

        return result


class CircleLoop(LoopPath):
    __slots__ = ("circle",)

    def __init__(self, circle: Circle, base_point, turns: int):
        if base_point != circle.base():
            raise ValueError("CircleLoop must start at the circle base point")

        super().__init__(base_point, turns)
        self.circle = circle

    @classmethod
    def identity(cls, circle: Circle):
        base_point = circle.base()
        result = cls(circle, base_point, 0)

        return result

    @classmethod
    def generator(cls, circle: Circle):
        base_point = circle.base()
        result = cls(circle, base_point, 1)

        return result

    def trans(self, other):
        if isinstance(other, CircleLoop):
            self._ensure_same_circle(other)
            total_turns = self.turns + other.turns
            result = CircleLoop(self.circle, self.start, total_turns)

            return result

        result = super().trans(other)

        return result

    def sym(self):
        result = CircleLoop(self.circle, self.start, -self.turns)

        return result

    def inverse(self):
        result = self.sym()

        return result

    def power(self, count: int):
        total_turns = self.turns * count
        result = CircleLoop(self.circle, self.start, total_turns)

        return result

    def same_group_element(self, other):
        same_circle = self.circle is other.circle
        same_turns = self.turns == other.turns
        result = same_circle and same_turns

        return result

    def _ensure_same_circle(self, other):
        if self.circle is not other.circle:
            raise ValueError("Cannot compose loops from different circles")


def basic_usage():
    circle = Circle()
    loop = CircleLoop.generator(circle)
    double_loop = loop.power(2)
    inverse_loop = loop.inverse()
    result = double_loop.trans(inverse_loop)

    return result


if __name__ == "__main__":
    print(basic_usage().turns)  #   2 + (-1) = 1
