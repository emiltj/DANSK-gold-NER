import spacy, os
import spacy_wrap
import srsly
from prodigy.components.db import connect
from spacy.tokens import DocBin
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline


# Two potential models:
# tner/roberta-large-ontonotes5
# flair/ner-english-ontonotes-large
# my own???

# Load gold-multi data as doc objects
db = DocBin()
gold_multi_train_rater_1_single = db.from_disk(
    "data/multi/gold/gold-multi-and-gold-rater-1-single.spacy"
)
nlp = spacy.blank("da")
gold_multi_train_rater_1_single = list(
    gold_multi_train_rater_1_single.get_docs(nlp.vocab)
)

# Get it as texts for the new classifier to classify on
texts = [doc.text for doc in gold_multi_train_rater_1_single]

######### Solution 2 (spacy wrap):
nlp = spacy.blank("da")
config = {"model": {"name": "tner/roberta-large-ontonotes5"}}
nlp.add_pipe("token_classification_transformer", config=config)

docs = []
for text in texts:
    try:
        docs.append(nlp(text))
    except Exception:
        pass


# Filter away docs that do not have a tag for either product or language
docs_with_lan_or_prod = [
    doc
    for doc in docs
    if [ent for ent in doc.ents if ent.label_ in ["LANGUAGE", "PRODUCT"]]
]

# Keep only ents with prod or lang
docs_with_lan_or_prod_no_other_tags = []
for doc in docs_with_lan_or_prod:
    prod_or_lang_ents = []
    for ent in doc.ents:
        if ent.label_ in ["LANGUAGE", "PRODUCT"]:
            prod_or_lang_ents.append(ent)
    doc.ents = tuple(prod_or_lang_ents)
    if doc.ents:
        docs_with_lan_or_prod_no_other_tags.append(doc)

# Check the doc predictions
# for doc in docs_with_lan_or_prod_no_other_tags:
#     print(doc)
#     for ent in doc.ents:
#         print(ent)
#         print(ent.label_)
#     print("\n")

docs_with_lan_or_prod_no_other_tags

# Save as .spacy
db = DocBin()
for doc in docs_with_lan_or_prod_no_other_tags:
    db.add(doc)
db.to_disk("data/multi/gold/gold-multi-and-gold-rater-1-single-preds-lang-prod.spacy")

print(
    "A new file has been created: data/multi/gold/gold-multi-and-gold-rater-1-single-preds-lang-prod.spacy"
)
# Scrapped solutions below:

######### Solution 1 (spacy normal):
# nlp = spacy.load("tner/roberta-large-ontonotes5")
# docs = [nlp(text) for text in texts]


######### Solution 3 (transformers, wrong output)
# Load tokenizer and model for NER token classification
# tokenizer = AutoTokenizer.from_pretrained("tner/roberta-large-ontonotes5")
# model = AutoModelForTokenClassification.from_pretrained("tner/roberta-large-ontonotes5")
# classifier = pipeline("ner", model=model, tokenizer=tokenizer)
# classifier(text)
