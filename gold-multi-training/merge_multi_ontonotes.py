import os
from spacy.tokens import DocBin
import spacy

# Change cwd
os.chdir("/Users/emiltrencknerjessen/Desktop/priv/DANSK-gold-NER/gold-multi-training/")

# Load language object
nlp = spacy.blank("da")

# Import data
ontonotes_path = "ontonotes.spacy"
multi_train_path = "gold-multi-train.spacy"
multi_train_db = DocBin().from_disk(multi_train_path)
ontonotes_db = DocBin().from_disk(ontonotes_path)

# Merge training data
multi_train_db.merge(ontonotes_db)

# Write to file
multi_train_db.to_disk("train.spacy")
