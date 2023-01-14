import dacy
import os
import json
import copy
import re
import glob
import pandas as pd
from collections import Counter
from spacy.tokens import DocBin, Doc, Span
from spacy.training.corpus import Corpus
from itertools import combinations

# Count how many raters have annotated a given doc
def count_raters_for_doc(doc, all_docs):
    doc_texts = [doc.text for doc in all_docs]
    return doc_texts.count(doc.text)


# Retrieve a list of annotated entities for a given doc, across all raters
def retrieve_all_ents(doc, all_docs):
    ents_for_doc = []
    # Acquire list of all ents for a doc
    for i in all_docs:
        if i.text == doc.text:
            for ent in i.ents:
                ents_for_doc.append(ent)
    return ents_for_doc


# Retrieve a exploded doc with exploded ents (returns a nested dictionary with all relevant information for a single doc)
def explode_doc(doc, ents):
    ents_exploded = [
        {
            "ent": ent,
            "ent.text": ent.text,
            "ent.label_": ent.label_,
            "ent.label_and_text": ent.text + ent.label_,
            "ent.start_char": ent.start_char,
            "ent.end_char": ent.end_char,
        }
        for ent in ents
    ]
    return {
        "doc.text": doc.text,
        "doc": doc,
        "doc.ents": ents_exploded,
    }


# From an exploded doc, retrieve:
# - A list of unique entities across raters for a doc
# - A list of unique entities counts across raters for a doc
# - A list of unique entities ratio of occurence across raters for a doc
# The "match_label_and_text" defines whether to match on text alone, or on label and text
def doc_ents_count(exploded_doc, n_raters, match_label_and_text=True):
    unique_ents = []
    unique_ents_count = []

    if match_label_and_text:
        for ent_idx in range(len(exploded_doc["doc.ents"])):
            ent = exploded_doc["doc.ents"][ent_idx]
            # If ent is in unique_ents, unique_ents_count += 1, for same index:
            if any(
                ent["ent.label_and_text"] == unique_ent["ent.label_and_text"]
                for unique_ent in unique_ents
            ):
                unique_ent_label_and_texts = [
                    unique_ent["ent.label_and_text"] for unique_ent in unique_ents
                ]
                index_of_same_ent = unique_ent_label_and_texts.index(
                    ent["ent.label_and_text"]
                )
                unique_ents_count[index_of_same_ent] += 1
            else:
                unique_ents.append(ent)
                unique_ents_count.append(1)

    else:
        for ent_idx in range(len(exploded_doc["doc.ents"])):
            ent = exploded_doc["doc.ents"][ent_idx]
            # If ent is in unique_ents, unique_ents_count += 1, for same index:
            if any(
                ent["ent.text"] == unique_ent["ent.text"] for unique_ent in unique_ents
            ):
                unique_ent_texts = [
                    unique_ent["ent.text"] for unique_ent in unique_ents
                ]
                index_of_same_ent = unique_ent_texts.index(ent["ent.text"])
                unique_ents_count[index_of_same_ent] += 1
            else:
                unique_ents.append(ent)
                unique_ents_count.append(1)

    unique_ents = [unique_ent["ent"] for unique_ent in unique_ents]
    unique_ents_ratio = [i / n_raters for i in unique_ents_count]
    return unique_ents, unique_ents_count, unique_ents_ratio


# Define a function for finding frequent annotations (above certain threshold)
def retrieve_freq_ents(
    unique_ents, unique_ents_count, unique_ents_ratio, threshold, n_raters
):
    if n_raters <= 2:
        freq_ents = []

    if n_raters in [3, 4, 5, 6]:
        freq_ents = [
            unique_ent
            for unique_ent, unique_ent_count in zip(unique_ents, unique_ents_count)
            if unique_ent_count >= 2
        ]

    if n_raters in [7, 8, 9, 10]:
        freq_ents = [
            unique_ent
            for unique_ent, unique_ent_count in zip(unique_ents, unique_ents_count)
            if unique_ent_count >= 3
        ]
    return freq_ents

    # return [
    #     unique_ent
    #     for unique_ent, unique_ent_ratio in zip(unique_ents, unique_ents_ratio)
    #     if unique_ent_ratio >= threshold
    # ]


# Define a function for finding infrequent annotations (below certain threshold)
def retrieve_infreq_ents(
    unique_ents, unique_ents_count, unique_ents_ratio, threshold, n_raters
):
    if n_raters <= 5:
        infreq_ents = []

    if n_raters in [6, 7, 8]:
        infreq_ents = [
            unique_ent
            for unique_ent, unique_ent_count in zip(unique_ents, unique_ents_count)
            if unique_ent_count <= 1
        ]

    if n_raters > 8:
        infreq_ents = [
            unique_ent
            for unique_ent, unique_ent_count in zip(unique_ents, unique_ents_count)
            if unique_ent_count <= 2
        ]

    return infreq_ents


# Function for determining whether two tokens occupy parts of the same span
def _tokens_occupy_same_span(token0, token1):
    # Return False if one isn't contained in the other, and True if it is. Order doesn't matter
    return bool(
        list(
            range(
                max(token0.start_char, token1.start_char),
                min(token0.end_char, token1.end_char) + 1,
            )
        )
    )


# Function for getting list of tokens that occupy the span of another token
def get_same_span_ents(ents_list):
    freq_ent_same_spans = []
    a = combinations(ents_list, 2)
    for i in a:
        if _tokens_occupy_same_span(i[0], i[1]):
            freq_ent_same_spans.extend(i)
    return list(set(freq_ent_same_spans))


# Define a function for finding the index of a list in which a doc exists
def get_same_doc_index(doc, list_of_docs):
    for i, e in enumerate(list_of_docs):
        if e.text == doc.text:
            return i


# Define a function for deleting any ents in a doc that exist in the same span as a frequent ent
def _rm_same_span_ent_in_doc(doc, frequent_ent_for_doc):
    # Find indexes of doc.ents where either ...
    idxs_of_removable_ents = [
        idx
        for idx, item in enumerate(list(doc.ents))
        if (  # ... the start- or end character is the same as for the frequent entity
            item.start_char == frequent_ent_for_doc.start_char
            or item.end_char
            == frequent_ent_for_doc.end_char  # OR instead of AND is the difference
        )
        or (  # ... the start character is smaller than for the freq entity and where the end-character is larger than the freq entity
            item.start_char <= frequent_ent_for_doc.start_char
            and item.end_char >= frequent_ent_for_doc.end_char
        )
        or (  # ... the start character is smaller than for the freq entity and where the end-character is smaller than the freq entity
            item.start_char <= frequent_ent_for_doc.start_char
            and item.end_char <= frequent_ent_for_doc.end_char
        )
        or (  # ... the start character is larger than for the freq entity and where the end-character is larger than the freq entity
            item.start_char >= frequent_ent_for_doc.start_char
            and item.end_char >= frequent_ent_for_doc.end_char
        )
    ]
    # Remove doc.ents with those indices
    doc_ents = list(doc.ents)
    for idx in sorted(idxs_of_removable_ents, reverse=True):
        del doc_ents[idx]
    doc.ents = tuple(doc_ents)
    return doc


# Define a function for deleting any ents in a doc that exists in any of the same spans as a list of frequent ents
def rm_same_span_ents_in_doc(doc, frequent_ents_for_doc):
    for frequent_ent_for_doc in frequent_ents_for_doc:
        doc = _rm_same_span_ent_in_doc(doc, frequent_ent_for_doc)
    return doc


# Define a function for deleting any ents in a doc that exist in the EXACT same span as a frequent ent
def _rm_exact_span_ent_in_doc(doc, frequent_ent_for_doc):
    # Find indexes of doc.ents where either the start- or end character is the same as for the frequent entity
    idxs_of_removable_ents = [
        idx
        for idx, item in enumerate(list(doc.ents))
        if (
            item.start_char == frequent_ent_for_doc.start_char
            and item.end_char
            == frequent_ent_for_doc.end_char  # AND instead of OR is the difference
        )
    ]
    # Remove doc.ents with those indices
    doc_ents = list(doc.ents)
    for idx in sorted(idxs_of_removable_ents, reverse=True):
        del doc_ents[idx]
    doc.ents = tuple(doc_ents)
    return doc


# Define a function for deleting any ents in a doc that exists in any of the same spans as a list of frequent ents
def rm_exact_span_ents_in_doc(doc, frequent_ents_for_doc):
    for frequent_ent_for_doc in frequent_ents_for_doc:
        doc = _rm_exact_span_ent_in_doc(doc, frequent_ent_for_doc)
    return doc


# Define a function for adding a frequent entity to a doc
def _add_freq_ent_to_doc(doc, frequent_ent_for_a_doc):
    new_doc_ents = doc.ents + (frequent_ent_for_a_doc,)
    doc.ents = new_doc_ents
    return doc


# Define a function for adding frequent ents in a list of ents to a doc
def add_freq_ents_to_doc(doc, frequent_ents_for_a_doc):
    for frequent_ent_for_a_doc in frequent_ents_for_a_doc:
        doc = _add_freq_ent_to_doc(doc, frequent_ent_for_a_doc)
    return doc


###########################################################################
############################################################
#############################################
############### Define a function for retrieving frequent and infrequent entities for a doc: ###############
#############################################
############################################################
###########################################################################

# Get list of frequent and infrequent entities for a doc
def retrieve_freq_and_infreq_ents_from_doc(
    doc, all_docs, threshold_freq, threshold_infreq
):
    # Get number of raters that have annotated the doc
    n_raters = count_raters_for_doc(doc, all_docs)

    # Retrieve a list of annotated entities for a given doc, across all raters
    ents = retrieve_all_ents(doc, all_docs)

    # Retrieve a exploded doc with exploded ents (returns a nested dictionary with all relevant information for a single doc)
    doc_exploded = explode_doc(doc, ents)

    # From an exploded doc, retrieve:
    # - A list of unique entities across raters for a doc
    # - A list of unique entities counts across raters for a doc
    # - A list of unique entities ratio of occurence across raters for a doc
    # The "match_label_and_text" defines whether to match on text alone, or on label and text
    (
        unique_ents_partial_match,
        unique_ents_partial_match_count,
        unique_ents_partial_match_ratio,
    ) = doc_ents_count(doc_exploded, n_raters, match_label_and_text=False)

    # Retrieve a list of ents that have a ratio under a certain threshold
    infreq_unique_ents_partial_match = retrieve_infreq_ents(
        unique_ents_partial_match,
        unique_ents_partial_match_count,
        unique_ents_partial_match_ratio,
        threshold_infreq,
        n_raters,
    )

    # If infrequent entities take up the same span, delete them from the infrequent entities list
    # This is in order to avoid deleting e.g. entities [dkpol, #dkpol]. Individually their ratios may be below threshold, but above if combined.
    same_span_ents = get_same_span_ents(infreq_unique_ents_partial_match)
    for ent in same_span_ents:
        if ent in infreq_unique_ents_partial_match:
            infreq_unique_ents_partial_match.remove(ent)

    # From an exploded doc, retrieve:
    # - A list of unique entities across raters for a doc
    # - A list of unique entities counts across raters for a doc
    # - A list of unique entities ratio of occurence across raters for a doc
    # The "match_label_and_text" defines whether to match on text alone, or on label and text
    (
        unique_ents_full_match,
        unique_ents_full_match_count,
        unique_ents_full_match_ratio,
    ) = doc_ents_count(doc_exploded, n_raters, match_label_and_text=True)

    # Retrieve a list of ents that have a ratio over a certain threshold
    freq_unique_ents_full_match = retrieve_freq_ents(
        unique_ents_full_match,
        unique_ents_full_match_count,
        unique_ents_full_match_ratio,
        threshold_freq,
        n_raters,
    )

    # Retrieve a list of ents that occupy the span of other ents
    unique_ents_full_match_same_span = get_same_span_ents(freq_unique_ents_full_match)

    # print(f"freq_ents: {freq_unique_ents_full_match}")
    # print(f"freq_ents_full_match_same_span: {unique_ents_full_match_same_span}")

    # Retrieve a list of indexes of same span ents
    unique_ents_full_match_same_span_indexes = [
        freq_unique_ents_full_match.index(ent)
        for ent in unique_ents_full_match_same_span
        # unique_ents_full_match.index(ent) for ent in unique_ents_full_match_same_span
    ]
    # print(freq_unique_ents_full_match)
    # print(unique_ents_full_match)
    # print(unique_ents_full_match_same_span)
    # print(unique_ents_full_match_same_span_indexes)

    # print(f"indexes of same span ents: {unique_ents_full_match_same_span_indexes}")

    # print("\nunique_ents_full_match_same_span_indexes:")
    # print(unique_ents_full_match_same_span_indexes)

    # print("\nunique_ents_full_match_same_span_indexes[0]:")
    # print(unique_ents_full_match_same_span_indexes[0])

    # print("\nunique_ents_full_match_same_span_indexes[1]:")
    # print(unique_ents_full_match_same_span_indexes[1])

    # print("\nfreq_unique_ents_full_match:")
    # print(freq_unique_ents_full_match)

    # print("\nfreq_unique_ents_full_match[unique_ents_full_match_same_span_indexes[0]]:")
    # print(freq_unique_ents_full_match[unique_ents_full_match_same_span_indexes[0]])

    # print("\nfreq_unique_ents_full_match[unique_ents_full_match_same_span_indexes[1]]:")
    # print(freq_unique_ents_full_match[unique_ents_full_match_same_span_indexes[1]])

    # print("\n")

    # If there are exactly 2 frequent entities that overlap in span, only keep the most frequent. If both equally, delete both
    if len(unique_ents_full_match_same_span_indexes) == 2:
        # print("exactly 2 span indexes")
        if (
            unique_ents_full_match_ratio[unique_ents_full_match_same_span_indexes[0]]
            > unique_ents_full_match_ratio[unique_ents_full_match_same_span_indexes[1]]
        ):
            del freq_unique_ents_full_match[unique_ents_full_match_same_span_indexes[1]]
            # print("one ratio is larger than the other")
        elif (
            unique_ents_full_match_ratio[unique_ents_full_match_same_span_indexes[0]]
            < unique_ents_full_match_ratio[unique_ents_full_match_same_span_indexes[1]]
        ):
            del freq_unique_ents_full_match[unique_ents_full_match_same_span_indexes[0]]
            # print("one ratio is larger than the other")
        elif (
            unique_ents_full_match_ratio[unique_ents_full_match_same_span_indexes[0]]
            == unique_ents_full_match_ratio[unique_ents_full_match_same_span_indexes[1]]
        ):
            # print("the ratio of these two are the same")
            for idx in sorted(unique_ents_full_match_same_span_indexes, reverse=True):
                del freq_unique_ents_full_match[idx]

    # Else:
    # Remove ents that span the same as other spans from the list of frequent entities
    # This is done to avoid having to deal with choosing which entity to keep in cases of conflict
    else:
        for idx in sorted(unique_ents_full_match_same_span_indexes, reverse=True):
            del freq_unique_ents_full_match[idx]

    # print(freq_unique_ents_full_match)

    return (
        unique_ents_full_match,
        unique_ents_partial_match,
        freq_unique_ents_full_match,
        infreq_unique_ents_partial_match,
        unique_ents_full_match_count,
        unique_ents_partial_match_count,
        n_raters,
    )


###########################################################################
############################################################
#############################################
############### Define a function for streamlining a doc: ###############
#############################################
############################################################
###########################################################################


def streamline_doc(doc, rater_docs, freq_ents, infreq_ents):
    # Get index of rater_docs in which the doc exists
    doc_index_in_rater_docs = get_same_doc_index(doc, rater_docs)

    # If the doc exists in the rater_docs
    if doc_index_in_rater_docs is not None:

        rater_doc = copy.deepcopy(rater_docs[doc_index_in_rater_docs])

        # Remove the ents in the rater_doc that occupy the same spans as the frequent ents
        rater_doc = rm_same_span_ents_in_doc(rater_doc, freq_ents)

        # Remove the ents in the rater_doc that occupy the same spans as the infrequent ents
        rater_doc = rm_exact_span_ents_in_doc(rater_doc, infreq_ents)

        # Add the ents from the frequent ents to the rater_doc
        rater_doc = add_freq_ents_to_doc(rater_doc, freq_ents)

        return rater_doc
