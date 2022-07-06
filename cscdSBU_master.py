#!/usr/bin/env python

from I3Tray import *
from icecube import icetray, dataio
import sys
import glob

from cscdSBU_weights import weights
from cscdSBU_selection import select_L3SC
from cscdSBU_monopod import monopod_reco
from cscdSBU_vars import addvars
from Redo_L3_monopod import Redo_L3_Monopod

# arguments below
from argparse import ArgumentParser
parser = ArgumentParser()

parser.add_argument("-i", "--infile",type=str,
                      default="",
                      dest="INFILE",nargs="+",
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
if i3:
    filenames = [gcd]+[filename for filename in i3]
elif glob.glob(i3):
    filenames = [gcd]+sorted(glob.glob(i3))
elif glob.glob(i3+"*.i3*"):
    filenames = [gcd]+sorted(glob.glob(i3+"*.i3*"))
else:
    print("no i3 file found")
print("********this is file name",filenames)

# exit script if filenames only has 1 file (GCD or data instead of at least both)
if len(filenames)<2:
   print("missing input files! (GCD or data)")
   sys.exit(1)

tray.AddModule('I3Reader', 'reader', FilenameList=filenames)

# Cascade L3 singles, contained
tray.AddSegment(select_L3SC, "select")

# Weights + MCTruth.
tray.AddSegment(weights, "weight", datatype=datatype)

# prepare photonics_service for monopod reco
# Try photon table from /data/sim/ first
# If it does not exist on grid try tables from /cvmfs/
if glob.glob('/data/sim/sim-new/spline-tables/cascade_single_spice_3.2.1_flat_z20_a10.%s.fits'):
    tabledir = '/data/sim/sim-new/spline-tables/'
    amplitudetable=tabledir+"cascade_single_spice_3.2.1_flat_z20_a5.abs.fits"
    timingtable=tabledir+"cascade_single_spice_3.2.1_flat_z20_a10.prob.fits"
else:
    tabledir = "/cvmfs/icecube.opensciencegrid.org/data/photon-tables/splines/"
    amplitudetable=tabledir+"cascade_single_spice_3.2.1_flat_z20_a5.abs.fits"
    timingtable=tabledir+"cascade_single_spice_3.2.1_flat_z20_a10.prob.fits"
tilt_table = "/cvmfs/icecube.opensciencegrid.org/py3-v4.1.1/metaprojects/combo/V01-01-01/ice-models/resources/models/spice_3.2.1/"
splinetabledir = '/cvmfs/icecube.opensciencegrid.org/data/photon-tables/splines'

from icecube import photonics_service, millipede
photonics_service = photonics_service.I3PhotoSplineService(amplitudetable=amplitudetable, timingtable=timingtable, timingSigma=0., tiltTableDir=tilt_table, effectivedistancetable = splinetabledir + '/cascade_effectivedistance_spice_3.2.1_z20.eff.fits')
print("using spice321 tilt effective distance icemodel")

# redo L3_Monopod with spice 3.2.1
print("redoing L3_monopod")
tray.AddSegment(Redo_L3_Monopod, "Redo_L3_Monopod", year = year, Pulses="OfflinePulses", my_photonics_service=photonics_service)

# Monopod 4iter (with and without DeepCore)
tray.AddSegment(monopod_reco, 'cscdSBU_MonopodFit4_noDC', ExcludeDeepCore='DeepCoreDOMs', pulses=monopod_pulses, my_photonics_service=photonics_service)

# some cscd L3 datasets have correct monopod (with DeepCore) already
if redo_monopod:
    tray.AddSegment(monopod_reco, 'cscdSBU_MonopodFit4', ExcludeDeepCore=False, pulses=monopod_pulses, my_photonics_service=photonics_service)
else:
    # correct monopod exists. rename.
    def rename_monopod(frame):
        reconame = 'L3_MonopodFit4_AmptFit'
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


