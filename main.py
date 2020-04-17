import json
import os
import re
from urllib.request import urlopen

import bs4
from bs4 import BeautifulSoup


def get_chapter(url):
    temp_chapter = dict()
    temp_chapter["header"] = get_header_attributes(url)
    temp_chapter["verses"] = get_verses(url)
    print(f"Chapter:{url} finished")
    return temp_chapter


def get_header_tag(url):
    html = urlopen(url)
    bs_obj = BeautifulSoup(html.read(), features="html.parser")
    return bs_obj.find("div", class_="body").header


def get_header_attributes(url):
    header_dict = dict()
    header = get_header_tag(url)
    for child in header.children:
        try:
            child_id = child['id']
            r = re.compile(r"(\D+)\d+")
            child_id_stripped = r.match(child_id).group(1)
            child_text = child.get_text(strip=True)
            header_dict[child_id_stripped] = child_text
        except KeyError:
            print(f"Object: {child} has no 'id'")
    return header_dict


def get_verse_tag(url):
    html = urlopen(url)
    bs_obj = BeautifulSoup(html.read(), features="html.parser")
    return bs_obj.find("div", class_="body-block")


def get_verses(url):
    verse_list = []
    verses = get_verse_tag(url)
    for verse in verses.children:
        verse_text = ""
        for verse_section in verse.children:
            try:
                if (len(verse_section.contents) == 1 and
                        isinstance(
                            verse_section.contents[0],
                            bs4.element.NavigableString)):
                    verse_text += verse_section.contents[0]
                elif len(verse_section.contents) == 2:
                    try:
                        verse_text += verse_section.contents[1]
                    except TypeError:
                        verse_text += verse_section.contents[1].get_text()
            except AttributeError:
                verse_text += verse_section
        verse_list.append(verse_text)
    return verse_list


lang_list = ["deu", "mlg", "swe"]
with open("ch_numbers.json", "r") as infile:
    book_code_dict = json.load(infile)

for lang in lang_list:
    for book, ch_max in book_code_dict.items():
        for ch_num in range(ch_max):
            url = f"https://www.churchofjesuschrist.org/study/scriptures/" \
                  f"bofm/{book}/{ch_num + 1}?lang={lang} "
            ch_dict = get_chapter(url)

            if not os.path.exists(f"./{lang}/{book}/"):
                os.makedirs(f"./{lang}/{book}/")
            with open(f"./{lang}/{book}/{ch_num + 1:02d}.json", "w") as outfile:
                outfile.write(json.dumps(ch_dict,
                                         indent=2,
                                         sort_keys=True,
                                         ensure_ascii=False))
