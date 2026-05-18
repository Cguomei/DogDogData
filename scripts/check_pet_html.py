import requests

r = requests.get("http://127.0.0.1:5000", timeout=10)
html = r.text
lines = html.split("\n")

for i, line in enumerate(lines):
    if "pet" in line.lower():
        print(f"{i+1}: {line[:100]}")
