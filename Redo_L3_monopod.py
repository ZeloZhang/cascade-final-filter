from icecube import icetray
from LatePulseCleaning import LatePulseCleaning

@icetray.traysegment
def Redo_L3_Monopod(tray, name,year,Pulses='OfflinePulses', my_photonics_service=None):
    from icecube.millipede import MonopodFit, HighEnergyExclusions
    from icecube import photonics_service, millipede
    from icecube import wavedeform
    from icecube import WaveCalibrator, wavedeform, DomTools

    tray.AddModule('Rename', 'rename', Keys=['RedoMonopodAmpFit','RedoMonopodAmpFit_mie_flat','RedoMonopodAmpFitFitParams','RedoMonopodAmpFitFitParams_mie_flat','L3_MonopodFit4_AmptFit','L3_MonopodFit4_AmptFit_mie_flat','L3_MonopodFit4_AmptFitFitParams','L3_MonopodFit4_AmptFitFitParams_mie_flat','SaturatedDOMs','SaturatedDOMs_mie_flat','BrightDOMs','BrightDOMs_mie_flat','CalibratedWaveforms','CalibratedWaveforms_old'])

    # recover CalibrationErrata
    kwargs = dict(Launches='InIceRawData', Waveforms='CalibratedWaveforms', Errata='CalibrationErrata')
    tray.AddModule('I3WaveCalibrator', name+'wavecal', If=lambda frame: (frame.Has('InIceRawData') and (not frame.Has("CalibrationErrata"))), WaveformRange="CalibratedWaveformRange_new", **kwargs)

    exclusions = tray.AddSegment(HighEnergyExclusions, 
            Pulses='SRTOfflinePulses',
            BrightDOMThreshold = 15,
            BadDomsList='BadDomsList',
            ExcludeDeepCore=False,
            ExcludeBrightDOMs = 'BrightDOMs',
            ExcludeSaturatedDOMs = 'SaturatedDOMs',
            CalibrationErrata='CalibrationErrata',
            SaturationWindows = 'SaturationWindows'
            )
    AmpSeed= 'CascadeLlhVertexFit_L2'
    if not my_photonics_service:
        tabledir = '/cvmfs/icecube.opensciencegrid.org/data/photon-tables/splines/'
        amplitudetable=tabledir+"cascade_single_spice_3.2.1_flat_z20_a5.abs.fits"
        timingtable=tabledir+"cascade_single_spice_3.2.1_flat_z20_a10.prob.fits"
        tilt_table = '/cvmfs/icecube.opensciencegrid.org/py3-v4.1.1/metaprojects/combo/V01-01-01/ice-models/resources/models/spice_3.2.1/'
        effectivedistancetable = '/cvmfs/icecube.opensciencegrid.org/data/photon-tables/splines/cascade_effectivedistance_spice_3.2.1_z20.eff.fits'
        my_photonics_service = photonics_service.I3PhotoSplineService(amplitudetable=amplitudetable, timingtable=timingtable, timingSigma=0., tiltTableDir=tilt_table, effectivedistancetable = effectivedistancetable)

    # if TimeRange is missing, recreate if from WaveformTimeRange
    tray.AddModule(wavedeform.AddMissingTimeWindow, name+'pulserange', Pulses=Pulses, If=lambda frame: not frame.Has(Pulses+'TimeRange'))

    tray.AddModule(LatePulseCleaning, name+"LatePulseCleaning",
            Pulses=Pulses, Residual=1500, If=lambda frame: not frame.Has(Pulses+'LatePulseCleaned'))
    exclusions.append(Pulses+'LatePulseCleanedTimeWindows')
    millipede_config = dict(Pulses=Pulses+"LatePulseCleaned",
            CascadePhotonicsService=my_photonics_service,
            PartialExclusion=True,
            DOMEfficiency=0.99,
            ReadoutWindow=Pulses+"LatePulseCleanedTimeRange",
            Parametrization='HalfSphere',
            BadDOMs=exclusions,
            MintimeWidth=8)

    tray.AddSegment(MonopodFit, 'RedoMonopodAmpFit', Seed=AmpSeed,
        PhotonsPerBin=-1, **millipede_config)
    tray.AddSegment(MonopodFit, 'L3_MonopodFit4_AmptFit',Seed='RedoMonopodAmpFit',
        PhotonsPerBin=0, Iterations=4, **millipede_config)

