import numpy
from icecube import dataclasses
def change_names(frame, year): 
    # only call this if year>2011
    obj = frame['cscdSBU_MaxQtotRatio_SplitInIcePulses']
    frame['cscdSBU_MaxQtotRatio_OfflinePulses'] = obj

    obj = frame['cscdSBU_Qtot_SplitInIcePulses']
    frame['cscdSBU_Qtot_OfflinePulses'] = obj

    if frame.Has('cscdSBU_Qtot_SplitInIcePulses_SPEuncorrected'):
        obj = frame['cscdSBU_Qtot_SplitInIcePulses_SPEuncorrected']
        frame['cscdSBU_Qtot_OfflinePulses_SPEuncorrected'] = obj

    obj = frame['cscdSBU_Qtot_SplitInIcePulses_IC']
    frame['cscdSBU_Qtot_OfflinePulses_IC'] = obj

    obj = frame['CascadeLlhVertexFit_L2Params']
    frame['CascadeLlhVertexFitParams'] = obj

    obj = frame['CascadeFillRatio_L2']
    frame['CascadeFillRatio'] = obj

    obj = frame['CascadeLast_L2']
    frame['CascadeLast'] = obj

    if frame.Has('NString_SRTInIcePulses'):
        obj = frame['NString_SRTInIcePulses']
        frame['NString_SRTOfflinePulses'] = obj

    '''
    if year=="2012":
        if frame.Has('CascadeFilter_LFVel'):
            obj = frame['CascadeFilter_LFVel']
            frame['CascadeFilt_LFVel'] = obj
        else:
            frame['CascadeFilt_LFVel'] = dataclasses.I3Double(numpy.nan)

        if frame.Has('CascadeFilter_ToiVal'):
            obj = frame['CascadeFilter_ToiVal']
            frame['CascadeFilt_ToiVal'] = obj
        else:
            frame['CascadeFilt_ToiVal'] = dataclasses.I3Double(numpy.nan)

        #obj = frame['CascadeFilter_CscdLlh']
        #frame['CascadeFilt_CscdLlh'] = obj
    '''

    if True:
        if frame.Has('PoleCascadeFilter_LFVel'):
            obj = frame['PoleCascadeFilter_LFVel']
            frame['CascadeFilt_LFVel'] = obj
        else:
            frame['CascadeFilt_LFVel'] = dataclasses.I3Double(numpy.nan)

        if frame.Has('PoleCascadeFilter_ToiVal'):
            obj = frame['PoleCascadeFilter_ToiVal']
            frame['CascadeFilt_ToiVal'] = obj
        else:
            frame['CascadeFilt_ToiVal'] = dataclasses.I3Double(numpy.nan)
        
        if frame.Has('PoleCascadeFilter_CscdLlh'):
            obj = frame['PoleCascadeFilter_CscdLlh']
            frame['CascadeFilt_CscdLlh'] = obj
        else:
            frame['PoleCascadeFilter_CscdLlh'] = dataclasses.I3Double(numpy.nan)

    return True

def OLDMuonGun2011LE(frame):
    obj = frame['CascadeLlhVertexFit_L2Params']
    frame['CascadeLlhVertexFitParams'] = obj

    obj = frame['CascadeFillRatio_L2']
    frame['CascadeFillRatio'] = obj

    obj = frame['CascadeLast_L2']
    frame['CascadeLast'] = obj

    return True


   

def tobook(datatype):

    keys = ['I3EventHeader', 'cscdSBU_LE_tags', 'cscdSBU_HE_tags', 'cscdSBU_LE_bdt_cascade', 'cscdSBU_LE_bdt_track', 'cscdSBU_LE_bdt_hybrid', 'cscdSBU_LE_bdt_input']
    
    # variable names can change between the years (e.g. L2-variables, OfflinePulses -> SplitInIcePulses
    keys += ['cscdSBU_MonopodFit4', 'cscdSBU_MonopodFit4_noDC', 'cscdSBU_MonopodFit4_final', 'cscdSBU_Veto_OfflinePulses']
    keys += ['cscdSBU_MonopodFit4iFitParams', 'cscdSBU_MonopodFit4_noDCFitParams']
    keys += ['cscdSBU_VetoEarliestLayer', 'cscdSBU_MaxQtotRatio_OfflinePulses', 'cscdSBU_MaxQtotRatio_HLC']
    keys += ['cscdSBU_Qtot_OfflinePulses','cscdSBU_Qtot_OfflinePulses_IC', 'cscdSBU_Qtot_HLC_IC', 'cscdSBU_Qtot_HLC']
    keys += ['cscdSBU_VetoMaxDomChargeOM', 'cscdSBU_VetoMaxDomChargeString', 'cscdSBU_VetoDepthFirstHit']
    keys += ['cscdSBU_MonopodFit4Contained', 'cscdSBU_MonopodFit4_noDCContained']
    keys += ['cscdSBU_MonopodFit4_Delay_ice', 'cscdSBU_MonopodFit4_noDC_Delay_ice', 'cscdSBU_L3Credo_Delay_ice']
    keys += ['cscdSBU_I3XYScale', 'cscdSBU_I3XYScale_noDC']
    keys += ['cscdSBU_L4StartingTrackHLC_cscdSBU_MonopodFit4VetoCharge']
    keys += ['cscdSBU_L4StartingTrackHLC_cscdSBU_MonopodFit4_OfflinePulsesHLC_noDCVetoCharge']
    keys += ['cscdSBU_L4StartingTrackHLC_cscdSBU_MonopodFit4_noDCVetoCharge']
    keys += ['cscdSBU_L4StartingTrackHLC_cscdSBU_MonopodFit4']
    keys += ['cscdSBU_L4StartingTrackHLC_cscdSBU_MonopodFit4_OfflinePulsesHLC_noDC']
    keys += ['cscdSBU_L4StartingTrackHLC_cscdSBU_MonopodFit4_noDC']
    keys += ['cscdSBU_L4VetoTrack_cscdSBU_MonopodFit4VetoCharge', 'cscdSBU_L4VetoTrack_cscdSBU_MonopodFit4_noDCVetoCharge']
    keys += ['cscdSBU_L4VetoTrack_cscdSBU_MonopodFit4', 'cscdSBU_L4VetoTrack_cscdSBU_MonopodFit4_noDC']
    keys += ['cscdSBU_PolygonContTag_cscdSBU_MonopodFit4', 'cscdSBU_PolygonContTag_cscdSBU_MonopodFit4_noDC']
    
    
    # variables from cscd-filter stream
    keys += ['CascadeLlhVertexFitParams', 'CscdL3_Credo_SpiceMie', 'CscdL3_Credo_SpiceMieFitParams', 'PoleMuonLlhFit']
    keys += ['CascadeFilt_CscdLlh', 'CascadeFilt_LFVel', 'CascadeFilt_ToiVal', 'LineFit', 'LineFitParams']
    keys += ['CscdL3_SPEFit16', 'CscdL3_SPEFit16FitParams', 'CascadeFillRatio', 'CscdL3_Cont_Tag']
    keys += ['TimeSplit_CascadeLlhVertexFit_0', 'TimeSplit_CascadeLlhVertexFit_1', 'CascadeLast']
    keys += ['NString_OfflinePulsesHLC', 'NString_SRTOfflinePulses']
    keys += ['NCh_OfflinePulses', 'NCh_OfflinePulsesHLC']
    keys += ['CscdL3_CascadeLlhVertexFit']
    
    # variables for nugen
    if datatype == 'nugen':
        keys += ['I3MCWeightDict', 'CorsikaWeightMap', 'cscdSBU_MCPrimary', 'cscdSBU_AtmWeight_Conv','cscdSBU_AtmWeight_Conv_PassRate','cscdSBU_AtmWeight_Prompt','cscdSBU_AtmWeight_Prompt_PassRate','cscdSBU_AtmWeight_Prompt_berss', 'cscdSBU_MCTruth', 'cscdSBU_MCMuon', 'cscdSBU_MCInIcePrimary']
        sv_muon_thresholds = [1.e2, 1.5e2, 2.e2, 2.5e2, 3.e2, 3.5e2, 4.e2, 4.5e2, 5.e2, 6.e2, 7.e2, 1.e3, 2.e3, 5.e3]
        kaon_fracs = [0.8, 0.9, 1.0, 1.1, 1.2]
        keys += ["cscdSBU_AtmWeight_Conv_kaon%d" %(kaon_frac * 100) for kaon_frac in kaon_fracs]
        keys += ["cscdSBU_AtmWeight_Conv_PassRate_muon%d" %(sv_muon_threshold) for sv_muon_threshold in sv_muon_thresholds]
        keys += ["cscdSBU_AtmWeight_Prompt_PassRate_muon%d" %(sv_muon_threshold) for sv_muon_threshold in sv_muon_thresholds]
    
    # variables for corsika
    if datatype == 'cors':
        keys += ["CorsikaWeightMap", "cscdSBU_mergedGaisserH3a","cscdSBU_mergedGaisserH4a", "cscdSBU_MCPrimary", 'cscdSBU_BundleMultiplicity_depth', 'cscdSBU_BundleMultiplicity_surface', 'cscdSBU_BundleInelasticity_surface', 'cscdSBU_TrackEnergy', 'cscdSBU_MaxBrems_energy']

    # variables for MuonGun
    if datatype == 'muongun':
        keys += ["cscdSBU_MCPrimary", "cscdSBU_MuonWeight_GaisserH4a", "cscdSBU_MCMuon", "cscdSBU_MuonWeight_GaisserH4a_charm"]

    if datatype == 'data':
        keys += ['cscdSBU_Qtot_OfflinePulses_SPEuncorrected']

    return keys


