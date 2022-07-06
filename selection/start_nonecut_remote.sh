#!/bin/sh

set -e

gcd="$1"
infile="$2"
outfile="$3"
datatype="$4"
year="$5"
nfile="$6"

INDIR="$(dirname $infile)"
INFILE_NAME="$(basename $infile)"
OUT_DIR="$(dirname $outfile)"
OUT_NAME="$(basename $outfile)"
GCDDIR="$(dirname $gcd)"
GCD_NAME="$(basename $gcd)"

export X509_CERT_DIR="/cvmfs/icecube.opensciencegrid.org/data/voms/share/certificates"
eval `/cvmfs/icecube.opensciencegrid.org/py3-v4.0.1/setup.sh`
globus-url-copy gsiftp://gridftp.icecube.wisc.edu/data/user/hmniederhausen/mariola/test/models/bdt_full.xgb ./bdt_full.xgb
globus-url-copy ${INDIR}/${INFILE_NAME} ./${INFILE_NAME}
globus-url-copy ${GCDDIR}/${GCD_NAME} ./${GCD_NAME}

env -i ./selection/start_main.sh "$GCD_NAME" "$INFILE_NAME" "$OUT_NAME" "$datatype" "$year" "$nfile" "None"
globus-url-copy ./${OUT_NAME} ${OUT_DIR}/${OUT_NAME}
rm -f ./${OUT_NAME}

rm -f ./bdt_full.xgb
rm -f ./${INFILE_NAME}
rm -f ./${GCD_NAME}

