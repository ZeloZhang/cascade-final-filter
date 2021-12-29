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
echo $GCD
echo $INFILE
echo $OUTFILE
INDIR="$(dirname $INFILE)"
INFILE_NAME="$(basename $INFILE)"
OUTDIR="$(dirname $OUTFILE)"
OUTFILE_NAME="$(basename $OUTFILE)"
GCDDIR="$(dirname $GCD)"
GCD_NAME="$(basename $GCD)"
export X509_CERT_DIR="/cvmfs/icecube.opensciencegrid.org/data/voms/share/certificates"

echo ${INDIR}
echo ${INFILE_NAME}
echo ${GCDDIR}
echo ${GCD_NAME}
eval `/cvmfs/icecube.opensciencegrid.org/py3-v4.0.1/setup.sh`
#globus-url-copy ${INDIR}/${INFILE_NAME} ./${INFILE_NAME}
globus-url-copy ${INDIR}/${INFILE_NAME} ./
globus-url-copy ${GCDDIR}/${GCD_NAME} ./
if [ $? -ne 0 ]
then
    echo "FAILED GRIDFTP"
    exit 1
fi
time /cvmfs/icecube.opensciencegrid.org/users/zzhang1/combo_stable_addatmo/env-shell.sh python ./cascade-final-filter/cscdSBU_master.py -i "./${INFILE_NAME}" -o "./${OUTFILE_NAME}" -g "$GCD_NAME" -d "$DATATYPE" -y "$YEAR" --redomonopod

globus-url-copy ./${OUTFILE_NAME} ${OUTDIR}/${OUTFILE_NAME}
if [ $? -ne 0 ]
then
    echo "FAILED GRIDFTP"
    exit 1
fi
rm -f ./${INFILE_NAME}
rm -f ./${OUTFILE_NAME}
rm -f ./${GCD_NAME}
