for data_size in full multi single
do
    mkdir ./data/DANSK-$data_size/
    for data_format in unprocessed streamlined gold-standard
    do 
       mkdir ./data/DANSK-$data_size/$data_format/
       for i in {1..10}
       do
            mkdir ./data/DANSK-$data_size/$data_format/rater_$i
        done
    done
        for i in {1..10}
    do
        rm -rf ./data/DANSK-$data_size/gold-standard/*
    done
done

mkdir ./data/DANSK-single/unprocessed/model_predictions/

for i in {1..10}
do
    mkdir ./data/DANSK-single/gold-standard/rater_$i/
done

rm -r ./data/DANSK-full/streamlined/