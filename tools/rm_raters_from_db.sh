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
    echo "Removing rater_"$i"_"$parent_dir"_"$dir" data from Prodigy database ..."
    prodigy drop rater_"$i"_"$parent_dir"_"$dir"
done