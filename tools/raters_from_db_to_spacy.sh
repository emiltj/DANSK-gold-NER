if [ ! -d "../data/DANSK-full/unprocessed" ];
then
mkdir ./data/DANSK-full/unprocessed
fi

for i in {1..10}
do
    echo "Exporting rater_$i data to Prodigy database ..."
    mkdir ./data/DANSK-full/unprocessed/rater_$i
    prodigy data-to-spacy data/DANSK-full/unprocessed/rater_$i/ --ner rater_$i --lang "da" --eval-split 0
done