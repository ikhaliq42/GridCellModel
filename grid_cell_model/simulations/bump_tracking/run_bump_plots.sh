#!/bin/sh
for c in 0 1 2 3 4 5 6 7 8 9 10
do
    for e in 0 1 2 3 4 5 6 7 
    do
        for t in 0 1 2 3 4 5 6 7 8 9
	do
            qsub cluster_submit_bump_plot.sh $c $e $t
	done
    done
done
