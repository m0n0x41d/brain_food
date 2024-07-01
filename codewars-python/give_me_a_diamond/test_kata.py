from .kata import diamond



def test_diamond():
    assert diamond(1) ==  "*\n"
    assert diamond(2) ==  None
    assert diamond(5) ==  "  *\n ***\n*****\n ***\n  *\n"
    assert diamond(0) ==  None
    assert diamond(-3) == None


