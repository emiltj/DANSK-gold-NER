mkdir data
for data_size in full multi single
do
    mkdir ./data/$data_size/
    for data_format in unprocessed streamlined gold
    do 
       mkdir ./data/$data_size/$data_format/
       for i in {1..10}
       do
            mkdir ./data/$data_size/$data_format/rater_$i
        done
    done
        for i in {1..10}
    do
        rm -rf ./data/$data_size/gold/*
    done
done

mkdir ./data/single/unprocessed/combined
mkdir ./data/single/streamlined/combined
mkdir ./data/single/gold/combined
mkdir ./data/multi/gold/output/
mkdir ./data/single/gold/combined/

for i in {1..10}
do
    mkdir ./data/single/gold/rater_$i/
    rm -r ./data/single/streamlined/rater_$i/
done

rm -r ./data/full/streamlined/