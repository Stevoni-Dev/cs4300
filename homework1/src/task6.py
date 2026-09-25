from pathlib import Path
import re
# Counts the words within task6_read_me.txt

def get_content(file_name: str):
    if not isinstance(file_name, str):
        raise TypeError("Provide a string that points to a file name")
    file_path = Path(__file__).resolve().parent / file_name
    if not file_path.is_file():
        raise TypeError("Provide an existing file")

    with open(file_name, "r", encoding="utf-8") as file:
        content = file.read()
    return content


def count_words_in_string(content: str):
    if not isinstance(content, str):
        raise TypeError("Provide string to evaluate")

    # Only counting words comprised of letters
    word_count = re.findall(r"\b\w+(\'\w)?\b", content)
    return len(word_count)

file_content = get_content("task6_read_me.txt")
print(count_words_in_string(file_content))
