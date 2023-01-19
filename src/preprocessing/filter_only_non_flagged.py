from prodigy.components.db import connect

db = connect()
examples = db.get_dataset("gold-multi-all")
filtered_examples = [eg for eg in examples if not eg.get("flagged")]
db.add_dataset("gold-multi-no-flagged")  # add empy dataset
db.add_examples(filtered_examples, "gold-multi-no-flagged")
