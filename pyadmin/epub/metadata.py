

import re
from os import listdir
from pathlib import Path

import ebooklib
from ebooklib import epub

directory = "data"

for filename in listdir(directory):

    if not filename.endswith("epub"):
        continue

    path = Path(directory, filename)
    basename = re.sub("\.epub", "", filename)

    # extract metadata from title
    author = basename.split(" - ")[0]
    title = basename.split(" - ")[1]

    # ebooklib object
    book = epub.read_epub(path)

    # ebooklib philosophy forces us to change metadata
    # directly in the metadata object
    for key, value in book.metadata.items():
        
        # has to be a dictionary
        if not isinstance(book.metadata[key], dict):
            continue

        # and the dictionary needs not to be empty
        if len(book.metadata[key]) == 0:
            continue

        # replace author
        for subkey, subvalue in book.metadata[key].items():
            if subkey == "creator":
                book.metadata[key][subkey] = [(author, None)]

        # replace title
        for subkey, subvalue in book.metadata[key].items():
            if subkey == "title":
                book.metadata[key][subkey] = [(title, None)]


    # save
    epub.write_epub(Path("tmp", filename), book, {})

