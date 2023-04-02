import spacy
from spacy.tokens import DocBin
import random


def partitioning():
    # Load DANSK
    nlp = spacy.blank("da")
    dansk_docs = list(DocBin().from_disk("dansk.spacy").get_docs(nlp.vocab))

    # Shuffle DANSK
    random.seed(0)
    random.shuffle(dansk_docs)

    # Execute split
    print("Splitting commencing ...\n")
    ten_percent = len(dansk_docs) // 100 * 10
    partitions = {
        "train": dansk_docs[ten_percent * 2 :],
        "dev": dansk_docs[:ten_percent],
        "test": dansk_docs[ten_percent : ten_percent * 2],
    }

    # Save split files and print tag counts to terminal
    for partition in partitions:
        print(f"Creating {partition}.spacy ...")
        db = DocBin()
        for doc in partitions[partition]:
            db.add(doc)
        db.to_disk(f"{partition}.spacy")
        print(f"{partition}.spacy created. \n")
    print("Finished splitting DANSK")


if __name__ == "__main__":
    partitioning()
