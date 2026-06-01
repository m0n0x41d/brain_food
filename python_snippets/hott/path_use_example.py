from dataclasses import dataclass
from decimal import Decimal

from core.base_types import Path

### pseudo business case


@dataclass(frozen=True)
class OrderItem:
    sku: str
    quantity: int
    total: Decimal


@dataclass(frozen=True)
class Order:
    order_id: str
    items: tuple[OrderItem, ...]
    total: Decimal


def money(value: str) -> Decimal:
    return Decimal(value)


def expected_order() -> Order:
    keyboard = OrderItem("keyboard", 1, money("120.00"))
    mouse = OrderItem("mouse", 2, money("70.00"))
    items = (keyboard, mouse)
    order = Order("order-1", items, money("190.00"))

    return order


def stored_order() -> Order:
    keyboard = OrderItem("keyboard", 1, money("120.00"))
    mouse = OrderItem("mouse", 2, money("70.00"))
    items = (keyboard, mouse)
    order = Order("order-1", items, money("190.00"))

    return order


def copy_order(order: Order) -> Order:
    items = tuple(order.items)
    return Order(order.order_id, items, order.total)


def example_path_between_two_orders() -> Path:
    left = stored_order()
    right = expected_order()
    order_path = Path(left, right)

    assert order_path.start == left
    assert order_path.end == right
    assert order_path.start == order_path.end

    return order_path


def example_loop_at_order() -> Path:
    order = expected_order()
    order_copy = copy_order(order)
    to_copy = Path(order, order_copy)
    back_to_order = to_copy.sym()
    order_loop = to_copy.trans(back_to_order)

    assert order_loop.start == order
    assert order_loop.end == order
    assert order_loop == Path.refl(order)

    return order_loop


if __name__ == "__main__":
    order_path = example_path_between_two_orders()
    order_loop = example_loop_at_order()

    print(order_path)
    print(order_loop)


### Simple math, same number is... same number?
# Yes, but how does that happen, same waaay or not?
# IT DOES NOT MATTER!!!?? WDYM?

left = 2 + 3
right = 10 // 2

same_number = Path(left, right)

assert same_number.start == 5
assert same_number.end == 5
assert same_number == Path.refl(5)


### The Hobbit, or There and Back Again


@dataclass(frozen=True, eq=False)
class CaseInsensitiveName:
    text: str

    def normalized(self) -> str:
        normalized_text = self.text.casefold()

        return normalized_text

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, CaseInsensitiveName)
            and self.normalized() == other.normalized()
        )

    def __hash__(self) -> int:
        normalized_text = self.normalized()
        result = hash(normalized_text)

        return result


name = CaseInsensitiveName("Bilbo Baggins")
normalized_name = CaseInsensitiveName("bilbo baggins")


# CaseInsensitiveName("Bilbo Baggins")
#   -> CaseInsensitiveName("bilbo baggins")
#   -> CaseInsensitiveName("Bilbo Baggins")
to_normalized = Path(name, normalized_name)
back = to_normalized.sym()
loop = to_normalized.trans(back)

assert to_normalized.start == to_normalized.end
assert loop.start == name
assert loop.end == name
assert loop == Path.refl(name)
