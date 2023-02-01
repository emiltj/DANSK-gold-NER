import spacy

text1 = "This is another text on Tuberculosis"
texts = [text1]
texts.append(
    "It was great that you and Riccardo came and visited us for lunch! Please do visit again"
)

texts

nlp2 = spacy.load("en_core_web_sm")
nlp = spacy.load("da_core_news_sm")

docs_nlp = [nlp(text) for text in texts]
docs_nlp2 = [nlp2(text) for text in texts]

docs_all_ents = []
for i, doc in enumerate(docs_nlp):
    doc_all_ents = list(docs_nlp[i].ents)
    doc_all_ents.extend(list(docs_nlp2[i].ents))

    print(doc_all_ents)

    doc.ents = doc_all_ents
    docs_all_ents.append(doc)

docs_all_ents[0].ents
