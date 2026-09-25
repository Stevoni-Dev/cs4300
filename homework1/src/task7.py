from tabulate import tabulate


def display_students(students):
    return tabulate(
        students,
        headers=["Name", "Age", "Major"],
        tablefmt="grid"
    )


students = [
    ["Alice", 22, "Computer Science"],
    ["Bob", 24, "Mathematics"],
    ["Charlie", 21, "Physics"]
]

print(display_students(students))