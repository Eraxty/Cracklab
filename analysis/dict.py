from analysis.patterns import word_pattern

class PatternDictionary:
    def __init__(self):
        self.patterns = {}

    def load(self, filename):
        with open(filename, "r") as file:
            for word in file:
                word = word.strip().upper()

                # Ignore tiny words
                if len(word) < 2:
                    continue

                pattern = word_pattern(word)

                if pattern not in self.patterns:
                    self.patterns[pattern] = []

                self.patterns[pattern].append(word)

    def find(self, pattern):
        return self.patterns.get(pattern, [])