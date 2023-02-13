from prodigy.components.db import connect
import srsly

db = connect()
extra_labels_for_dataset = db.get_dataset(
    "gold-multi-and-gold-rater-1-single-extra-lang-prod"
)
gold_multi_rater_1 = db.get_dataset("gold-multi-and-gold-rater-1-single-ner-manual")

extra_labels_for_dataset_texts = [e["text"] for e in extra_labels_for_dataset]

gold_multi_rater_1_no_extra_labels_docs = [
    e for e in gold_multi_rater_1 if e["text"] not in extra_labels_for_dataset_texts
]

srsly.write_jsonl(
    "data/multi/gold/gold-multi-rater-1.jsonl", gold_multi_rater_1_no_extra_labels_docs
)

print("New file has been created: data/multi/gold/gold-multi-rater-1.jsonl")
