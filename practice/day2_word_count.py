from pathlib import Path
import re


def read_text(file_path):
    """Read text from a txt file."""
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()
    return text


def count_words(text):
    """Count word frequency in the text."""
    words = re.findall(r"[a-zA-Z]+", text.lower())

    word_count = {}

    for word in words:
        if word in word_count:
            word_count[word] += 1
        else:
            word_count[word] = 1

    return word_count


def save_result(word_count, output_path):
    """Save word frequency result to a txt file."""
    sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)

    with open(output_path, "w", encoding="utf-8") as file:
        for word, count in sorted_words:
            file.write(f"{word}: {count}\n")


def main():
    project_root = Path(__file__).resolve().parents[1]

    input_path = project_root / "data" / "sample.txt"
    output_path = project_root / "data" / "result.txt"

    text = read_text(input_path)
    word_count = count_words(text)
    save_result(word_count, output_path)

    print("Word count finished.")
    print(f"Result saved to: {output_path}")


if __name__ == "__main__":
    main()