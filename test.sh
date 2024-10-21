#!/bin/bash

echo 'TESTING STAN FILE CREATION'

OUTFILE='test_00.stan'
DEGREE=3
DIRECTORY='test'

python build_bcs_stan.py $OUTFILE \
       --directory $DIRECTORY \
       -v \
       --degree $DEGREE

OUTFILE='test_01.stan'
python build_bcs_stan.py $OUTFILE \
       --directory $DIRECTORY \
       -v \
       --degree $DEGREE \
       --phi 0.99 \
       --drift-sd 1 \
       --kernel-opts '(7,0.5,0)' 
       
