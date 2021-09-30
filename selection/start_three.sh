#!/bin/sh

gcd="$1"
infile="$2"
outfile_cascade="$3"
outfile_hybrid="$4"
outfile_muon="$5"
datatype="$6"
year="$7"
nfile="$8"

# Absolute path to this script, e.g. /home/user/bin/foo.sh
SCRIPT=$(readlink -f "$0")
# Absolute path this script is in, thus /home/user/bin
SCRIPTPATH=$(dirname "$SCRIPT")

eval `/cvmfs/icecube.opensciencegrid.org/py3-v4.0.1/setup.sh`

export PYTHONPATH=/data/user/zzhang1/xgboost/python-package
export HDF5_USE_FILE_LOCKING=FALSE
time /data/user/zzhang1/combo/stable_addatmo/build/env-shell.sh /data/user/zzhang1/leptonInjectorCheck/nugen/code/finallevel/github/selection/run.py -g "$gcd" -i "$infile" -o "$outfile_cascade" -d "$datatype" -y "$year" -n "$nfile" -s "cascade"
time /data/user/zzhang1/combo/stable_addatmo/build/env-shell.sh /data/user/zzhang1/leptonInjectorCheck/nugen/code/finallevel/github/selection/run.py -g "$gcd" -i "$infile" -o "$outfile_hybrid" -d "$datatype" -y "$year" -n "$nfile" -s "hybrid"
time /data/user/zzhang1/combo/stable_addatmo/build/env-shell.sh /data/user/zzhang1/leptonInjectorCheck/nugen/code/finallevel/github/selection/run.py -g "$gcd" -i "$infile" -o "$outfile_muon" -d "$datatype" -y "$year" -n "$nfile" -s "muon"
