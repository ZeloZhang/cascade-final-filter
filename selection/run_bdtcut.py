#!/bin/sh /cvmfs/icecube.opensciencegrid.org/py2-v2/icetray-start
#METAPROJECT: /cvmfs/icecube.opensciencegrid.org/py2-v2/RHEL_7_x86_64/metaprojects/icerec/V05-01-02/

from I3Tray import *
from icecube import icetray,dataio,dataclasses
from icecube.icetray import traysegment
from cscdSBU_selection import selection, selection_mlb
from icecube import fill_ratio, cscd_llh, gulliver, millipede, finiteReco, linefit, lilliput, dipolefit, clast, CascadeVariables
import glob
from argparse import ArgumentParser
import os
import sys

parser = ArgumentParser()

parser.add_argument("-g", "--gcd",type=str,
                      default="",
                      dest="GCD",
                      help="read input physcis to INFILE (.i3.bz2 format)")

parser.add_argument("-i", "--infile",type=str,
                      default="",
                      dest="INFILE",
                      help="read input physcis to INFILE (.i3.bz2 format)")

parser.add_argument("-o", "--outfile",type=str,
                      default="",
                      dest="OUTFILE",
                      help="output file name")

parser.add_argument("-d", "--datatype",type=str,
                    default="",
                    dest="DATATYPE",
                    help="possible values: nugen, cors, data, muongun")

parser.add_argument("-y", "--year",type=str,
                    default="",
                    dest="YEAR",
                    help="possible values: 2011, 2012, 2013, 2014, 2015")

parser.add_argument("-n", "--nfiles",type=int,
                    default=0,
                    dest="NFILES",
                    help="only relevant for muongun. use default NFILES=0 for other datatypes.")

parser.add_argument("-s", "--selection",type=str,
                    default="cascade",
                    #default="muon",
                    dest="SELECTION",
                    help="possible values: None, cascade, hybrid, muon")

args = parser.parse_args()
# filename or the regular expression of the filename is provided
i3 = sorted(glob.glob(args.INFILE))
# dir name is provided
if not i3:
    i3 = sorted(glob.glob(args.INFILE+"/*i3.*"))
i3 = [f for f in i3 if os.path.getsize(f) > 40000]
infiles = [args.GCD] + i3
print(infiles)
outfile = args.OUTFILE
datatype = args.DATATYPE
year = args.YEAR
nfiles = args.NFILES

tray = I3Tray()

tray.AddModule("I3Reader","reader",FilenameList = infiles)
tray.AddSegment(selection, "cscdSBU", selection=args.SELECTION) # None, 'cascade', 'hybrid', 'muon'

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
                                      icetray.I3Frame.Stream('M'),
                                      icetray.I3Frame.Stream('Q')],
                   )

tray.Execute()
tray.Finish()

