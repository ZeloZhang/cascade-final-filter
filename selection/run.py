#!/usr/bin/env python

from I3Tray import *
from icecube import icetray,dataio,dataclasses
from icecube.icetray import traysegment
from icecube import hdfwriter
from icecube import fill_ratio, cscd_llh,gulliver, millipede, finiteReco, linefit, lilliput, dipolefit, clast, CascadeVariables

from cscdSBU_book import tobook, change_names, OLDMuonGun2011LE
from cscdSBU_weights import weights
from cscdSBU_reco import reco

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
# pass2 is uniform
#tray.AddSegment(selection, "cscdSBU", selection=args.SELECTION) # None, 'cascade', 'hybrid', 'muon'

tray.AddSegment(weights, 'background_weights', nfile=nfiles, infiles=infiles, datatype=datatype, year=year)

# xsec analysis needs inice neutrino
if datatype=="nugen":
    def InIceNu(frame):
        import numpy as n
        tree = frame['I3MCTree']
        neutrinos = []

        for p in tree:
            if p.is_neutrino == True and p.location_type == dataclasses.I3Particle.LocationType.InIce and not n.isnan(p.length):
                neutrinos.append(p)
        if len(neutrinos)>0:
            frame['cscdSBU_MCInIcePrimary']=neutrinos[0]

        return True

    tray.AddModule(InIceNu, 'thenusinice')

# if data add reconstruction with partial exclusion
#if datatype=='data' and int(year)>2010:
#    tray.AddSegment(reco, 'reco_with_pe')

# some L2 variable names differ from year to year. revert to 2011 names.
# pass2 is uniform
tray.AddModule(change_names, year=year)

# create list of things to be booked
book_keys = tobook(datatype)
# add more keys, I modified 
book_keys += ['CascadeLast_L2Params',
     "CascadeLlhVertexFit_L2",
     "coincident_I3MCPE_zelong",
     "coincident_I3MCTreePrimaries_zelong",
     "CscdL3_Cont_Tag",
     "cscdSBU_AtmWeight_Conv",
     "cscdSBU_AtmWeight_Conv_kaon100",
     "cscdSBU_AtmWeight_Conv_PassRate",
     "cscdSBU_AtmWeight_Conv_PassRate_muon100",
     "cscdSBU_AtmWeight_Prompt",
     "cscdSBU_MonopodFit4",
     "cscdSBU_MonopodFit4FitParams",
     "cscdSBU_Qtot_HLC",
     "cscdSBU_Qtot_SplitInIcePulses",
     'I3EventHeader',
     "I3MCWeightDict",
     'InIcePulses',
     "L3_MonopodFit4",
     "L3_MonopodFit4FitParams",
     "L3_MonopodFit4_AmptFit",
     "L3_MonopodFit4_AmptFitFitParams",
     "NCh_OfflinePulsesHLC",
     "NCh_OfflinePulsesHLC_DCOnly",
     "NCh_OfflinePulsesHLC_noDC",
     "NString_OfflinePulsesHLC",
     "NString_OfflinePulsesHLC_DCOnly",
     "NString_OfflinePulsesHLC_noDC",
     'PoleCascadeFilter_CscdLlh',
     'PoleMuonLlhFit',
     "PolyplopiaInfo",
     'PolyplopiaPrimary',
     'SplitInIcePulses',
     'SRTInIcePulses',
     'OfflinePulsesHLC',
     'OfflinePulsesSLC',
 ]

book_keys = list(set(book_keys))

# not writing to /data/ana/ to save space
'''
tray.AddSegment(hdfwriter.I3HDFWriter, 'hdf',
                Output=outfile+".h5",
                Keys = book_keys,
                SubEventStreams=['in_ice', 'nullsplit', 'ice_top', 'InIceSplit'])
'''
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

tray.AddModule("TrashCan","trash")
tray.Execute()
tray.Finish()

