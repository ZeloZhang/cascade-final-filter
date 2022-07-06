#!/bin/sh

set -e

gcd="$1"
infile="$2"
outfile="$3"
datatype="$4"
year="$5"
nfile="$6"

#SCRIPT="$0"
#SCRIPTPATH="$(dirname $0)"
SCRIPTPATH="/home/zzhang1/private_cascade_filter/cascade-final-filter/selection/"
${SCRIPTPATH}/start_main.sh "$gcd" "$infile" "$outfile" "$datatype" "$year" "$nfile" "None"
