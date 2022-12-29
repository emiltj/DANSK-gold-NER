for i in {1..10}
do
    echo "Removing rater $i data from Prodigy database ..."
    prodigy drop rater_"$i"
done