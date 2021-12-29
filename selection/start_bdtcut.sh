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

#eval `/cvmfs/icecube.opensciencegrid.org/py2-v2/setup.sh`
export PYTHONPATH="${PYTHONPATH}:/cvmfs/icecube.opensciencegrid.org/users/zzhang1/xgboost-0.47/lib/python2.7/site-packages/"
export HDF5_USE_FILE_LOCKING=FALSE
#time /cvmfs/icecube.opensciencegrid.org/py2-v2/RHEL_7_x86_64/metaprojects/icerec/V05-01-02/env-shell.sh ${SCRIPTPATH}/run_bdtcut.py -g "$gcd" -i "$infile" -o "$outfile" -d "$datatype" -y "$year" -n "$nfile" -s "$selection"
time ${SCRIPTPATH}/run_bdtcut.py -g "$gcd" -i "$infile" -o "$outfile" -d "$datatype" -y "$year" -n "$nfile" -s "$selection"
