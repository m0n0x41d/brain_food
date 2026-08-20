module CalculusOfConstructions

(*
    Course core transcribed from pages 2-12 of the saved third course.

    The saved pages use eval and equate without defining them. Their definitions
    below are a direct F# translation of the matching OCaml source, CoC-60.ml.

    Assignments are intentionally kept in separate scripts.
*)

type Term =
    | Lam of (Term -> Term)
    | Pi of Term * (Term -> Term)
    | Appl of Term * Term
    | Ann of Term * Term
    | Go of int
    | Star
    | Box

let discard _a b = b

let rec pp lvl = function
    | Lam f -> "(λ" + pp (lvl + 1) (f (Go lvl)) + ")"
    | Pi (a, f) -> "(Π" + pp lvl a + "." + pp (lvl + 1) (f (Go lvl)) + ")"
    | Appl (m, n) -> "(" + pp lvl m + " " + pp lvl n + ")"
    | Ann (m, a) -> "(" + pp lvl m + " : " + pp lvl a + ")"
    | Go x -> string x
    | Star -> "*"
    | Box -> "☐"

let rec eval = function
    | Lam f -> Lam(fun n -> eval (f n))
    | Pi (a, f) -> Pi(eval a, fun n -> eval (f n))
    | Appl (m, n) ->
        match eval m, eval n with
        | Lam f, n -> f n
        | m, n -> Appl(m, n)
    | Ann (m, _a) -> eval m
    | (Go _ | Star | Box) as t -> t

let rec equate lvl = function
    | Lam f, Lam g -> equate (lvl + 1) (f (Go lvl), g (Go lvl))
    | Pi (a, f), Pi (b, g) ->
        equate lvl (a, b) && equate (lvl + 1) (f (Go lvl), g (Go lvl))
    | Appl (m, n), Appl (m', n') -> equate lvl (m, m') && equate lvl (n, n')
    | Ann (m, a), Ann (m', b) -> equate lvl (m, m') && equate lvl (a, b)
    | Go x, Go y -> x = y
    | Star, Star
    | Box, Box -> true
    | _, _ -> false

let panic lvl t fmt =
    sprintf fmt >> (fun s -> failwith (s + ": " + pp lvl t))

let rec infer (lvl: int) (ctx: Term list) (term: Term) : Term =
    match term with
    | Pi (a, f) ->
        discard (infer_sort lvl ctx a)
            (infer_sort (lvl + 1) (eval a :: ctx) (f (Go lvl)))
    | Appl (m, n) ->
        match infer lvl ctx m with
        | Pi (a, f) -> discard (check lvl ctx (n, a)) (f n)
        | m_ty -> panic lvl m "Want Π, got %s" (pp lvl m_ty)
    | Ann (m, a) -> discard (infer_sort lvl ctx a) (check lvl ctx (m, eval a))
    | Go x -> List.item (lvl - x - 1) ctx
    | Star -> Box
    | t -> raise(failwith (sprintf "Not inferrable: %s" (pp lvl t)))

and infer_sort lvl ctx a =
    match infer lvl ctx a with
    | Star
    | Box as s -> s
    | ty -> panic lvl a "Want a sort, got %s" (pp lvl ty)

and check (lvl: int) (ctx: Term list) : Term * Term -> Term = function
    | Lam f, Pi (a, g) ->
        discard
            (check (lvl + 1) (a :: ctx) (f (Go lvl), g (Go lvl)))
            (Pi (a, g))
    | Lam f, ty ->
        raise(failwith (sprintf "Want Π, got %s: %s" (pp lvl ty) (pp lvl (Lam f)))) : Term
    | t, ty ->
        let got_ty = infer lvl ctx t

        if equate lvl (ty, got_ty) then ty
        else
            raise(failwith (sprintf "Want type %s, got %s: %s"
                (pp lvl ty) (pp lvl got_ty) (pp lvl t))) : Term

// Тест 1: Проверка базовой сортовой иерархии (* : □)
let test1 () =
    let result = infer 0 [] Star
    printfn "Test 1: Type of *: %s" (pp 0 result)
    assert (equate 0 (result, Box))

// Тест 2: Проверка простой функции идентичности
let test2 () =
    let id_type = Pi(Star, fun _ -> Star)
    let id = Lam(fun x -> x)  // id : * -> *
    let id_ann = Ann(id, id_type)

    let result = infer 0 [] id_ann
    printfn "Test 2: Type of id: %s" (pp 0 result)
    assert (equate 0 (result, id_type))
