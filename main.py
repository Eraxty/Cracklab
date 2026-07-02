import string
x = "Hello, World!"

chars = string.ascii_letters + string.digits

def analyze_frequency(text: str):
    frequency = {char: 0 for char in chars}

    for char in text:
        if char in frequency:
            frequency[char] += 1

    return frequency

analyzed_frequency = analyze_frequency(x)

length = sum(analyzed_frequency.values())

print(f"Length of the string: {length}")
print("Character frequency:")

import string
x = "Hello, World!"

chars = string.ascii_letters + string.digits

def analyze_frequency(text: str):
    frequency = {char: 0 for char in chars}

    for char in text:
        if char in frequency:
            frequency[char] += 1

    return frequency

analyzed_frequency = analyze_frequency(x)

length = sum(analyzed_frequency.values())

print(f"Length of the string: {length}")

print("Character frequency:")
sorted_frequency = sorted(
    analyzed_frequency.items(),
    key=lambda item: item[1],
    reverse=True
)

for char, freq in sorted_frequency:
    if freq:
        print(f"{char}: {freq}")