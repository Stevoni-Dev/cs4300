

favorite_books = [("The Blade Itself", "Joe Abercrombie"), ("Lord of the Rings", "J.R.R. Tolkein"), ("Mistborn", "Brandon Sanderson"), ("Red Rising", "Pierce Brown"), ("The Name of the Wind", "Patrick Rothfuss")]

# From a list of tuples representing book and author, print the first three books on the list.
def print_first_three_book_titles(favorite_book_list: list[tuple[str, str]]):
    if not isinstance(favorite_book_list, list):
        print("Must provide a list of tuples representing books and authors")
        return False
    if not all(
            isinstance(item, tuple) and 
            len(item) == 2 and 
            isinstance(item[0], str) and 
            isinstance(item[1], str)
            for item in favorite_book_list
        ):
        print("Must provide a list of tuples representing books and authors")
        return False
    first_three_books = [item[0] for item in favorite_book_list[0:3]]
    for book_title in first_three_books:
        print(book_title)
    return True

print_first_three_book_titles(favorite_books)

students = {
    1001: {"name": "Emma Johnson", "id": 1001},
    1002: {"name": "Liam Martinez", "id": 1002},
    1003: {"name": "Olivia Williams", "id": 1003},
    1004: {"name": "Noah Brown", "id": 1004},
    1005: {"name": "Ava Davis", "id": 1005},
    1006: {"name": "Ethan Wilson", "id": 1006},
    1007: {"name": "Sophia Anderson", "id": 1007},
    1008: {"name": "Mason Taylor", "id": 1008},
    1009: {"name": "Isabella Thomas", "id": 1009},
    1010: {"name": "James Moore", "id": 1010}
}