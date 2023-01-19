# DANSK-gold-NER

## Pipeline 'chunked up'
```bash
bash tools/create_data_folders.sh
python src/preprocessing/merge_and_rm_dupli.py
bash tools/raters_to_db.sh -o 1 # Add DANSK to database
bash tools/raters_from_db_to_spacy.sh
bash tools/rm_raters_from_db.sh
rm -r -f data/full/unprocessed/rater_2/* # Remove rater 2 
rm -r -f data/full/unprocessed/rater_10/* # Remove rater 10
python src/preprocessing/rater_8_fix.py # Fix rater 8 data
python src/preprocessing/rm_product_and_language.py # Remove PRODUCT and LANGUAGE tags
python src/preprocessing/split_full_to_single_multi.py
python src/preprocessing/streamline/streamline_multi.py
bash tools/raters_spacy_to_jsonl.sh -p multi -d streamlined # Convert the streamlined multi from .spacy to .jsonl
bash tools/raters_to_db.sh -p multi -d streamlined -o 0 # Add the streamlined data to the prodigy database
prodigy review gold-multi-all rater_1,rater_3,rater_4,rater_5,rater_6,rater_7,rater_8,rater_9 --label PERSON,NORP,FACILITY,ORGANIZATION,LOCATION,EVENT,LAW,DATE,TIME,PERCENT,MONEY,QUANTITY,ORDINAL,CARDINAL,GPE -S -A
```

## Repository pipeline
- **Create folder structure for the data in the different stages**
```bash
bash tools/create_data_folders.sh
```

- **Download data**
```bash
Download DANSK, unzip and place unzipped folder in data/
```

- **Merge original data and remove duplicates**
    - Removing duplicates that matches on both 'meta' and on 'text' - only keep the last rated (from timestamp)
    - No removal of duplicates matching only on 'text'
```bash
python src/preprocessing/merge_and_rm_dupli.py
```

- **Converting data to DocBins/.spacy files**
```bash
bash tools/raters_to_db.sh -o 1 # Add DANSK to database
bash tools/raters_from_db_to_spacy.sh
bash tools/rm_raters_from_db.sh
```

- **Assess data**
    - Assessment of:
        - Interrater reliability 
        - Annotations for the different raters
        - Number of raters for each unique doc (later stage, not now actually)
        - Duplicates
    - Current findings: 
        - Poor annotations from rater 2
        - Poor annotations from rater 10
        - Rater 8 annotates "man", "sig selv" as PER ents
        - No tags for LANGUAGE, and very poor tagging for PRODUCT
```bash
# src/data_assessment/n_duplicates_for_files.ipynb
# src/data_assessment/interrater_reliability/interrater_reliability.ipynb
```

- **Make appropriate changes in accordance with the the assesment of the raters**
    - Cut away rater 2
    - Cut away rater 10
    - For rater 8:
        - Exclude all PER annotations if the individual tokens.is_stop = True
    - Remove all ents with LANGUAGE and PRODUCT
```bash
rm -r -f data/full/unprocessed/rater_2/* # Remove rater 2 
rm -r -f data/full/unprocessed/rater_10/* # Remove rater 10
python src/preprocessing/rater_8_fix.py # Fix rater 8 data
python src/preprocessing/rm_product_and_language.py # Remove PRODUCT and LANGUAGE tags
```

- **Split data for each rater up into docs that have been rated by multiple raters, and into docs that have only been annotated by a single rater**
    - Split the unprocessed data up into multi and single folders, as they shall be handled in different steps
```bash
python src/preprocessing/split_full_to_single_multi.py
```

- **Investigate the distribution of the number of raters for the multi data**
    - Roughly 25% of multi docs have been rated by 2 raters
    - Roughly 25% of multi docs have been rated by 10 raters
    - Roughly 50% of multi docs have been rated by >2 and <10
```bash
# src/data_assessment/n_raters_for_each_doc.ipynb
```

- **Streamline the multi data, automatically accepting highly frequent annotations while rejecting highly infrequent annotations**
    - Reason: If there are e.g. 3 raters for a doc, then a 20% freq threshold for frequent ents is too low. But for 7 raters it is fine.
    - For each rater:
        - For each doc:
            - Adding frequent ents:
                - If the doc has been annotated by fewer than 4 raters:
                    - Do nothing
                - If the doc has been annotated by 4-8 raters:
                    - If an entity has been annotated by 3 or more raters (Strict match as defined by https://pypi.org/project/nervaluate/ meaning that the span AND tag is the exact same) then:
                        - Add it to list of frequent entities
                    - If a span appears twice (full or partial overlap) in the list of frequent entities, delete the least frequent of the two from the list
                    - If a span appears 3 times or more (full or partial overlap) in the list of frequent entities, delete all frequent ents with this overlap from the list
                    - For each frequent entity in the list:
                        - Delete any annotations from any raters that overlap (even partially) the span of the frequent entity
                        - Add the frequent annotation for all raters for the given doc
            - Deleting infrequent ents:
                - If the doc has been annotated by 2-5 raters:
                    - Do nothing 
                - If the doc has been annotated by 6-8 raters:
                    - If a ent/span has been annotated by 1 rater (Exact match as defined by https://pypi.org/project/nervaluate/ meaning that the span is the same, but tag can differ) and no other annotations overlap then:
                        - If no other ents exists in the same span for any rater (even partially)
                            - Delete ent (strict match) in all raters
```bash
python src/preprocessing/streamline/streamline_multi.py
```

- **Adding streamlined data to database**
    - First convert from .spacy to .jsonl
bash tools/raters_spacy_to_jsonl.sh -p multi -d streamlined # Convert the streamlined multi from .spacy to .jsonl
bash tools/raters_to_db.sh -p multi -d streamlined -o 0 # Add the streamlined data to the prodigy database


- **Manually resolve conflicts in the streamlined data**
    - Ignoring cases with doubt, and flagging them (created a prodigy.json file enabling flagging)
        - E.g. In cases where a doc with minimal context is provided and multiple tags may be appropriate. E.g. 'Pande' might be tagged as verb or noun.
    - - In cases where two entities are correct, yet have different spans, the broadest span takes precedence. E.g. 'Taler 8' might be tagged as a PER, but 8 may be tagged as a cardinal
    - Save as 'gold-multi' in db
    - LANGUAGE and PRODUCT are not included removed
    - Cases with no conflict are automatically accepted (-A)
    
    
```bash
prodigy review gold-multi-all rater_1,rater_3,rater_4,rater_5,rater_6,rater_7,rater_8,rater_9 --label PERSON,NORP,FACILITY,ORGANIZATION,LOCATION,EVENT,LAW,DATE,TIME,PERCENT,MONEY,QUANTITY,ORDINAL,CARDINAL,GPE -S -A
```

- **Export the gold-multi-no-flagged cases**
```bash
python src/preprocessing/filter_only_non_flagged.py
prodigy db-out gold-multi-no-flagged > data/multi/gold/gold-multi-no-flagged.jsonl
```

- **Export the ignored, flagged cases**
```bash
prodigy db-out gold-multi-all > data/multi/gold/gold-multi-flagged.jsonl --flagged-only
```

- **Review the ignored, flagged cases after discussion with team**
    - See predictions of a direct translation from the Roberta Large Ontonotes
    - Discuss with Kenneth/Rebekah/others
```bash
# ????
```

- **Merge the gold-multi-no-flagged and the gold-multi-flagged
```bash
prodigy db-merge gold-multi-flagged,gold-multi-no-flagged gold-multi
```

- **Export the gold-multi dataset to local machine**
    - Both as .jsonl and split into training and validation data as .spacy. Includes default config for the spaCy training.
```bash
prodigy db-out gold-multi data/multi/gold
prodigy data-to-spacy data/multi/gold/ --ner gold-multi --lang "da" --eval-split .2
```

- **Train a model on the gold-multi dataset**
    - Use contextual embeddings from a transformer model (see DaCy and ask Kenneth at this point)
```bash
# python -m spacy train data/multi/gold/config.cfg --paths.train data/multi/gold/train.spacy --paths.dev data/multi/gold/dev.spacy --output data/multi/gold/output
```

- **Predict on the single data for each rater**
    - In a script

- **Assess agreement between rater and model**
    - Make assessment fine-grained, and assess for each type of ent.

- **Potentially. Make appropriate changes on gold-standard-multi data on the basement of assessment between rater and model**

- **Potentially. Re-train model on new gold-standard-multi data**

- **Potentially. Re-predict on single data for each rater**

- **Potentially. Re-assess agreement between rater and model**

- **Potentially. Repeat above process**

- **Manually resolve conflicts in single data (between model predictions and annotators)**
    - Save the gold-single dataset

- **Merge gold-single and gold-multi dataset into gold-dansk**

- **Save gold-dansk**


## Named Entity Recognition (NER) tagging guidelines

This type of tagging is to determine what entities are present in a given text. There are 18 possible tags that can be used and the visual below describes them all. 

### Named Entity types
Names (often referred to as *"Named entities"*) are annotated to the following set of types:
|              |                                                      |
| ------------ | ---------------------------------------------------- |
| PERSON       | People, including fictional                          |
| NORP         | Nationalities or religious or political groups       |
| FACILITY     | Building, airports, highways, bridges, etc.          |
| ORGANIZATION | Companies, agencies, institutions, etc.              |
| LOCATION     | Non-GPE locations, mountain ranges, bodies of water  |
| PRODUCT      | Vehicles, weapons, foods, etc. (not services)        |
| EVENT        | Named hurricanes, battles, wars, sports events, etc. |
| WORK OF ART  | Titles of books, songs, etc.                         |
| LAW          | Named documents made into laws                       |
| LANGUAGE     | Any named language                                   |
| GPE          | Countries, cities, states.


The following values are also annotated in style similar to names:

|          |                                             |
| -------- | ------------------------------------------- |
| DATE     | Absolute or relative dates or periods       |
| TIME     | Times smaller than a day                    |
| PERCENT  | Percentage (including *"%"*)                |
| MONEY    | Monetary values, including unit             |
| QUANTITY | Measurements, as of weight or distance      |
| ORDINAL  | "first", "second"                           |
| CARDINAL | Numerals that do no fall under another type |

### Named Entity inconsistencies and the chosen way of resolvement
#### Pipeline for resolving inconsistencies in which there is doubt, during the manual Prodigy review

#### Examples
**Doc:**
- 
**Conflicting ents:**
- 
**Ents:**
- 

