from src.task5 import favorite_books, print_first_three_book_titles, students
import pytest

# Validating data structures for task 5.
invalid_book_lists = [
    None,
    "not a list",
    123,
    {},
    set(),
    [("Book",)],                    
    [("Book", "Author", "Extra")],  
    [["Book", "Author"]],           
    [{"title": "Book", "author": "Author"}],  
    [(123, "Author")],           
    [("Book", 123)],                
    [(None, "Author")],           
    [("Book", None)],              
    [("Book", "Author"), "invalid"],  
    [("Book", "Author"), (123, "Author")],
]

@pytest.mark.parametrize(
    "favorite_book_list, expected_output",
    [
        (
            [
                ("The First Law", "Joe Abercrombie"),
                ("The Lord of the Rings", "J.R.R. Tolkien"),
                ("Red Rising", "Pierce Brown"),
            ],
            "The First Law\nThe Lord of the Rings\nRed Rising\n",
        ),
        (
            [
                ("Mistborn", "Brandon Sanderson"),
                ("The Name of the Wind", "Patrick Rothfuss"),
                ("Dune", "Frank Herbert"),
            ],
            "Mistborn\nThe Name of the Wind\nDune\n",
        ),
        (
            [
                ("1984", "George Orwell"),
                ("Animal Farm", "George Orwell"),
                ("Brave New World", "Aldous Huxley"),
                ("Fahrenheit 451", "Ray Bradbury"),
            ],
            "1984\nAnimal Farm\nBrave New World\n",
        ),
        (
            [
                ("A", "Author A"),
                ("B", "Author B"),
                ("C", "Author C"),
            ],
            "A\nB\nC\n",
        ),
        (
            [
                ("The Very Long Book Title That Contains Many Words", "Author"),
                ("Short", "Author"),
                ("Another Book", "Author"),
            ],
            "The Very Long Book Title That Contains Many Words\nShort\nAnother Book\n",
        ),
        (
            [
                ("Book 1", "Author 1"),
                ("Book 2", "Author 2"),
                ("Book 3", "Author 3"),
                ("Book 4", "Author 4"),
                ("Book 5", "Author 5"),
            ],
            "Book 1\nBook 2\nBook 3\n",
        ),
        (
            [
                ("Harry Potter and the Sorcerer's Stone", "J.K. Rowling"),
                ("The Hobbit", "J.R.R. Tolkien"),
                ("The Way of Kings", "Brandon Sanderson"),
                ("The Poppy War", "R.F. Kuang"),
            ],
            "Harry Potter and the Sorcerer's Stone\nThe Hobbit\nThe Way of Kings\n",
        ),
        (
            [
                ("Book With Numbers 123", "Author 1"),
                ("Book-With-Symbols!", "Author 2"),
                ("Book's Title", "Author 3"),
            ],
            "Book With Numbers 123\nBook-With-Symbols!\nBook's Title\n",
        ),
    ],
)
def test_print_first_three_book_titles_valid(
    favorite_book_list, expected_output, capsys
):
    print_first_three_book_titles(favorite_book_list)
    captured = capsys.readouterr()
    assert captured.out == expected_output



@pytest.mark.parametrize("invalid_list", invalid_book_lists)
def test_print_first_three_books_invalid_input(invalid_list):
    with pytest.raises(TypeError):
        assert print_first_three_book_titles(invalid_list) == False

def test_student_is_dictionary():
    assert isinstance(students, dict)


def test_student_has_10_students():
    assert len(students) == 10


def test_student_records_have_correct_structure():
    for student_id, student in students.items():
        assert isinstance(student_id, int)
        assert isinstance(student, dict)

        assert "name" in student
        assert "id" in student

        assert isinstance(student["name"], str)
        assert isinstance(student["id"], int)

        assert student["id"] == student_id