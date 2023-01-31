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


if [[ $original = 0 ]]; 
then
    for i in {1..10}
    do
        echo "Removing rater_"$i"_"$parent_dir"_"$dir" data from Prodigy database ..."
        prodigy drop rater_"$i"_"$parent_dir"_"$dir"
    done
fi

if [[ $original = 1 ]]; 
then
    for i in {1..10}
    do
        echo "Removing rater_"$i" data from Prodigy database ..."
        prodigy drop rater_"$i"_original
    done
#rm -r data/prodigy_exports
rm data/prodigy_exports.zip
fi
