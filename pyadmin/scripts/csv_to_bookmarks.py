"""
Convert CSV data frame to bookmarks Netscape HTML file.
"""

# coding: utf-8

from os import getenv
from os.path import join
import click
import pandas as pd

from pyadmin.chromium import bookmarks

# pylint: disable=no-value-for-parameter
@click.command()
@click.argument("csv_path")
@click.argument("html_path")
def main(csv_path, html_path):
    """
    Takes bookmarks CSV data frame and converts in to Netscape HTML file.
    """
    dframe = pd.read_csv(csv_path)
    bmk = bookmarks.to_dict(dframe)
    bookmarks.export_netscape(bmk, html_path)

if __name__ == "__main__":
    main()
