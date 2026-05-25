from typing import Callable, Generic, Literal, TypeVar

from core.base_types import Product, Sum, unit

### first.

type Name = str
type RegularUser = Literal["Regular"]
type PremiumUser = Literal["Premium"]

InitialLevel = Sum(RegularUser, PremiumUser, True)

type User = Product[Name, Sum]

JustUser = Product("John", InitialLevel)


def process_vip(user: User):
    return user.second_value.match(
        lambda _regular: "give a kick",
        lambda _premium: "give a snack",
    )


print(process_vip(JustUser))  # "give a kick"


### second

T = TypeVar("T")  # lucky
E = TypeVar("E")  # unlucky
R = TypeVar("R")  # type for match result


class Result(Generic[T, E]):
    # it aims to be private constructor .success / .failure
    def __init__(self, inner: Sum):
        self._inner = inner

    @classmethod
    def success(cls, value: T) -> "Result[T, E]":
        return cls(Sum.left(value, None))

    @classmethod
    def failure(cls, error: E) -> "Result[T, E]":
        return cls(Sum.right(error, None))

    def match(
        self,
        on_success: Callable[[T], R],
        on_failure: Callable[[E], R],
    ) -> R:
        return self._inner.match(on_success, on_failure)

    def then(self, f: Callable[[T], "Result[R, E]"]) -> "Result[R, E]":
        # Mmmmonadic composition or something, idk, I am not CS Professor.
        return self.match(
            lambda v: f(v),
            lambda e: Result.failure(e),
        )

    def map(self, f: Callable[[T], R]) -> "Result[R, E]":
        # pure func for ok branch is okay
        return self.then(lambda v: Result.success(f(v)))

    def __str__(self) -> str:
        return self.match(
            lambda v: f"Success({v!r})",
            lambda e: f"Failure({e!r})",
        )


def very_safe_div(a: int, b: int) -> Result[int, str]:
    if b == 0:
        return Result.failure("division by zero is impossible, you dummy!")
    return Result.success(a // b)


print(very_safe_div(1, 0))  # Failure('division by zero is impossible, you dummy!')


### another one.


# HoTT natural numbers!
class Nat:
    def __init__(self, inner: Sum):
        self._inner = inner

    @classmethod
    def zero(cls) -> "Nat":
        return cls(Sum.left(unit, None))

    @classmethod
    def succ(cls, n: "Nat") -> "Nat":
        return cls(Sum.right(n, unit))

    def match(self, on_zero, on_succ):
        return self._inner.match(on_zero, on_succ)

    def to_python_int(self) -> int:
        return self.match(
            lambda _unit: 0,
            lambda prev: 1 + prev.to_python_int(),
        )

    def __add__(self, other: "Nat") -> "Nat":
        return self.match(
            lambda _unit: other,
            lambda prev: Nat.succ(prev + other),
        )


two = Nat.succ(Nat.succ(Nat.zero()))
three = Nat.succ(two)
five = two + three
print(five.to_python_int())  # 5
