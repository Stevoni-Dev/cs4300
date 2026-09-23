from src.task2 import get_integer, get_float, get_string, get_bool

def test_get_integer():
    assert get_integer() == 42
    assert isinstance(get_integer(), int)

def test_get_float():
    assert get_float() == 3.14
    assert isinstance(get_float(), float)

def test_get_string():
    assert get_string() == "Orange"
    assert isinstance(get_string(), str)

def test_get_bool():
    assert get_bool() == True
    assert isinstance(get_bool(), bool)