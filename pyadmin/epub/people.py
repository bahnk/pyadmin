
import sys
import re
import ebooklib
from ebooklib import epub
from collections import defaultdict

book = epub.read_epub(sys.argv[1])

names = []

for item in book.get_items():
    if item.get_type() == ebooklib.ITEM_DOCUMENT:

        content = item.get_content().decode("utf-8").replace(u"\xa0", u" ")

        regex_name = r"[A-Z]\w+\s"
        for i in range(2, 6):
            m = re.findall(i*regex_name, content)
            if m:
                names += [ x.rstrip() for x in m ]

names = sorted(list(set( names )))

f = open(sys.argv[2], "w+")
f.write( "\n".join(names)+"\n" )
f.close()

