from sortings.binary_search import BinarySearch, SearchStatus


def test_BinarySearch_initializes_full_range_and_in_progress():
    searcher = BinarySearch([1, 3, 5, 7])

    assert searcher.Left == 0
    assert searcher.Right == 3
    assert searcher.GetResult() == int(SearchStatus.IN_PROGRESS)


def test_BinarySearch_keeps_search_in_progress_when_more_than_two_candidates_remain():
    searcher = BinarySearch([1, 3, 5, 7, 9, 11, 13])

    searcher.Step(11)

    assert searcher.Left == 4
    assert searcher.Right == 6
    assert searcher.GetResult() == int(SearchStatus.IN_PROGRESS)


def test_BinarySearch_finds_middle_element_on_first_step():
    searcher = BinarySearch([1, 3, 5, 7, 9])

    searcher.Step(5)

    assert searcher.GetResult() == int(SearchStatus.FOUND)


def test_BinarySearch_finds_value_when_two_candidates_remain():
    searcher = BinarySearch([1, 3, 5, 7])

    searcher.Step(7)

    assert searcher.Left == 2
    assert searcher.Right == 3
    assert searcher.GetResult() == int(SearchStatus.FOUND)


def test_BinarySearch_marks_not_found_when_two_candidates_remain():
    searcher = BinarySearch([1, 3, 5, 7])

    searcher.Step(6)

    assert searcher.Left == 2
    assert searcher.Right == 3
    assert searcher.GetResult() == int(SearchStatus.NOT_FOUND)


def test_BinarySearch_marks_not_found_for_empty_array():
    searcher = BinarySearch([])

    searcher.Step(42)

    assert searcher.GetResult() == int(SearchStatus.NOT_FOUND)


def test_BinarySearch_does_nothing_after_search_is_finished():
    searcher = BinarySearch([1, 3, 5, 7, 9])

    searcher.Step(5)
    left_after_found = searcher.Left
    right_after_found = searcher.Right

    searcher.Step(9)

    assert searcher.Left == left_after_found
    assert searcher.Right == right_after_found
    assert searcher.GetResult() == int(SearchStatus.FOUND)
