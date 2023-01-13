from spacy.tokens import DocBin
import os
import dacy
import copy

# Change cwd
os.chdir("/Users/emiltrencknerjessen/Desktop/priv/DANSK-gold-NER")

# Load language object
nlp = spacy.blank("da")

# Import data
path = "./data/full/unprocessed/rater_8/train.spacy"
doc_bin = DocBin().from_disk(path)
docs = list(doc_bin.get_docs(nlp.vocab))


def is_stop_ent(span):
    return all(t.is_stop for t in span)


def remove_stopword_ents_from_doc(doc):
    new_doc = doc
    orig_ents = new_doc.ents
    orig_ents_is_stop = [is_stop_ent(ent) for ent in new_doc.ents]
    orig_ents_is_not_stop = [not elem for elem in orig_ents_is_stop]
    new_ents = [
        orig_ent
        for orig_ent, orig_ent_is_not_stop in zip(orig_ents, orig_ents_is_not_stop)
        if orig_ent_is_not_stop
    ]
    new_doc.ents = new_ents
    return new_doc


new_docs = [remove_stopword_ents_from_doc(doc) for doc in docs]

db = DocBin()
for doc in new_docs:
    db.add(doc)
db.to_disk(path)
