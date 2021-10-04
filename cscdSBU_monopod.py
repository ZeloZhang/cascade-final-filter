from I3Tray import *
from icecube import icetray

@icetray.traysegment
def monopod_reco(tray, name, ExcludeDeepCore=False, pulses='OfflinePulses'):
    from icecube import wavedeform
    from icecube.millipede import MonopodFit, HighEnergyExclusions
    from icecube import photonics_service, millipede

    # saturatedDOMs already exists
    tray.AddModule('Delete', name+'Delete2', Keys=['SaturatedDOMs', 'BrightDOMs'])
  
    if "InIce" in pulses:
        srtpulses = 'SRTInIcePulses'
    else:
        srtpulses = 'SRTOfflinePulses'
     
    exclusions = tray.AddSegment(HighEnergyExclusions, Pulses=srtpulses,ExcludeDeepCore=ExcludeDeepCore, BadDomsList='BadDomsList')
    table_base = '/data/sim/sim-new/spline-tables/cascade_single_spice_3.2.1_flat_z20_a10.%s.fits'
    tilt_table = "/cvmfs/icecube.opensciencegrid.org/py3-v4.1.1/metaprojects/combo/V01-01-01/ice-models/resources/models/spice_3.2.1/"
    photonics_service = photonics_service.I3PhotoSplineService(table_base % 'abs', table_base % 'prob', 0., tiltTableDir=tilt_table)

    # if TimeRange is missing, recreate if from WaveformTimeRange
    tray.AddModule(wavedeform.AddMissingTimeWindow, name+'pulserange', Pulses=pulses, If=lambda frame: not frame.Has(pulses+'TimeRange'))
     
    millipede_config = dict(Pulses=pulses, CascadePhotonicsService=photonics_service, 
        PartialExclusion=False,
         Parametrization='HalfSphere') 

    def add_L3_MonopodFit4_AmptFit(frame):
        if not frame.Has("L3_MonopodFit4_AmptFit"):
            frame["L3_MonopodFit4_AmptFit"] = frame["L3_MonopodFit4"]
            return True
    
    tray.Add(add_L3_MonopodFit4_AmptFit,name+"_add_AmptFit")
    tray.AddSegment(MonopodFit, name, Seed='L3_MonopodFit4_AmptFit',
        PhotonsPerBin=5, Iterations=4,DOMEfficiency=0.99,BinSigma=2,MintimeWidth=15,BadDOMs=exclusions, **millipede_config)

