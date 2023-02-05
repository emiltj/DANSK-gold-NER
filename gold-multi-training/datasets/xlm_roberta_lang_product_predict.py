import spacy, os
from spacy.tokens import DocBin
import spacy_wrap
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline

# Load tokenizer and model for NER token classification
# tokenizer = AutoTokenizer.from_pretrained("xlm-roberta-large-finetuned-conll03-english")
# model = AutoModelForTokenClassification.from_pretrained(
#     "xlm-roberta-large-finetuned-conll03-english"
# )
# classifier = pipeline("ner", model=model, tokenizer=tokenizer)

spacy.load("xlm-roberta-large-finetuned-conll03-english")

# Change dir
os.chdir("/Users/emiltrencknerjessen/Desktop/priv/DANSK-gold-NER")

# Load gold-multi data as doc objects
db = DocBin()
gold_multi_train = db.from_disk("gold-multi-training/datasets/gold-multi-train.spacy")
nlp = spacy.blank("da")
gold_multi_train = list(gold_multi_train.get_docs(nlp.vocab))

# Get it as texts for the new classifier to classify on
texts = [doc.text for doc in gold_multi_train]

# specify model from the hub
# config = {"model": {"name": "tner/roberta-large-ontonotes5"}}

# add it to the pipe
# nlp.add_pipe("token_classification_transformer", config=config)

# Use xlm-roberta NER pipeline to tag text
# docs = [nlp(text) for text in texts]

# Filter away docs that do not have a tag for either product or language

# L1 = [2, 3, 4, 5, 6, 7]
# L2 = [1, 2]
# [i for i in L1 if i in L2]

docs_with_lan_or_prod = [
    doc
    for doc in docs
    if [ent for ent in doc.ents if ent.label_ in ["LANGUAGE", "PRODUCT"]]
]

docs_with_lan_or_prod[0].ents
