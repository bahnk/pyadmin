
import re
import ebooklib
from ebooklib import epub
from collections import defaultdict

book = epub.read_epub("noiriel.epub")

dates = []
names = []

mois = [
    "janvier",
    "février",
    "mars",
    "avril",
    "mai",
    "juin",
    "juillet",
    "août",
    "septembre",
    "octobre",
    "novembre",
    "décembre"
        ]

for item in book.get_items():
    if item.get_type() == ebooklib.ITEM_DOCUMENT:

        content = item.get_content().decode("utf-8").replace(u"\xa0", u" ")

        regex_year = r"\d{4}"
        regex_year = r"(\d{2})\s(\w+)\s(\d{4})"
        m = re.findall(regex_year, content)
        if m:
            for date in m:
                if date[1] in mois:
                    dates.append(date)

        regex_name = r"[A-Z]\w+\s[A-Z]\w+\s"
        m = re.findall(regex_name, content)
        if m:
            names += m

dates = sorted( dates, key=lambda x:(x[2],x[1],x[0]) )
#dates = sorted(list(set(map( lambda x: int(x) , dates ))))
dates_rank = defaultdict(lambda : 0)
for date in dates:
    dates_rank[date] += 1

for date in dates:
    print( " ".join([ d for d in date ]) )

names = sorted(list(set( names )))



