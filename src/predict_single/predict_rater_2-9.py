import spacy, os
from spacy.tokens import DocBin

# Change dir
os.chdir("/Users/emiltrencknerjessen/Desktop/priv/DANSK-gold-NER")

# Load rater_2-9 data
db = DocBin()
raters = [3, 4, 5, 6, 7, 8, 9]
nlp = spacy.blank("da")
print("Loading model ...")
nlp2 = spacy.load("da_multi_dupli_rater_1_onto")
print("Model loaded, predicting on raters")

# For each rater
for r in [3, 4, 5, 6, 7, 8, 9]:  # raters:
    print(f"Predicting on rater {r} ...")
    r_data = db.from_disk(f"data/single/unprocessed/rater_{r}/train.spacy")
    r_docs = list(r_data.get_docs(nlp.vocab))
    texts = [doc.text for doc in r_docs]
    predicted_docs = [nlp2(text) for text in texts]
    savepath = f"data/single/unprocessed/rater_{r}/rater_{r}_preds.spacy"
    db2 = DocBin()
    for doc in predicted_docs:
        db2.add(doc)
    db2.to_disk(savepath)
    print(f"new file with preds saved: {savepath}")
