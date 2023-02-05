import spacy

text = "This is a text in the English language on the new Macbook product by Apple"

nlp = spacy.load("en_core_web_sm")

doc = nlp(text)

for doc in doc.ents:
    print(doc)
    print(doc.label_)
    print(doc.label)
