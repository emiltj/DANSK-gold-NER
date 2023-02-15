from prodigy.components.db import connect
import srsly

db = connect()
examples = db.get_dataset("rater_1_single_gold_all")
srsly.write_jsonl("./data/single/gold/rater_1/gold_all.jsonl", examples)

accepted = [e for e in examples if e["answer"] == "accept"]
srsly.write_jsonl("./data/single/gold/rater_1/gold_accepted.jsonl", accepted)
db.add_examples(accepted, ["rater_1_single_gold_accepted"])

ignored = [e for e in examples if e["answer"] == "ignore"]
srsly.write_jsonl("./data/single/gold/rater_1/gold_ignored.jsonl", ignored)
db.add_examples(ignored, ["rater_1_single_gold_ignored"])

rejected = [e for e in examples if e["answer"] == "reject"]
srsly.write_jsonl("./data/single/gold/rater_1/gold_rejected.jsonl", rejected)
db.add_examples(rejected, ["rater_1_single_gold_rejected"])
