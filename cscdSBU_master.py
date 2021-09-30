#!/usr/bin/env python

from I3Tray import *
#import I3Tray
from icecube import icetray, dataclasses, dataio, hdfwriter
from icecube.icetray import traysegment
import sys
import glob

from cscdSBU_weights import weights
from cscdSBU_selection import select_L3SC
from cscdSBU_monopod import monopod_reco
from cscdSBU_vars import addvars

# arguments below
from argparse import ArgumentParser
parser = ArgumentParser()

parser.add_argument("-i", "--infile",type=str,
                      default="",
                      dest="INFILE",
                      help="read input physcis to INFILE (.i3.bz2 format)")

parser.add_argument("-o", "--outfile",type=str,
                      default="",
                      dest="OUTFILE",
                      help="output file name")

parser.add_argument("-g", "--geofile",type=str,
                      default="",
                      dest="GEOFILE",
                      help="geometry file")

parser.add_argument("-y", "--year",type=str,
                    default="",
                    dest="YEAR",
                    help="possible values: 2011, 2012, 2013, 2014, 2015...")

parser.add_argument("-d", "--datatype",type=str,
                    default="",
                    dest="DATATYPE",
                    help="possible values: nugen, cors, data")

parser.add_argument("-r", "--redomonopod",
                    default="",
                    dest="REDO_MONOPOD",
		    action="store_true",
                    help="whether or not to redo Monopod4 reconstrcution.")

args = parser.parse_args ()

gcd = args.GEOFILE
i3 = args.INFILE
outfile = args.OUTFILE
datatype = args.DATATYPE

# years = ['2011', '2012', '2013', '2014', '2015'...] 
year = args.YEAR
# data is uniform for each year for pass2, so just give a random year to make sure the process is the same.

redo_monopod = args.REDO_MONOPOD
if int(year) <= 2010:
    ic_config = "IC79"
else:
    ic_config = "IC86"
 
monopod_pulses = "SplitInIcePulses"
pulses = monopod_pulses

if redo_monopod:
    print("... redoing monopod 4iter.")
else:
    print("... assuming monopod 4iter exists at CscdL3.")

tray = I3Tray()

# For data
filenames = [gcd]+sorted(glob.glob(i3+"*.i3*"))
#print("********this is file name",filenames)

# exit script if filenames only has 1 file (GCD or data instead of at least both)
if len(filenames)<2:
   print("missing input files! (GCD or data)")
   sys.exit(1)

tray.AddModule('I3Reader', 'reader', FilenameList=filenames)

# Cascade L3 singles, contained
tray.AddSegment(select_L3SC, "select")

# Weights + MCTruth.
tray.AddSegment(weights, "weight", datatype=datatype)

# Monopod 4iter (with and without DeepCore)
tray.AddSegment(monopod_reco, 'cscdSBU_MonopodFit4_noDC', ExcludeDeepCore='DeepCoreDOMs', pulses=monopod_pulses)

# some cscd L3 datasets have correct monopod (with DeepCore) already
if redo_monopod:
    tray.AddSegment(monopod_reco, 'cscdSBU_MonopodFit4', ExcludeDeepCore=False, pulses=monopod_pulses)
else:
    # correct monopod exists. rename.
    def rename_monopod(frame):
        reconame = 'L3_MonopodFit4'
        if frame.Has(reconame):
            frame['cscdSBU_MonopodFit4'] = frame[reconame]
        return True

    tray.AddModule(rename_monopod, "fun_with_names")

# Misc variables.
tray.AddSegment(addvars, "misc", pulses=pulses, ic_config=ic_config)

tray.AddModule("I3Writer", "EventWriter",
                   FileName=outfile,
                   Streams=[icetray.I3Frame.TrayInfo,
                            icetray.I3Frame.DAQ,
                            icetray.I3Frame.Physics,
                            icetray.I3Frame.Stream('S'),
                            icetray.I3Frame.Stream('M')],
                   DropOrphanStreams=[icetray.I3Frame.DAQ,
                                      icetray.I3Frame.TrayInfo,
                                      icetray.I3Frame.Stream('S'),
                                      icetray.I3Frame.Stream('Q'),
                                      icetray.I3Frame.Stream('M')]
                   )

tray.AddModule('TrashCan','can')
tray.Execute()
tray.Finish()


