from functools import reduce
from typing import Any, Callable, Protocol, TypeVar

T = TypeVar("T")


class Monoid(Protocol[T]):
    @property
    def zero(self) -> T: ...

    def plus(self, left: T, right: T) -> T: ...


def mconcat(monoid: Monoid[T], items: list[T]) -> T:
    return reduce(monoid.plus, items, monoid.zero)


class Person:
    def __init__(
        self,
        name: str,
        money: int,
    ):
        self.name = name
        self.money = money

    def __repr__(self):
        return f"Person('{self.name}', {self.money})"


class MaxMoneyMonoid:
    @property
    def zero(self) -> Person:
        return Person("", -float("inf"))

    def plus(self, left: Person, right: Person) -> Person:
        return left if left.money >= right.money else right


class Stats:
    def __init__(
        self,
        sum_val: float = 0,
        count: int = 0,
    ):
        self.sum_val = sum_val
        self.count = count

    @property
    def average(self) -> float:
        return self.sum_val / self.count if self.count > 0 else 0

    def __repr__(self):
        return f"Stats(avg={self.average:.2f}, count={self.count})"


class StatsMonoid:
    @property
    def zero(self) -> Stats:
        return Stats()

    def plus(self, left: Stats, right: Stats) -> Stats:
        return Stats(
            left.sum_val + right.sum_val,
            left.count + right.count,
        )


class PredicateOrMonoid:
    @property
    def zero(self) -> Callable[[Any], bool]:
        return lambda x: False

    def plus(
        self, left: Callable[[Any], bool], right: Callable[[Any], bool]
    ) -> Callable[[Any], bool]:
        return lambda x: left(x) or right(x)


if __name__ == "__main__":
    people = [
        Person("Bob", 1000),
        Person("Alice", 2500),
        Person("Charlie", 800),
        Person("Diana", 3000),
    ]

    richest = mconcat(MaxMoneyMonoid(), people)
    print(f"Most Rich: {richest}")

    values = [10, 20, 30, 40, 50]
    stats_list = [Stats(v, 1) for v in values]
    total_stats = mconcat(StatsMonoid(), stats_list)
    print(f"Total stats: {total_stats}")

    predicates = [
        lambda x: x > 10,
        lambda x: x < 5,
        lambda x: x == 7,
    ]
    combined_predicate = mconcat(PredicateOrMonoid(), predicates)

    test_values = [3, 7, 12, 6]
    filtered = [x for x in test_values if combined_predicate(x)]
    print(f"Filtered: {filtered}")  # [3, 7, 12]
