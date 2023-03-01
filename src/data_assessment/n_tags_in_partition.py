import spacy
from spacy.tokens import DocBin

nlp = spacy.load("da_core_news_lg")
db_in_dansk = DocBin().from_disk("data/full/gold/dansk.spacy")
docs = list(db_in_dansk.get_docs(nlp.vocab))

db_in_dansk = DocBin().from_disk("data/full/gold/dansk_train.spacy")
docs_train = list(db_in_dansk.get_docs(nlp.vocab))

db_in_dansk = DocBin().from_disk("data/full/gold/dansk_dev.spacy")
docs_dev = list(db_in_dansk.get_docs(nlp.vocab))

db_in_dansk = DocBin().from_disk("data/full/gold/dansk_test.spacy")
docs_test = list(db_in_dansk.get_docs(nlp.vocab))

unique_ent_labels_ = []
for doc in docs:
    for ent in doc.ents:
        if ent.label_ not in unique_ent_labels_:
            unique_ent_labels_.append(ent.label_)

count_of_ents = {}
for doc in docs_train:
    for ent in doc.ents:
        if ent.label_ in count_of_ents:
            count_of_ents[f"{ent.label_}"] += 1

        else:
            count_of_ents[f"{ent.label_}"] = 1
count_of_ents

count_of_ents = {}
for doc in docs_dev:
    for ent in doc.ents:
        if ent.label_ in count_of_ents:
            count_of_ents[f"{ent.label_}"] += 1

        else:
            count_of_ents[f"{ent.label_}"] = 1
count_of_ents

count_of_ents = {}
for doc in docs_test:
    for ent in doc.ents:
        if ent.label_ in count_of_ents:
            count_of_ents[f"{ent.label_}"] += 1

        else:
            count_of_ents[f"{ent.label_}"] = 1
count_of_ents
