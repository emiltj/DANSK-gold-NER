import spacy
import copy
import os
import re
import glob
from operator import itemgetter
from spacy.tokens import DocBin

subset = False

# Change cwd
os.chdir("/Users/emiltrencknerjessen/Desktop/priv/DANSK-gold-NER")

# Load language object
nlp = spacy.blank("da")

# List relevant data and sort by rater number
data_paths = glob.glob("./data/full/unprocessed/rater*/train.spacy")
data_paths.sort()
data_paths.sort(key="./data/full/unprocessed/rater_10/train.spacy".__eq__)
print("\n\nReading in data")

data_paths

# Load in data and get rater indices (if not already loaded)
data = []
raters = []
for path in data_paths:
    print(f"Reading in data from {path} as DocBin ...")
    # Get rater indices
    rater = re.search(r"\d+", path).group()
    raters.append(int(rater))

    # Load data
    doc_bin = DocBin().from_disk(path)
    if subset == True:
        docs = list(doc_bin.get_docs(nlp.vocab))[:20]
    else:
        docs = list(doc_bin.get_docs(nlp.vocab))
    data.append(docs)


raters_idx = list(range(len(raters)))
raters_idx_lookup = {0: 1, 1: 3, 2: 4, 3: 5, 4: 6, 5: 7, 6: 8, 7: 9}
# Keys = Index
# Value = Rater number

print("Retrieving list of unique docs ...\n")

# Get a list of all unique docs
unique_docs_texts = []
unique_docs_idx_in_flat_list = []
flat_list = [item for sublist in data for item in sublist]
for idx, doc in enumerate(flat_list):
    print(f"doc with idx {idx} out of {len(flat_list)-1} indices")
    if doc.text not in unique_docs_texts:
        unique_docs_texts.append(doc.text)
        unique_docs_idx_in_flat_list.append(idx)
unique_docs = list(itemgetter(*unique_docs_idx_in_flat_list)(flat_list))

print("Retrieving list of unique docs with multiple raters ...\n")
# Find unique docs with > 1 raters
flat_list = [item for sublist in data for item in sublist]
docs_multiple_raters = [False] * len(unique_docs)
flat_list_texts = [doc.text for doc in flat_list]
for i, unique_doc in enumerate(unique_docs):
    print(
        f"Checking whether unique doc index {i} out of a total of {len(unique_docs)-1} unique docs indexes have been rated by multiple .."
    )
    if flat_list_texts.count(unique_doc.text) > 1:
        docs_multiple_raters[i] = True


# print("Retrieving list of unique docs with multiple raters ...\n")
# # Find unique docs with > 1 raters
# docs_multiple_raters = [False] * len(unique_docs)
# for i in range(len(unique_docs)):
#     print(
#         f"Checking whether unique doc number {i} out of a total of {len(unique_docs)} unique docs has been rated by multiple .."
#     )
#     unique_doc = unique_docs[i]
#     all_doc_texts = [doc.text for doc in flat_list]
#     if all_doc_texts.count(unique_doc.text) > 1:
#         docs_multiple_raters[i] = True


# Function for splitting rater_data into rater_data_single and rater_data_multiple
def split_by_n_raters(rater_data, unique_docs, docs_multiple_raters):
    multiple_docs_for_rater = []
    single_docs_for_rater = []
    unique_docs_texts = [unique_doc.text for unique_doc in unique_docs]
    for doc in rater_data:
        # unique_docs_texts = [unique_doc.text for unique_doc in unique_docs]
        unique_docs_index = unique_docs_texts.index(doc.text)
        if docs_multiple_raters[unique_docs_index] == True:
            multiple_docs_for_rater.append(doc)
        else:  # docs_multiple_raters[unique_docs_index] == False:
            single_docs_for_rater.append(doc)
    return single_docs_for_rater, multiple_docs_for_rater


# for rater_idx, rater in enumerate(raters):
#     print(f"rater_idx: {rater_idx} \n rater: {rater}")

print("\n\nCommencing splitting of docs for raters ...")
# Split data for each rater into docs with single raters, and docs with multiple raters.
# Also save as DocBin
for rater_idx, rater in enumerate(raters):
    print(f"Splitting and saving data from rater_{rater}")
    single_docs_for_rater, multiple_docs_for_rater = split_by_n_raters(
        data[rater_idx], unique_docs, docs_multiple_raters
    )

    # Saving single_docs_for_rater
    outpath_single = f"./data/single/unprocessed/rater_{rater}/data.spacy"
    db_single = DocBin(store_user_data=True)
    print(
        f"Saving docs that have been annotated by not other raters (single) to '{outpath_single}' ..."
    )
    for doc in single_docs_for_rater:
        db_single.add(doc)
    db_single.to_disk(outpath_single)

    # Saving multiple_docs_for_rater
    outpath_multi = f"./data/multi/unprocessed/rater_{rater}/data.spacy"
    db_multi = DocBin(store_user_data=True)
    print(
        f"Saving docs that have been annotated by other raters as well (multi) to '{outpath_multi}'... \n\n"
    )
    for doc in multiple_docs_for_rater:
        db_multi.add(doc)
    db_multi.to_disk(outpath_multi)

print("Data has been split successfully")
