"""Print one kural with its chapter and translations, for writing its story.

    python3 show.py N
"""
import json
import os
import sys

n = int(sys.argv[1])
k = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "kurals.json")))["kurals"][n - 1]
print(f"Kural {n}  -  chapter {k['chapter']}: {k['chapter_en']} ({k['chapter_ta']}), book of {k['book_en']} ({k['book_ta']})\n")
print(k["line1"])
print(k["line2"])
print(f"({k['translit']})\n")
print(f"G. U. Pope (1886): {k['pope']}")
print(f"Drew/Lazarus:      {k['drew']}")
