#!/bin/sh

gcd="$1"
infile="$2"
outfile="$3"
datatype="$4"
year="$5"
nfile="$6"
selection="$7"
outfile_temp="${outfile}.temp"
/data/user/zzhang1/combo/private_cascade_filter/cascade-final-filter/selection/start_bdtcut.sh $gcd $infile "${outfile}.temp" $datatype $year $nfile $selection

/data/user/zzhang1/combo/private_cascade_filter/cascade-final-filter/selection/start.sh $gcd "${outfile}.temp" $outfile $datatype $year $nfile $selection
rm "${outfile}.temp"

