#!/bin/sh

gcd="$1"
infile="$2"
outfile="$3"
datatype="$4"
year="$5"
nfile="$6"
selection="$7"

eval `/cvmfs/icecube.opensciencegrid.org/py2-v2/setup.sh`
export PYTHONPATH="${PYTHONPATH}:/data/user/hmniederhausen/sandbox/xgboost-0.47/python-package/:/cvmfs/icecube.opensciencegrid.org/py2-v2/RHEL_7_x86_64/lib/python2.7/site-packages/"
export HDF5_USE_FILE_LOCKING=FALSE
time /data/user/hmniederhausen/icerec_V05-01-12/build/env-shell.sh /data/user/zzhang1/combo/private_cascade_filter/cascade-final-filter/selection/run_bdtcut.py -g "$gcd" -i "$infile" -o "$outfile" -d "$datatype" -y "$year" -n "$nfile" -s "$selection"
