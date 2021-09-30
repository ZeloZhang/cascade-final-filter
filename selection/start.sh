#!/bin/sh

gcd="$1"
infile="$2"
outfile="$3"
datatype="$4"
year="$5"
nfile="$6"
selection="$7"

eval `/cvmfs/icecube.opensciencegrid.org/py3-v4.0.1/setup.sh`

export HDF5_USE_FILE_LOCKING=FALSE
time /data/user/zzhang1/combo/stable_addatmo/build/env-shell.sh /data/user/zzhang1/combo/private_cascade_filter/cascade-final-filter/selection/run.py -g "$gcd" -i "$infile" -o "$outfile" -d "$datatype" -y "$year" -n "$nfile" -s "$selection"
