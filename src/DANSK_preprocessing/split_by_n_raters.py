import dacy
import os
import re
import glob
from spacy.tokens import DocBin


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
    docs = list(doc_bin.get_docs(nlp.vocab))[:200]
    data.append(docs)

# Get a list of all unique docs
unique_docs = []
flat_list = [item for sublist in data for item in sublist]
for doc in flat_list:
    if all(doc.text != unique_doc.text for unique_doc in unique_docs):
        unique_docs.append(doc)

# Find unique docs with > 1 raters
docs_multiple_raters = [False] * len(unique_docs)
for i in range(len(unique_docs)):
    doc = unique_docs[i]
    all_doc_texts = [doc.text for doc in flat_list]
    if all_doc_texts.count(doc.text) > 1:
        docs_multiple_raters[i] = True

# Function for splitting rater_data into rater_data_single and rater_data_multiple
def split_by_n_raters(rater_data, unique_docs, docs_multiple_raters):
    multiple_docs_for_rater = []
    single_docs_for_rater = []
    for doc in rater_data:
        unique_docs_texts = [unique_doc.text for unique_doc in unique_docs]
        unique_docs_index = unique_docs_texts.index(doc.text)
        if docs_multiple_raters[unique_docs_index] == True:
            multiple_docs_for_rater.append(doc)
        else:  # docs_multiple_raters[unique_docs_index] == False:
            single_docs_for_rater.append(doc)
    return single_docs_for_rater, multiple_docs_for_rater


# Split data for each rater into docs with single raters, and docs with multiple raters.
# Also save as DocBin
for rater in raters:
    single_docs_for_rater, multiple_docs_for_rater = split_by_n_raters(
        data[rater], unique_docs, docs_multiple_raters
    )
    # Saving single_docs_for_rater
    db_single = DocBin(store_user_data=True)
    for doc in single_docs_for_rater:
        db_single.add(doc)
    db_single.to_disk(f"./data/DANSK-single/unprocessed/rater_{rater+1}/data.spacy")

    # Saving multiple_docs_for_rater
    db_multi = DocBin(store_user_data=True)
    for doc in multiple_docs_for_rater:
        db_multi.add(doc)
    db_multi.to_disk(f"./data/DANSK-multi/unprocessed/rater_{rater+1}/data.spacy")
