"""
My Python Admin tools.
"""

from setuptools import setup, find_packages

setup(
    name="pyadmin",
    version="0.0.0",
    description="Python admin tools",
    author="bahnk",
    author_email="nourdinebah@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["click"],
    entry_points={"console_scripts": [
        "admin_epub_annot=pyadmin.scripts.epub_annot:main",
        "admin_bookmarks_to_csv=pyadmin.scripts.bookmarks_to_csv:main",
        "admin_bookmarks_to_html=pyadmin.scripts.csv_to_bookmarks:main"
    ]}
)
