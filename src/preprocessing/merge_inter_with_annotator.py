import pandas as pd
import os

os.chdir("/Users/emiltrencknerjessen/Desktop/priv/DANSK-gold-NER")

# annotator = pd.read_json(
#     path_or_buf="./data/prodigy_exports/prodigy1_db_exports/NER_annotator1.jsonl",
#     lines=True,
# )

# inter = pd.read_json(
#     path_or_buf="./data/prodigy_exports/prodigy1_db_exports/NER_interannotator_annotator1.jsonl",
#     lines=True,
# )

# pd.concat([annotator, inter], axis=0)


merged_jsonl = []
for i in range(10):
    i = i + 1
    annotator_path = (
        f"./data/prodigy_exports/prodigy{i}_db_exports/NER_annotator{i}.jsonl"
    )
    inter_path = f"./data/prodigy_exports/prodigy{i}_db_exports/NER_interannotator_annotator{i}.jsonl"

    annotator = pd.read_json(
        path_or_buf=annotator_path,
        lines=True,
    )
    inter = pd.read_json(
        path_or_buf=inter_path,
        lines=True,
    )
    merged = pd.concat([annotator, inter], axis=0)
    merged = merged.to_json
    print(merged)
    print(type(merged))
    merged_jsonl.append(merged)

    # Writing to .json
    with open(
        f"./data/prodigy_exports/prodigy{i}_db_exports/NER_merged.json", "w"
    ) as outfile:
        outfile.write(merged)


type(merged_jsonl[0])
