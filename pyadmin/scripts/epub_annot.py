"""
Extract Kobo annoation context from epub file.
"""

# coding: utf-8

import click

from pyadmin.epub.annotations import get_annotation_dataframe

# pylint: disable=no-value-for-parameter
@click.command()
@click.argument("annot_path")
@click.argument("epub_path")
@click.argument("base_path")
def main(annot_path, epub_path, base_path):
    """
    Takes annotation and associated epub, extracts annoation and saves
    as CSV and JSON file.
    """
    df = get_annotation_dataframe(annot_path, epub_path)
    df.to_csv(f"{base_path}.csv", index=False)
    df.to_json(f"{base_path}.json", "records", indent=3, force_ascii=False)

if __name__ == "__main__":
    main()
