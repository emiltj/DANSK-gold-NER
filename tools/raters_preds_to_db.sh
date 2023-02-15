for i in {1..10}
do
    echo "Exporting rater_"$i"_preds to jsonl"
    python ./src/preprocessing/load_docbin_as_jsonl.py ./data/single/unprocessed/rater_$i/rater_"$i"_preds.spacy blank:da --ner > ./data/single/unprocessed/rater_$i/rater_"$i"_preds.jsonl
    echo "Importing rater_"$i"_preds to db"
    prodigy db-in rater_"$i"_single_unprocessed_preds ./data/single/unprocessed/rater_$i/rater_"$i"_preds.jsonl
done