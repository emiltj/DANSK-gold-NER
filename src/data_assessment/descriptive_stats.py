from prodigy.components.db import connect

db = connect()

all_dataset_names = db.datasets
all_dataset_names

dataset_descriptive_stats = []
for dataset_name in all_dataset_names:
    examples = db.get_dataset(dataset_name)
    accept = [e for e in examples if e["answer"] == "accept"]
    reject = [e for e in examples if e["answer"] == "reject"]
    ignore = [e for e in examples if e["answer"] == "ignore"]

    if len(accept) + len(reject) + len(ignore) != len(examples):
        break

    descriptive_stats = {
        "name": dataset_name,
        "full_len": len(examples),
        "accept_len": len(accept),
        "reject_len": len(reject),
        "ignore_len": len(ignore),
    }

    dataset_descriptive_stats.append(descriptive_stats)

for i in dataset_descriptive_stats:
    # print(f"{i}\n")
    print(i)


# data/single/unprocessed/rater_1/train.spacy

# import spacy, os
# from spacy.tokens import DocBin

# os.chdir("/Users/emiltrencknerjessen/Desktop/priv/DANSK-gold-NER")

# db = DocBin()
# a = db.from_disk("train.spacy")
# nlp = spacy.blank("da")
# docs = list(a.get_docs(nlp.vocab))
# len(docs)
