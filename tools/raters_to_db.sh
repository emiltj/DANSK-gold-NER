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
        echo "Exporting rater_$i data to Prodigy database ..."
        prodigy db-in rater_"$parent_dir"_"$dir"_"$i" ./data/prodigy_exports/prodigy"$i"_db_exports/NER_merged_annotator"$i".jsonl
    done
#rm -r data/prodigy_exports
rm data/prodigy_exports.zip
fi

if [[ $original = 0 ]];
then
    for i in {1..10}
    do
        echo "Exporting rater_$i data to Prodigy database from ./data/$parent_dir/$dir/* ..."
        prodigy db-in rater_"$i" ./data/$parent_dir/$dir/rater_$i/data.jsonl
    done
fi

