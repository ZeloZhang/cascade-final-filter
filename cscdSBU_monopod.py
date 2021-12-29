from I3Tray import *
from icecube import icetray
from LatePulseCleaning import LatePulseCleaning

@icetray.traysegment
def monopod_reco(tray, name, ExcludeDeepCore=False, pulses='OfflinePulses', my_photonics_service=None):
    from icecube import wavedeform
    from icecube.millipede import MonopodFit, HighEnergyExclusions
    from icecube import photonics_service, millipede

    # saturatedDOMs already exists
    tray.AddModule('Delete', name+'Delete2', Keys=['SaturatedDOMs', 'BrightDOMs'])
  
    if "InIce" in pulses:
        srtpulses = 'SRTInIcePulses'
    else:
        srtpulses = 'SRTOfflinePulses'
     
    exclusions = tray.AddSegment(HighEnergyExclusions,
            Pulses=srtpulses,
            BrightDOMThreshold = 15,
            BadDomsList='BadDomsList',
            ExcludeDeepCore=ExcludeDeepCore,
            ExcludeBrightDOMs = 'BrightDOMs',
            ExcludeSaturatedDOMs = 'SaturatedDOMs',
            CalibrationErrata='CalibrationErrata',
            SaturationWindows = 'SaturationWindows')

    if not my_photonics_service:
        tabledir = '/cvmfs/icecube.opensciencegrid.org/data/photon-tables/splines/'
        amplitudetable=tabledir+"cascade_single_spice_3.2.1_flat_z20_a5.abs.fits"
        timingtable=tabledir+"cascade_single_spice_3.2.1_flat_z20_a10.prob.fits"
        tilt_table = '/cvmfs/icecube.opensciencegrid.org/py3-v4.1.1/metaprojects/combo/V01-01-01/ice-models/resources/models/spice_3.2.1/'
        effectivedistancetable = '/cvmfs/icecube.opensciencegrid.org/data/photon-tables/splines/cascade_effectivedistance_spice_3.2.1_z20.eff.fits'

    # if TimeRange is missing, recreate if from WaveformTimeRange
    tray.AddModule(wavedeform.AddMissingTimeWindow, name+'pulserange', Pulses=pulses, If=lambda frame: not frame.Has(pulses+'TimeRange'))
     
    tray.AddModule(LatePulseCleaning, name+"LatePulseCleaning",
            Pulses=pulses, Residual=1500, If=lambda frame: not frame.Has(pulses+'LatePulseCleaned'))
    exclusions.append(pulses+'LatePulseCleanedTimeWindows')
    millipede_config = dict(Pulses=pulses+"LatePulseCleaned",
            CascadePhotonicsService=my_photonics_service,
            PartialExclusion=True,
            DOMEfficiency=0.99,
            ReadoutWindow=pulses+"LatePulseCleanedTimeRange",
            Parametrization='HalfSphere',
            PhotonsPerBin=0,
            BadDOMs=exclusions,
            MintimeWidth=8)

    def add_L3_MonopodFit4_AmptFit(frame):
        frame["L3_MonopodFit4_AmptFit"] = frame["L3_MonopodFit4"]
        return True
    
    tray.Add(add_L3_MonopodFit4_AmptFit,name+"_add_AmptFit",If=lambda frame: not frame.Has("L3_MonopodFit4_AmptFit"))
    tray.AddSegment(MonopodFit, name, Seed='L3_MonopodFit4_AmptFit',
                    Iterations=4, **millipede_config)

