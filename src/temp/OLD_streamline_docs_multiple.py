import spacy
import dacy
import os
import re
import glob
import pandas as pd
from collections import Counter
from spacy.tokens import DocBin, Doc, Span
from spacy.training.corpus import Corpus
import json


# Change cwd
os.chdir("/Users/emiltrencknerjessen/Desktop/priv/DANSK-gold-NER")


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

data
data[0]
data[0][0]
doc = data[0][0]

# Get a dictionary with key: str = doc.text, and with value: list = ents
doc_ents = {}
for rater_data in data:
    for doc in rater_data:
        if doc.text in doc_ents:
            ents = list(doc.ents)
            doc_ents[doc.text].extend(ents)
        else:
            doc_ents[doc.text] = list(doc.ents)

doc_ents[text]
doc_text = "Deres forældre havde ingen muligheder, allerede dengang blev de set ned på i samfundet, på kommunen og i parlamentet."
doc_ents[doc_text]

# Function for retrieving number of occurrences of each entity for a doc
def count_n_tags(doc_ents_element):
    entss = []
    for text, label_ in zip(
        [ent.text for ent in doc_ents_element],
        [ent.label_ for ent in doc_ents_element],
    ):
        tuplee = (text, label_)
        entss.append(tuplee)
    entss
    return dict(Counter(iter(entss)))  # dict(Counter(x for x in entss))


# Function for getting a dataframe with entities for a doc
def calc_doc_ents_count(doc_ents, doc_text, counted_n_tags):
    docs_ents_counted = []
    for i in doc_ents[doc_text]:
        n_occurrences_for_i = l[(i.text, i.label_)]
        docs_ents_counted.append(
            {
                "ent_text": i.text,
                "ent_label": i.label_,
                "ent": i,
                "n_occurrences_for_i": n_occurrences_for_i,
            }
        )
    df = pd.DataFrame(docs_ents_counted)
    df.drop_duplicates(["ent_text", "ent_label"], inplace=True)
    return {df}


l = count_n_tags(doc_ents[doc_text])

calc_doc_ents_count(doc_ents, doc_text, l)
