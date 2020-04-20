import json
import os
from pymongo import MongoClient

# define the client, the database, and the collection
# the database and the collection are created at first insert
# if needed
client = MongoClient("mongodb://jake:nobodyworshipdullexpression@157.245.137.233:27017/reader")
with client:
    mydb = client.reader
    print(mydb.chapters.estimated_document_count())
    quit()
    chapters = mydb["chapters"]
    chapters.delete_many({})
    # get a list of language folders
    lang_list = [x for x in os.walk('./texts/')][0][1]
    print(lang_list)

    with open("ch_numbers.json", "r") as infile:
        book_code_dict = json.load(infile)
    for lang in lang_list:
        for book, ch_max in book_code_dict.items():
            for ch_num in range(ch_max):
                with open(f"./texts/{lang}/{book}/{ch_num + 1:02d}.json",
                          "r") as infile:
                    ch_dict = json.loads(infile.read())
                    # eliminate weird empty verses
                    while "" in ch_dict["verses"]:
                        ch_dict["verses"].remove("")
                    # add a meta key
                    ch_dict["meta"] = {"lang": lang, "book": book, "ch_num": (ch_num + 1)}
                    chapters.insert_one(ch_dict)
                    print(f"added{ ch_dict }")
