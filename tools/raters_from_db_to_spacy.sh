while getopts p:d:o: flag
do
    case "${flag}" in
        p) parent_dir=${OPTARG};;
        d) dir=${OPTARG};;
        o) original=${OPTARG};;
        ?) echo "script usage: [-p] [-d] [-o]" >&2
        exit 1
    esac
done


if [[ $original = 1 ]]; 
then
    for i in {1..10}
    do
        echo "Exporting data from data base for rater_"$i"_original to  ..."
        prodigy data-to-spacy data/full/unprocessed/rater_"$i"/ --ner rater_"$i"_original --lang "da" --eval-split 0 #0.2
        rm -r data/full/unprocessed/rater_$i/labels
        rm data/full/unprocessed/rater_$i/config.cfg
    done
fi


if [[ $original = 0 ]]; 
then
    for i in {1..10}
    do
        echo "Exporting data from data base for rater_"$i"_"$parent_dir"_"$dir" to  ..."
        prodigy data-to-spacy data/full/unprocessed/rater_"$i"/ --ner rater_$i --lang "da" --eval-split 0 #0.2
        rm -r data/full/unprocessed/rater_$i/labels
        rm data/full/unprocessed/rater_$i/config.cfg
    done
fi