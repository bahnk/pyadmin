"""
Convert chromium JSON bookmarks file to CSV data frame.
"""

# coding: utf-8

from os import getenv
from os.path import join
import click

from pyadmin.chromium import bookmarks

# pylint: disable=no-value-for-parameter
@click.command()
@click.argument("json_path")
@click.argument("csv_path")
def main(json_path, csv_path):
    """
    Takes chromium JSON bookmarks file, extracts bookmarks and convert them
    to CSV data frame.
    """
    dframe = bookmarks.convert(json_path)
    dframe.to_csv(csv_path, index=False)

if __name__ == "__main__":
    main()
