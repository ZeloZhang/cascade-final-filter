#!/bin/sh

gcd="$1"
infile="$2"
outfile="$3"
datatype="$4"
year="$5"
nfile="$6"
selection="$7"
outfile_temp="${outfile}.temp"

SCRIPT="$0"
SCRIPTPATH="$(dirname $0)"
export OMP_NUM_THREADS=1
${SCRIPTPATH}/start_bdtcut.sh $gcd $infile "${outfile}.temp" $datatype $year $nfile $selection

${SCRIPTPATH}/start.sh $gcd "${outfile}.temp" $outfile $datatype $year $nfile $selection
rm "${outfile}.temp"


