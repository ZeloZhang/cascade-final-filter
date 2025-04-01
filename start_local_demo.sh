#!/bin/sh

GCD="/data/exp/IceCube/2020/filtered/level2/0602/Run00134150/Level2_IC86.2020_data_Run00134150_0602_78_529_GCD.i3.zst" # corresponding GCD file.
#INFILE="/data/ana/Cscd/IC86-2020/level3/exp/2020/0602/Run00134150/Level3*_Run00134150*.i3.zst"
INFILE="/data/ana/analyses/diffuse/cascades/pass2/sim/nugen/level3/21218/0000000-0000999/Level3_IC86.2016_NuE.021218.000000.i3.zst" # cascade level3 file
OUTFILE="Level3_sc_IC86_2020_data_Run00134150.i3.zst" # output file path and name
DATATYPE="data" # "data", "nugen", "cors"
YEAR="2020" # 2010 -> IC79 or year > 2010 -> IC86

# No difference for year > 2010
if [ -z "$YEAR" ]
then
   YEAR="2015"
fi

# Absolute path to this script, e.g. /home/user/bin/foo.sh
SCRIPT=$(readlink -f "$0")
# Absolute path this script is in, thus /home/user/bin
SCRIPTPATH=$(dirname "$SCRIPT")

eval `/cvmfs/icecube.opensciencegrid.org/py3-v4.0.1/setup.sh`
set -f 
time /cvmfs/icecube.opensciencegrid.org/users/zzhang1/combo_stable_addatmo/env-shell.sh python /home/zzhang1/private_cascade_filter/cascade-final-filter/cscdSBU_master.py -i ${INFILE} -o "${OUTFILE}" -g "$GCD" -d "$DATATYPE" -y "$YEAR" --redomonopod # --redomonopod is the defult setting.

