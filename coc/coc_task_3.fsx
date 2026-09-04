#load "CalculusOfConstructions.fs"

open CalculusOfConstructions

// Definitions from the previous course test.
let Nat = Pi(Star, fun A -> Pi(Pi(A, fun _ -> A), fun _ -> Pi(A, fun _ -> A)))

let zero = Lam(fun _A -> Lam(fun _s -> Lam(fun z -> z)))
let zero_ann = Ann(zero, Nat)

let succ =
    Lam(fun n ->
        Lam(fun A ->
            Lam(fun s ->
                Lam(fun z ->
                    Appl(s, Appl(Appl(Appl(n, A), s), z))))))

let succ_type = Pi(Nat, fun _ -> Nat)
let succ_ann = Ann(succ, succ_type)
let one = Appl(succ_ann, zero_ann)

let testChurchAddition () =
    // add : Nat -> Nat -> Nat
    // add = λm. λn. λA. λs. λz. m A s (n A s z)
    let add =
        Lam(fun m ->
            Lam(fun n ->
                Lam(fun A ->
                    Lam(fun s ->
                        Lam(fun z ->
                            Appl(
                                Appl(
                                    Appl(m, A),
                                    s
                                ),
                                Appl(
                                    Appl(
                                        Appl(n, A),
                                        s
                                    ),
                                    z
                                )
                            )
                        )
                    )
                )
            ))

    let add_type = Pi(Nat, fun _ -> Pi(Nat, fun _ -> Nat))
    let add_ann = Ann(add, add_type)

    // Check the types of add and one + one.
    let add_check = infer 0 [] add_ann
    let two = Appl(Appl(add_ann, one), one)
    let two_type = infer 0 [] two

    printfn "Type of add: %s" (pp 0 add_check)
    printfn "Type of two: %s" (pp 0 two_type)

    assert (equate 0 (add_check, add_type))
    assert (equate 0 (two_type, Nat))

testChurchAddition ()
