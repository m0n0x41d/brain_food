from enum import Enum
from typing import Any, List, Optional, Protocol, TypeVar

T = TypeVar("T")


class Group(Protocol[T]):
    @property
    def zero(self) -> T: ...

    def plus(self, left: T, right: T) -> T: ...

    def inverse(self, item: T) -> T: ...


# Example 1: Event catalog with operation cancellation capability
class EventType(Enum):
    ADD = "add"
    REMOVE = "remove"
    NOTHING = "nothing"


class CatalogEvent:
    def __init__(self, event_type: EventType, data: Any = None):
        self.event_type = event_type
        self.data = data

    def __repr__(self):
        return f"CatalogEvent({self.event_type.value}, {self.data})"


class EventLog:
    def __init__(self, events: Optional[List[CatalogEvent]] = None):
        self.events = events or []

    def __repr__(self):
        return f"EventLog({len(self.events)} events)"


class EventLogGroup:
    @property
    def zero(self) -> EventLog:
        return EventLog([])

    def plus(self, left: EventLog, right: EventLog) -> EventLog:
        return EventLog(left.events + right.events)

    def inverse(self, item: EventLog) -> EventLog:
        """Inverts events: ADD -> REMOVE, REMOVE -> ADD"""
        inverted_events = []
        for event in reversed(item.events):  # Reverse the order
            if event.event_type == EventType.ADD:
                inverted_events.append(CatalogEvent(EventType.REMOVE, event.data))
            elif event.event_type == EventType.REMOVE:
                inverted_events.append(CatalogEvent(EventType.ADD, event.data))
            else:  # NOTHING remains NOTHING
                inverted_events.append(event)
        return EventLog(inverted_events)


# Example 2: Semiring for graph algorithms (shortest path)
class MinPlusSemiRing:
    @property
    def zero(self) -> float:
        return float("inf")

    @property
    def one(self) -> float:
        return 0.0

    def plus(self, left: float, right: float) -> float:
        return min(left, right)

    def times(self, left: float, right: float) -> float:
        return left + right


class Graph:
    def __init__(self, adjacency_matrix: List[List[float]]):
        self.matrix = adjacency_matrix
        self.size = len(adjacency_matrix)

    def shortest_path_k_steps(self, start: int, end: int, k: int) -> float:
        semiring = MinPlusSemiRing()

        current_matrix = [row[:] for row in self.matrix]  # copy

        for _ in range(k - 1):
            current_matrix = self._multiply_matrices(
                current_matrix, self.matrix, semiring
            )

        return current_matrix[start][end]

    def _multiply_matrices(
        self, A: List[List[float]], B: List[List[float]], semiring: MinPlusSemiRing
    ) -> List[List[float]]:
        n = len(A)
        result = [[semiring.zero for _ in range(n)] for _ in range(n)]

        for i in range(n):
            for j in range(n):
                for k in range(n):
                    product = semiring.times(A[i][k], B[k][j])
                    result[i][j] = semiring.plus(result[i][j], product)

        return result


class Permutation:
    def __init__(self, mapping: List[int]):
        self.mapping = mapping  # mapping[i] shows where element i goes
        self.size = len(mapping)

    def __repr__(self):
        return f"Perm({self.mapping})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Permutation) and self.mapping == other.mapping


class SymmetricGroup:
    def __init__(self, n: int):
        self.n = n

    @property
    def zero(self) -> Permutation:
        return Permutation(list(range(self.n)))

    def plus(self, left: Permutation, right: Permutation) -> Permutation:
        result = [0] * self.n
        for i in range(self.n):
            result[i] = left.mapping[right.mapping[i]]
        return Permutation(result)

    def inverse(self, perm: Permutation) -> Permutation:
        result = [0] * self.n
        for i in range(self.n):
            result[perm.mapping[i]] = i
        return Permutation(result)


if __name__ == "__main__":
    print("=== Event catalog ===")
    group = EventLogGroup()

    log1 = EventLog(
        [CatalogEvent(EventType.ADD, "item1"), CatalogEvent(EventType.ADD, "item2")]
    )

    log2 = EventLog(
        [CatalogEvent(EventType.REMOVE, "item1"), CatalogEvent(EventType.ADD, "item3")]
    )

    combined = group.plus(log1, log2)
    print(f"Combined log: {combined}")

    undo_log1 = group.inverse(log1)
    print(f"Undo log1: {undo_log1}")

    print("\n=== Shortest paths ===")
    # Graph: 0->1 (weight 2), 1->2 (weight 3), 0->2 (weight 10)
    adj_matrix = [
        [0.0, 2.0, 10.0],
        [float("inf"), 0.0, 3.0],
        [float("inf"), float("inf"), 0.0],
    ]

    graph = Graph(adj_matrix)
    shortest_2_steps = graph.shortest_path_k_steps(0, 2, 2)
    print(f"Shortest path from 0 to 2 in 2 steps: {shortest_2_steps}")

    print("\n=== Permutation group ===")
    sym_group = SymmetricGroup(3)

    # Permutation (0->1, 1->2, 2->0)
    perm1 = Permutation([1, 2, 0])
    # Permutation (0->2, 1->0, 2->1)
    perm2 = Permutation([2, 0, 1])

    composition = sym_group.plus(perm1, perm2)
    inverse_perm1 = sym_group.inverse(perm1)

    print(f"Composition {perm1} ∘ {perm2} = {composition}")
    print(f"Inverse of {perm1} = {inverse_perm1}")

    identity_check = sym_group.plus(perm1, inverse_perm1)
    print(f"Check: {perm1} ∘ {inverse_perm1} = {identity_check}")
    print(f"Is this the identity permutation? {identity_check == sym_group.zero}")
