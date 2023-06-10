#!/usr/bin/python

from os import wait
from pathlib import Path
from collections import defaultdict
import json
import pandas as pd
import networkx as nx
from bs4 import BeautifulSoup

def append(node: dict, folders: list[str], bookmarks: list[dict]) -> None:
    """\
    Appends bookmarks to bookmarks list as dictionary.
    
    It's recursive method that doesn't return anything but append bookmarks to
    a bookmarks list.

    Parameters
    ----------
        node
            Current node as `dict`.
        folders
            Current node's ancestors as `list` of `str`.
        bookmarks
            Bookmarks as `list` of `dict`.
    """
    if node["type"] == "folder":
        for child in node["children"]:
            append(child, folders+[node["name"]], bookmarks)

    if node["type"] == "url":
        dirs = {}
        for i, folder in enumerate(folders):
            dirs[f"Dir_{i}"] = folder

        bookmarks.append({
            **dirs,
            "Name": node["name"],
            "URL": node["url"]
        })

def convert(path: str) -> pd.DataFrame:
    """\
    Converts chromium bookmarks JSON file to `pandas` `DataFrame`.

    Method return a `pandas` `DataFrame` and raises:

        * `FileNotFoundError` if chromium bookmarks JSON doesn't exist
        * `OSError` if chromium bookmarks JSON file can't be open
        * `JSONDecodeError` if chromium bookmarks JSON is not valid

    Parameters
    ----------
        path
            Path to chromium bookmarks JSON file as `str`.
    """
    # check file existence
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"{path} doesn't exist.")

    # open JSON file
    try:
        f_obj = open(path, "r")
    except OSError as os_err:
        print(f"Can't open bookmarks file with path: {path}.")
        raise os_err

    # parse JSON file
    try:
        bookmarks_json = json.loads(f_obj.read())
    except json.JSONDecodeError as json_err:
        print(f"Bookmarks file with path: {path} is not a valid JSON.")
        raise(json_err)

    # close file
    f_obj.close()

    # create data frame
    bookmarks = []
    for node_name, node in bookmarks_json["roots"].items():
        append(node, [], bookmarks)
    dframe = pd.DataFrame.from_records(bookmarks)

    # index is a tuple of folders
    dir_columns = dframe\
        .columns\
        .to_series()\
        .where(lambda x: x.str.startswith("Dir_"))\
        .dropna()\
        .sort_values()\
        .to_list()
    dframe = dframe.set_index(dir_columns)

    # we had every folder just in a separate column but we replase them
    # with a path now
    new_index = dframe\
        .index\
        .to_frame()\
        .apply(lambda x: "/".join(x.dropna().to_list()), axis=1)
    dframe.index = new_index
    dframe.index.name = "Path"
    dframe = dframe.reset_index()

    return dframe

def to_dict(dframe: pd.DataFrame) -> dict:
    """\
    Converts bookmarks `pandas` `DataFrame` hierarchical `dict`.

    Parameters
    ----------
        dframe
            `pandas` `DataFrame` containing bookmarks.
    """
    # dictionary containing bookmarks as a hierarchical structure
    bookmarks = {"root":{"folders": {}}}
    
    # filling the dictionary
    for i, row in dframe.iterrows():

        path = tuple(row.Path.split("/"))
        current_dict = bookmarks["root"]["folders"]

        for f, folder in enumerate(path):

            if not folder in current_dict.keys():
                current_dict[folder] = {"folders": {}, "bookmarks": []}

            if (f+1) == len(path):
                bookmark = {"name": row.Name, "url": row.URL}
                current_dict[folder]["bookmarks"].append(bookmark)

            current_dict = current_dict[folder]["folders"]

        current_dict = bookmarks["root"]

    return bookmarks

def to_graph(dframe: pd.DataFrame) -> nx.Graph:
    """\
    Converts bookmarks `pandas` `DataFrame` to `networkx` `Graph`.

    Parameters
    ----------
        dframe
            `pandas` `DataFrame` containing bookmarks.
    """

    G = nx.Graph()
    
    for i in range(dframe.shape[0]):
    
        row = dframe.iloc[i]
        path = row.Path.split("/")
    
        ############################################################################
        # ancestors nodes
    
    
        if len(path) == 1:
            folder_name = path[0]
            folder_path = tuple(path)
            G.add_node(folder_name, name=folder_name, path=folder_path, type="folder")
    
        if len(path) > 1:
    
            for j in range(len(path)-1):
    
                # parent node
                parent_name = path[j]
                parent_path = tuple(path[:max(j, 1)])
    
                # child node
                child_name = path[j+1]
                child_path = tuple(path[:j+2])
    
                # add to graph
                G.add_node(parent_name, name=parent_name, path=parent_path, type="folder")
                G.add_node(child_name, name=child_name, path=child_path, type="folder")
                G.add_edge(parent_name, child_name)
    
        ############################################################################
        # bookmark as leaf
    
        node = tuple(path + [row.Name])
        G.add_node(node, name=row.Name, path=node, type="url", url=row.URL)
        G.add_edge(path[-1], node)

    return G

def export(node: dict) -> None:
    """\

    Parameters
    ----------
        node
            Current node as `dict`.
        folders
            Current node's ancestors as `list` of `str`.
        bookmarks
            Bookmarks as `list` of `dict`.
    """
    for bookmark in node["bookmarks"]:
        print(bookmark["name"])

    folders = sorted([key for key in node.keys() if key != "bookmarks"])
    for folder in folders:
        export(folder)

def unwrap_html(folder, soup, element):
    """

    <DL> -> <p> -> <DT> -> (<H3> -> <DL> -> <p> -> <DT>...) or (<A>)

    Parameters
    ----------
        folder
        soup
        element
    """
    # description list of this folder
    dl_tag = soup.new_tag("dl")

    # we add all the bookmarks for this section
    if "bookmarks" in folder.keys():

        p_tag = soup.new_tag("p")

        for bookmark in folder["bookmarks"]:

            # bookmark as a link
            a_tag = soup.new_tag("a", href=bookmark["url"])
            a_tag.string = bookmark["name"]

            # adding the description term to descrition list
            dt_tag = soup.new_tag("dt")
            dt_tag.append(a_tag)
            p_tag.append(dt_tag)

        dl_tag.append(p_tag)

    # folders are addeed after bookmarks
    if "folders" in folder.keys():

        for name, subfolder in folder["folders"].items():

            # folder is added as a description term
            dt_tag = soup.new_tag("dt")

            # folder title
            h3_tag = soup.new_tag("h3")
            h3_tag.string = name
            dt_tag.append(h3_tag)

            unwrap(subfolder, soup, dt_tag)

    # we add description list to the parent element
    element.append(dl_tag)

def to_html():
    soup = BeautifulSoup(features="html.parser")
    soup.append(soup.new_tag("meta"))
    soup.meta.append(soup.new_tag("title"))
    soup.meta.append(soup.new_tag("h1"))
    soup.meta.title.string = "Bookmarks"
    soup.meta.h1.string = "Bookmarks"
    dl_tag = soup.new_tag("dl")
    unwrap(bookmarks["root"], soup, dl_tag)
    soup.meta.append(dl_tag)

    with open("/home/hibari/test.html", "w") as file_obj:
        file_obj.write(soup.prettify())


def unwrap_json(folder, node):
    """
    """
    children = []

    if "bookmarks" in folder.keys():
        for bookmark in folder["bookmarks"]:
            children.append({**bookmark, **{"type": "url"}})

    if "folders" in folder.keys():
        for name, subfolder in folder["folders"].items():
            current_folder = {"name": name, "type": "folder"}
            unwrap_json(subfolder, current_folder)
            children.append(current_folder)

    node["children"] = children

def to_json(path):
    """
    """
    bmks = {}
    unwrap_json(bookmarks["root"], bmks)

    bmks = {
        "version": 1,
        "roots": {
            "bookmark_bar": {
                "children": [],
                "name": "Barre de favoris",
                "id": 1
            },
            "synced": {
                "children": [],
                "name": "Favoris sur mobile",
                "id": 2
            },
            "other": {
                "children": bmks["children"],
                "name": "Central",
                "type": "Autres favoris",
                "id": 3
            }
        }
    }

    with open(path, "w") as file_obj:
        file_obj.write(json.dumps(bmks, indent=3))

def unwrap_netscape(html: list[str], folder: dict) -> None:
    """\
    Recursively export bookmarks and bookmarks folders as Netscape bookmarks
    HTML.

    Parameters
    ----------
        html
            HTML lines as `list`.
        folder
            Bookmarks folder as `dict`.
    """
    html += ["<DL><p>\n"]

    # we add all the bookmarks for this section
    if "bookmarks" in folder.keys():
        for bookmark in folder["bookmarks"]:
            url = bookmark["url"]
            title = bookmark["name"]
            html += [f'<DT><A HREF="{url}">{title}</A>\n']

    # folders are addeed after bookmarks
    if "folders" in folder.keys():
        for name, subfolder in folder["folders"].items():
            html += [f"<DT><H3>{name}</H3>\n"]
            unwrap_netscape(html, subfolder)
    
    html += ["</DL><p>\n"]

def export_netscape(bookmarks: dict, path: Path) -> None:
    """\
    Takes a bookmarks `dict` and export it as Netscape bookmark HTML.

    Parameters
    ----------
        bookmarks
            Bookmarks to export as `dict`.
        path
            Path to exported HTML file.
    """
    html = [
        "<!DOCTYPE NETSCAPE-Bookmark-file-1>\n",
        '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">\n',
        "<TITLE>Bookmarks</TITLE>\n",
        "<H1>Bookmarks</H1>\n"
    ]
    
    unwrap_netscape(html, bookmarks["root"])
    html += ["</DL><p>\n"]
    
    # Write HTML to a file
    with open(path, "w") as file:
        file.writelines(html)

