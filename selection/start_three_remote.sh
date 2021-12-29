#!/bin/sh

set -e

gcd="$1"
infile="$2"
outfile_cascade="$3"
outfile_hybrid="$4"
outfile_muon="$5"
datatype="$6"
year="$7"
nfile="$8"

INDIR="$(dirname $infile)"
INFILE_NAME="$(basename $infile)"
OUT_CASCADE_DIR="$(dirname $outfile_cascade)"
OUT_CASCADE_NAME="$(basename $outfile_cascade)"
OUT_HYBRID_DIR="$(dirname $outfile_hybrid)"
OUT_HYBRID_NAME="$(basename $outfile_hybrid)"
OUT_MUON_DIR="$(dirname $outfile_muon)"
OUT_MUON_NAME="$(basename $outfile_muon)"
GCDDIR="$(dirname $gcd)"
GCD_NAME="$(basename $gcd)"

export X509_CERT_DIR="/cvmfs/icecube.opensciencegrid.org/data/voms/share/certificates"
eval `/cvmfs/icecube.opensciencegrid.org/py3-v4.0.1/setup.sh`
globus-url-copy gsiftp://gridftp.icecube.wisc.edu/data/user/hmniederhausen/mariola/test/models/bdt_full.xgb ./bdt_full.xgb
globus-url-copy ${INDIR}/${INFILE_NAME} ./${INFILE_NAME}
globus-url-copy ${GCDDIR}/${GCD_NAME} ./${GCD_NAME}

env -i ./selection/start_main.sh "$GCD_NAME" "$INFILE_NAME" "$OUT_CASCADE_NAME" "$datatype" "$year" "$nfile" "cascade"
globus-url-copy ./${OUT_CASCADE_NAME} ${OUT_CASCADE_DIR}/${OUT_CASCADE_NAME}
rm -f ./${OUT_CASCADE_NAME}

env -i ./selection/start_main.sh "$GCD_NAME" "$INFILE_NAME" "$OUT_HYBRID_NAME" "$datatype" "$year" "$nfile" "hybrid"
globus-url-copy ./${OUT_HYBRID_NAME} ${OUT_HYBRID_DIR}/${OUT_HYBRID_NAME}
rm -f ./${OUT_HYBRID_NAME}

env -i ./selection/start_main.sh "$GCD_NAME" "$INFILE_NAME" "$OUT_MUON_NAME" "$datatype" "$year" "$nfile" "muon"
globus-url-copy ./${OUT_MUON_NAME} ${OUT_MUON_DIR}/${OUT_MUON_NAME}
rm -f ./${OUT_MUON_NAME}

rm -f ./bdt_full.xgb
rm -f ./${INFILE_NAME}
rm -f ./${GCD_NAME}

