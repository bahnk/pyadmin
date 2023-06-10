
import sys
import re
import ebooklib
from ebooklib import epub
from collections import defaultdict
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import pandas as pd

def extract_content(text: str):
    """
    Extract content between parentheses.

    :param text: String to parse.
    :type text: str
    :rtype text: str
    """
    content = re.findall(r"\((.*)\)", text)

    if content:
        return content[0]

    return ""

# path to the annotation file
annot_path = "kobo/Digital Editions/Annotations/epub/Bihouix,Philippe - L'age des low techs.epub.annot"
epub_path = "/home/hibari/politique/books/Philippe Bihouix/âge des low-tech, L'/âge des low-tech, L' - Philippe Bihouix.epub"

def get_annotation_dataframe(annotation_file: str, epub_file: str):
    """
    Parse Kobo annotation file and extract annotation context.

    :param annotation_file: Kobo annotation file path.
    :type annotation_file: str
    :param epub_file: Associated epub file path.
    :type epub_file: str
    :rtype: pandas.DataFrame
    """
    # parse the annotation file
    tree = ET.parse(annotation_file)
    root = tree.getroot()
    
    ns = {"default": "http://ns.adobe.com/digitaleditions/annotations"}
    
    book = epub.read_epub(epub_file)
    
    rows = []
    
    # iterate over each annotation in the annotation set
    for annotation in root.findall("./default:annotation", ns):
    
        word = ""
    
        # get the text within the <text> element of the fragment
        try:
            word = annotation.find("./default:target/default:fragment/default:text", ns).text
        except Exception as exc:
            pass
    
        # get the start and end points of the fragment
        start_point = annotation.find("./default:target/default:fragment", ns).attrib["start"]
        end_point = annotation.find("./default:target/default:fragment", ns).attrib["end"]
    
        # extract the content between parentheses
        start_content = extract_content(start_point)
        end_content = extract_content(end_point)
    
        # positions
        indexes = start_content.strip("/").split("/")[:-1]
        begin = start_content.split("/")[-1].split(":")[-1]
        end = end_content.split("/")[-1].split(":")[-1]
    
        # line in the HTML file
        line = int(indexes[-1]) + 4
    
        # HTML file in EPUB file
        html_name = re.sub("#.*", "", start_point).split("/")[-1]
    
        context = ""
    
        for elem in book.get_items():
    
            if isinstance(elem, epub.EpubHtml):
    
                name = elem.get_name().split("/")[-1]
    
                if name == html_name:
                    html_content = elem.get_content().decode("utf-8").split("\n")
                    p = html_content[line]
                    context = BeautifulSoup(p, "html.parser").text
    
        row = {
                "Annotation": word,
                "Context": context,
                "Start": start_point,
                "End": end_point
        }
    
        rows.append(row)
    
    df = pd.DataFrame.from_records(rows)

    return df

