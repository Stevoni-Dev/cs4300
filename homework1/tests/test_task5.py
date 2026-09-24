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

valid_book_lists = [   
    [("The Name of the Wind", "Patrick Rothfuss"),
     ("The Wise Man's Fear", "Patrick Rothfuss"),
     ("The Hobbit", "J.R.R. Tolkien")],
    
    [("1984", "George Orwell"),
     ("Brave New World", "Aldous Huxley"),
     ("Fahrenheit 451", "Ray Bradbury"),
     ("Animal Farm", "George Orwell")],
    
    [("The Way of Kings", "Brandon Sanderson"),
     ("Words of Radiance", "Brandon Sanderson"),
     ("Oathbringer", "Brandon Sanderson"),
     ("Rhythm of War", "Brandon Sanderson"),
     ("Wind and Truth", "Brandon Sanderson")],
    
    [("Pride and Prejudice", "Jane Austen"),
     ("Jane Eyre", "Charlotte Bronte"),
     ("Wuthering Heights", "Emily Bronte")],
    
    [("The Great Gatsby", "F. Scott Fitzgerald"),
     ("To Kill a Mockingbird", "Harper Lee"),
     ("The Catcher in the Rye", "J.D. Salinger"),
     ("Of Mice and Men", "John Steinbeck"),
     ("The Grapes of Wrath", "John Steinbeck")],
    
    [("The Fellowship of the Ring", "J.R.R. Tolkien"),
     ("The Two Towers", "J.R.R. Tolkien"),
     ("The Return of the King", "J.R.R. Tolkien")],
    
    [("Red Rising", "Pierce Brown"),
     ("Golden Son", "Pierce Brown"),
     ("Morning Star", "Pierce Brown"),
     ("Iron Gold", "Pierce Brown"),
     ("Dark Age", "Pierce Brown"),
     ("Light Bringer", "Pierce Brown")]
]

@pytest.mark.parametrize("valid_list", valid_book_lists)
def test_print_first_three_books_valid_input(valid_list):
    assert print_first_three_book_titles(valid_list) == True

@pytest.mark.parametrize("invalid_list", invalid_book_lists)
def test_print_first_three_books_invalid_input(invalid_list):
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