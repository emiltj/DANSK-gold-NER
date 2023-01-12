# DANSK-gold-NER

# The repository structure

# Overarching idea for obtaining a gold-standard DANSK dataset
- *Create folder structure for the data in the different stages*
- *Import data*
- *Assess data
    - Interrater reliability 
    - Annotations for the different raters
    - Number of raters for each unique doc
        - Current findings: 
            - Poor annotations from rater 2
            - Poor annotations from rater 10
            - Rater 8 annotates "man", "sig selv" as PER ents
- *Make appropriate changes in accordance with the the assesment of the raters*
    - Cut away rater 2
    - Cut away rater 10
    - For rater 8:
        - Exclude all PER annotations if the individual tokens.is_stop = True
        - Consider using:
            def is_stop_ent(span):
                return all([t.is_stop for t in span])
- *Split data for each rater up into docs that have been rated by multiple raters, and into docs that have only been annotated by a single rater*
- *Streamline the multi data, automatically accepting highly frequent annotations while rejecting highly infrequent annotations*
    ***** NOTE: ONLY RELEVANT IF - CHECK FIRST:
    - If many docs are rated by somewhere between 1 and 10, create rules for when to apply the streamlining (e.g. only in docs with > 3 raters)
    - If very few docs are rated by somewhere between 1 and 10, potentially delete these from the multiple streamlining
    - If all docs are rated by either 10 or 1, no problem - don't do anything
    - Reason: If there are e.g. 3 raters for a doc, then a 20% freq threshold for frequent ents is too low. But for 7 raters it is fine.

    - For each rater:
        - For each doc:
            - If the doc has been annotated by 3 raters:
                - If an entity has been annotated by 2/3 of raters (Strict match as defined by https://pypi.org/project/nervaluate/) then:
                    - Delete all annotations that overlap the span of the frequent entity
                    - Add annotation to all raters for the given doc
            - If the doc has been annotated by 4 raters:
                - If an entity has been annotated by +2 raters (Strict match as defined by https://pypi.org/project/nervaluate/) then:
                    - If there are no other frequent entities for the same span:
                        - Delete all annotations that overlap the span of the frequent entity
                        - Add annotation to all raters for the given doc
            - If the doc has been annotated by > 4 raters:
                - If an entity has been annotated by 1 or fewer raters:
                    - Delete this annotation in the doc for all rater
                - If an entity has been annotated by +2 raters (Strict match as defined by https://pypi.org/project/nervaluate/) then:
                    - If there are no other frequent entities for the same span:
                        - Delete all annotations that overlap the span of the frequent entity
                        - Add annotation to all raters for the given doc
- *Manually resolve the remaining conflicts in the streamlined data*
    - Save the gold-multi dataset
- *Train a model on the gold-multi dataset*
    - Use contextual embeddings from a transformer model (see DaCy and ask Kenneth at this point)
- *Predict on the single data for each rater*
    - In a script
- *Assess agreement between rater and model*
    - Make assessment fine-grained, and assess for each type of ent.
- *Potentially. Make appropriate changes on gold-standard-multi data on the basement of assessment between rater and model*
- *Potentially. Re-train model on new gold-standard-multi data*
- *Potentially. Re-predict on single data for each rater*
- *Potentially. Re-assess agreement between rater and model*
- *Potentially. Repeat above process*
- *Manually resolve conflicts in single data (between model predictions and annotators)*
    - Save the gold-single dataset
- *Merge gold-single and gold-multi dataset into gold-dansk
- *Save gold-dansk*


                
            



# Running this repo
```bash
# Create folders for the data
bash tools/create_data_folders.sh
```

Download DANSK, unzip and place unzipped folder in data/

```bash
# Add DANSK to database
bash tools/raters_to_db.sh -o 1

# As DANSK is only available in .jsonl format, convert it to DocBins /.spacy files, using prodigy's database (and remove them from db again)
bash tools/raters_from_db_to_spacy.sh
bash tools/rm_raters_from_db.sh

# Split the unprocessed data up into multi and single folders, as they shall be handled in different steps
python src/preprocessing/split_full_to_single_multi.py

# Add unprocessed-single to the prodigy database
bash tools/raters_spacy_to_jsonl.sh -p single -d unprocessed
bash tools/raters_to_db.sh -p single -d unprocessed -o 0

# Merge the unprocessed-single data into a single "unprocessed-single-combined" .jsonl file
prodigy db-merge rater_1,rater_3,rater_4,rater_5,rater_6,rater_7,rater_9 unprocessed-single-combined
prodigy db-out unprocessed-single-combined data/single/unprocessed/combined

# Clear database again
bash tools/rm_raters_from_db.sh
prodigy drop unprocessed-single-combined

# Streamline the multi data by overwriting frequently tagged annotations to all raters data. Save as .spacy
src/preprocessing/streamline/streamline_multi.ipynb

# Convert the streamlined multi from .spacy to .jsonl
bash tools/raters_spacy_to_jsonl.sh -p multi -d streamlined

# Add the streamlined data to the prodigy database
bash tools/raters_to_db.sh -p multi -d streamlined -o 0

# Manually resolve the remaining conflicts in the streamlined data
prodigy review gold-multi rater_1,rater_3,rater_4,rater_5,rater_6,rater_7,rater_9 --label PERSON,NORP,FACILITY,ORGANIZATION,LOCATION,PRODUCT,EVENT,LAW,LANGUAGE,DATE,TIME,PERCENT,MONEY,QUANTITY,ORDINAL,CARDINAL -S -A --view-id ner-manual

# Export the gold-multi dataset to local machine, both as .jsonl and split into training and validation data as .spacy. Includes default config for the spaCy training.
prodigy db-out gold-multi data/multi/gold
prodigy data-to-spacy data/multi/gold/ --ner gold-multi --lang "da" --eval-split .2

# Train a NER-model on the gold-multi
python -m spacy train data/multi/gold/config.cfg --paths.train data/multi/gold/train.spacy --paths.dev data/multi/gold/dev.spacy --output data/multi/gold/output

# Predict on the unprocessed-single-combined using the gold-multi-NER model
# ??

# Resolve conflicts between model and single raters
# ??
# Maybe something like: prodigy review gold-single <name_of_original_raters>,<name_of_predictions> --label PERSON,NORP,FACILITY,ORGANIZATION,LOCATION,PRODUCT,EVENT,LAW,LANGUAGE,DATE,TIME,PERCENT,MONEY,QUANTITY,ORDINAL,CARDINAL -S -A

# Merge the combined gold-dansk-single with gold-dansk-multi
prodigy db-merge gold-single,gold-multi gold-full

# Export gold-full as .jsonl and as .spacy
prodigy db-out gold-full data/full/gold
prodigy data-to-spacy data/full/gold data/full/gold --ner gold-full --lang "da" --eval-split 0
```
