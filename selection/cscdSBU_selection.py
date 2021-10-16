from I3Tray import *
from icecube import icetray, dataclasses
from icecube.icetray import traysegment

from cscdSBU_LE_GBDT import LE_GBDT
from cscdSBU_LE_tags import LE_tags
from cscdSBU_HE_tags import HE_tags

import numpy

@icetray.traysegment
def selection(tray, name, selection='None'):
        # selection = 'None', 'cascade', 'hybrid', 'muon'

        '''
        implement the Multi-Year Cascade event selection described in
        https://wiki.icecube.wisc.edu/index.php/Multi_Year_Cascades

        cut = True: removes events that don't make it into final cascade selections (LE or HE)
        '''
        # In contrast to pass1, the variable names are uniform for each year.

        tray.AddModule(LE_GBDT, "bdt") 
        tray.AddModule(LE_tags, "tags_LE")
        tray.AddModule(HE_tags, "tags_HE")
        
        def keep_cascades(frame):
                # remove all events that have failed recos:
                passed_reco = (frame['LineFit'].fit_status == dataclasses.I3Particle.FitStatus.OK)&(frame['cscdSBU_MonopodFit4_noDC'].fit_status == dataclasses.I3Particle.FitStatus.OK)
                if not passed_reco:
                        return False

                # keep if event is part of LE cascades
                if frame['cscdSBU_LE_tags']['LE_cascade'] and frame['cscdSBU_LE_tags']['LE_below60TEV']:
                        return True
                
                # keep if event is part of HE cascades
                if frame['cscdSBU_HE_tags']['HE_vars'] and frame['cscdSBU_HE_tags']['HE_above60TEV']:
                        return True

                # cut event otherwise
                return False

        def keep_hybrids(frame):
                # remove all events that have failed recos:
                passed_reco = (frame['LineFit'].fit_status == dataclasses.I3Particle.FitStatus.OK)&(frame['cscdSBU_MonopodFit4_noDC'].fit_status == dataclasses.I3Particle.FitStatus.OK)
                if not passed_reco:
                        return False

                # keep event if below 60 TeV and hybrid
                if frame['cscdSBU_LE_tags']['LE_hybrid'] and frame['cscdSBU_LE_tags']['LE_below60TEV']:
                        return True
                # cut event otherwise:
                return False

        def keep_muons(frame):
                # remove all events that have failed recos:
                passed_reco = (frame['LineFit'].fit_status == dataclasses.I3Particle.FitStatus.OK)&(frame['cscdSBU_MonopodFit4_noDC'].fit_status == dataclasses.I3Particle.FitStatus.OK)
                if not passed_reco:
                        return False
                # keep event if below 60 TeV and muon
                if frame['cscdSBU_LE_tags']['LE_muon'] and frame['cscdSBU_LE_tags']['LE_below60TEV']:
                        return True
                # cut event otherwise
                return False

        if selection=='cascade':
                tray.AddModule(keep_cascades, "cut_backgrounds")

        if selection=='hybrid':
                tray.AddModule(keep_hybrids, "cut_backgrounds")

        if selection=='muon':
                tray.AddModule(keep_muons, "cut_backgrounds")


@icetray.traysegment
def selection_mlb(tray, name, year):

        def select(frame):
                # IC79, IC86-2011
                
                # 10 TeV cut
                if not ( frame['cscdSBU_MonopodFit4'].energy > 1.e4 ):
                        return False

                # VetoDepthFH 430m
                vetodepth = frame['cscdSBU_VetoDepthFirstHit'].value
                if not ( vetodepth>-430. and vetodepth<430. ):
                        return False

                # earliest Layer <= 4 (not needed, part of Cascade-L3 cuts)

                # 58>= MaxChargeDOM >= 8 
                vetodom = frame['cscdSBU_VetoMaxDomChargeOM'].value
                if not ( vetodom>=8. and vetodom<=58. ):
                        return False

                # Monopod.Z 450m
                recoz = frame['cscdSBU_MonopodFit4'].pos.z
                if not ( recoz>-450. and recoz<450. ):
                        return False

                # Polygon Cont Tag
                if not ( frame['cscdSBU_PolygonContTag_cscdSBU_MonopodFit4'].value >= 0.5 ):
                        return False

                # NString >= 4
                if not ( frame['NString_OfflinePulsesHLC'].value >= 4):
                        return False

                # TimeSplitPos <= 40
                # calculate TimeSplitPosition

                def distance(x1, x2, y1, y2, z1, z2):
                        return dataclasses.I3Double(numpy.sqrt((x2-x1)**2+(y2-y1)**2+(z2-z1)**2))

                x1 = frame['TimeSplit_CascadeLlhVertexFit_0'].pos.x
                y1 = frame['TimeSplit_CascadeLlhVertexFit_0'].pos.y
                z1 = frame['TimeSplit_CascadeLlhVertexFit_0'].pos.z
                x2 = frame['TimeSplit_CascadeLlhVertexFit_1'].pos.x
                y2 = frame['TimeSplit_CascadeLlhVertexFit_1'].pos.y
                z2 = frame['TimeSplit_CascadeLlhVertexFit_1'].pos.z
                frame['cscdSBU_TimeSplitPosition'] = distance(x1, x2, y1, y2, z1, z2)        
                if not ( frame['cscdSBU_TimeSplitPosition'].value <= 40. ):
                        return False

                # MaxQtotRatio < 0.35
                if not ( frame['cscdSBU_MaxQtotRatio_OfflinePulses'].value < 0.35 ):
                        return False

                # cscd.rlogl < 7.5
                if not ( frame['CascadeLlhVertexFitParams'].ReducedLlh<7.5 ):
                        return False

                # Log10(Qtot) > 2.45
                if not ( numpy.log10(frame['cscdSBU_Qtot_OfflinePulses'].value)>2.45 ):
                        return False

                # delaytime
                if frame['cscdSBU_MonopodFit4'].energy < 6.e5:
                        if not ( frame['cscdSBU_MonopodFit4_Delay_ice'].value>-100 ):
                                return False


                return True

        tray.AddModule(select, "select0r1z0r")
