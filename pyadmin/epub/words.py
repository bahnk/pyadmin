
import re
import ebooklib
from ebooklib import epub
from collections import defaultdict

book = epub.read_epub("David Copperfield.epub")

pieces = []

for item in book.get_items():
    if item.get_type() == ebooklib.ITEM_DOCUMENT:

        content = item.get_content().decode("utf-8").replace(u"\xa0", u" ")

        for piece in content.split(" "):
            pieces.append(piece)

f = open("pieces.txt", "w+")
f.write( "\n".join(pieces) )
f.close()

