import numpy as np
import pandas as pd


def preprocess_rater(raw_df, id):
    """Process raw json/csv of rater

    Args:
        raw_data (pd.Dataframe): Dataframe of rater (converted from json)
        id (int): Rater ID

    Returns:
        pd.Dataframe: Processed dataframe
    """
    # Only keep accepted answers
    df = raw_df[raw_df.answer == "accept"]
    # Add column for rater id
    df.insert(0, "rater_id", id)
    # Replace text column name with "doc"
    df.columns = df.columns.str.replace("text", "doc")
    # Drop rows with any duplicates in doc column
    df = df.drop_duplicates("doc")
    # Drop rows where doc is only one token
    df = df[df["tokens"].apply(lambda x: len(x) > 1)]
    # Reset index
    df.reset_index(inplace=True, drop=True)

    return df


def list_overlap(lst1, lst2):
    return list(set(lst1) & set(lst2))


def rater_avg_df(score_df):
    score_df_copy = score_df.copy()
    np.fill_diagonal(score_df_copy.values, np.nan)
    score_df["rater_avg"] = score_df_copy.mean(axis=1).round(2).tolist()
    return score_df


def average_score(score_df, print_score=True):
    average_df = score_df.copy()
    average_df.values[np.tril_indices_from(score_df)] = np.nan
    mean = average_df.unstack().mean(skipna=True)
    sd = average_df.unstack().std()
    if print_score == True:
        print(f"Mean (SD) Score: {mean} ({sd})")
    elif print_score == False:
        return (mean, sd)
