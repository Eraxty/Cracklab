INPUT = "data/words.txt"
OUTPUT = "data/cleaned_words.txt"

with open(INPUT, "r") as infile, open(OUTPUT, "w") as outfile:
    for word in infile:
        word = word.strip().upper()

        # Only keep alphabetic words
        if not word.isalpha():
            continue

        # Ignore 1-letter words (except A and I)
        if len(word) == 1 and word not in ("A", "I"):
            continue

        outfile.write(word + "\n")

print("done")