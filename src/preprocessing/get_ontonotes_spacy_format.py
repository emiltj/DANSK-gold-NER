from datasets import load_dataset
from spacy.tokens import Doc, DocBin
import spacy
import json, os

os.chdir("/Users/emiltrencknerjessen/Desktop/priv/DANSK-gold-NER/src/preprocessing")
from spacemodel import SpaceModel, load_texts

# Define spacemodel
spacemodel = SpaceModel(lang="en")

# Fit spacemodel
texts = load_texts("da", 50_000)  #
spacemodel.fit(texts[:10000])

os.chdir("/Users/emiltrencknerjessen/Desktop/priv/DANSK-gold-NER")
# Loading labels lookup
with open("./src/preprocessing/ontonotes_labels.json") as json_file:
    labels_lookup = json.load(json_file)

os.chdir("/Users/emiltrencknerjessen/Desktop/priv/DANSK-gold-NER/src/preprocessing")

labels_lookup

# Loading dataset
ontonotes_dicts = load_dataset("tner/ontonotes5", split="train")

ontonotes_dicts[0]

# Convert ontonotes dicts to list of spacy docs
ontonotes_docs = []
IOB_tag_labels_lookup = list(labels_lookup.keys())
nlp = spacy.blank("en")
for ontonotes_dict in ontonotes_dicts:
    IOB_tag_labels = [IOB_tag_labels_lookup[tag] for tag in ontonotes_dict["tags"]]
    spaces = spacemodel.followed_by_space(ontonotes_dict["tokens"])
    spaces[-1] = False
    doc = Doc(
        nlp.vocab, words=ontonotes_dict["tokens"], spaces=spaces, ents=IOB_tag_labels
    )
    ontonotes_docs.append(doc)

# for i, doc in enumerate(ontonotes_docs):
#     for ent in doc.ents:
#         if ent.label_ in ["LANGUAGE", "PRODUCT"]:
#             print(i)
#             print(ent)

# ontonotes_docs[58044].ents[0].label

os.chdir("/Users/emiltrencknerjessen/Desktop/priv/DANSK-gold-NER")

# Dump ontonotes in docbin format
if not os.path.exists("data/ontonotes"):
    os.mkdir("data/ontonotes")


db = DocBin()
for doc in ontonotes_docs:
    db.add(doc)
db.to_disk("data/ontonotes/ontonotes.spacy")
db.to_disk("gold-multi-training/datasets/ontonotes.spacy")
