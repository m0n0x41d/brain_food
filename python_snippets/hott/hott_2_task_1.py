from typing import TypeVar

from core.infinity_groupoid import CoherenceConditions, HigherPath, InfinityGroupoid

T = TypeVar("T")


def higher_compose(p: HigherPath[T], q: HigherPath[T]) -> HigherPath[T]:
    if p.dimension != q.dimension:
        raise ValueError("Can't compose paths from different dimensions.")

    if p.end != q.start:
        raise ValueError(
            "Paths not composable, since starting point of q is not the same as the ending point of p."
        )

    if len(p.previous_paths) != len(q.previous_paths):
        raise ValueError("Higher paths must have matching previous path's structure.")

    if p.dimension == 1:
        return InfinityGroupoid.compose(p, q)  # pyright: ignore

    composed_previous_paths = [
        higher_compose(prev_p, prev_q)
        for prev_p, prev_q in zip(p.previous_paths, q.previous_paths)
    ]

    return HigherPath(
        p.dimension,
        p.start,
        q.end,
        composed_previous_paths,
        None,
    )


def pentagon_identity(
    p: HigherPath[T],
    q: HigherPath[T],
    r: HigherPath[T],
    s: HigherPath[T],
) -> HigherPath[T]:
    paths = (p, q, r, s)
    if not all(path.dimension == 1 for path in paths):
        raise ValueError("Pentagon identity requires all paths to have dimension 1.")

    pq = higher_compose(p, q)
    qr = higher_compose(q, r)
    rs = higher_compose(r, s)

    assoc_pqr = CoherenceConditions.associativity(p, q, r)
    assoc_qrs = CoherenceConditions.associativity(q, r, s)
    assoc_pq_r_s = CoherenceConditions.associativity(pq, r, s)
    assoc_p_q_rs = CoherenceConditions.associativity(p, q, rs)
    assoc_p_qr_s = CoherenceConditions.associativity(p, qr, s)

    return HigherPath(
        3,
        p.start,
        s.end,
        [
            assoc_pqr,
            assoc_qrs,
            assoc_pq_r_s,
            assoc_p_q_rs,
            assoc_p_qr_s,
        ],
        None,
    )
