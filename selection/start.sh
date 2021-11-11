#!/bin/sh

gcd="$1"
infile="$2"
outfile="$3"
datatype="$4"
year="$5"
nfile="$6"
selection="$7"

SCRIPT="$0"
SCRIPTPATH="$(dirname $0)"
eval `/cvmfs/icecube.opensciencegrid.org/py3-v4.0.1/setup.sh`

export HDF5_USE_FILE_LOCKING=FALSE
time /cvmfs/icecube.opensciencegrid.org/users/zzhang1/combo_stable_addatmo/env-shell.sh ${SCRIPTPATH}/run.py -g "$gcd" -i "$infile" -o "$outfile" -d "$datatype" -y "$year" -n "$nfile" -s "$selection"
