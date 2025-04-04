#!/bin/sh

set -e

# parameters for run_bdtcut.py and run.py
gcd="/data/exp/IceCube/2011/filtered/level2pass2/0107/Run00117332/Level2pass2_IC79.2010_data_Run00117332_0107_38_20_GCD.i3.zst" # Coresponding GCD file
infile="/data/ana/analyses/diffuse/cascades/pass2/data/IC79_2010/blind//Level3_sc_IC86_2010_data_Run00117332.i3.zst" # Input file, generated by "/home/zzhang1/private_cascade_filter/cascade-final-filter/cscdSBU_master.py"
outfile_cascade="./final_cascade/Finallevel_IC79_2010_data_Run00117332.i3.zst" # Output file, final cascade event
outfile_hybrid="./final_hybrid/Finallevel_IC79_2010_data_Run00117332.i3.zst" # Output file, final hybrid (starting track) event
outfile_muon="./final_muon/Finallevel_IC79_2010_data_Run00117332.i3.zst" # Output file, final muon (trak) event
datatype="data" # nugen, cors, data, muongun.  
year="2010" # year of data, 2010 -> IC79, year > 2010 -> IC86
nfile="0" # only relevent for muongun weighting

#SCRIPT="$0"
#SCRIPTPATH="$(dirname $0)"
SCRIPTPATH="/home/zzhang1/private_cascade_filter/cascade-final-filter/selection/"
${SCRIPTPATH}/start_main.sh "$gcd" "$infile" "$outfile_cascade" "$datatype" "$year" "$nfile" "cascade"
${SCRIPTPATH}/start_main.sh "$gcd" "$infile" "$outfile_hybrid" "$datatype" "$year" "$nfile" "hybrid"
${SCRIPTPATH}/start_main.sh "$gcd" "$infile" "$outfile_muon" "$datatype" "$year" "$nfile" "muon"
