#!/bin/sh

gcd="/data/sim/IceCube/2013/filtered/level2/CORSIKA-in-ice/10649/00000-00999/GeoCalibDetectorStatus_2013.56429_V1.i3.gz"
infile="/data/ana/Cscd/cscdSBU/MuonGun/low_energy/IC86_2013/cscdSBU_level3_sc_0000001.i3.bz2"
outfile="./hah.i3.bz2"
datatype="muongun"
year="2015"
nfile="10"
L2DIR=" "
selection="cascade"

# Absolute path to this script, e.g. /home/user/bin/foo.sh
SCRIPT=$(readlink -f "$0")
# Absolute path this script is in, thus /home/user/bin
SCRIPTPATH=$(dirname "$SCRIPT")

eval `/cvmfs/icecube.opensciencegrid.org/py3-v4.0.1/setup.sh`
#source /data/user/zzhang1/ROOT/build/bin/thisroot.sh
export PYTHONPATH=/data/user/zzhang1/xgboost/python-package
export HDF5_USE_FILE_LOCKING=FALSE
time /data/user/zzhang1/combo/stable_addatmo/build/env-shell.sh /data/user/zzhang1/leptonInjectorCheck/nugen/code/finallevel/github/selection/run.py -g "$gcd" -i "$infile" -o "$outfile" -d "$datatype" -y "$year" -n "$nfile" -l "$L2DIR" -s "$selection"
