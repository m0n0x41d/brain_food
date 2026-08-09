#load "CalculusOfConstructions.fs"

open CalculusOfConstructions

// 1. Π(A : *). A -> A

let identityFunctionType a =
    Pi(a, fun _ -> a)

let dependentIdentityType =
    Pi(Star, identityFunctionType)

let identityAtAnyType _type =
    Lam(fun value -> value)

let dependentIdentity =
    Lam(identityAtAnyType)

let testDependentFunctionType () =
    let annotatedIdentity =
        Ann(dependentIdentity, dependentIdentityType)

    let inferredType =
        annotatedIdentity
        |> infer 0 []

    let hasExpectedType =
        equate 0 (inferredType, dependentIdentityType)

    printfn "Dependent identity type: %s" (pp 0 inferredType)
    assert hasExpectedType

// 2. Bool = Π(A : *). A -> A -> A

let twoChoicesType a =
    let secondChoiceType =
        Pi(a, fun _ -> a)

    Pi(a, fun _ -> secondChoiceType)

let boolType =
    Pi(Star, twoChoicesType)

let returnFirstChoice firstChoice =
    Lam(fun _secondChoice -> firstChoice)

let trueAtAnyType _type =
    Lam(returnFirstChoice)

let churchTrue =
    Lam(trueAtAnyType)

let returnSecondChoice _firstChoice =
    Lam(fun secondChoice -> secondChoice)

let falseAtAnyType _type =
    Lam(returnSecondChoice)

let churchFalse =
    Lam(falseAtAnyType)

let inferAnnotatedType term expectedType =
    let annotatedTerm =
        Ann(term, expectedType)

    annotatedTerm
    |> infer 0 []

let testBoolType () =
    let trueType =
        inferAnnotatedType churchTrue boolType

    let falseType =
        inferAnnotatedType churchFalse boolType

    let trueHasBoolType =
        equate 0 (trueType, boolType)

    let falseHasBoolType =
        equate 0 (falseType, boolType)

    printfn "Church true type: %s" (pp 0 trueType)
    printfn "Church false type: %s" (pp 0 falseType)
    assert trueHasBoolType
    assert falseHasBoolType

testDependentFunctionType ()
testBoolType ()
