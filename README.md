# DANSK-gold-NER

## Repository pipeline
- **Create folder structure for the data in the different stages**
```bash
bash tools/create_data_folders.sh
```

- **Download DANSK and place in data/**

- **Merge NER_annotator1 with NER_interannotator_annotator1 and remove duplicates**
    - Removing duplicates that matches on both 'meta' and on 'text' - only keep the last rated (from timestamp)
    - No removal of duplicates matching only on 'text'
    - Saves to data/prodigy_exports/prodigy1_db_exports/NER_merged_annotator1.jsonl
```bash
python src/preprocessing/merge_and_rm_dupli.py
```

- **Convert data to DocBins/.spacy files**
    - Saves to data/full/unprocessed/rater_1/train.spacy
```bash
bash tools/raters_to_db.sh -o 1 # Add DANSK to database
bash tools/raters_from_db_to_spacy.sh -o 1
#bash tools/rm_raters_from_db.sh -o 1
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
    - Very low agreement and number of annotations for LANGUAGE and PRODUCT. However, as we will add tags using a different model, this is okay, and we won't remove it.
```bash
#rm -r -f data/full/unprocessed/rater_2/* # Remove rater 2 # Just filtered away at the streamline_multi script
#rm -r -f data/full/unprocessed/rater_10/* # Remove rater 10 # Just filtered away at the streamline_multi script
python src/preprocessing/rater_8_fix.py # Fix rater 8 data
#python src/preprocessing/rm_product_and_language.py # Could remove PRODUCT and LANGUAGE tags.
```

- **Split data for each rater up into docs that have been rated by multiple raters, and into docs that have only been annotated by a single rater**
    - Split the unprocessed data up into multi and single folders, as they shall be handled in different steps
    - New files: 
        - data/multi/unprocessed/rater_1/train.spacy
        - data/single/unprocessed/rater_1/train.spacy
```bash
python src/preprocessing/split_full_to_single_multi.py
```

- **Have the single unprocessed and full unprocessed and multi_unprocessed not only as .spacy but also as jsonl**
    - New files:
        - data/single/unprocessed/rater_1/train.jsonl
```bash
bash tools/raters_spacy_to_jsonl.sh -p single -d unprocessed
bash tools/raters_spacy_to_jsonl.sh -p full -d unprocessed
bash tools/raters_spacy_to_jsonl.sh -p multi -d unprocessed
```

- **Add single_unprocessed and multi_unprocessed to db
```bash
bash tools/raters_to_db.sh -p multi -d unprocessed -o 0
bash tools/raters_to_db.sh -p single -d unprocessed -o 0
```

- **Investigate the distribution of the number of raters for the multi data**
    - Roughly 25% of multi docs have been rated by 2 raters
    - Roughly 25% of multi docs have been rated by 10 raters
    - Roughly 50% of multi docs have been rated by >2 and <10
    - Useful for knowing how to streamline docs.
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
```bash
bash tools/raters_spacy_to_jsonl.sh -p multi -d streamlined -o 0 # Convert the streamlined multi from .spacy to .jsonl
bash tools/raters_to_db.sh -p multi -d streamlined -o 0 # Add the streamlined data to the prodigy database
```

- **Manually resolve conflicts in the streamlined data**
    - "Ignoring" (prodigy no parking sign, button) cases with doubt, for later discussion.
    - "Rejecting" (prodigy cross, button) cases where the text is wrong. E.g. wrongly tokenized. (Aarhus2005)
    - When in doubt:
        - Use rules from resolved_edge_cases/resolved-edge-cases-multi.txt
            - These rules are self-written but stem from the annotation rules from the Ontonotes dataset
        - Use consensus from discussion with team Rebekah.
    - Save as 'gold-multi-all' in db
    - LANGUAGE and PRODUCT are included, although shitty
    - Cases with no conflicts are automatically accepted (-A)
```bash
prodigy review gold-multi-all rater_1_multi_streamlined,rater_3_multi_streamlined,rater_4_multi_streamlined,rater_5_multi_streamlined,rater_6_multi_streamlined,rater_7_multi_streamlined,rater_8_multi_streamlined,rater_9_multi_streamlined --label PERSON,NORP,FACILITY,ORGANIZATION,LOCATION,EVENT,LAW,DATE,TIME,PERCENT,MONEY,QUANTITY,ORDINAL,CARDINAL,GPE,WORK\ OF\ ART,LANGUAGE,PRODUCT -S -A
```

- **Export the gold-multi-ignored and the gold-multi-accepted and the rejected cases**
    - Creates new files: 
        ./data/multi/gold/gold-multi-rejected.jsonl
        ./data/multi/gold/gold-multi-ignored.jsonl
        ./data/multi/gold/gold-multi-accepted.jsonl
        ./data/multi/gold/gold-multi-all.jsonl
```bash
python src/preprocessing/split_by_answer_gold_multi.py # Retrieve all ignored and accepted instances. Loads them into db datasets 'gold-multi-accepted' and 'gold-multi-ignored' (also saves these as .jsonl to data/multi/gold)
```

- **Review the ignored cases after discussion with team**
```bash
prodigy mark gold-multi-ignored-resolved dataset:gold-multi-ignored --view-id review --label PERSON,NORP,FACILITY,ORGANIZATION,LOCATION,EVENT,LAW,DATE,TIME,PERCENT,MONEY,QUANTITY,ORDINAL,CARDINAL,GPE,WORK\ OF\ ART,LANGUAGE,PRODUCT
# If stream is empty due to gold-multi-ignored being empty, just skip.
```

- **Get a count of how many documents needs to be resolved manually, and how many are already identical across all raters**
    - Take the number "TOTAL" - this is the total number of texts that we have already been through (i.e. texts that were annotated identically
        - (789 texts)
    - Subtract this number from the total number of texts in the gold-multi-all (see full_len of gold-multi-all in script src/data_assessment/descriptive_stats.py)
        - (886 texts)
    - This gives:
        886-789 = 97 texts that were manually gone through
```bash
prodigy review test rater_1_multi_streamlined,rater_3_multi_streamlined,rater_4_multi_streamlined,rater_5_multi_streamlined,rater_6_multi_streamlined,rater_7ulti_streamlined,rater_8_multi_streamlined,rater_9_multi_streamlined --label PERSON,NORP,FACILITY,ORGANIZATION,LOCATION,EVENT,LAW,DATE,TIME,PERCENT,MONEY,QUANTITY,ORDINAL,CARDINAL,GPE,WORK\ OF\ ART,LANGUAGE,PRODUCT
prodigy drop test
```

- **Dump the gold-multi-ignored-resolved**
```bash
prodigy db-out gold-multi-ignored-resolved data/multi/gold
# If error, just skip. Just means that gold-multi-ignored was empty, and that gold-multi-ignored-resolved doesn't exist.
```

- **Write down the gold-multi-ignored-resolved cases**
    - Retrieve the ignored-resolved cases as text with annotations (using prodigy print-dataset)
    - Save retrieved ignored cases to resolved_edge_cases/gold-multi-ignored-resolved.txt
    - For EACH EXAMPLE, write notes on rules I used
```bash
prodigy print-dataset gold-multi-ignored-resolved
# If empty or error, just skip
```

- **Merge the gold-multi-ignored-resolved and the gold-multi-accepted**
```bash
prodigy db-merge gold-multi-accepted,gold-multi-ignored-resolved gold-multi
# If error, just run below code:
# prodigy db-merge gold-multi-accepted,gold-multi-ignored gold-multi
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
rm -rf gold-multi-training/datasets/labels
rm gold-multi-training/datasets/config.cfg
```

- **Get access to the Ontonotes NER data in Conll-u format**
    - Await answer from Stephan
    - https://github.com/ontonotes/conll-formatted-ontonotes-5.0/blob/master/conll-formatted-ontonotes-5.0/data/test/data/english/annotations/bn/cnn/01/cnn_0109.gold_skel
    - https://huggingface.co/datasets/tner/ontonotes5

- **Get access to Ontonotes and convert to .spacy**
    - Using spacy's convert functionality
    - Saves to :
        - "data/ontonotes/ontonotes.spacy" and 
        - "gold-multi-training/datasets/ontonotes.spacy"
```bash
python src/preprocessing/get_ontonotes_spacy_format.py
#python -m spacy convert <inputfile> --converter conllu
```

- **SKIPPED THIS STEP: Remove ents with language and product from Ontonotes (to match DANSK)**
```bash
#python src/preprocessing/ontonotes_filter_tags.py
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
pip install wheel==0.38.4 # no version works
pip install numpy==1.23.3
pip install spacy==3.5.0 # no version works
#pip install spacy-transformers # below version has dependency of transformers that matches the dependency of spacy-huggingface-hub
pip install spacy-transformers==1.1.2
pip install torch==1.13.1 # no version works
pip install spacy[cuda101] # no idea about version? but version from 30 Jan 2023 works
pip install huggingface==0.0.1 # no version works
pip install spacy-huggingface-hub==0.0.8 #no version works
pip install wandb==0.13.9 # no version works
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
cd gold-multi-training

source ucloud_setup/environments/training/bin/activate
#python -m spacy train configs/config_trf.cfg --paths.train datasets/gold-multi-train.spacy --paths.dev datasets/gold-multi-dev.spacy --output models/multi-alone --gpu-id 0
#python -m spacy train configs/config_trf.cfg --paths.train datasets/onto_and_gold_multi_train.spacy --paths.dev datasets/gold-multi-dev.spacy --output models/multi-and-onto --gpu-id 0
python -m spacy train configs/config_trf.cfg --paths.train datasets/onto_and_gold_multi_train_dupli.spacy --paths.dev datasets/gold-multi-dev.spacy --output models/multi-dupli-and-onto --gpu-id 0
```

- **Get metrics of performance**
    - Manually go through these metrics
```bash
#python -m spacy evaluate models/multi-alone/model-best/ datasets/gold-multi-dev.spacy --output metrics/multi-alone.json --gpu-id 0
#python -m spacy evaluate models/multi-and-onto/model-best/ datasets/gold-multi-dev.spacy --output metrics/multi-and-onto.json --gpu-id 0
python -m spacy evaluate models/multi-dupli-and-onto/model-best/ datasets/gold-multi-dev.spacy --output metrics/multi-dupli-and-onto.json --gpu-id 0
```

- **Assess which model is best, using wandb and metrics of performance from spacy evaluate**
    - https://wandb.ai/emil-tj/gold-multi-train
    - Model chosen was multi-dupli-onto

- **Change meta.json to an appropriate name for pipeline MUST NOT CONTAIN -**
    - e.g. multi_dupli_onto_xlm_roberta_large

- **Package best model**
```bash
huggingface-cli login
# insert token (WRITE) from https://huggingface.co/settings/tokens

# python -m spacy package models/multi-alone/model-best/ packages/multi-alone --build wheel
# python -m spacy package models/multi-and-onto/model-best/ packages/multi-and-onto --build wheel
python -m spacy package models/multi-dupli-and-onto/model-best/ packages/multi-dupli-and-onto --build wheel
```

- **Push package to huggingfacehub**
    - https://huggingface.co/blog/spacy
```bash
python -m spacy huggingface-hub push packages/multi-dupli-and-onto/da_multi_dupli_onto_xlm_roberta_large-0.0.0/dist/da_multi_dupli_onto_xlm_roberta_large-0.0.0-py3-none-any.whl
```

- **Download package of best model to local**
```bash
huggingface-cli login
# insert token (READ) from https://huggingface.co/settings/tokens
pip install https://huggingface.co/emiltj/da_multi_dupli_onto_xlm_roberta_large/resolve/main/da_multi_dupli_onto_xlm_roberta_large-any-py3-none-any.whl
```

- **Use model to predict the rater with highest agreement with others**
    - Based on the script: src/data_assessment/interrater_reliability/interrater_reliability.ipynb
    - I chose rater 1
```bash
python src/predict_single/predict_rater_1
```

- **Convert the predicted ratings into .jsonl to have both formats and add to db**
```bash
python src/preprocessing/load_docbin_as_jsonl.py data/single/unprocessed/rater_1/rater_1_preds.spacy blank:da --ner > data/single/unprocessed/rater_1/rater_1_preds.jsonl
prodigy db-in rater_1_single_unprocessed_preds data/single/unprocessed/rater_1/rater_1_preds.jsonl
```

- **Resolve differences between rater 1 and first_best_model**
    - "Ignoring" (prodigy no parking sign, button) cases with doubt, for later discussion.
    - "Rejecting" (prodigy cross, button) cases where the text is wrong. E.g. wrongly tokenized. (Aarhus2005)
    - When in doubt:
        - Use rules from resolved_edge_cases/resolved-edge-cases-multi.txt
            - These rules are self-written but stem from the annotation rules from the Ontonotes dataset
        - Use consensus from discussion with team Rebekah.
    - Save as '' in db
    - LANGUAGE and PRODUCT are included, although shitty
    - Cases with no conflicts are automatically accepted (-A)
```bash
prodigy review rater_1_single_gold_all rater_1_single_unprocessed,rater_1_single_unprocessed_preds --label PERSON,NORP,FACILITY,ORGANIZATION,LOCATION,EVENT,LAW,DATE,TIME,PERCENT,MONEY,QUANTITY,ORDINAL,CARDINAL,GPE,WORK\ OF\ ART,LANGUAGE,PRODUCT -S -A
```

- **Get a count of how many documents needs to be resolved manually, and how many are already identical across model and rater**
    - Take the number "TOTAL" - this is the total number of texts that we have already been through (i.e. texts that were annotated identically)
        - (789 texts)
    - Subtract this number from the total number of texts in the rater_1_single_unprocessed (see full_len of rater_1_single_unprocessed in script src/data_assessment/descriptive_stats.py)
        - (1412 texts)
    This gives:
        1412-789 = 623 texts that were manually gone through
```bash
prodigy review test rater_1_single_unprocessed,rater_1_single_unprocessed_preds --label PERSON,NORP,FACILITY,ORGANIZATION,LOCATION,EVENT,LAW,DATE,TIME,PERCENT,MONEY,QUANTITY,ORDINAL,CARDINAL,GPE,WORK\ OF\ ART,LANGUAGE,PRODUCT
prodigy drop test
```

- **Export the rater_1_single_gold_ignored and the rater_1_single_gold_accepted cases**
    - Creates files:
        ./data/single/gold/rater_1/gold_rejected.jsonl
        ./data/single/gold/rater_1/gold_accepted.jsonl
        ./data/single/gold/rater_1/gold_ignored.jsonl
        ./data/single/gold/rater_1/gold_all.jsonl
```bash
python src/preprocessing/split_by_answer_rater_1_single_gold.py.py # Retrieve all ignored and accepted instances. Loads them into db datasets 'gold-multi-accepted' and 'gold-multi-ignored' (also saves these as .jsonl to data/multi/gold)
```

# GOTTEN TO HERE(!)

# Before progressing: Split rater_1_single_gold_all into rejected, ignored and accepted. AND THEN GO THROUGH rater_1_single_gold_accepted, using maybe "MARK". Accept all the time, untill I reach the things about camper vans. Then start rejecting bad examples. Then progress


- **Review the ignored cases after discussion with team**
```bash
prodigy mark rater_1_single_gold_ignored_resolved dataset:rater_1_single_gold_ignored --view-id review --label PERSON,NORP,FACILITY,ORGANIZATION,LOCATION,EVENT,LAW,DATE,TIME,PERCENT,MONEY,QUANTITY,ORDINAL,CARDINAL,GPE,WORK\ OF\ ART,LANGUAGE,PRODUCT -S -A
```

- **Dump the rater_1_single_gold_ignored_resolved**
```bash
prodigy db-out rater_1_single_gold_ignored_resolved data/single/gold/rater_1
```

- **Merge the rater_1_single_gold_ignored_resolved and the rater_1_single_gold_accepted into rater_1_single_gold**
```bash
prodigy db-merge rater_1_single_gold_accepted,rater_1_single_gold_ignored_resolved rater_1_single_gold
```

- **Merge rater_1_single_gold and gold-multi and write as files (both .json and .spacy)**
```bash
prodigy db-merge rater_1_single_gold,gold-multi gold-multi-and-gold-rater-1-single
prodigy data-to-spacy data/multi/gold/ --ner gold-multi-and-gold-rater-1-single --lang "da" --eval-split 0
mv data/multi/gold/train.spacy mv data/multi/gold/gold-multi-and-gold-rater-1-single.spacy
rm -rf labels
prodigy db-out gold-multi-and-gold-rater-1-single data/multi/gold/gold-multi-and-gold-rater-1-single.jsonl
```














# Below steps have not been written out yet

- **Use a model to add extra labels with Product and Language**
    - Using a multi-lingual model (XLM-ROBERTA-LARGE)
    - Is it possible to increase sensitivity? At the cost of specificity
```bash
# Consider using https://github.com/KennethEnevoldsen/spacy-wrap
# Add a new python script that predicts on the texts of the docs of gold-multi-and-gold-rater-1-single.
# Subset the new docs to only include those that include at least 1 ent
# Add the subset to the db
# Use prodigy review on the subset of texts and gold-multi-and-gold-rater-1-single
# Resolve conflicts
```

- **Train a new model**
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
pip install wheel==0.38.4 # no version works
pip install numpy==1.23.3
pip install spacy==3.5.0 # no version works
#pip install spacy-transformers # below version has dependency of transformers that matches the dependency of spacy-huggingface-hub
pip install spacy-transformers==1.1.2
pip install torch==1.13.1 # no version works
pip install spacy[cuda101] # no idea about version? but version from 30 Jan 2023 works
pip install huggingface==0.0.1 # no version works
pip install spacy-huggingface-hub==0.0.8 #no version works
pip install wandb==0.13.9 # no version works
wandb login
# insert API-key from https://wandb.ai/settings

# Manually transfer data/multi/gold/gold-multi-and-gold-rater-1-single.spacy to datasets/

python -m spacy train configs/config_trf.cfg --paths.train datasets/gold-multi-and-gold-rater-1-single.spacy --paths.dev datasets/gold-multi-dev.spacy --output models/multi-dupli-and-rater1-and-onto --gpu-id 0

# Change meta.json to an appropriate name for pipeline. NOTE USE UNDERSCORES AND NOT - AS THIS MAKES IT CRASH

python -m spacy package models/multi-dupli-and-rater1-and-onto/model-best/ packages/multi-dupli-and-rater1-and-onto --build wheel

huggingface-cli login
# insert token (WRITE) from https://huggingface.co/settings/tokens
python -m spacy huggingface-hub push multi-dupli-and-rater1-and-onto-0.0.0-py3-none-any.whl
```

- **Predict on the single data for each rater**
    - In a script, locally
```bash
# Move to local and run below
huggingface-cli login
# insert token (READ) from https://huggingface.co/settings/tokens
python -m spacy huggingface-hub push multi-dupli-and-rater1-and-onto-0.0.0-py3-none-any.whl
```

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

- **Review any potential extra processing of the tags and/or texts**
    - Go through the documents in "resolved edge cases"
```bash
code resolved_edge_cases/other_thoughts.txt
```

- **Save gold-dansk**

- **Save all gold-multi-ignored and gold-single-ignored (both prior to resolvement), in order for me to be able to get back to it at a later stage for the methods section.**

- **Gain access to Huggingface account centre-for-humanities-computing**

- **Train a NER model on the gold-dansk and package it**
    - Everything must be done on UCloud as packaging can't be done locally
    - Ensure that relevant information on Weights and Biases (wandb) is saved so I can use for report. 
    https://docs.wandb.ai/guides/integrations/spacy
    - Packaging to centre-for-humanities-computing

- **Nice to do, not need to do, depends also on performance**
    - Fix bad labeling in the dataset (Ask Kenneth, he very briefly mentioned below methods)
    - Do it using one of the following approaches:
        - Using Spancategorizer
        - Use the model to predict on parts of the DANSK dataset. And then go through these faulty classifications and see whether the classification is wrong, or whether the labeling is wrong. Go through the wrong labeling and fix it. Iterate this processUse the models' wrong predictions


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

