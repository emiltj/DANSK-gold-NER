import dacy
import os
import re
import glob
import pandas as pd
from collections import Counter
from spacy.tokens import DocBin, Doc, Span
from spacy.training.corpus import Corpus

############ Defining functions ############

# Defining a function for retriveing all ents for a given doc
def retrieve_all_ents(doc, all_docs):
    ents_for_doc = []
    # Acquire list of all ents for a doc
    for i in flat_list:
        if i.text == doc.text:
            for ent in i.ents:
                ents_for_doc.append(ent)
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
            # print(f"""ent "{ent["ent.text"]}" already in unique_ents""")
            unique_ent_label_and_texts = [
                unique_ent["ent.label_and_text"] for unique_ent in unique_ents
            ]
            index_of_same_ent = unique_ent_label_and_texts.index(
                ent["ent.label_and_text"]
            )
            unique_ents_count[index_of_same_ent] += 1
        else:
            # print(f"""ent "{ent["ent.text"]}" not already in unique_ents""")
            unique_ents.append(ent)
            unique_ents_count.append(1)
    return exploded_doc["doc"], unique_ents, unique_ents_count


# Define function for getting ratio of docs where ent appears
def get_ratio(doc, unique_ents, unique_ents_count, all_docs):
    all_doc_texts = [doc.text for doc in all_docs]
    # print(all_doc_texts.count(doc.text))
    unique_ents_proportion = [i / 10 for i in unique_ents_count]
    return doc, unique_ents, unique_ents_proportion


# Define a function for finding frequent annotations (above certain threshold)
def retrieve_frequent_ents(doc, unique_ents, unique_ents_ratio, threshold=0.5):
    frequent_ents_for_doc = [
        unique_ent["ent"]
        for unique_ent, unique_ent_ratio in zip(unique_ents, unique_ents_ratio)
        if unique_ent_ratio > threshold
    ]
    return doc, frequent_ents_for_doc


# Define a function for deleting any ents in a doc that exist in the same span as a frequent ent
def del_ents_from_freq(doc, frequent_ent_for_doc):
    # Find indexes of doc.ents where either the start- or end character is the same as for the frequent entity
    idxs_of_removable_ents = [
        idx
        for idx, item in enumerate(list(doc.ents))
        if (
            item.start_char == frequent_ent_for_doc.start_char
            or item.end_char == frequent_ent_for_doc.end_char
        )
    ]
    # Remove doc.ents with those indices
    doc_ents = list(doc.ents)
    for idx in sorted(idxs_of_removable_ents, reverse=True):
        del doc_ents[idx]
    doc.ents = tuple(doc_ents)
    return doc


# Define a function for deleting any ents in a doc that exists in any of the same spans as a list of frequent ents
def del_ents_from_freq_multiple(doc, frequent_ents_for_doc):
    for frequent_ent_for_doc in frequent_ents_for_doc:
        doc = del_ents_from_freq(doc, frequent_ent_for_doc)
    return doc


# Define a function for adding a frequent entity to a doc
def add_freq_ent_to_doc(doc, frequent_ent_for_a_doc):
    new_doc_ents = doc.ents + (frequent_ent_for_a_doc,)
    doc.ents = new_doc_ents
    return doc


# Define a function for adding frequent ents in a list of ents to a doc
def add_freq_ents_to_doc(doc, frequent_ents_for_a_doc):
    for frequent_ent_for_a_doc in frequent_ents_for_a_doc:
        doc = add_freq_ent_to_doc(doc, frequent_ent_for_a_doc)
    return doc


# Define a function for finding the index of a list, in which the doc matches another doc
def get_same_doc_index(doc, list_of_docs):
    for i, e in enumerate(list_of_docs):
        if e.text == doc.text:
            return i


# Define a function for finding and streamlining a doc in a list of docs, in accordance with frequent_ents_for_doc
def streamline_rater_data_for_a_doc(doc, rater_data, frequent_ents_for_doc):
    # Find index of doc that matches the doc we are streamlining
    idx = get_same_doc_index(doc, rater_data)
    if not idx == None:
        # Delete all entities in the doc that has the same span as the frequent entities
        rater_data[idx] = del_ents_from_freq_multiple(
            rater_data[idx], frequent_ents_for_doc
        )
        # Add all frequent entities to the doc
        rater_data[idx] = add_freq_ents_to_doc(rater_data[idx], frequent_ents_for_doc)
    return rater_data


############ Running script and functions ############

# Change cwd
os.chdir("/Users/emiltrencknerjessen/Desktop/priv/DANSK-gold-NER")

# Load language object
nlp = dacy.load("medium")

# List relevant data and sort by rater number
data_paths = glob.glob("./data/DANSK-multi/unprocessed/rater*/data.spacy")
data_paths.sort()
data_paths.sort(key="./data/DANSK-multi/unprocessed/rater_10/data.spacy".__eq__)

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
        unique_docs.append(doc)

############ Streamlining a single doc, across all raters ############

# Have a doc and a list of all docs (with duplicates from each rater)
doc = unique_docs[0]
flat_list = flat_list

# Retrieve all annotations across raters for a doc
ents = retrieve_all_ents(doc, flat_list)

# Add all entities to doc, and "explode" the doc (dictionary format, with all relevant info)
exploded_doc = explode_doc(doc, ents)

# Get a count of all unique ents
doc, unique_ents, unique_ents_count = doc_ents_count(exploded_doc)

# Get the ratio of occurrence of all unique entities
doc, unique_ents, unique_ents_ratio = get_ratio(
    doc, unique_ents, unique_ents_count, flat_list
)

# Retrieve the entities that are frequent across all raters
doc, frequent_ents_for_doc = retrieve_frequent_ents(
    doc, unique_ents, unique_ents_ratio, threshold=0.3
)

# Streamline the doc, using the frequent entities for all raters
# For each raters data
n_data = []
for rater in raters:
    rater_data = data[rater]
    rater_data = streamline_rater_data_for_a_doc(doc, rater_data, frequent_ents_for_doc)
    n_data.append(rater_data)
data = n_data.copy()

# Checking to see that everything works
data[0][0].ents
n_data[0][0].ents

# Define a function for retrieving a list of infrequent ents

# Define a function for deleting an ent (from the list of infrequent ents) from a doc

# Define a function for deleting all ents (from the list of infrequent ents) from a doc

# Update streamline_rater_data_for_a_doc() so that it also deletes all ents from the list of infrequent ents, from a doc

# # Save all streamlined docs as DocBins
# for rater in raters:
#     db = DocBin()
#     savepath = f"./data/DANSK-multi/streamlined/rater_{rater+1}"
#     for doc in data[rater]:
#         db.add(doc)
#     db.to_disk(savepath)
