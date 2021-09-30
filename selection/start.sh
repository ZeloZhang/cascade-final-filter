#!/bin/sh

gcd="$1"
infile="$2"
outfile="$3"
datatype="$4"
year="$5"
nfile="$6"
selection="$7"

# Absolute path to this script, e.g. /home/user/bin/foo.sh
SCRIPT=$(readlink -f "$0")
# Absolute path this script is in, thus /home/user/bin
SCRIPTPATH=$(dirname "$SCRIPT")

eval `/cvmfs/icecube.opensciencegrid.org/py3-v4.0.1/setup.sh`

export PYTHONPATH=/data/user/zzhang1/xgboost/python-package
export HDF5_USE_FILE_LOCKING=FALSE
time /data/user/zzhang1/combo/stable_addatmo/build/env-shell.sh /data/user/zzhang1/leptonInjectorCheck/nugen/code/finallevel/github/selection/run.py -g "$gcd" -i "$infile" -o "$outfile" -d "$datatype" -y "$year" -n "$nfile" -s "$selection"
