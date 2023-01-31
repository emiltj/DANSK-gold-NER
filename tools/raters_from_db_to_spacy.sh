while getopts p:d: flag
do
    case "${flag}" in
        p) parent_dir=${OPTARG};;
        d) dir=${OPTARG};;
        ?) echo "script usage: [-p] [-d]" >&2
        exit 1
    esac
done

for i in {1..10}
do
    echo "Exporting data from data base for rater_"$i"_"$parent_dir"_"$dir" to  ..."
    prodigy data-to-spacy data/full/unprocessed/rater_"$i"_"$parent_dir"_"$dir"/ --ner rater_$i --lang "da" --eval-split 0 #0.2
    rm -r data/full/unprocessed/rater_$i/labels
    rm data/full/unprocessed/rater_$i/config.cfg
done