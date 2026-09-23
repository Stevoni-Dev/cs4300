# Test to validate task1.
from src.task1 import *

def test_say_hello(capsys):
    captured = capsys.readouterr()
    assert captured.out == "Hello, world!\n"