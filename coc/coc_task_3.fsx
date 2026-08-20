#load "CalculusOfConstructions.fs"

open CalculusOfConstructions

let testChurchAddition () =
    // Nat : *
    let Nat = Pi(Star, fun A -> Pi(Pi(A, fun _ -> A), fun _ -> Pi(A, fun _ -> A)))

    // add : Nat -> Nat -> Nat
    let add_type = Pi(Nat, fun _ -> Pi(Nat, fun _ -> Nat))
    let add =
        Lam(fun m -> Lam(fun n -> Lam(fun A -> Lam(fun s -> Lam(fun z ->
            Appl(Appl(Appl(m, A), s), Appl(Appl(Appl(n, A), s), z)))))))
    let add_ann = Ann(add, add_type)

    let result = infer 0 [] add_ann
    printfn "Type of add: %s" (pp 0 result)
    assert (equate 0 (result, add_type))

testChurchAddition ()
