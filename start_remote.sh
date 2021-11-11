#!/bin/sh

set -e 

GCD="$1"
INFILE="$2"
OUTFILE="$3"
DATATYPE="$4" 
YEAR="$5"
if [ -z "$YEAR" ]
then
   YEAR="2015"
fi
INDIR="$(dirname $INFILE)"
INFILE_NAME="$(basename $INFILE)"
OUTDIR="$(dirname $OUTFILE)"
OUTFILE_NAME="$(basename $OUTFILE)"
export X509_CERT_DIR="/cvmfs/icecube.opensciencegrid.org/data/voms/share/certificates"

globus-url-copy ${INDIR}/${INFILE_NAME} ./${INFILE_NAME}
if [ $? -ne 0 ]
then
    echo "FAILED GRIDFTP"
    exit 1
fi

# Absolute path to this script, e.g. /home/user/bin/foo.sh
SCRIPT=$(readlink -f "$0")
# Absolute path this script is in, thus /home/user/bin
SCRIPTPATH=$(dirname "$SCRIPT")

eval `/cvmfs/icecube.opensciencegrid.org/py3-v4.0.1/setup.sh`
#export PYTHONPATH="/cvmfs/icecube.opensciencegrid.org/users/zzhang1/private_cascade_filter/cascade-final-filter/:$PYTHONPATH"
time /cvmfs/icecube.opensciencegrid.org/users/zzhang1/combo_stable_addatmo/env-shell.sh python ./cascade-final-filter/cscdSBU_master.py -i "./${INFILE_NAME}" -o "./${OUTFILE_NAME}" -g "$GCD" -d "$DATATYPE" -y "$YEAR" --redomonopod

globus-url-copy ./${OUTFILE_NAME} ${OUTDIR}/${OUTFILE_NAME}
if [ $? -ne 0 ]
then
    echo "FAILED GRIDFTP"
    exit 1
fi
rm -f ./${INFILE_NAME}
rm -f ./${OUTFILE_NAME}
