#!/bin/sh

set -f
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
time /cvmfs/icecube.opensciencegrid.org/users/zzhang1/combo_stable_addatmo/env-shell.sh python /home/zzhang1/private_cascade_filter/cascade-final-filter/cscdSBU_master.py -i "${INFILE}" -o "${OUTFILE}" -g "$GCD" -d "$DATATYPE" -y "$YEAR" --redomonopod

