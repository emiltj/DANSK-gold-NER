import spacy, os
import spacy_wrap
from prodigy.components.db import connect
from spacy.tokens import DocBin
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline

# Two potential models:
# tner/roberta-large-ontonotes5
# flair/ner-english-ontonotes-large
# my own???

# Load gold-multi data as doc objects
# db = DocBin()
# gold_multi_train = db.from_disk("gold-multi-training/datasets/gold-multi-train.spacy")
# nlp = spacy.blank("da")
# gold_multi_train = list(gold_multi_train.get_docs(nlp.vocab))

# Get it as texts for the new classifier to classify on
# texts = [doc.text for doc in gold_multi_train]

######### Solution 2 (spacy wrap):
# nlp = spacy.blank("da")
# config = {"model": {"name": "tner/roberta-large-ontonotes5"}}
# nlp.add_pipe("token_classification_transformer", config=config)

# docs = []
# for text in texts:
#     try:
#         docs.append(nlp(text))
#     except Exception:
#         pass


# Filter away docs that do not have a tag for either product or language
# docs_with_lan_or_prod = [
#     doc
#     for doc in docs
#     if [ent for ent in doc.ents if ent.label_ in ["LANGUAGE", "PRODUCT"]]
# ]


# Add new dataset to DB
# db = connect()
# db.add_examples(docs_with_lan_or_prod, ["gold-multi-lang-and-prod"])


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
