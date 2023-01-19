import spacy
import os
import json
import copy
import re
import glob
import pandas as pd
from operator import itemgetter
from collections import Counter
from spacy.tokens import DocBin, Doc, Span
from spacy.training.corpus import Corpus
from itertools import combinations
from utils import *

subset = False

# Change cwd
os.chdir("/Users/emiltrencknerjessen/Desktop/priv/DANSK-gold-NER")

# Load language object
nlp = spacy.blank("da")
# nlp = dacy.load('medium')

# List relevant data and sort by rater number
data_paths = glob.glob("./data/multi/unprocessed/rater*/data.spacy")
data_paths.sort()
data_paths.sort(key="./data/multi/unprocessed/rater_10/data.spacy".__eq__)

# Load in data and get rater indices (if not already loaded)
data = []
raters = []
for path in data_paths:
    # Get rater indices
    rater = int(re.search(r"\d+", path).group())
    raters.append(rater)

    # Load data
    doc_bin = DocBin().from_disk(path)
    if subset:
        docs = list(doc_bin.get_docs(nlp.vocab))[:10]
    else:
        docs = list(doc_bin.get_docs(nlp.vocab))
    data.append(docs)

# Define raters indexes
raters_idx = list(range(len(raters)))

# Have a lookup table for the index vs. rater number.
raters_lookup = dict(zip(raters_idx, raters))

# Keys = index
# Value = rater

# Get a list with all docs from all raters (including duplicate docs)
all_docs = [item for sublist in data for item in sublist]

# Get a list of all unique docs
unique_docs = []
for doc in all_docs:
    if all(doc.text != unique_doc.text for unique_doc in unique_docs):
        unique_docs.append(copy.deepcopy(doc))

# Ensure that unique_docs don't already have entities
for i in unique_docs:
    i.ents = ()

threshold_freq = 0.1
threshold_infreq = 0.075
n_raters = len(raters_idx)

streamlined_data = []

for rater_idx in raters_idx:
    print(f"streamlining rater: {rater_idx} ...")
    streamlined_rater_docs = []
    rater_docs = copy.deepcopy(data[rater_idx])
    for doc in unique_docs:
        if get_same_doc_index(doc, rater_docs) is None:
            pass  # print("Doc does not exist for rater")
        else:
            (
                unique_ents_full_match,
                unique_ents_partial_match,
                freq_unique_ents_full_match,
                infreq_unique_ents_partial_match,
                unique_ents_full_match_count,
                unique_ents_partial_match_count,
                n_raters,
            ) = retrieve_freq_and_infreq_ents_from_doc(
                doc, all_docs, threshold_freq, threshold_infreq
            )
            streamlined_doc = streamline_doc(
                doc,
                rater_docs,
                freq_unique_ents_full_match,
                infreq_unique_ents_partial_match,
            )
        #     print(f"Current rater: {raters_lookup[rater_idx]}")
        #     print(f"Current rater_idx: {rater_idx}")
        #     print(f"N_raters for doc: {n_raters}")

        #     print(f"Current doc index in rater: {get_same_doc_index(doc, rater_docs)}")
        #     print(f"Current doc: {doc}")

        #     print(f"Unique_ents_full: {unique_ents_full_match}")
        #     print(f"Unique_ents_full count: {unique_ents_full_match_count}")
        #     print(f"Freq ents (no duplicates): {freq_unique_ents_full_match}")

        #     print(f"Unique_ents_partial: {unique_ents_partial_match}")
        #     print(f"Unique_ents_partial count: {unique_ents_partial_match_count}")
        #     print(f"Infreq ents (no overlaps): {infreq_unique_ents_partial_match}")

        #     print(
        #         f"Current doc ents PRIOR to streamlining: {rater_docs[get_same_doc_index(doc, rater_docs)].ents}"
        #     )
        #     print(f"Current doc ents AFTER streamlining: {streamlined_doc.ents}")
        # print("\n\n\n")

        if streamlined_doc != None:
            streamlined_rater_docs.append(streamlined_doc)
            streamlined_doc = None
    streamlined_data.append(streamlined_rater_docs)

# Save all streamlined docs as .jsonl
for rater_idx in raters_idx:
    db = DocBin()
    # savepath = f"./data/multi/streamlined/rater_{raters_lookup[rater_idx]}/train.jsonl"
    savepath = f"./data/multi/streamlined/rater_{raters_lookup[rater_idx]}/train.spacy"
    for doc in streamlined_data[rater_idx]:
        db.add(doc)
    db.to_disk(savepath)
