while getopts p:d:o: flag
do
    case "${flag}" in
        p) parent_dir=${OPTARG};;
        d) dir=${OPTARG};;
        o) original=${OPTARG};;
    esac
done

if [[ $original = 1 ]]; 
then
    for i in {1..10}
    do
        echo "Exporting rater_$i data to Prodigy database ..."
        prodigy db-in rater_"$i" ./data/prodigy_exports/prodigy"$i"_db_exports/NER_annotator"$i".jsonl
    done
fi

if [[ $original = 0 ]];
then
    for i in {1..10}
    do
        echo "Exporting rater_$i data to Prodigy database from ./data/$parent_dir/$dir/* ..."
        prodigy db-in rater_"$i" ./data/$parent_dir/$dir/rater_$i/data.jsonl
    done
fi