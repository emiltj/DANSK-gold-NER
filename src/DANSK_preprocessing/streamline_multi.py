import dacy
import os
import re
import glob
import pandas as pd
from collections import Counter
from spacy.tokens import DocBin, Doc, Span
from spacy.training.corpus import Corpus


# Change cwd
os.chdir("/Users/emiltrencknerjessen/Desktop/priv/masters_thesis")

# Load language object
nlp = dacy.load("medium")

# List relevant data and sort by rater number
data_paths = glob.glob("./data/DANSK-full/unprocessed/rater*/train.spacy")
data_paths.sort()
data_paths.sort(key="./data/DANSK-full/unprocessed/rater_10/train.spacy".__eq__)

# Load in data and get rater indices (if not already loaded)
data = []
raters = []
for path in data_paths:
    # Get rater indices
    rater = re.search(r"\d+", path).group()
    raters.append(int(rater) - 1)

    # Load data
    doc_bin = DocBin().from_disk(path)
    docs = list(doc_bin.get_docs(nlp.vocab))[:20]
    data.append(docs)

# Get a list of all unique docs
unique_docs = []
flat_list = [item for sublist in data for item in sublist]
for doc in flat_list:
    if not any([doc.text == unique_doc.text for unique_doc in unique_docs]):
        print("doc not in unique_docs, now appending to list")
        unique_docs.append(doc)

# Defining a function for retriveing all ents for a given doc
def retrieve_all_ents(doc, all_docs):
    ents_for_doc = []
    # Acquire list of all ents for a doc
    for i in flat_list:
        if i.text == doc.text:
            for ent in i.ents:
                ents_for_doc.append(ent)
    # all_ents.append(ents_for_doc)
    return ents_for_doc


# Defining a function for exploding a doc and exploding its ents
def explode_doc(doc, ents):
    ents_exploded = [
        {
            "ent": ent,
            "ent.text": ent.text,
            "ent.label_": ent.label_,
            "ent.label_and_text": ent.text + ent.label_,
        }
        for ent in ents
    ]
    return {
        "doc.text": doc.text,
        "doc": doc,
        "doc.ents": ents_exploded,
    }


# Defining function for retrieving a list with unique ents, and the count of the unique ents
def doc_ents_count(exploded_doc):
    unique_ents = []
    unique_ents_count = []
    for ent_idx in range(len(exploded_doc["doc.ents"])):
        ent = exploded_doc["doc.ents"][ent_idx]

        # If ent is in unique_ents, unique_ents_count += 1, for same index:
        if any(
            ent["ent.label_and_text"] == unique_ent["ent.label_and_text"]
            for unique_ent in unique_ents
        ):
            print(f"""ent "{ent["ent.text"]}" already in unique_ents""")
            unique_ent_label_and_texts = [
                unique_ent["ent.label_and_text"] for unique_ent in unique_ents
            ]
            index_of_same_ent = unique_ent_label_and_texts.index(
                ent["ent.label_and_text"]
            )
            unique_ents_count[index_of_same_ent] += 1
        else:
            print(f"""ent "{ent["ent.text"]}" not already in unique_ents""")
            unique_ents.append(ent)
            unique_ents_count.append(1)

    return exploded_doc["doc"], unique_ents, unique_ents_count


# Define function for getting ratio of docs where ent appears
def get_ratio(doc, unique_ents, unique_ents_count, all_docs):
    all_doc_texts = [doc.text for doc in all_docs]
    print(all_doc_texts.count(doc.text))
    unique_ents_proportion = [i / 10 for i in unique_ents_count]
    return doc, unique_ents, unique_ents_proportion


ents = retrieve_all_ents(unique_docs[0], flat_list)
exploded_doc = explode_doc(unique_docs[0], ents)
doc, unique_ents, unique_ents_count = doc_ents_count(exploded_doc)
doc, unique_ents, unique_ents_ratio = get_ratio(
    doc, unique_ents, unique_ents_count, flat_list
)
doc, unique_ents, unique_ents_ratio


# Find docs with > 1 raters
docs_multiple_raters = [False] * len(unique_docs)
for i in range(len(unique_docs)):
    doc = unique_docs[i]
    all_doc_texts = [doc.text for doc in flat_list]
    if all_doc_texts.count(doc.text) > 1:
        docs_multiple_raters[i] = True

docs_multiple_raters


# Define a function for overwriting annotations with frequent annotations for a doc
def overwrite_freq_ents(doc, unique_ents, unique_ents_ratio, threshold):
    
    
    