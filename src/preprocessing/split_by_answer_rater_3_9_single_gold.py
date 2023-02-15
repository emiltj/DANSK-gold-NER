from prodigy.components.db import connect
import srsly

db = connect()

raters = [3, 4, 5, 6, 7, 8, 9]

for r in raters:
    print(f"Splitting rater {r}")

    examples = db.get_dataset(f"rater_{r}_single_gold_all")
    srsly.write_jsonl(
        f"./data/single/gold/rater_{r}/rater_{r}_single_gold_all.jsonl", examples
    )
    print(
        f"New file has been created: ./data/single/gold/rater_{r}/rater_{r}_single_gold_all.jsonl"
    )

    accepted = [e for e in examples if e["answer"] == "accept"]
    srsly.write_jsonl(
        f"./data/single/gold/rater_{r}/rater_{r}_single_gold_accepted.jsonl", accepted
    )
    db.add_examples(accepted, [f"rater_{r}_single_gold_accepted"])
    print(
        f"New file has been created: ./data/single/gold/rater_{r}/rater_{r}_single_gold_accepted.jsonl"
    )
    print(f"New dataset has been added to db: rater_{r}_single_gold_accepted")

    ignored = [e for e in examples if e["answer"] == "ignore"]
    srsly.write_jsonl(
        f"./data/single/gold/rater_{r}/rater_{r}_single_gold_ignored.jsonl", ignored
    )
    db.add_examples(ignored, [f"rater_{r}_single_gold_ignored"])
    print(
        f"New file has been created: ./data/single/gold/rater_{r}/rater_{r}_single_gold_ignored.jsonl"
    )
    print(f"New dataset has been added to db: rater_{r}_single_gold_ignored")

    rejected = [e for e in examples if e["answer"] == "reject"]
    srsly.write_jsonl(
        f"./data/single/gold/rater_{r}/rater_{r}_single_gold_rejected.jsonl", rejected
    )
    db.add_examples(rejected, [f"rater_{r}_single_gold_rejected"])
    print(
        f"New file has been created: ./data/single/gold/rater_{r}/rater_{r}_single_gold_rejected.jsonl"
    )
    print(f"New dataset has been added to db: rater_{r}_single_gold_rejected")
