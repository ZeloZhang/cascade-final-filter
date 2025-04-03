from I3Tray import *
from icecube import icetray, dataclasses
from icecube.icetray import traysegment
import copy

import sys,os
import argparse

import logging
import numpy as np

from icecube import dataclasses, VHESelfVeto
from icecube.filterscripts import filter_globals
from icecube.filterscripts.offlineL2 import Recalibration
from icecube.icetray import I3Tray, I3Units
from icecube import photonics_service, icetray
from icecube.millipede import HighEnergyExclusions
from snowflake import library, unfold
from reco.masks import (maskdc,
                        pulse_cleaning)
from reco.truth import truth, druth
from reco.mlpd import (MonopodWrapper,
                       define_splines)
from types import SimpleNamespace

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


@icetray.traysegment
def reco_ftp(tray, name, **args):

    # set default values
    defaults = {
        'seed': 'L3_MonopodFit4_AmptFit', # user specified seeds for the *pod based recos
        'isdata': False, # running on data
        'binsigma': np.nan, # set the binsigma parameter for BBlocks
        'mintimewidth': 8, # set the min time width parameter for millipede
        'idc': False, # include DeepCore DOMs
        'isat': False, # include Saturated DOMs
        'ibr': False, # include Bright DOMs
        'itw': False, # include Saturation/CalibrationErrata windows
        'nouh': False, # exclude unhit doms
        'unfold': False, # unfold expectations from reconstructed particle
        'residual': 1500 * I3Units.ns, # time residual for PulseCleaning
        'bdthres': 15, # bright DOMs threshold
        'relerr': 0.05, # relative error for LLH
        'qepsilon': 1.0, # quantile above which use double precision
        'tsig': 0.0, # jitter in [ns] for B-spline convolution
        'pulse_type': 'SplitInIcePulses', # specify the pulse_type type (default SplitInIcePulses)
        'icemodel': 'ftp-v1', # The ice model to use for reconstruction.
        'tilt': True, # use the tiltTableDir, based on --icemodel
        'effd': True, # use the effectivedistancetable, based on --icemodel
        'effp': True, # use the effectivedistancetable for prob and tmod, based on --icemodel
        'mini': 'iMIGRAD', # run reco with minimizer (iMIGRAD, MIGRAD, SIMPLEX)
        }

    # defaults.update(args)
    # args = defaults
    # args = {**defaults, **args}
    args = SimpleNamespace(**{**defaults, **args})
    cascade_service = define_splines(args.icemodel,
                                     args.tilt,
                                     args.effd,
                                     args.effp,
                                     args.qepsilon,
                                     args.tsig)

    wrapperfn = MonopodWrapper
    specifier = 'MonopodFit'
    loss_vector_suffix = ''
    
    if args.isdata:
        rde_map = library.get_rde_map(os.path.expandvars(
            f'$I3_BUILD/ice-models/resources/models/PPCTABLES/misc/eff-f2k.FTP125max'))
        tray.Add(library.update_dom_eff, rde_map=rde_map, Streams=[icetray.I3Frame.Calibration])
        # rerun for updated calibration errata
        _raw = 'InIceRawData'
        tray.Add('Delete',
                 keys=['CalibratedWaveformRange', 'CalibrationErrata', 'SaturationWindows'],
                 If=lambda f: f.Has(_raw))
        tray.Add(Recalibration.InIceCalibration, InputLaunches=_raw,
                 OutputPulses='InIcePulses_temp',
                 WavedeformSPECorrections=True,
                 If=lambda f: f.Has(_raw))
        tray.Add('Delete', keys=['InIcePulses_temp'])
        tray.Add(druth, hypo='cascade', If=lambda frame: not frame.Has('cc'))
    else:
        tray.Add(truth, hypo='cascade', If=lambda frame: not frame.Has('cc'))
    tray.Add('Delete', keys=['BrightDOMs',
                             'SaturatedDOMs',
                             'DeepCoreDOMs',
                             'CausalQTot'])
    
    tray.AddModule('I3LCPulseCleaning', 'cleaning',
                   OutputHLC=args.pulse_type+'HLC',
                   OutputSLC='', Input=args.pulse_type,
                   If=lambda frame: not frame.Has(args.pulse_type+'HLC'))
    tray.AddModule('VHESelfVeto',
                   Pulses=f"{args.pulse_type}HLC",
                   VetoThreshold=3,
                   VertexThreshold=250,
                   If=lambda frame: not frame.Has('VHESelfVeto'))
    # this only runs if the previous module did not return anything
    tray.AddModule('VHESelfVeto', 'selfveto-emergency-lowen-settings',
                   # usually this is at 250pe - use a much lower setting here to get a seed
                   VertexThreshold=5.,
                   Pulses=f"{args.pulse_type}HLC",
                   OutputBool='VHESelfVeto_meaningless_lowen',
                   OutputVertexTime='VHESelfVetoVertexTime',
                   OutputVertexPos='VHESelfVetoVertexPos',
                   If=lambda frame: (frame.Stop == icetray.I3Frame.Physics) and not frame.Has("VHESelfVeto"))
    tray.AddModule('HomogenizedQTot',
                   Pulses=args.pulse_type,
                   Output='CausalQTot',
                   VertexTime='VHESelfVetoVertexTime')

    Seed = 'L3_MonopodFit4_AmptFit'
    tray.Add(maskdc, origpulses=args.pulse_type, maskedpulses=f'{args.pulse_type}IC',
             If=lambda frame: not frame.Has(f'{args.pulse_type}IC'))
    pulses_for_reco = args.pulse_type if args.idc else f'{args.pulse_type}IC'
    tray.Add(pulse_cleaning,
             Pulses=pulses_for_reco, Residual=args.residual,
             If=lambda frame: not frame.Has(pulses_for_reco+'PulseCleaned'))
    excludedDOMs = tray.Add(HighEnergyExclusions,
                            Pulses=pulses_for_reco,
                            BrightDOMThreshold=args.bdthres,
                            ExcludeDeepCore=False if args.idc else 'DeepCoreDOMs',
                            BadDomsList='BadDomsList',
                            CalibrationErrata='CalibrationErrata',
                            SaturationWindows='SaturationWindows')
    # this isn't placed in by default as SaturatedDOMs are excluded fully
    # here we decide later in the MonopodWrapper
    excludedDOMs.append('SaturationWindows')

    # update millipede_params
    excludedDOMs.append(pulses_for_reco+'PulseCleanedTimeWindows')

    millipede_params = {'Pulses': f'{pulses_for_reco}PulseCleaned',
                        'CascadePhotonicsService': cascade_service,
                        'MuonPhotonicsService': None,
                        'ExcludedDOMs': excludedDOMs,
                        'ReadoutWindow': f'{pulses_for_reco}PulseCleanedTimeRange',
                        'PartialExclusion': True,
                        'UseUnhitDOMs': not args.nouh,
                        'MinTimeWidth': args.mintimewidth,
                        'RelUncertainty': args.relerr}

    tray.Add(wrapperfn,
             f'cscdSBU_MonopodFit4_noDC_ftp_v1',
             Seed=args.seed,
             BrightsFit=args.ibr,
             SaturatedFit=args.isat,
             BadTimeWindowsFit=args.itw,
             Minimizer=args.mini,
             Unfold=args.unfold,
             BinSigma=args.binsigma,
             AmplitudeFit=Seed,
             **millipede_params)

