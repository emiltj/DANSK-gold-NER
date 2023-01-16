import os
import glob
import spacy
import re
from spacy.tokens import DocBin


subset = False

# Change cwd
os.chdir("/Users/emiltrencknerjessen/Desktop/priv/DANSK-gold-NER")

# Load language object
nlp = spacy.blank("da")
# nlp = dacy.load('medium')

# List relevant data and sort by rater number
data_paths = glob.glob("./data/full/unprocessed/rater*/train.spacy")
data_paths.sort()
data_paths.sort(key="./data/full/unprocessed/rater_10/train.spacy".__eq__)

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

new_data = []
for rater in raters_idx:
    new_docs_for_rater = []
    for doc in data[rater]:
        new_ents = [
            ent for ent in doc.ents if ent.label_ not in ["PRODUCT", "LANGUAGE"]
        ]
        doc.ents = new_ents
        new_docs_for_rater.append(doc)
    new_data.append(new_docs_for_rater)

# Save all streamlined docs as .spacy
for rater_idx in raters_idx:
    db = DocBin()
    savepath = f"./data/full/unprocessed/rater_{raters_lookup[rater_idx]}/train.spacy"
    for doc in new_data[rater_idx]:
        db.add(doc)
    db.to_disk(savepath)
