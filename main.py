from analysis.frequency import analyze_frequency

text = "Hello, World!"

frequency = analyze_frequency(text)

print("Character Frequency\n")

sorted_frequency = sorted(
    frequency.items(),
    key=lambda item: item[1]["count"],
    reverse=True
)

for char, data in sorted_frequency:
    if data["count"] > 0:
        print(f"{char}: {data['count']} ({data['percent']:.2f}%)")