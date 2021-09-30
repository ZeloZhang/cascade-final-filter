from icecube import icetray

@icetray.traysegment
def Redo_L3_Monopod(tray, name,year,Pulses='OfflinePulses'):
    from icecube.millipede import MonopodFit, HighEnergyExclusions
    from icecube import photonics_service, millipede

    tray.AddModule('Rename', 'rename', Keys=['RedoMonopodAmpFit','RedoMonopodAmpFit_mie_flat','RedoMonopodAmpFitFitParams','RedoMonopodAmpFitFitParams_mie_flat','L3_MonopodFit4_AmptFit','L3_MonopodFit4_AmptFit_mie_flat','L3_MonopodFit4_AmptFitFitParams','L3_MonopodFit4_AmptFitFitParams_mie_flat','SaturatedDOMs','SaturatedDOMs_mie_flat','BrightDOMs','BrightDOMs_mie_flat'])

    exclusions = tray.AddSegment(HighEnergyExclusions, Pulses='SRTOfflinePulses',ExcludeDeepCore=False,BadDomsList='BadDomsList')
    AmpSeed= 'CascadeLlhVertexFit_L2'
    table_base = '/data/sim/sim-new/spline-tables/cascade_single_spice_3.2.1_flat_z20_a10.%s.fits'
    tilt_table = '/cvmfs/icecube.opensciencegrid.org/py3-v4.1.1/metaprojects/combo/V01-01-01/ice-models/resources/models/spice_3.2.1/'
    photonics_service = photonics_service.I3PhotoSplineService(table_base % 'abs', table_base % 'prob', 0., 
            tiltTableDir=tilt_table)

    millipede_config = dict(Pulses=Pulses, CascadePhotonicsService=photonics_service,
        PartialExclusion=False,
        Parametrization='HalfSphere')
    tray.AddSegment(MonopodFit, 'RedoMonopodAmpFit', Seed=AmpSeed,
        PhotonsPerBin=-1, **millipede_config)
    tray.AddSegment(MonopodFit, 'L3_MonopodFit4_AmptFit',Seed='RedoMonopodAmpFit',
        PhotonsPerBin=5, Iterations=4,DOMEfficiency=0.99,BinSigma=2,MintimeWidth=15,BadDOMs=exclusions,**millipede_config)

