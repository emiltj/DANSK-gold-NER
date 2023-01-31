from prodigy.components.db import connect
import srsly

db = connect()
examples = db.get_dataset("gold-multi-all")
srsly.write_jsonl("./data/multi/gold/gold-multi-all.jsonl", examples)

accepted = [e for e in examples if e["answer"] == "accept"]
srsly.write_jsonl("./data/multi/gold/gold-multi-accepted.jsonl", accepted)
db.add_examples(accepted, ["gold-multi-accepted"])

ignored = [e for e in examples if e["answer"] == "ignore"]
srsly.write_jsonl("./data/multi/gold/gold-multi-ignored.jsonl", ignored)
db.add_examples(ignored, ["gold-multi-ignored"])

rejected = [e for e in examples if e["answer"] == "reject"]
srsly.write_jsonl("./data/multi/gold/gold-multi-rejected.jsonl", rejected)
db.add_examples(ignored, ["gold-multi-rejected"])
