import pandas as pd
import os
import gzip
import json
import copy

os.chdir("/Users/emiltrencknerjessen/Desktop/priv/DANSK-gold-NER")

# from https://ml-gis-service.com/index.php/2022/04/27/toolbox-python-list-of-dicts-to-jsonl-json-lines/
def dicts_to_jsonl(data: list, filename: str, compress: bool = True) -> None:
    """
    Method saves list of dicts into jsonl file.
    :param data: (list) list of dicts to be stored,
    :param filename: (str) path to the output file. If suffix .jsonl is not given then methods appends
        .jsonl suffix into the file.
    :param compress: (bool) should file be compressed into a gzip archive?
    """
    sjsonl = ".jsonl"
    sgz = ".gz"
    # Check filename
    if not filename.endswith(sjsonl):
        filename = filename + sjsonl
    # Save data

    if compress:
        filename = filename + sgz
        with gzip.open(filename, "w") as compressed:
            for ddict in data:
                jout = json.dumps(ddict) + "\n"
                jout = jout.encode("utf-8")
                compressed.write(jout)
    else:
        with open(filename, "w") as out:
            for ddict in data:
                jout = json.dumps(ddict) + "\n"
                out.write(jout)


for i in range(10):
    i = i + 1
    annotator_path = (
        f"./data/prodigy_exports/prodigy{i}_db_exports/NER_annotator{i}.jsonl"
    )
    inter_path = f"./data/prodigy_exports/prodigy{i}_db_exports/NER_interannotator_annotator{i}.jsonl"
    merged_path = (
        f"./data/prodigy_exports/prodigy{i}_db_exports/NER_merged_annotator{i}.jsonl"
    )
    annotator = pd.read_json(
        path_or_buf=annotator_path,
        lines=True,
    )
    inter = pd.read_json(
        path_or_buf=inter_path,
        lines=True,
    )

    df = pd.concat([annotator, inter], axis=0)
    if i == 10:
        print(f"annotator_len: {len(annotator)}")
        print(f"inter_len: {len(inter)}")
        print(f"inter+annotator_len: {len(annotator) + len(inter)}")
        print(f"merged_len: {len(df)}")

    # Convert all columns to strings, since the pd.duplicated() doesn't work if df contains dict
    df_strings = copy.deepcopy(df)
    for column in df_strings.columns:
        df_strings[f"{column}"] = df_strings[f"{column}"].astype("string")

    # Sort by _timestamp (earliest is first)
    df = df.sort_values(by=["_timestamp"])
    df_strings = df_strings.sort_values(by=["_timestamp"])

    # Mark all duplicates in pd, except for the latest occurrence (if they duplicate on the columns 'text' and 'meta').
    df["duplicate"] = df_strings.duplicated(subset=["text", "meta"], keep="last")

    # Keep only non-duplicates
    df = df[df["duplicate"] == False]

    # More output to check it works
    if i == 10:
        print(f"merged_len_no_dupli: {len(df)}")

    # Convert df to dict
    dictt = df.to_dict("records")

    dicts_to_jsonl(data=dictt, filename=merged_path, compress=False)
