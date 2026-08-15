#load "CalculusOfConstructions.fs"

open CalculusOfConstructions

let testPolymorphicIdentity () =
    // Π(A : *). A -> A
    // The first Pi accepts an arbitrary type A.
    // The second Pi accepts a value of type A and returns a value of the same type A.
    let polymorphicIdType =
        Pi(Star, fun a -> Pi(a, fun _ -> a))

    // λA. λx. x
    // The function accepts a type A, then a value x of type A, and returns x unchanged.
    let polymorphicId =
        Lam(fun _a -> Lam(fun x -> x))

    // The annotation tells the type checker the expected type of the lambda function.
    let annotatedId =
        Ann(polymorphicId, polymorphicIdType)

    let inferredType =
        infer 0 [] annotatedId

    printfn "Polymorphic id type: %s" (pp 0 inferredType)

    // Verify that the inferred type matches Π(A : *). A -> A.
    assert (equate 0 (inferredType, polymorphicIdType))

testPolymorphicIdentity ()
