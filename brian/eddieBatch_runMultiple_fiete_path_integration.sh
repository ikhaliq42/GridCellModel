#!/bin/sh

########################################
# Submit fiete_path_integration.py jobs
# with different network parameters
# into the cluster
########################################

# Constant parameters
F_SHEET_SIZE="96"
F_TIME="150"

# Parameters different for each job
CONN_MULT="20"

#F_ALPHA="0.025 0.027 0.03 0.035 0.04 0.045 0.050 0.055 0.060 0.07 0.08 0.09 0.100"
F_ALPHA="0.015"

#F_INPUT="0.3000    0.4000    0.5000    0.6000    0.7000    0.8000"
F_INPUT="0.3"

F_TAUM="10"

F_TAUI="9"

REPEAT=4

F_LAMBDA_NET="20"

#F_THRESHOLD="-60 -59 -58 -57 -56 -55 -54 -53 -52 -51 -50 -40 -30 -20"
F_THRESHOLD="-40 -30 -20"

#F_L="0 1 2 3 4 5 6 7 8 9 10"
F_L="2"

job_id=19500
for alpha in $F_ALPHA; do
    for conn_mult in $CONN_MULT; do
        for input in $F_INPUT; do
            for taum in $F_TAUM; do
                for taui in $F_TAUI; do
                    for lambda_net in $F_LAMBDA_NET; do
                        for threshold in $F_THRESHOLD; do
                            for l_param in $F_L; do
                                for sheet_size in $F_SHEET_SIZE; do

#####################
repeat=1
while [ $repeat -le $REPEAT ]; do
    echo "sheet_size=$sheet_size"
    echo "conn_mult=$conn_mult"
    echo "alpha=$alpha"
    echo "job_id=$job_id"
    echo "lambda_net=$lambda_net"
    echo "threshold=$threshold"

    qsub ./eddieBatch_fiete_path_integration.sh $sheet_size $F_TIME $alpha $conn_mult $job_id $input $taum $taui $lambda_net $threshold $l_param

    echo

    let job_id=$job_id+1
    let repeat=$repeat+1
done
#####################

                                done
                            done
                        done
                    done
                done
            done
        done
    done
done