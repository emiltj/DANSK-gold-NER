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
python src/preprocessing/split_by_answer.py
prodigy mark gold-multi-ignored-resolved dataset:gold-multi-ignored --view-id review --label PERSON,NORP,FACILITY,ORGANIZATION,LOCATION,EVENT,LAW,DATE,TIME,PERCENT,MONEY,QUANTITY,ORDINAL,CARDINAL,GPE
prodigy db-merge gold-multi-accepted,gold-multi-ignored-resolved gold-multi
prodigy db-out gold-multi data/multi/gold
prodigy data-to-spacy data/multi/gold/ --ner gold-multi --lang "da" --eval-split .2
```
Move to UCLOUD
0. Clone this repo 
```bash
Run following code:
git clone https://github.com/emiltj/DANSK-gold-NER.git
bash server_dependencies.sh
bash cuda_dependencies
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
    - Ignoring cases with doubt (and writing them down, to later discuss with team)
        - E.g. In cases where a doc with minimal context is provided and multiple tags may be appropriate. E.g. 'Pande' might be tagged as verb or noun.
    - - In cases where two entities are correct, yet have different spans, the broadest span takes precedence. E.g. 'Taler 8' might be tagged as a PER, but 8 may be tagged as a cardinal
    - Save as 'gold-multi-all' in db
    - LANGUAGE and PRODUCT are not included removed
    - Cases with no conflict are automatically accepted (-A)
```bash
prodigy review gold-multi-all rater_1,rater_3,rater_4,rater_5,rater_6,rater_7,rater_8,rater_9 --label PERSON,NORP,FACILITY,ORGANIZATION,LOCATION,EVENT,LAW,DATE,TIME,PERCENT,MONEY,QUANTITY,ORDINAL,CARDINAL,GPE -S -A
```

- **Export the gold-multi-ignored and the gold-multi-accepted cases**
```bash
python src/preprocessing/split_by_answer.py # Retrieve all ignored and accepted instances. Loads them into db datasets 'gold-multi-accepted' and 'gold-multi-ignored' (also saves these as .jsonl to data/multi/gold)
```

- **Review the ignored cases after discussion with team**
    - See predictions of a direct translation from the Roberta Large Ontonotes # https://huggingface.co/tner/roberta-large-ontonotes5
    - Discuss with Kenneth/Rebekah/others
```bash
prodigy mark gold-multi-ignored-resolved dataset:gold-multi-ignored --view-id review --label PERSON,NORP,FACILITY,ORGANIZATION,LOCATION,EVENT,LAW,DATE,TIME,PERCENT,MONEY,QUANTITY,ORDINAL,CARDINAL,GPE
```

- **Dump the gold-multi-ignored-resolved**
```bash
prodigy db-out gold-multi-ignored-resolved data/multi/gold
```

- **Write down the gold-multi-ignored-resolved cases**
    - Retrieve the ignored cases as text with annotations (using prodigy print-dataset)
    - Save retrieved ignored cases to 'edge-cases.txt'
```bash
prodigy print-dataset gold-multi-ignored-resolved
```

- **Merge the gold-multi-ignored-resolved and the gold-multi-accepted
```bash
prodigy db-merge gold-multi-accepted,gold-multi-ignored-resolved gold-multi
```

- **Export the gold-multi dataset to local machine**
    - Both as .jsonl and split into training and validation data as .spacy. Includes default config for the spaCy training.
```bash
prodigy db-out gold-multi data/multi/gold
prodigy data-to-spacy gold-multi-training/datasets/ --ner gold-multi --lang "da" --eval-split 0
mv gold-multi-training/datasets/train.spacy gold-multi-training/datasets/gold-multi-full.spacy
prodigy data-to-spacy gold-multi-training/datasets/ --ner gold-multi --lang "da" --eval-split .2
mv gold-multi-training/datasets/train.spacy gold-multi-training/datasets/gold-multi-train.spacy
mv gold-multi-training/datasets/dev.spacy gold-multi-training/datasets/gold-multi-dev.spacy
```

- **Get access to the Ontonotes NER data in Conll-u format**
    - See Slack w. Kenneth - got message
    - Await answer from Stephan
    - https://github.com/ontonotes/conll-formatted-ontonotes-5.0/blob/master/conll-formatted-ontonotes-5.0/data/test/data/english/annotations/bn/cnn/01/cnn_0109.gold_skel
    - https://huggingface.co/datasets/tner/ontonotes5


- **Convert ontonotes to .spacy**
    - Using spacy's convert functionality
```bash
python src/preprocessing/get_ontonotes_spacy_format.py
#python -m spacy convert <inputfile> --converter conllu
```

- **Remove ents with language and product from Ontonotes (to match DANSK)**
```bash
python src/preprocessing/ontonotes_filter_tags.py
```

- **Merge ontonotes with gold-multi-train**
    - Both duplicating the gold-multi-train to have same weight, but also just with the original size
```bash
python gold-multi-training/datasets/merge_multi_ontonotes.py
```

- **Specify a config for the training**
    - Change config to basic settings with GPU, DA, from https://spacy.io/usage/training#quickstart
    - Add wandb for later tracking
    - Change to KennethEnevoldsen/dfm-bert-large-v1-2048bsz-1Msteps, which has highest performance, given scandeval.
    - Also maybe try: the google rembert model: https://huggingface.co/google/rembert (alternatively ROBERTA Base transformer model: en_core_web_trf)

- **Setup Ucloud for GPU-use**
    - Open UCloud instance ( https://cloud.sdu.dk/app/jobs/create?app=cuda-jupyter-ubuntu-aau&version=20.04 )
    - Clone this repo
    - Run below code
1. Open *https://cloud.sdu.dk/app/jobs/create?app=cuda-jupyter-ubuntu-aau&version=20.04*
2. Insert SSH-key *gold-multi-training/ucloud_setup/key_for_ucloud.txt*
3. In VSCODE, add new SSH under remote. Write the following but fill out UCloud instance IP: *ssh -i /Users/emiltrencknerjessen/Desktop/priv/DANSK-gold-NER/gold-multi-training/ucloud_setup/key_file <ucloud@xxx.xxx.xx.xxx>*
4. Add to first recommended
5. Reload remote
6. Connect in current window
7. Run below bash lines
```bash
git clone https://github.com/emiltj/DANSK-gold-NER.git
cd DANSK-gold-NER/gold-multi-training
bash ucloud_setup/server_dependencies.sh
cd DANSK-gold-NER/gold-multi-training
python3 -m venv ucloud_setup/environments/training
source ucloud_setup/environments/training/bin/activate
pip install numpy==1.23.3
pip install spacy
pip install wandb
pip install spacy-transformers
pip install torch
pip install spacy[cuda101]
wandb login
# insert API-key from https://wandb.ai/settings
#pip install -r "requirements_training.txt"
#pip install torch==1.8.1+cu101 -f https://download.pytorch.org/whl/torch_stable.html
```

- **Transfer data to UCLOUD**
    - Manual transfer of:
    - gold-multi-dev.spacy, onto_and_gold_multi_train.spacy, gold-multi-full.spacy, onto_and_gold_multi_train_dupli.spacy, gold-multi-train.spacy, ontonotes.spacy to ucloud in the folder "gold-multi-training/datasets"

- **Train 3 models on the gold-multi dataset (or on a combination of ontonotes also)**
    - Train it on UCLOUD (Ask Kenneth how to set up GPU)
    - Use the spacy -m train to train a new head for the transformer to NER on gold-multi and Ontonotes
    - Try different batch-sizes (see that it runs, then shut it down) -> the larger batch-size the better
```bash
python -m spacy train configs/config_gpu.cfg --paths.train datasets/gold-multi-train.spacy --paths.dev datasets/gold-multi-dev.spacy --output models/dansk-alone --gpu-id 0

python -m spacy train configs/config_gpu.cfg --paths.train datasets/onto_and_gold_multi_train.spacy --paths.dev datasets/gold-multi-dev.spacy --output models/dansk-and-onto --gpu-id 0

python -m spacy train configs/config_gpu.cfg --paths.train datasets/onto_and_gold_multi_train_dupli.spacy --paths.dev datasets/gold-multi-dev.spacy --output models/dansk-dupli-and-onto --gpu-id 0
```

- **Assess which model is best**
    - Manually go through these metrics
```bash
python -m spacy evaluate models/dansk-alone/model-best/ datasets/gold-multi-dev.spacy --output metrics/dansk-alone.json
python -m spacy evaluate models/dansk-and-onto/model-best/ datasets/gold-multi-dev.spacy --output metrics/dansk-and-onto.json
python -m spacy evaluate models/dansk-dupli-and-onto/model-best/ datasets/gold-multi-dev.spacy --output metrics/dansk-dupli-and-onto.json
```

- **Download best model to local**
    - Into same folder

- **Load single-unprocessed into database**
```bash 
cd DANSK-gold-ner
bash tools/raters_spacy_to_jsonl.sh -p single -d unprocessed # Convert the unprocessed single from .spacy to .jsonl
bash tools/raters_to_db.sh -p single -d unprocessed -o 0 # Add the unprocessed single data to the prodigy database
```

- **Use model to predict the rater with highest agreement with others**
    - Based on the script: src/data_assessment/interrater_reliability/interrater_reliability.ipynb
    - I chose rater 1
```bash
???
```

- **Resolve differences between rater 1 and first_best_model**
    - Save to data/single/gold/rater_1
```bash
prodigy review rater_1_single_gold rater_single_unprocessed_1,*MODEL_PREDICTIONS???*, --label PERSON,NORP,FACILITY,ORGANIZATION,LOCATION,EVENT,LAW,DATE,TIME,PERCENT,MONEY,QUANTITY,ORDINAL,CARDINAL,GPE -S -A
```

- **Add this data to a new training dataset**
```bash
prodigy db-in gold-multi-train_???maybe_ontoifitisbest?? gold-multi-training/datasets/onto_and_gold_multi_train.spacy
prodigy db-merge rater_1_single_gold,gold-multi-train_???maybe_ontoifitisbest? gold-multi-train-and-rater1_resolved
```

- **Train a new model**


- **Predict on the single data for each rater**
    - In a script, locally

- **Assess agreement between rater and model**
    - Make assessment fine-grained, and assess for each type of ent, in prodigy using the review recipe

- **Potentially. Make appropriate changes on gold-standard-multi data based on the assessment between rater and model**

- **Potentially. Re-train model on new gold-standard-multi data**

- **Potentially. Re-predict on single data for each rater**

- **Potentially. Re-assess agreement between rater and model**

- **Potentially. Repeat above process**

- **Manually resolve conflicts in single data (between model predictions and annotators)**
    - Save the gold-single dataset

- **Merge gold-single and gold-multi dataset into gold-dansk**

- **Save gold-dansk**

- **Save all gold-multi-ignored and gold-single-ignored (both prior to resolvement), in order for me to be able to get back to it at a later stage for the methods section.**

- **Gain access to Huggingface account centre-for-humanities-computing**

- **Train a NER model on the gold-dansk and package it**
    - Everything must be done on UCloud as packaging can't be done locally
    - Ensure that relevant information on Weights and Biases (wandb) is saved so I can use for report. 
    https://docs.wandb.ai/guides/integrations/spacy
    - Packaging to centre-for-humanities-computing


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

