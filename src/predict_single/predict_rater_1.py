import spacy, os
from spacy.tokens import DocBin


# Change dir
os.chdir("/Users/emiltrencknerjessen/Desktop/priv/DANSK-gold-NER")

# Load rater_1 data
db = DocBin()
r1 = db.from_disk("data/single/unprocessed/rater_1/train.spacy")
nlp = spacy.blank("da")
r1_docs = list(r1.get_docs(nlp.vocab))

# Predict on rater_1 data
# nlp = spacy.load("da_core_news_sm")  # da-pipeline-0.0.0")
nlp = spacy.load("da_multi_dupli_onto_xlm_roberta_large")  # da-pipeline-0.0.0")
r1_texts = [doc.text for doc in r1_docs]
r1_new_docs = [nlp(text) for text in r1_texts]

# Save new predictions on rater_1 data
db = DocBin()
savepath = "data/single/unprocessed/rater_1/rater_1_preds.spacy"
for doc in r1_new_docs:
    db.add(doc)
db.to_disk(savepath)
print(f"new file with preds saved: {savepath}")
