import pytest
from src.task7 import display_students


@pytest.mark.parametrize("students, expected", [
    (
        [
            ["Alice", 22, "Computer Science"],
            ["Bob", 24, "Mathematics"]
        ],
        ["Alice", "22", "Computer Science", "Bob", "24", "Mathematics"]
    ),
    (
        [
            ["John", 18, "Engineering"]
        ],
        ["John", "18", "Engineering"]
    ),
    (
        [
            ["Alice", 20, "Computer Science"],
            ["Bob", 21, "Physics"],
            ["Charlie", 22, "Mathematics"]
        ],
        ["Alice", "20", "Computer Science",
         "Bob", "21", "Physics",
         "Charlie", "22", "Mathematics"]
    ),
    (
        [
            ["Alice Smith", 25, "Computer Science"],
            ["Bob Jones", 30, "History"]
        ],
        ["Alice Smith", "25", "Computer Science",
         "Bob Jones", "30", "History"]
    ),
])
def test_display_students(students, expected):
    result = display_students(students)

    for value in expected:
        assert value in result

def test_display_students_empty_list():
    result = display_students([])

    assert "Name" in result
    assert "Age" in result
    assert "Major" in result