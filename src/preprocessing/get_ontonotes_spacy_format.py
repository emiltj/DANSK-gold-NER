from datasets import load_dataset
from spacy.tokens import Doc
import spacy
import json, os

os.chdir("/Users/emiltrencknerjessen/Desktop/priv/DANSK-gold-NER")

# Loading labels lookup
with open("./src/preprocessing/ontonotes_labels.json") as json_file:
    labels_lookup = json.load(json_file)

# Loading dataset
on_train = load_dataset("tner/ontonotes5", split="train")
nlp = spacy.blank("da")

doc = on_train[0]


doc = Doc(nlp.vocab, words=doc["tokens"], spaces=spaces)


# Tag den simplese format ontonotes 5. tokens: [], iob_tag: [],
# og lav dog objects ud af det.
# Brug language module fra blank spacy model.
# Spaces ud fra Kenneths anvisninger.
