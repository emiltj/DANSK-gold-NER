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
bash tools/raters_spacy_to_jsonl.sh -p multi -d streamlined # Convert the streamlined multi from .spacy to .jsonl
bash tools/raters_to_db.sh -p multi -d streamlined -o 0 # Add the streamlined data to the prodigy database
```

- **Manually resolve conflicts in the streamlined data**
    - Resolvement is based off of the data/ontonotes/ontonotes-named-entity-guidelines-v14.pdf guidelines.
    - "Ignoring" (prodigy no parking sign, button) cases with doubt, for later discussion.
    - "Rejecting" (prodigy cross, button) cases where the text is wrong. E.g. wrongly tokenized. (Aarhus2005)
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
prodigy review test rater_1_multi_streamlined,rater_3_multi_streamlined,rater_4_multi_streamlined,rater_5_multi_streamlined,rater_6_multi_streamlined,rater_7_multi_streamlined,rater_8_multi_streamlined,rater_9_multi_streamlined --label PERSON,NORP,FACILITY,ORGANIZATION,LOCATION,EVENT,LAW,DATE,TIME,PERCENT,MONEY,QUANTITY,ORDINAL,CARDINAL,GPE,WORK\ OF\ ART,LANGUAGE,PRODUCT
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

- **Add Language and Product predictions on the gold-multi dataset**
    - Use tner/roberta-large-ontonotes5
    - Only adds one, wrong label. So I'll skip it
    - Perhaps to make sense to mention in methods, regardless
```bash
#gold-multi-training/datasets/lang_product_predict_gold_multi.py
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
    - This link has the Ontonotes in conll format, but needs to be converted to .spacy 
        - https://data.mendeley.com/datasets/zmycy7t9h9/2
    - These two links are previous things I tried out. The first is dehydrated, and the second does not include all texts (and does not hold information on whitespacing for the sentences)
        - https://github.com/ontonotes/conll-formatted-ontonotes-5.0/blob/master/conll-formatted-ontonotes-5.0/data/test/data/english/annotations/bn/cnn/01/cnn_0109.gold_skel
        - https://huggingface.co/datasets/tner/ontonotes5

- **Get access to Ontonotes and convert to .spacy and .jsonl**
    - Using spacy's convert functionality
    - Saves to :
        - "data/ontonotes/ontonotes.spacy" and 
        - "gold-multi-training/datasets/ontonotes.spacy"
```bash
python src/preprocessing/get_ontonotes_spacy_format.py
python ./src/preprocessing/load_docbin_as_jsonl.py data/ontonotes/ontonotes.spacy blank:da --ner > data/ontonotes/ontonotes.jsonl
#python -m spacy convert <inputfile> --converter conllu
```

- **SKIPPED THIS STEP: Remove ents with language and product from Ontonotes (to match DANSK)**
```bash
#python src/preprocessing/ontonotes_filter_tags.py
```

- **Merge ontonotes with gold-multi-train**
    - Both duplicating the gold-multi-train to have same weight, but also just with the original size
    - Creates:
        - onto_and_gold_multi_train.spacy
        - onto_and_gold_multi_train_dupli.spacy
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
    - Save to local under "metrics"
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
    - Creates "data/single/unprocessed/rater_1/rater_1_preds.spacy"
```bash
python src/predict_single/predict_rater_1
```

- **Convert the predicted ratings into .jsonl to have both formats and add to db**
    - Creates data/single/unprocessed/rater_1/rater_1_preds.jsonl
    - and 
    - data/single/unprocessed/rater_1/train.jsonl
```bash
python src/preprocessing/load_docbin_as_jsonl.py data/single/unprocessed/rater_1/rater_1_preds.spacy blank:da --ner > data/single/unprocessed/rater_1/rater_1_preds.jsonl
prodigy db-in rater_1_single_unprocessed_preds data/single/unprocessed/rater_1/rater_1_preds.jsonl
```

- **Resolve differences between rater 1 and first_best_model**
    - "Ignoring" (prodigy no parking sign, button) cases with doubt, for later discussion.
    - "Rejecting" (prodigy cross, button) cases where the text is wrong. E.g. wrongly tokenized. (Aarhus2005)
    - Using data/ontonotes/ontonotes-named-entity-guidelines-v14.pdf for guidelines
    
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
    - Take the number "TOTAL" - this is the total number of texts that we have already been through (i.e. texts that were annotated already as they were identical between machine and human rater)
        - (759 texts)
    - Subtract this number from the total number of texts in the rater_1_single_unprocessed (see full_len of rater_1_single_unprocessed in script src/data_assessment/descriptive_stats.py)
        - (1412 texts)
    This gives:
        1412-759 = 653 texts that were manually gone through
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
python src/preprocessing/split_by_answer_rater_1_single_gold.py # Retrieve all ignored and accepted instances. Loads them into db datasets 'gold-multi-accepted' and 'gold-multi-ignored' (also saves these as .jsonl to data/multi/gold)
```

- **Review the ignored cases after discussion with team**
```bash
prodigy mark rater_1_single_gold_ignored_resolved dataset:rater_1_single_gold_ignored --view-id review --label PERSON,NORP,FACILITY,ORGANIZATION,LOCATION,EVENT,LAW,DATE,TIME,PERCENT,MONEY,QUANTITY,ORDINAL,CARDINAL,GPE,WORK\ OF\ ART,LANGUAGE,PRODUCT
```
- **Dump the rater_1_single_gold_ignored_resolved**
```bash
prodigy db-out rater_1_single_gold_ignored_resolved data/single/gold/rater_1
```

- **Merge the rater_1_single_gold_ignored_resolved and the rater_1_single_gold_accepted into rater_1_single_gold**
```bash
prodigy db-merge rater_1_single_gold_accepted,rater_1_single_gold_ignored_resolved rater_1_single_gold
```

- **Get count of rejected vs accepted for rater_1_single_gold**
    - Out of 1412 text, 12 were ignored for later review and 42 were rejected
    - Out of the ignored 12, 1 was rejected and 11 were accepted
    - Total:
        - Accepted: 1370
        - Rejected: 43
```bash
python src/data_assessment/descriptive_stats.py
```

- **Merge rater_1_single_gold and gold-multi and write as files (both .json and .spacy)**
    - Creates in folders:
        - data/multi/gold/gold-multi-and-gold-rater-1-single-ner-manual.jsonl
        - data/multi/gold/gold-multi-and-gold-rater-1-single.jsonl
        - data/multi/gold/gold-multi-and-gold-rater-1-single.spacy

    - Creates in db
        - gold-multi-and-gold-rater-1-single
        - gold-multi-and-gold-rater-1-single-ner-manual
```bash
prodigy db-merge rater_1_single_gold,gold-multi gold-multi-and-gold-rater-1-single
prodigy data-to-spacy data/multi/gold/ --ner gold-multi-and-gold-rater-1-single --lang "da" --eval-split 0
mv data/multi/gold/train.spacy data/multi/gold/gold-multi-and-gold-rater-1-single.spacy
rm -rf data/multi/gold/labels
rm -rf data/multi/gold/output
rm data/multi/gold/config.cfg
prodigy db-out gold-multi-and-gold-rater-1-single data/multi/gold/gold-multi-and-gold-rater-1-single
mv data/multi/gold/gold-multi-and-gold-rater-1-single/gold-multi-and-gold-rater-1-single.jsonl data/multi/gold/gold-multi-and-gold-rater-1-single.jsonl
python src/preprocessing/review_to_ner_manual_for_jsonl.py gold-multi-and-gold-rater-1-single data/multi/gold/gold-multi-and-gold-rater-1-single-ner-manual.jsonl
prodigy db-in gold-multi-and-gold-rater-1-single-ner-manual data/multi/gold/gold-multi-and-gold-rater-1-single-ner-manual.jsonl
rm -r data/multi/gold/gold-multi-and-gold-rater-1-single
```

- **Make Language and Product predictions on the gold-multi-rater-1**
    - Predict on entire dataset using tner/roberta-large-ontonotes5
    - Keep only docs with ents LANGUAGE and/or PRODUCT
    - Remove all other ents apart from LANGUAGE and product
    - Saves in folders:
                - data/multi/gold/gold-multi-and-gold-rater-1-single-preds-lang-prod.spacy
        - data/multi/gold/gold-multi-and-gold-rater-1-single-preds-lang-prod.jsonl
        - data/multi/gold/gold-multi-and-gold-rater-1-single-preds-lang-prod-ner-manual.jsonl
    - Saves in db:
        - gold-multi-and-gold-rater-1-single-preds-lang-prod-ner-manual
```bash
python gold-multi-training/datasets/lang_product_predict_gold_multi_rater_1.py
python src/preprocessing/load_docbin_as_jsonl.py data/multi/gold/gold-multi-and-gold-rater-1-single-preds-lang-prod.spacy blank:da --ner > data/multi/gold/gold-multi-and-gold-rater-1-single-preds-lang-prod.jsonl # add as jsonl also
prodigy db-in gold-multi-and-gold-rater-1-single-preds-lang-prod data/multi/gold/gold-multi-and-gold-rater-1-single-preds-lang-prod.jsonl
python src/preprocessing/review_to_ner_manual_for_jsonl.py gold-multi-and-gold-rater-1-single-preds-lang-prod data/multi/gold/gold-multi-and-gold-rater-1-single-preds-lang-prod-ner-manual.jsonl
prodigy db-in gold-multi-and-gold-rater-1-single-preds-lang-prod-ner-manual data/multi/gold/gold-multi-and-gold-rater-1-single-preds-lang-prod-ner-manual.jsonl
```

- **Review the gold-multi-and-gold-rater-1-single and the gold-multi-and-gold-rater-1-single-preds-lang-prod**
    - 38 were added
    - 35 were gone through manually using the review (the remaining 6 were identical to the gold-multi-and-golder-rater-1-single texts)
```bash
prodigy review test gold-multi-and-gold-rater-1-single-preds-lang-prod-ner-manual,gold-multi-and-gold-rater-1-single-ner-manual --label PERSON,NORP,FACILITY,ORGANIZATION,LOCATION,EVENT,LAW,DATE,TIME,PERCENT,MONEY,QUANTITY,ORDINAL,CARDINAL,GPE,WORK\ OF\ ART,LANGUAGE,PRODUCT -S -A
prodigy review gold-multi-and-gold-rater-1-single-extra-lang-prod gold-multi-and-gold-rater-1-single-preds-lang-prod-ner-manual,gold-multi-and-gold-rater-1-single-ner-manual --label PERSON,NORP,FACILITY,ORGANIZATION,LOCATION,EVENT,LAW,DATE,TIME,PERCENT,MONEY,QUANTITY,ORDINAL,CARDINAL,GPE,WORK\ OF\ ART,LANGUAGE,PRODUCT -S -A
```

- **The reviewed is saved as a file**
    - Creates:
        - gold-multi-and-gold-rater-1-single-extra-lang-prod.jsonl
        - gold-multi-and-gold-rater-1-single-extra-lang-prod.spacy
```bash
prodigy db-out gold-multi-and-gold-rater-1-single-extra-lang-prod data/multi/gold/gold-multi-and-gold-rater-1-single-extra-lang-prod
mv data/multi/gold/gold-multi-and-gold-rater-1-single-extra-lang-prod/gold-multi-and-gold-rater-1-single-extra-lang-prod.jsonl data/multi/gold/gold-multi-and-gold-rater-1-single-extra-lang-prod.jsonl
rm -r data/multi/gold/gold-multi-and-gold-rater-1-single-extra-lang-prod
prodigy data-to-spacy data/multi/gold/ --ner gold-multi-and-gold-rater-1-single-extra-lang-prod --lang "da" --eval-split 0
mv data/multi/gold/train.spacy data/multi/gold/gold-multi-and-gold-rater-1-single-extra-lang-prod.spacy  
rm -rf data/multi/gold/labels
rm -rf data/multi/gold/config.cfg
```

- **Overwrite the texts from gold-multi-and-gold-rater-1-single-extra-lang-prod.jsonl into gold-multi-and-gold-rater-1-single-ner-manual**
    - Creates in folder:
        - data/multi/gold/gold-multi-rater-1.jsonl
        - data/multi/gold/gold-multi-rater-1.spacy
        - gold-multi-training/datasets/gold-multi-rater-1/gold-multi-rater-1-full.spacy
    - Creates in db:
        - gold-multi-rater-1
```bash
python src/preprocessing/overwrite.py
prodigy db-in gold-multi-rater-1 data/multi/gold/gold-multi-rater-1.jsonl
prodigy data-to-spacy data/multi/gold/ --ner gold-multi-rater-1 --lang "da" --eval-split 0
cp data/multi/gold/train.spacy gold-multi-training/datasets/gold-multi-rater-1/gold-multi-rater-1-full.spacy
mv data/multi/gold/train.spacy data/multi/gold/gold-multi-rater-1.spacy
rm -rf data/multi/gold/labels
rm -rf data/multi/gold/config.cfg
prodigy data-to-spacy gold-multi-training/datasets/gold-multi-rater-1/ --ner gold-multi-rater-1 --lang "da" --eval-split 0.2
mv gold-multi-training/datasets/gold-multi-rater-1/train.spacy gold-multi-training/datasets/gold-multi-rater-1/gold-multi-rater-1-train.spacy
mv gold-multi-training/datasets/gold-multi-rater-1/dev.spacy gold-multi-training/datasets/gold-multi-rater-1/gold-multi-rater-1-dev.spacy
rm -rf gold-multi-training/datasets/gold-multi-rater-1/labels
rm -rf gold-multi-training/datasets/gold-multi-rater-1/config.cfg
```

- **Create a few different training sets, merging from ontonotes**
    - Creates:
        - onto_and_gold_multi_rater_1_train_dupli.spacy
        - onto_and_gold_multi_rater_1_train.spacy
```bash
python datasets/gold-multi-rater-1/merge_multi_ontonotes.py
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

# Manually transfer gold-multi-training/datasets to gold-multi-training/datasets
gold-multi-training/datasets/gold-multi-rater-1/onto_and_gold_multi_rater_1_train_dupli.spacy
python -m spacy train configs/config_trf.cfg --paths.train datasets/gold-multi-rater-1/onto_and_gold_multi_rater_1_train_dupli.spacy --paths.dev datasets/gold-multi-rater-1/gold-multi-rater-1-dev.spacy --output models/multi-dupli-rater_1-onto --gpu-id 0

python -m spacy evaluate models/multi-dupli-rater_1-onto/model-best/ datasets/gold-multi-rater-1/gold-multi-rater-1-dev.spacy --output metrics/multi-dupli-rater_1-onto.json --gpu-id 0

# Manually transfer gold-multi-training/metrics/multi-dupli-rater_1-onto.json to local

# Change meta.json to an appropriate name for pipeline. NOTE USE UNDERSCORES AND NOT - AS THIS MAKES IT CRASH
# e.g. multi_dupli_rater_1_onto

python -m spacy package models/multi-dupli-rater_1-onto/model-best/ packages/multi-dupli-rater-1-onto --build wheel

huggingface-cli login
# insert token (WRITE) from https://huggingface.co/settings/tokens
python -m spacy huggingface-hub push packages/multi-dupli-rater-1-onto/da_multi_dupli_rater_1_onto-0.0.0/dist/da_multi_dupli_rater_1_onto-0.0.0-py3-none-any.whl

# This creates https://huggingface.co/emiltj/da_multi_dupli_rater_1_onto
```

- **Pip install new model on local**
```bash
pip install https://huggingface.co/emiltj/da_multi_dupli_rater_1_onto/resolve/main/da_multi_dupli_rater_1_onto-any-py3-none-any.whl
```

- **Predict on the single data for each rater**
    - In a script, locally
```bash
python src/predict_single/predict_rater_2-9.py
```

- **Assess agreement between rater and model**
    - Make assessment fine-grained, and assess for each type of ent, in prodigy using the review recipe
    For rater 3:
    Cases where ents are same between predicted and model: 638
    Cases where ents are NOT same between preds and model: 888
    For rater 4:
    Cases where ents are same between predicted and model: 1114
    Cases where ents are NOT same between preds and model: 1363
    For rater 5:
    Cases where ents are same between predicted and model: 422
    Cases where ents are NOT same between preds and model: 980
    For rater 6:
    Cases where ents are same between predicted and model: 1046
    Cases where ents are NOT same between preds and model: 1213
    For rater 7:
    Cases where ents are same between predicted and model: 754
    Cases where ents are NOT same between preds and model: 1148
    For rater 8:
    Cases where ents are same between predicted and model: 622
    Cases where ents are NOT same between preds and model: 1076
    For rater 9:
    Cases where ents are same between predicted and model: 906
    Cases where ents are NOT same between preds and model: 1203
    Total cases where ents are same 5502
    Total cases where ents are NOT same 7871
```bash
# Go through script manually:
# src/data_assessment/model_and_raters_agreement.ipynb
```

- **Add predictions to db**
    - Creates in db:
        - rater_"$i"_single_unprocessed_preds
    - Creates in folders:
        - ./data/single/unprocessed/rater_$i/rater_"$i"_preds.jsonl
```bash
# tools/raters_preds_to_db.sh
prodigy drop rater_2_single_unprocessed_preds
prodigy drop rater_10_single_unprocessed_preds
```



- **Review raters 3, 4, 5, 6, 7, 8, 9**
```bash
prodigy review rater_3_single_gold_all rater_3_single_unprocessed,rater_3_single_unprocessed_preds --label PERSON,NORP,FACILITY,ORGANIZATION,LOCATION,EVENT,LAW,DATE,TIME,PERCENT,MONEY,QUANTITY,ORDINAL,CARDINAL,GPE,WORK\ OF\ ART,LANGUAGE,PRODUCT -S -A

prodigy review rater_4_single_gold_all rater_4_single_unprocessed,rater_4_single_unprocessed_preds --label PERSON,NORP,FACILITY,ORGANIZATION,LOCATION,EVENT,LAW,DATE,TIME,PERCENT,MONEY,QUANTITY,ORDINAL,CARDINAL,GPE,WORK\ OF\ ART,LANGUAGE,PRODUCT -S -A

prodigy review rater_5_single_gold_all rater_5_single_unprocessed,rater_5_single_unprocessed_preds --label PERSON,NORP,FACILITY,ORGANIZATION,LOCATION,EVENT,LAW,DATE,TIME,PERCENT,MONEY,QUANTITY,ORDINAL,CARDINAL,GPE,WORK\ OF\ ART,LANGUAGE,PRODUCT -S -A

prodigy review rater_6_single_gold_all rater_6_single_unprocessed,rater_6_single_unprocessed_preds --label PERSON,NORP,FACILITY,ORGANIZATION,LOCATION,EVENT,LAW,DATE,TIME,PERCENT,MONEY,QUANTITY,ORDINAL,CARDINAL,GPE,WORK\ OF\ ART,LANGUAGE,PRODUCT -S -A

prodigy review rater_7_single_gold_all rater_7_single_unprocessed,rater_7_single_unprocessed_preds --label PERSON,NORP,FACILITY,ORGANIZATION,LOCATION,EVENT,LAW,DATE,TIME,PERCENT,MONEY,QUANTITY,ORDINAL,CARDINAL,GPE,WORK\ OF\ ART,LANGUAGE,PRODUCT -S -A

prodigy review rater_8_single_gold_all rater_8_single_unprocessed,rater_8_single_unprocessed_preds --label PERSON,NORP,FACILITY,ORGANIZATION,LOCATION,EVENT,LAW,DATE,TIME,PERCENT,MONEY,QUANTITY,ORDINAL,CARDINAL,GPE,WORK\ OF\ ART,LANGUAGE,PRODUCT -S -A

prodigy review rater_9_single_gold_all rater_9_single_unprocessed,rater_9_single_unprocessed_preds --label PERSON,NORP,FACILITY,ORGANIZATION,LOCATION,EVENT,LAW,DATE,TIME,PERCENT,MONEY,QUANTITY,ORDINAL,CARDINAL,GPE,WORK\ OF\ ART,LANGUAGE,PRODUCT -S -A
```

- **Save all reviewed data**
    - Creates files:
        - data/single/gold/rater_{r}/rater_{r}_single_gold_all.jsonl
```bash
prodigy db-out rater_3_single_gold_all data/single/gold/rater_3
prodigy db-out rater_4_single_gold_all data/single/gold/rater_4
prodigy db-out rater_5_single_gold_all data/single/gold/rater_5
prodigy db-out rater_6_single_gold_all data/single/gold/rater_6
prodigy db-out rater_7_single_gold_all data/single/gold/rater_7
prodigy db-out rater_8_single_gold_all data/single/gold/rater_8
prodigy db-out rater_9_single_gold_all data/single/gold/rater_9
```

- **Merge all the reviewed rater data**
    - Creates in DB:
        - single-gold-all
        - single-gold-accept
        - single-gold-reject
        - single-gold-ignore
    Creates in folders:
        - data/single/gold/combined/single-gold-all.jsonl
        - data/single/gold/combined/single-gold-accept.jsonl
        - data/single/gold/combined/single-gold-reject.jsonl
        - data/single/gold/combined/single-gold-ignore.jsonl
```bash
prodigy db-merge rater_3_single_gold_all,rater_4_single_gold_all,rater_5_single_gold_all,rater_6_single_gold_all,rater_7_single_gold_all,rater_8_single_gold_all,rater_9_single_gold_all single-gold-all
python src/preprocessing/single-gold-split.py
prodigy db-out single-gold-all data/single/gold/combined/
prodigy db-out single-gold-accept data/single/gold/combined/
prodigy db-out single-gold-reject data/single/gold/combined/
prodigy db-out single-gold-ignore data/single/gold/combined/
```

- **Get info on number of accepted and rejected**
    - Retrieved info:
        {'name': 'rater_3_single_gold_all', 'full_len': 1526, 'accept_len': 1440, 'reject_len': 86, 'ignore_len': 0}
        {'name': 'rater_4_single_gold_all', 'full_len': 2477, 'accept_len': 2380, 'reject_len': 97, 'ignore_len': 0}
        {'name': 'rater_5_single_gold_all', 'full_len': 1402, 'accept_len': 1379, 'reject_len': 23, 'ignore_len': 0}
        {'name': 'rater_6_single_gold_all', 'full_len': 2259, 'accept_len': 2144, 'reject_len': 115, 'ignore_len': 0}
        {'name': 'rater_7_single_gold_all', 'full_len': 1902, 'accept_len': 1823, 'reject_len': 79, 'ignore_len': 0}
        {'name': 'rater_8_single_gold_all', 'full_len': 1698, 'accept_len': 1632, 'reject_len': 66, 'ignore_len': 0}
        {'name': 'rater_9_single_gold_all', 'full_len': 2109, 'accept_len': 2011, 'reject_len': 98, 'ignore_len': 0}
        {'name': 'single-gold', 'full_len': 13373, 'accept_len': 12809, 'reject_len': 564, 'ignore_len': 0}
```bash
src/data_assessment/descriptive_stats.py
```

- **Resolve ignored cases in rater_{r}_single_gold_ignored**
    - Creates in db:
        - rater_{r}_single_gold_ignored_resolved
```bash
#None prodigy mark rater_3_single_gold_ignored_resolved dataset:rater_3_single_gold_ignored --view-id review --label PERSON,NORP,FACILITY,ORGANIZATION,LOCATION,EVENT,LAW,DATE,TIME,PERCENT,MONEY,QUANTITY,ORDINAL,CARDINAL,GPE,WORK\ OF\ ART,LANGUAGE,PRODUCT

#None prodigy mark rater_4_single_gold_ignored_resolved dataset:rater_4_single_gold_ignored --view-id review --label PERSON,NORP,FACILITY,ORGANIZATION,LOCATION,EVENT,LAW,DATE,TIME,PERCENT,MONEY,QUANTITY,ORDINAL,CARDINAL,GPE,WORK\ OF\ ART,LANGUAGE,PRODUCT

#None for the rest
# prodigy mark rater_5_single_gold_ignored_resolved dataset:rater_5_single_gold_ignored --view-id review --label PERSON,NORP,FACILITY,ORGANIZATION,LOCATION,EVENT,LAW,DATE,TIME,PERCENT,MONEY,QUANTITY,ORDINAL,CARDINAL,GPE,WORK\ OF\ ART,LANGUAGE,PRODUCT

# prodigy mark rater_6_single_gold_ignored_resolved dataset:rater_6_single_gold_ignored --view-id review --label PERSON,NORP,FACILITY,ORGANIZATION,LOCATION,EVENT,LAW,DATE,TIME,PERCENT,MONEY,QUANTITY,ORDINAL,CARDINAL,GPE,WORK\ OF\ ART,LANGUAGE,PRODUCT

# prodigy mark rater_7_single_gold_ignored_resolved dataset:rater_7_single_gold_ignored --view-id review --label PERSON,NORP,FACILITY,ORGANIZATION,LOCATION,EVENT,LAW,DATE,TIME,PERCENT,MONEY,QUANTITY,ORDINAL,CARDINAL,GPE,WORK\ OF\ ART,LANGUAGE,PRODUCT

# prodigy mark rater_8_single_gold_ignored_resolved dataset:rater_8_single_gold_ignored --view-id review --label PERSON,NORP,FACILITY,ORGANIZATION,LOCATION,EVENT,LAW,DATE,TIME,PERCENT,MONEY,QUANTITY,ORDINAL,CARDINAL,GPE,WORK\ OF\ ART,LANGUAGE,PRODUCT

# prodigy mark rater_9_single_gold_ignored_resolved dataset:rater_9_single_gold_ignored --view-id review --label PERSON,NORP,FACILITY,ORGANIZATION,LOCATION,EVENT,LAW,DATE,TIME,PERCENT,MONEY,QUANTITY,ORDINAL,CARDINAL,GPE,WORK\ OF\ ART,LANGUAGE,PRODUCT
```

- **Dump the rater_{r}_single_gold_ignored**
```bash
#prodigy db-out rater_{r}_single_gold_ignored data/single/gold/rater_{r}
```

- **Merge the rater_{r}_single_gold_ignored and the rater_{r}_single_gold_accepted**
    - Creates in db:
        - rater_{r}_single_gold
```bash
#prodigy db-merge rater-{r}-single-gold-accepted,rater-{r}-single-gold-ignored rater_{r}_single_gold
```

- **Merge all single_gold dataset in db**
    - Creates in db:
        - gold-single
```bash
#prodigy db-merge rater_3_single_gold,rater_4_single_gold,rater_5_single_gold,rater_6_single_gold,rater_7_single_gold,rater_8_single_gold,rater_9_single_gold gold-single
```

- **Merge all gold datasets in db and save as files**
    - Creates in db:
        - gold-full
    - Creates in folders:
        - data/full/gold/gold-full.jsonl
        - data/full/gold/gold-full.spacy
```bash
prodigy db-merge single-gold-accept,gold-multi-and-gold-rater-1-single gold-full
prodigy db-out gold-full data/full/gold/
prodigy data-to-spacy data/full/gold/ --ner gold-full --lang "da" --eval-split 0
mv data/full/gold/train.spacy data/full/gold/gold-full.spacy
rm data/full/gold/config.cfg
rm -rf data/full/gold/labels
```

- **Use a script to filter away cases where regex pattern matches a common mistake so it may be reviewed**
    - E.g.:
        - GUD (remove)
        - Himlen (remove)
        - Tal m. bogstaver (add dem)
        - All Cardinals med / og :
        - den 14. april (remove den)
            - Do NOT include determiners or articles in the extent
            - However, we INCLUDE IT(!) if no month and year is shown. It is not a date without it.
                - "d. [11 Juni 1814]", "[Vi skal betale fra her den 1.]", "den [30. april 2015]"
            - Include in "det første århundrede"
            - Include in 
        - Adresser
            - Chunk up into cardinals, faciities og GPE (jævnfør kinesiske ekstra regler: "For address, break it down into several mentions. For example, 2899 Xietu Road, Room 207, Shanghai City“上海市斜土路二八九九 号二零七室”, tag [Shanghai City] [上海市] as a GPE, [Xietu Road] [斜土路] as a Facility, [2899] as a Cardinal, and [207] as another Cardinal.")
            - Completely contrasting the other rule "Nothing should be marked in "cnn.com," "1600 Pennsylvania Ave," or "1-800-555-"
        - Telefonnumre (Ontonotes siger at kontaktinformationer ikke skal tagges)
            - Should not be tagged. "Numerals, including whole numbers, fractions, and decimals, that provide a count or quantity and do not fall under a unit of measurement, money, percent, date or time"
        - Hjemmesider. Er ikke blevet tagget konsistent
            - Nothing should be marked in "cnn.com," "1600 Pennsylvania Ave," or "1-800-555-"
            - MEDMINDRE det specifikt bliver nævnt som en organization
        - FN og EU er organisationer men ikke nødvendigvis tagget konsistent
            - Should be tagged as organizations, rather than GPE
        - Tidsrum (ofte skrevet som 18:00 - 20:00)
            - Durations should be marked inclusively: [from 1995 to 2000]
        - Dates:
            - Durations should be marked inclusively: [from 1995 to 2000]
        - Hotels and resorts
            - Marked as facilities rather than ORGANIZATIONS
        - Cardinals med bogstaver i. Cardinals med /, cardinals med .
            - No letters or / are allowed
            - "Numerals, including whole numbers, fractions, and decimals, that provide a count or quantity and do not fall under a unit of measurement, money, percent, date or time"
        - Ret (såsom Fortrydelsesret og Ophavsret og Menneskerettigheder)
            - Inkluderes ikke. De inkluderes kun hvis der bliver nævnt "Ophavsretsloven"
        - Ytringsfrihed
            - Ytringsfrihed er noget vi har, som følge af lovgivningen, og er derfor ikke en lovgivning i sig selv.
        - Copyright og ®
            - Er ikke en lov - inkluderes ikke.
        - ORG som ender på ApS eller A/S skal være med i tagget (og der det vist hovedsageligt også)
            - Cadbury Schweppes Australia Ltd. er tagget, men uden .
    - Creates in folders:
        - data/full/gold/gold-bad.spacy
        - data/full/gold/gold-bad-no-tags.spacy
        - data/full/gold/gold-good.spacy
    - Creates in db:
        - gold-good
        - gold-bad
        - gold-bad-no-tags
```bash
src/preprocessing/regex_filter.ipynb
python ./src/preprocessing/load_docbin_as_jsonl.py data/full/gold/gold-good.spacy blank:da --ner > data/full/gold/gold-good.jsonl
python ./src/preprocessing/load_docbin_as_jsonl.py data/full/gold/gold-bad.spacy blank:da --ner > data/full/gold/gold-bad.jsonl
python ./src/preprocessing/load_docbin_as_jsonl.py data/full/gold/gold-bad-no-tags.spacy blank:da --ner > data/full/gold/gold-bad-no-tags.jsonl
prodigy db-in gold-bad data/full/gold/gold-bad.jsonl
prodigy db-in gold-good data/full/gold/gold-good.jsonl
prodigy db-in gold-bad-no-tags data/full/gold/gold-bad-no-tags.jsonl
git status
```

- **Review the bad cases**
    - YIELDED 449 CASES THAT WERE GONE THROUGH
```bash
prodigy review gold-bad-resolved gold-bad,gold-bad-no-tags --label PERSON,NORP,FACILITY,ORGANIZATION,LOCATION,EVENT,LAW,DATE,TIME,PERCENT,MONEY,QUANTITY,ORDINAL,CARDINAL,GPE,WORK\ OF\ ART,LANGUAGE,PRODUCT -S -A
#prodigy review gold-bad-resolved gold-bad --view-id ner --label PERSON,NORP,FACILITY,ORGANIZATION,LOCATION,EVENT,LAW,DATE,TIME,PERCENT,MONEY,QUANTITY,ORDINAL,CARDINAL,GPE,WORK\ OF\ ART,LANGUAGE,PRODUCT -S
#prodigy mark gold-bad-resolved dataset:gold-bad --view-id review --label PERSON,NORP,FACILITY,ORGANIZATION,LOCATION,EVENT,LAW,DATE,TIME,PERCENT,MONEY,QUANTITY,ORDINAL,CARDINAL,GPE,WORK\ OF\ ART,LANGUAGE,PRODUCT
#prodigy mark gold-bad-resolved dataset:gold-bad --view-id ner --label PERSON,NORP,FACILITY,ORGANIZATION,LOCATION,EVENT,LAW,DATE,TIME,PERCENT,MONEY,QUANTITY,ORDINAL,CARDINAL,GPE,WORK\ OF\ ART,LANGUAGE,PRODUCT
```

- **Merge gold-bad-resolved and gold-good**
    - Creates in db:
        - gold
    - Creates in folders:
        - data/full/gold/dansk.spacy
        - data/full/gold/dansk.jsonl
```bash
prodigy db-merge gold-bad-resolved,gold-good gold
prodigy db-out gold data/full/gold/
prodigy data-to-spacy data/full/gold/ --ner gold --lang "da" --eval-split 0
mv data/full/gold/train.spacy data/full/gold/dansk.spacy
mv data/full/gold/gold.jsonl data/full/gold/dansk.jsonl
rm data/full/gold/config.cfg
rm -rf data/full/gold/labels
```

- **Split dansk up into train, dev, test**'
    - Creates in folders:
        - data/full/gold/dansk_train.spacy (.7 of full)
        - data/full/gold/dansk_dev.spacy (.15 of full)
        - data/full/gold/dansk_test.spacy (.15 of full)
    - Creates in db:
        - dansk_dev
```bash
prodigy data-to-spacy data/full/gold/ --ner gold --lang "da" --eval-split .3
mv data/full/gold/train.spacy data/full/gold/dansk_train.spacy
mv data/full/gold/dev.spacy data/full/gold/dansk_dev.spacy
python ./src/preprocessing/load_docbin_as_jsonl.py data/full/gold/dansk_dev.spacy blank:da --ner > data/full/gold/dansk_dev.jsonl
prodigy db-in dansk_dev data/full/gold/dansk_dev.jsonl
prodigy data-to-spacy data/full/gold/ --ner dansk_dev --lang "da" --eval-split .5
mv data/full/gold/dev.spacy data/full/gold/dansk_dev.spacy
mv data/full/gold/train.spacy data/full/gold/dansk_test.spacy

rm data/full/gold/config.cfg
rm -rf data/full/gold/labels
```

- **Get DaNE**
    - Creates in folders:
        - data/dane/dane_train.conllu
        - data/dane/dane_dev.conllu
        - data/dane/dane_test.conllu
        - data/dane/dane_train.spacy
        - data/dane/dane_dev.spacy
        - data/dane/dane_test.spacy
        - data/dane/dane.spacy
```bash
python src/get_dane.py
python -m spacy convert data/dane/dane_dev.conllu data/dane/ --converter conllu --merge-subtokens -n 10
python -m spacy convert data/dane/dane_train.conllu data/dane/ --converter conllu --merge-subtokens -n 10
python -m spacy convert data/dane/dane_test.conllu data/dane/ --converter conllu --merge-subtokens -n 10
python src/merge_dane.py
```

- **Upload to sciencedata.dk
```bash
# Manually
````


# GOTTEN TO HERE

- **Assess interrater reliability of model and annotators**
```bash
#src/data_assessment/interrater_reliability/interrater_reliability_final.ipynb
```

# Go through: https://github.com/explosion/spaCy/discussions/12307 









Vigtig info fra møde m. Kenneth:
	- Når jeg er færdig med DANSK, lav da interrater reliability test igen, men denne gange også med "the true values" fra datasættet. Brug dette i paperet som en måde hvorpå jeg kan validere datasættet (hvis der er høj interrater reliability). Hvis den er lav, få da Kenneth, Rebekah eller en uvildig til at gennemgå nogle og se uenigheden dér.
	- Lav post på spaCy forum: Hvordan håndterer spaCy training missing values? Jeg har 2 datasæt, hvoraf den ene indeholder NER tags og den anden indeholder POS og Dependency Parsing. Kan jeg merge dette data og træne uden at NER komponenten bliver opdateret i tilfælde af batches med data uden NER? Og vice versa? Og hvordan sikrer jeg mig at spacy train håndterer det som "missing value" og ikke bare som om at der ER tagget, men at der ikke var nogen tags? https://github.com/explosion/spaCy/discussions/12307 
	- Til den endelige træning, brug da følgende modeller (valgt ud fra https://scandeval.github.io/nlu-benchmark/):
		○ Jonfd-nordic (i stedet for ælectra)
		○ Nb-scandi (i stedet for DaBERT)
		○ Dfm-bert-large (i stedet for XLM-R). Alternativt xlm-r, hvis jeg inkluderer ontonotes engelsk i træning også.
	- Til den endelige træning, merge DDT med DANSK, men fjern al NER fra DDT, således at det er missing values under træningen.
	- Til den endelige træning, overvej at lægge engelsk ontonotes ind også
    - Til den endelige træning, opskalér da DDT, så det ikke fylder for lidt
	- Til den endelige træning, lav da en fork af DaCy med en ny mappe under "training", som her er lavet i helt samme stil som kenneths sidste.
	- Til den endelige træning, lav da en "final-model" og en "final-model-no-test". No-test versionen kan bruges til at replikere, mens den anden kan bruges i praksis. Hvis for doven, lav da kun en "final-model-no-test"
	- Til evaluering af performance på testsættet, overvej da at bruge flere evalueringsmetoder, vha. "scorer"
	- DANSK behøver ikke udgives før DaCy kan trænes på det (unpublished dataset yet to be published)
	- DANSK kan udgives på et hemmeligt datascience link til specialet, hvis det skulle være nødvendigt
    - DaCy behøves i princippet ikke udgives helt til specialet, men kan ligge på en ny branch











- **Calculate how many tags there are of each type**
```bash
?????
```

- **If few of some tags, add tags**
```bash
# Empty unless few tags of some of them
```

- **Train a new model**

- **Use model to predict on all data**

- **Review cases where model and data disagrees**

- **Use newly reviewed data to train a new model**

- **Evaluate performance, and do qualitative error analysis**

- **Nice to do, not need to do, depends also on performance**
    - Predict on bad labels (e.g. product and language) on existing dataset, and subsequently use prodigy review on only these docs
        - Make predictions using Zero shot predictions (Zshot - https://spacy.io/universe/project/Zshot)
        - Make predictions using and English trained model (same style as: gold-multi-training/datasets/lang_product_predict_gold_multi_rater_1.py)
    - Fix bad labeling in the dataset (Ask Kenneth, he very briefly mentioned below methods)
    - Do it using one of the following approaches:
        - Using Spancategorizer
        - Use the model to predict on parts of the DANSK dataset. And then go through these faulty classifications and see whether the classification is wrong, or whether the labeling is wrong. Go through the wrong labeling and fix it. Iterate this processUse the models' wrong predictions

- **Gain access to Huggingface account centre-for-humanities-computing**

- **Train a NER model on the gold-dansk and package it**
    - Everything must be done on UCloud as packaging can't be done locally
    - Ensure that relevant information on Weights and Biases (wandb) is saved so I can use for report. 
    https://docs.wandb.ai/guides/integrations/spacy
    - Packaging to centre-for-humanities-computing
