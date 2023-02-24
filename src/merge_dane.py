import spacy
from spacy.tokens import DocBin

all_docs = []

for partition in ["train", "dev", "test"]:
    db = DocBin()
    db = db.from_disk(f"data/dane/dane_{partition}.spacy")
    nlp = spacy.blank("da")
    docs = list(db.get_docs(nlp.vocab))
    print(len(docs))
    for doc in docs:
        all_docs.append(doc)

db2 = DocBin()
for doc in all_docs:
    db2.add(doc)
db2.to_disk("data/dane/dane.spacy")
