# DANSK-gold-NER

```bash
# Create folders for the data
bash tools/create_data_folders.sh
```

Download DANSK, unzip and place unzipped folder in data/

```bash
# Add DANSK to database
bash tools/raters_to_db.sh -o 1

# As DANSK is only available in .jsonl format, convert it to DocBins /.spacy files, using prodigy's database
bash tools/raters_from_db_to_spacy.sh

# Remove it from db again
bash tools/rm_raters_from_db.sh

# Split the unprocessed data up into multi and single folders, as they shall be handled in different steps
python src/preprocessing/split_full_to_single_multi.py

# Add unprocessed-single to the prodigy database -> Can't because I can't convert DocBins to .jsonl
# Merge the unprocessed-single data into a single .jsonl file
# bash tools/raters_to_db.sh -p single -d unprocessed -o 0 # 
# prodigy db-merge rater_1,rater_3,rater_4,rater_5,rater_6,rater_8,rater_1,rater_9 unprocessed-single-combined
# prodigy db-out unprocessed-single-combined data/single/unprocessed/combined

# Streamline the multi data by overwriting frequently tagged annotations to all raters data
src/preprocessing/streamline/streamline_multi.ipynb

# Add the streamlined data to the prodigy database
bash tools/raters_to_db.sh -p multi -d streamlined -o 0

# Manually resolve the remaining conflicts in the streamlined data
prodigy review gold-multi rater_1,rater_3,rater_4,rater_5,rater_6,rater_7,rater_9 --label PERSON,NORP,FACILITY,ORGANIZATION,LOCATION,PRODUCT,EVENT,LAW,LANGUAGE,DATE,TIME,PERCENT,MONEY,QUANTITY,ORDINAL,CARDINAL -S -A # Can't because I can't convert Docs/DocBins to .jsonl

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
