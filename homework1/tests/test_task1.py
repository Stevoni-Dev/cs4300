# Test to validate task1. Import in the test since task1 has no methods
from src.task1 import say_hello

def test_say_hello(capsys):
    say_hello()
    captured = capsys.readouterr()
    assert captured.out == "Hello, World!\n"