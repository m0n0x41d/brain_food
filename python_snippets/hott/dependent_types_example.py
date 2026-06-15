from dataclasses import dataclass
from typing import Callable

from core.dependent_types import Pi, Sigma


# It would be nice to also provide a way with Pi types to save
# ourselves from incorrect operations. lets try it with vectors of same sizes.
@dataclass(frozen=True)
class Vector:
    items: tuple[int, ...]

    def length(self) -> int:
        result = len(self.items)

        return result


@dataclass(frozen=True)
class VectorLengthMismatch:
    expected: int
    observed: int


# using failures as values here,
# feels like an easier way to see the type story in the example.
VectorResult = Vector | VectorLengthMismatch
NumberResult = int | VectorLengthMismatch


# here are our operations
@dataclass(frozen=True)
class VectorOperations:
    create: Callable[[tuple[int, ...]], VectorResult]
    zero: Callable[[], Vector]
    add: Callable[[Vector, Vector], VectorResult]
    dot: Callable[[Vector, Vector], NumberResult]


def _length_mismatch(vector: Vector, expected: int) -> VectorLengthMismatch:
    observed = vector.length()
    result = VectorLengthMismatch(expected=expected, observed=observed)

    return result


def _same_expected_length(left: Vector, right: Vector, expected: int) -> bool:
    left_length_matches = left.length() == expected
    right_length_matches = right.length() == expected
    result = left_length_matches and right_length_matches

    return result


def _first_length_mismatch(
    left: Vector, right: Vector, expected: int
) -> VectorLengthMismatch:
    left_length_matches = left.length() == expected

    if not left_length_matches:
        return _length_mismatch(left, expected)

    result = _length_mismatch(right, expected)

    return result


def vector_operations_pi_example() -> Pi[int, VectorOperations]:
    # Pi example: take n first, then get the small "API" for vectors of that length.
    def operations_for_length(expected_length: int) -> VectorOperations:
        def create(items: tuple[int, ...]) -> VectorResult:
            vector = Vector(items=items)

            # lame sized vector gets kick
            if vector.length() != expected_length:
                return _length_mismatch(vector, expected_length)

            return vector

        def zero() -> Vector:
            items = tuple(0 for _ in range(expected_length))
            result = Vector(items=items)

            return result

        def add(left: Vector, right: Vector) -> VectorResult:
            if not _same_expected_length(left, right, expected_length):
                return _first_length_mismatch(left, right, expected_length)

            pairs = zip(left.items, right.items)
            items = tuple(left_item + right_item for left_item, right_item in pairs)
            result = Vector(items=items)

            return result

        def dot(left: Vector, right: Vector) -> NumberResult:
            if not _same_expected_length(left, right, expected_length):
                return _first_length_mismatch(left, right, expected_length)

            pairs = zip(left.items, right.items)
            products = tuple(left_item * right_item for left_item, right_item in pairs)
            result = sum(products)

            return result

        result = VectorOperations(create=create, zero=zero, add=add, dot=dot)

        return result

    result = Pi(
        domain=int,
        codomain=lambda length: VectorOperations,
        function=operations_for_length,
    )

    return result


# small sigma type example. It is quite cool to bundle vector and its size at a type level
def vector_with_length_sigma_example(
    vector: Vector, claimed_length: int
) -> Sigma[Vector, int] | VectorLengthMismatch:
    observed_length = vector.length()

    # if lies, don't build the pairs
    if observed_length != claimed_length:
        return VectorLengthMismatch(expected=claimed_length, observed=observed_length)

    result = Sigma(
        domain=Vector,
        codomain=lambda selected_vector: int,
        first=vector,
        second=claimed_length,
    )

    return result


def run_vector_operations_pi_example() -> bool:
    vector_operations = vector_operations_pi_example()
    length_three_operations = vector_operations(3)

    # happy case
    left = length_three_operations.create((1, 2, 3))
    right = length_three_operations.create((10, 20, 30))

    # to test failure
    shorter = Vector(items=(1, 2))

    assert isinstance(left, Vector)
    assert isinstance(right, Vector)

    added = length_three_operations.add(left, right)
    dotted = length_three_operations.dot(left, right)
    failed_add = length_three_operations.add(left, shorter)

    assert added == Vector(items=(11, 22, 33))
    assert dotted == 140
    assert failed_add == VectorLengthMismatch(expected=3, observed=2)

    return True


def run_vector_with_length_sigma_example() -> bool:
    vector = Vector(items=(4, 8, 15, 16))

    valid_pair = vector_with_length_sigma_example(vector, 4)
    invalid_pair = vector_with_length_sigma_example(vector, 3)

    assert isinstance(valid_pair, Sigma)
    assert valid_pair.first == vector
    assert valid_pair.second == 4
    assert invalid_pair == VectorLengthMismatch(expected=3, observed=4)

    return True


# -----------------------------------------------------------------------------
# Let's try to use the same Pi/Sigma ideas, but closer to boring business app logic.
# I came to the realization that dependent types are very nice. Functions,
# some "logic," are types too after all, and we are constantly reinventing the wheel
# in the form of heuristic cyclomatic madness "if-elif-elif-then-else-wtf" while
# solving business requirements. What is a dependent type? Well... it is a type
# dependent on a value, and not only on other types. So why not buckle up
# and pack in the emulation of dependent types all the enum and cyclomatic stuff we have
# already done? Let's explore a simple example of parameterizing basic fintech
# logic cases with... Markets/Countries!!!
#
# Pi part: Market -> PricingPolicy. We choose the market first, and then the
# pricing function already belongs to that market. No one has to drag a country
# enum through a giant branching mess.
#
# Sigma part: PricedOrder + OrderValidationProof. We don't pass a naked order
# forward; we pass the order together with proof that subtotal, total, currency
# and lines were checked.
#
# This example show how we can use dependent type ideas in languages where
# dependent types are not supported. It is literraly drag us to place where
# it is more natuarel and solid to express real like logic in code.
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class Market:
    code: str
    currency: str


US_MARKET = Market(code="US", currency="USD")
EU_MARKET = Market(code="EU", currency="EUR")
AM_MARKET = Market(code="AM", currency="AMD")
### an so on, three is enough here


@dataclass(frozen=True)
class OrderLine:
    sku: str
    quantity: int
    unit_price_cents: int


@dataclass(frozen=True)
class DraftOrder:
    market: Market
    lines: tuple[OrderLine, ...]
    discount_cents: int
    shipping_cents: int


# I must use more concrete types here instead of ints, but let it be.
# It is just an example after all.
@dataclass(frozen=True)
class PricedOrder:
    draft: DraftOrder
    subtotal_cents: int
    discount_cents: int
    shipping_cents: int
    tax_cents: int
    total_cents: int
    currency: str


@dataclass(frozen=True)
class PricingMarketMismatch:
    expected: Market
    observed: Market


# using mistakes as values again.
PricingResult = PricedOrder | PricingMarketMismatch


@dataclass(frozen=True)
class TaxRateBps:
    value: int

    def tax_cents_for(self, taxable_cents: int) -> int:
        result = taxable_cents * self.value // 10_000

        return result


@dataclass(frozen=True)
class PricingPolicy:
    market: Market
    tax_rate: TaxRateBps
    price: Callable[[DraftOrder], PricingResult]


@dataclass(frozen=True)
class MissingPricingPolicy:
    market: Market


PricingPolicyResult = PricingPolicy | MissingPricingPolicy


def _line_total_cents(line: OrderLine) -> int:
    result = line.quantity * line.unit_price_cents

    return result


def _subtotal_cents(order: DraftOrder) -> int:
    line_totals = tuple(_line_total_cents(line) for line in order.lines)
    result = sum(line_totals)

    return result


def _tax_cents(taxable_cents: int, tax_rate: TaxRateBps) -> int:
    result = tax_rate.tax_cents_for(taxable_cents)

    return result


def _price_order(
    order: DraftOrder, market: Market, tax_rate: TaxRateBps
) -> PricingResult:
    if order.market != market:
        return PricingMarketMismatch(expected=market, observed=order.market)

    subtotal_cents = _subtotal_cents(order)
    taxable_cents = subtotal_cents - order.discount_cents
    tax_cents = _tax_cents(taxable_cents, tax_rate)
    total_cents = taxable_cents + order.shipping_cents + tax_cents

    result = PricedOrder(
        draft=order,
        subtotal_cents=subtotal_cents,
        discount_cents=order.discount_cents,
        shipping_cents=order.shipping_cents,
        tax_cents=tax_cents,
        total_cents=total_cents,
        currency=market.currency,
    )

    return result


def market_pricing_policy_pi_example() -> Pi[Market, PricingPolicyResult]:
    # finally – pi type example: every market gets its own pricing function.
    def policy_for_market(market: Market) -> PricingPolicyResult:
        market_tax_rates = {
            US_MARKET: TaxRateBps(value=825),
            EU_MARKET: TaxRateBps(value=2000),
            AM_MARKET: TaxRateBps(value=2000),
        }

        if market not in market_tax_rates:
            return MissingPricingPolicy(market=market)

        tax_rate = market_tax_rates[market]
        result = PricingPolicy(
            market=market,
            tax_rate=tax_rate,
            price=lambda order: _price_order(order, market, tax_rate),
        )

        return result

    result = Pi(
        domain=Market,
        codomain=lambda market: PricingPolicyResult,
        function=policy_for_market,
    )

    return result


@dataclass(frozen=True)
class OrderValidationProof:
    line_count: int
    subtotal_cents: int
    total_cents: int
    currency: str


@dataclass(frozen=True)
class OrderValidationError:
    reasons: tuple[str, ...]


ValidatedOrderResult = Sigma[PricedOrder, OrderValidationProof] | OrderValidationError


def _expected_total_cents(order: PricedOrder) -> int:
    taxable_cents = order.subtotal_cents - order.discount_cents
    result = taxable_cents + order.shipping_cents + order.tax_cents

    return result


def _empty_order_reasons(order: PricedOrder) -> tuple[str, ...]:
    if order.draft.lines:
        return ()

    return ("order has no lines",)


def _line_quantity_reasons(order: PricedOrder) -> tuple[str, ...]:
    result = tuple(
        f"{line.sku} quantity must be positive"
        for line in order.draft.lines
        if line.quantity <= 0
    )

    return result


def _line_price_reasons(order: PricedOrder) -> tuple[str, ...]:
    result = tuple(
        f"{line.sku} price must be non-negative"
        for line in order.draft.lines
        if line.unit_price_cents < 0
    )

    return result


def _subtotal_reasons(order: PricedOrder) -> tuple[str, ...]:
    expected_subtotal = _subtotal_cents(order.draft)

    if expected_subtotal == order.subtotal_cents:
        return ()

    return (f"subtotal must be {expected_subtotal}",)


def _discount_reasons(order: PricedOrder) -> tuple[str, ...]:
    discount_is_negative = order.discount_cents < 0
    discount_exceeds_subtotal = order.discount_cents > order.subtotal_cents

    if discount_is_negative:
        return ("discount must be non-negative",)

    if discount_exceeds_subtotal:
        return ("discount cannot exceed subtotal",)

    return ()


def _total_reasons(order: PricedOrder) -> tuple[str, ...]:
    expected_total = _expected_total_cents(order)

    if expected_total == order.total_cents:
        return ()

    return (f"total must be {expected_total}",)


def _currency_reasons(order: PricedOrder) -> tuple[str, ...]:
    expected_currency = order.draft.market.currency

    if expected_currency == order.currency:
        return ()

    return (f"currency must be {expected_currency}",)


def _priced_order_reasons(order: PricedOrder) -> tuple[str, ...]:
    reason_groups = (
        _empty_order_reasons(order),
        _line_quantity_reasons(order),
        _line_price_reasons(order),
        _subtotal_reasons(order),
        _discount_reasons(order),
        _total_reasons(order),
        _currency_reasons(order),
    )
    result = tuple(reason for group in reason_groups for reason in group)

    return result


def validated_order_sigma_example(order: PricedOrder) -> ValidatedOrderResult:
    # sigma-type example: keep the order together with the proof we checked.
    reasons = _priced_order_reasons(order)

    if reasons:
        return OrderValidationError(reasons=reasons)

    proof = OrderValidationProof(
        line_count=len(order.draft.lines),
        subtotal_cents=order.subtotal_cents,
        total_cents=order.total_cents,
        currency=order.currency,
    )
    result = Sigma(
        domain=PricedOrder,
        codomain=lambda priced_order: OrderValidationProof,
        first=order,
        second=proof,
    )

    return result


def _sample_us_order() -> DraftOrder:
    lines = (
        OrderLine(sku="course", quantity=1, unit_price_cents=10_000),
        OrderLine(sku="book", quantity=2, unit_price_cents=1_500),
    )
    result = DraftOrder(
        market=US_MARKET,
        lines=lines,
        discount_cents=500,
        shipping_cents=1_200,
    )

    return result


def run_market_pricing_policy_pi_example() -> bool:
    pricing_policy = market_pricing_policy_pi_example()
    us_policy = pricing_policy(US_MARKET)
    eu_policy = pricing_policy(EU_MARKET)
    unknown_policy = pricing_policy(Market(code="ZZ", currency="ZZZ"))

    assert isinstance(us_policy, PricingPolicy)
    assert isinstance(eu_policy, PricingPolicy)
    assert isinstance(unknown_policy, MissingPricingPolicy)
    assert us_policy.tax_rate == TaxRateBps(value=825)

    us_order = _sample_us_order()
    priced_order = us_policy.price(us_order)
    wrong_market_result = eu_policy.price(us_order)

    assert isinstance(priced_order, PricedOrder)
    assert priced_order.subtotal_cents == 13_000
    assert priced_order.tax_cents == 1_031
    assert priced_order.total_cents == 14_731
    assert wrong_market_result == PricingMarketMismatch(
        expected=EU_MARKET, observed=US_MARKET
    )

    return True


def run_validated_order_sigma_example() -> bool:
    pricing_policy = market_pricing_policy_pi_example()
    us_policy = pricing_policy(US_MARKET)

    assert isinstance(us_policy, PricingPolicy)

    priced_order = us_policy.price(_sample_us_order())

    assert isinstance(priced_order, PricedOrder)

    validated_order = validated_order_sigma_example(priced_order)
    invalid_order = PricedOrder(
        draft=priced_order.draft,
        subtotal_cents=priced_order.subtotal_cents + 1,
        discount_cents=priced_order.discount_cents,
        shipping_cents=priced_order.shipping_cents,
        tax_cents=priced_order.tax_cents,
        total_cents=priced_order.total_cents,
        currency=priced_order.currency,
    )
    rejected_order = validated_order_sigma_example(invalid_order)

    assert isinstance(validated_order, Sigma)
    assert validated_order.first == priced_order
    assert validated_order.second.line_count == 2
    assert validated_order.second.total_cents == 14_731
    assert rejected_order == OrderValidationError(
        reasons=("subtotal must be 13000", "total must be 14732")
    )

    return True


if __name__ == "__main__":
    assert run_vector_operations_pi_example()
    assert run_vector_with_length_sigma_example()
    assert run_market_pricing_policy_pi_example()
    assert run_validated_order_sigma_example()
    print("Dependent type examples passed")
