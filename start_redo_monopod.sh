#!/bin/sh

GCD="$1"
INFILE="$2"
OUTFILE="$3"
DATATYPE="$4" 
YEAR="$5"
if [ -z "$YEAR" ]
then
   YEAR="2015"
fi

# Absolute path to this script, e.g. /home/user/bin/foo.sh
SCRIPT=$(readlink -f "$0")
# Absolute path this script is in, thus /home/user/bin
SCRIPTPATH=$(dirname "$SCRIPT")

eval `/cvmfs/icecube.opensciencegrid.org/py3-v4.0.1/setup.sh`
time /data/user/zzhang1/combo/stable_addatmo/build/env-shell.sh python /data/user/zzhang1/leptonInjectorCheck/nugen/code/finallevel/github_safe60/cscdSBU_master.py -i "$INFILE" -o "$OUTFILE" -g "$GCD" -d "$DATATYPE" -y "$YEAR" --redomonopod



