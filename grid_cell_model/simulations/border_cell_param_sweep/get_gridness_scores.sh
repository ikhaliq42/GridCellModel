#!/bin/sh
for i in 2 4 6 8 10
do
    qsub cluster_submit_gridness_scores.sh $i 
done
