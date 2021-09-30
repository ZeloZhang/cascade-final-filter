#!/bin/sh

gcd="$1"
infile="$2"
outfile_cascade="$3"
outfile_hybrid="$4"
outfile_muon="$5"
datatype="$6"
year="$7"
nfile="$8"

/data/user/zzhang1/combo/private_cascade_filter/cascade-final-filter/selection/start_main.sh "$gcd" "$infile" "$outfile_cascade" "$datatype" "$year" "$nfile" "cascade"
/data/user/zzhang1/combo/private_cascade_filter/cascade-final-filter/selection/start_main.sh "$gcd" "$infile" "$outfile_hybrid" "$datatype" "$year" "$nfile" "hybrid"
/data/user/zzhang1/combo/private_cascade_filter/cascade-final-filter/selection/start_main.sh "$gcd" "$infile" "$outfile_muon" "$datatype" "$year" "$nfile" "muon"
