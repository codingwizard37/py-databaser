from urllib.error import HTTPError

from pymongo import MongoClient
import json
import os
import re
from urllib.request import urlopen
import bs4
from bs4 import BeautifulSoup

# Globals
book_code_dict = {
    "1-ne": 22,
    "2-ne": 33,
    "jacob": 7,
    "enos": 1,
    "jarom": 1,
    "omni": 1,
    "w-of-m": 1,
    "mosiah": 29,
    "alma": 63,
    "hel": 16,
    "3-ne": 30,
    "4-ne": 1,
    "morm": 9,
    "ether": 15,
    "moro": 10
}


# Given a url, returns a dictionary of the contents of that chapter
def get_chapter(url):
    temp_chapter = dict()
    temp_chapter["header"] = get_header_attributes(url)
    temp_chapter["verses"] = get_verses(url)
    print(f"Chapter:{url} finished")
    return temp_chapter


# Given a url, returns a bs4 tag of the header
def get_header_tag(url):
    html = urlopen(url)
    bs_obj = BeautifulSoup(html.read(), features="html.parser")
    return bs_obj.find("div", class_="body").header


# Given a url, returns a dictionary containg the conetents of the chapter header
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


# Given a url, returns a bs4 tag of the verses
def get_verse_tag(url):
    html = urlopen(url)
    bs_obj = BeautifulSoup(html.read(), features="html.parser")
    return bs_obj.find("div", class_="body-block")


# Given a url, returns a list containg the conetents of each verse
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


def add_new_languages(new_lang):
    # I'm aware of list comprehension, which I could've used to make a list of
    # urls, instead of this triple for loop, but that was causing request issues
    # for some reason.
    for new_book, new_ch_max in book_code_dict.items():
        for new_ch_num in range(new_ch_max):
            url = f"https://www.churchofjesuschrist.org/study/scriptures/" \
                  f"bofm/{new_book}/{new_ch_num + 1}?lang={new_lang}"
            try:

                ch_dict = get_chapter(url)
                # creates folders which don't exist yet
                if not os.path.exists(f"./texts/{new_lang}/{new_book}/"):
                    os.makedirs(f"./texts/{new_lang}/{new_book}/")
                with open(f"./texts/{new_lang}/{new_book}/{new_ch_num + 1:02d}.json",
                          "w") as outfile:
                    outfile.write(json.dumps(ch_dict,
                                             indent=2,
                                             sort_keys=True,
                                             ensure_ascii=False))
            except HTTPError as err:
                print(err.code)

def add_lang_to_database(lang_short, collection):
    results = collection.find_one({"lang_short": lang_short})
    if not results:
        lang_long = input(f"Please input the long-form of {lang_short}: ")
        lang_dict = {"lang_short": lang_short, "lang_long": lang_long}
        collection.insert_one(lang_dict)


input_string = input("Enter new language codes seperated by a blank space, "
                     "or \"NONE\" if none: ")
input_list = []
if input_string.lower() != "none":
    input_list = input_string.split(" ")

is_refresh_old = input("Should all languages be refreshed in database from text folder? (Y/n): ") == "Y"


# define the client, the database, and the collection
# the database and the collection are created at first insert
# if needed
client = MongoClient("mongodb://jake:nobodyworshipdullexpression@157.245.137.233:27017/reader")

with client:
    mydb = client.reader
    chapter_collection = mydb["chapters"]
    language_collection = mydb["languages"]

    # get a list of language folders
    if is_refresh_old:
        lang_list = [x for x in os.walk('./texts/')][0][1]
    else:
        lang_list = input_list

    for lang in lang_list:
        add_lang_to_database(lang, language_collection)

        for book, ch_max in book_code_dict.items():
            for ch_num in range(ch_max):

                results = chapter_collection.find_one({"meta": {"lang": lang,
                                                                "book": book,
                                                                "ch_num": (
                                                                            ch_num + 1)}})
                filename = f"./texts/{lang}/{book}/{ch_num + 1:02d}.json"
                if not results:
                    if not os.path.isfile(filename):
                        add_new_languages(lang)
                    with open(filename, "r") as infile:
                        ch_dict = json.loads(infile.read())
                        # TODO: add to add chapter part of program
                        # eliminate weird empty verses
                        while "" in ch_dict["verses"]:
                            ch_dict["verses"].remove("")
                        # add a meta key
                        ch_dict["meta"] = {"lang": lang, "book": book,
                                           "ch_num": (ch_num + 1)}
                        # END TODO
                        chapter_collection.insert_one(ch_dict)
                        print(f"Added: {lang} {book} {ch_num + 1}")
                else:
                    print(f"Skipped: {lang} {book} {ch_num + 1}")