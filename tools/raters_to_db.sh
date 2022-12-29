for i in {1..10}
do
    echo "Exporting rater $i data to Prodigy database ..."
    prodigy db-in rater_"$i" ./data/prodigy_exports/prodigy"$i"_db_exports/NER_annotator"$i".jsonl
done