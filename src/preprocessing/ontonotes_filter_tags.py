from spacy.tokens import DocBin
import spacy
import os

os.chdir("/Users/emiltrencknerjessen/Desktop/priv/DANSK-gold-NER")


# Load language object
nlp = spacy.blank("da")

# Load data as Docs
db = DocBin()
doc_bin = db.from_disk("data/ontonotes/ontonotes.spacy")
docs = list(doc_bin.get_docs(nlp.vocab))

# Remove tags from Language and Product
for doc in docs:
    new_ents = tuple(
        ent for ent in doc.ents if ent.label_ not in ["PRODUCT", "LANGUAGE"]
    )
    doc.ents = new_ents

# Ensure there are no ents of type language and product
# for doc in docs:
#     for ent in doc.ents:
#         if ent.label_ in ["LANGUAGE", "PRODUCT"]:
#             print(ent)

# Convert docs back into docbins
db = DocBin()
for doc in docs:
    db.add(doc)

# Overwrite existing files
db.to_disk("gold-multi-training/datasets/ontonotes.spacy")
db.to_disk("data/ontonotes/ontonotes.spacy")
