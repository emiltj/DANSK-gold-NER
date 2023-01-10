for i in {1..10}
do
    echo "Exporting data from data base for rater_$i to  ..."
    prodigy data-to-spacy data/full/unprocessed/rater_$i/ --ner rater_$i --lang "da" --eval-split 0 #0.2
    #rm -r data/full/unprocessed/rater_$i/labels
    #rm data/full/unprocessed/rater_$i/config.cfg
done