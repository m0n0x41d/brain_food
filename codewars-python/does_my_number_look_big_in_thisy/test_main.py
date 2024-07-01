from .main import narcissistic


def test_narcissistic():
    assert narcissistic(0) == True
    assert narcissistic(1) == True
    assert narcissistic(9) == True
    assert narcissistic(153) == True
    assert narcissistic(370) == True
    assert narcissistic(371) == True
    assert narcissistic(407) == True
    assert narcissistic(123) == False
    assert narcissistic(1652) == False
    assert narcissistic(9474) == True
    assert narcissistic(35452590104031691935943) == True
    assert narcissistic(9926315) == True
    assert narcissistic(24678050) == True
    assert narcissistic(10) == False
    assert narcissistic(4070) == False

