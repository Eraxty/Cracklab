import re

from analysis.frequency import analyze_frequency
from analysis.ngrams import count_ngrams
from analysis.dict import PatternDictionary
from analysis.solver import solve

dictionary = PatternDictionary()
dictionary.load("data/cleaned_words.txt")

with open("crack.txt", "r") as file:
    text = file.read()

cipher_words = re.findall(r"[A-Z]+", text.upper())
solution = solve(cipher_words, dictionary)

print("Solver Result\n")

if solution is None:
    print("No mapping-consistent solution found.")
else:
    print("Words:")
    print(" ".join(solution["words"]))
    print("\nMapping:")

    for cipher_letter in sorted(solution["mapping"]):
        plain_letter = solution["mapping"][cipher_letter]
        print(f"{cipher_letter} -> {plain_letter}")

print("\n")

frequency = analyze_frequency(text)
bigrams = count_ngrams(text, 2)

print(bigrams)
print("Character Frequency\n")

sorted_frequency = sorted(
    frequency.items(),
    key=lambda item: item[1]["count"],
    reverse=True
)

for char, data in sorted_frequency:
    if data["count"] > 0:
        print(f"{char}: {data['count']} ({data['percent']:.2f}%)")
