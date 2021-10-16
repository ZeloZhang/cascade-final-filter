from I3Tray import *
from icecube import icetray, dataclasses
from icecube.icetray import traysegment
import copy

@icetray.traysegment
def reco(tray, name):
        def rename(frame):
                if frame.Has('SaturatedDOMs'):
                        sat = frame['SaturatedDOMs']
                        frame['SaturatedDOMs_old'] = copy.copy(sat)
        
                if frame.Has('BrightDOMs'):
                        bright = frame['BrightDOMs']
                        frame['BrightDOMs_old'] = copy.copy(bright)
                return True
        
        tray.AddModule(rename, 'name0r')
        tray.AddModule('Delete', 'Delete01', Keys=['SaturatedDOMs', 'BrightDOMs', 'DeepCoreDOMs'])
        
        from icecube.millipede import MonopodFit, HighEnergyExclusions
        from icecube import photonics_service, millipede
        
        
        monopod_pulses = "SplitInIcePulses"
        pulses = monopod_pulses
        
        splinedir = '/data/sim/sim-new/spline-tables/'
        timingSigma = 0.
        photonics_service_mie = photonics_service.I3PhotoSplineService(amplitudetable = splinedir + '/ems_mie_z20_a10.abs.fits',
                                                   timingtable = splinedir + '/ems_mie_z20_a10.prob.fits',
                                                   timingSigma = timingSigma)
        
        if "InIce" in pulses:
                srtpulses = 'SRTInIcePulses'
        else:
                srtpulses = 'SRTOfflinePulses'
        
        # redo with DeepCore
        exclusions = tray.AddSegment(HighEnergyExclusions, Pulses=srtpulses, ExcludeDeepCore=False, BadDomsList='BadDomsList')
        
        millipede_config = dict(Pulses=pulses, CascadePhotonicsService=photonics_service_mie,
                PartialExclusion=True,
                Parametrization='HalfSphere', ExcludedDOMs=exclusions)
        
        name = 'cscdSBU_MonopodFit4_final'
        tray.AddSegment(MonopodFit, name, Seed='L3_MonopodFit4_AmptFit',
                PhotonsPerBin=5, Iterations=4,DOMEfficiency=0.99,BinSigma=2,MintimeWidth=15, **millipede_config)
