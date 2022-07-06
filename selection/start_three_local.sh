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

#SCRIPT="$0"
#SCRIPTPATH="$(dirname $0)"
SCRIPTPATH="/home/zzhang1/private_cascade_filter/cascade-final-filter/selection/"
${SCRIPTPATH}/start_main.sh "$gcd" "$infile" "$outfile_cascade" "$datatype" "$year" "$nfile" "cascade"
${SCRIPTPATH}/start_main.sh "$gcd" "$infile" "$outfile_hybrid" "$datatype" "$year" "$nfile" "hybrid"
${SCRIPTPATH}/start_main.sh "$gcd" "$infile" "$outfile_muon" "$datatype" "$year" "$nfile" "muon"
