import spacy, os
from spacy.tokens import DocBin
import spacy_wrap


# Change dir
os.chdir("/Users/emiltrencknerjessen/Desktop/priv/DANSK-gold-NER")

# Load gold-multi-and-gold-rater-1-single data as doc objects
db = DocBin()
gold_multi_and_rater_1_single = db.from_disk(
    "gold-multi-training/datasets/gold-multi-dev.spacy"
)  #
# "data/multi/gold/gold-multi-and-gold-rater-1-single.spacy"
# )
nlp = spacy.blank("da")
gold_multi_and_rater_1_single = list(gold_multi_and_rater_1_single.get_docs(nlp.vocab))


# specify model from the hub
config = {"model": {"name": "flair/ner-english-ontonotes-large"}}

# add it to the pipe
nlp.add_pipe("token_classification_transformer", config=config)

# See pipeline
nlp.pipeline

l = "Denne model fungerer okay på forskellige sprog. Jeg håber den virker på dansk, engelsk og måske fransk. Og så håber jeg at den fungerer på produkter. F.eks. skal den kunne tagge macbook eller Steelseries Keyboard 3000."
k = nlp(l)

for i in k.ents:
    i.label_

# Get as texts
texts = [doc.text for doc in gold_multi_and_rater_1_single]


# Use xlm-roberta NER pipeline to tag text
docs = [nlp(text) for text in texts]

docs[0]
docs[0].ents

# Filter away docs that do not have a tag for either product or language


docs[0]
