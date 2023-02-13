import sys
from prodigy.components.db import connect
from clumper import Clumper
import srsly

db = connect()

dataset_from_db = "gold-multi-and-gold-rater-1-single-preds-lang-prod"
# # outpath = "data/multi/gold/gold-multi-and-gold-rater-1-single-preds-lang-prod-ner-manual.jsonl"
# reviews = db.get_dataset(dataset_from_db)
# reviews[0].keys()
# reviews[0]["_view_id"]

if __name__ == "__main__":
    dataset_from_db = str(sys.argv[1])
    outpath = str(sys.argv[2])
    reviews = db.get_dataset(dataset_from_db)

    appropriate_keys = (
        "text",
        "tokens",
        "_is_binary",
        "_view_id",
        "answer",
        "_timestamp",
        "spans",
        # "_input_hash",
        # "_task_hash",
        # "_session_id",
        # "view_id",
    )
    ner_manuals = []
    for review in reviews:
        ner_manual = {k: review[k] for k in appropriate_keys if k in appropriate_keys}
        ner_manual["_view_id"] = "ner_manual"
        ner_manuals.append(ner_manual)

    # review_only = (
    #     Clumper(reviews)
    #     .keep(lambda d: d["_view_id"] == "review")
    #     .mutate(_view_id=lambda d: "ner_manual")
    # )

    srsly.write_jsonl(outpath, ner_manuals)
