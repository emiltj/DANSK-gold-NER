import os
from spacy.tokens import DocBin
import spacy
import copy

# Change cwd
os.chdir(
    "/Users/emiltrencknerjessen/Desktop/priv/DANSK-gold-NER/gold-multi-training/datasets/"
)

# Load language object
nlp = spacy.blank("da")

# Import data
ontonotes_path = "ontonotes.spacy"
multi_train_path = "gold-multi-rater-1/gold-multi-rater-1-train.spacy"
multi_train_db = DocBin().from_disk(multi_train_path)
ontonotes_db = DocBin().from_disk(ontonotes_path)

# Merge training data (but duplicate multi_train)
multi_train_db_with_dupli = copy.deepcopy(multi_train_db)
multi_train_db_for_dupli = copy.deepcopy(multi_train_db)
for _ in range(len(ontonotes_db) // len(multi_train_db) - 1):
    multi_train_db_with_dupli.merge(multi_train_db_for_dupli)

# Merge training data
multi_train_db.merge(ontonotes_db)

# Write to file
multi_train_db.to_disk("gold-multi-rater-1/onto_and_gold_multi_rater_1_train.spacy")
multi_train_db_with_dupli.to_disk(
    "gold-multi-rater-1/onto_and_gold_multi_rater_1_train_dupli.spacy"
)
