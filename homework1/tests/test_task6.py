from src.task6 import get_content, count_words_in_string
from unittest.mock import patch, mock_open
import pytest

@patch("pathlib.Path.is_file", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data="Hello, world!")
# Verify that get_content returns info
def test_get_content_valid_file(mock_file, mock_exists):
    result = get_content("../fake_path.txt")
    mock_file.assert_called_once()
    mock_exists.assert_called_once()
    assert result == "Hello, world!"

# Verifies that non-existing files return False, no longer providing mock decorator
def test_get_content_non_existing_file(capsys):
    with pytest.raises(TypeError) as exc_info:
        result = get_content("fake_path.txt")
    assert str(exc_info.value) == "Provide an existing file"   

invalid_string_input = [
    None,
    123,
    3.14,
    True,
    False,
    [],
    [1, 2, 3],
    {},
    {"key": "value"},
    ("hello",),
    b"hello",
]

@pytest.mark.parametrize("invalid_input", invalid_string_input)
def test_get_content_invalid_input(capsys, invalid_input):
    with pytest.raises(TypeError) as exc_info:
        result = get_content(invalid_input)
    assert str(exc_info.value) == "Provide a string that points to a file name"   

def test_task6_script():
    content = get_content("../task6_read_me.txt")
    count_words_in_string(content) == 104
    

valid_word_inputs = [
    ("hello world", 2),
    ("The quick brown fox", 4),
    ("hello123 world456", 2),
    ("123 456 789", 3),
    ("hello, world!", 2),
    ("hello-world", 2),
    ("one_two three_four", 2),
    ("$100 costs 50 dollars", 4),
    ("This is John's book", 4),
    ("John's dog", 2),
    ("can't won't shouldn't", 3),
    ("hello... world???", 2),
    ("42 apples and 17 oranges", 5),
    ("Python3 is great", 3),
    ("123abc abc123", 2),
    ("hello @world #python", 3),
    ("email@example.com", 3),
    ("www.example.com", 3),
]

@pytest.mark.parametrize(["valid_input", "actual_word_count"], valid_word_inputs)
def test_count_words_in_string(valid_input, actual_word_count):
    result = count_words_in_string(valid_input)
    assert result == actual_word_count

@pytest.mark.parametrize("invalid_input", invalid_string_input)
def test_count_words_invalid_input(capsys, invalid_input):
    with pytest.raises(TypeError) as exc_info:
        result = count_words_in_string(invalid_input)
    assert str(exc_info.value) == "Provide string to evaluate"