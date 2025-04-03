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

export PYTHONPATH="${PYTHONPATH}:/cvmfs/icecube.opensciencegrid.org/users/zzhang1/cascade-final-filter-venv/lib/python3.11/site-packages/"
export HDF5_USE_FILE_LOCKING=FALSE
time ${SCRIPTPATH}/run_bdtcut.py -g "$gcd" -i "$infile" -o "$outfile" -d "$datatype" -y "$year" -n "$nfile" -s "$selection"
