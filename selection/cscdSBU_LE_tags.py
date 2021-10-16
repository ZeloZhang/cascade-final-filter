from icecube import icetray,dataclasses
import xgboost
import pickle
import numpy
import re

class LE_tags(icetray.I3Module):

    '''
    This module applies the selection described in
    https://wiki.icecube.wisc.edu/index.php/Multi_Year_Cascades#Low_Energy_Sample
    
    Note: no cuts are applied. the cut decisions are stored as flags!
    '''

    def __init__(self,context):
        icetray.I3Module.__init__(self,context)
        self.AddOutBox("OutBox")
        #self.AddParameter("Year", "Specify what year's processing is used ('2011', '2012', etc). Need to anticipate variable names.", None)
        self.tags = {'LE_L3A':False, 'LE_L3B':False, 'LE_L3C':False, 'LE_L3D':False, \
                'LE_L3all': False, 'LE_L4A': False, 'LE_neutrino': False, 'LE_cascade': False, 'LE_hybrid': False, \
                'LE_muon': False, 'LE_below60TEV': False}
         
    def Configure(self):
        print("configured cscdSBU LE tagging")

        #self.year = self.GetParameter("Year")
        '''
        if self.year == "2011":
                self.cscdllh_name = "CascadeLlhVertexFitParams"

        elif (self.year == "2012") or (self.year == "2013") or (self.year == "2014") or (self.year == "2015"):
                self.cscdllh_name = "CascadeLlhVertexFit_L2Params"

        else:
                print("can not identify CascadeLlhVertexFitParams! please choose a year between 2011 and 2015!")
                self.cscdllh_name = None # cause crash downstream
        '''
        self.cscdllh_name = "CascadeLlhVertexFit_L2Params"

    def check_L3A(self, frame):
        '''
        https://wiki.icecube.wisc.edu/index.php/Multi_Year_Cascades/Low_Energy#L3A_.28Anti-Dust-Layer.29
        ''' 

        var1 = frame['cscdSBU_VetoMaxDomChargeOM'].value
        cut11 = 30
        cut12 = 39

        var2 = frame[self.cscdllh_name].ReducedLlh
        cut2 = 9.1
        cut22 = 7.5

        var3 = frame['cscdSBU_MonopodFit4_noDC'].pos.z
        cut31 = 50.
        cut32 = -200.

        var4 = frame['cscdSBU_Qtot_HLC'].value
        cut4 = 200. 

        passed_cuts = (var2<cut2)&((var1<=cut11)|(var1>=cut12)|(var2<cut22)|((var3<=cut31)&(var3>=cut32))|(var4>cut4))

        if passed_cuts:
                self.tags['LE_L3A']=True

        return


    def check_L3B(self, frame):
        '''
        https://wiki.icecube.wisc.edu/index.php/Multi_Year_Cascades/Low_Energy#L3B_.28Containment.29
        '''

        var1 = frame['cscdSBU_MonopodFit4_noDC'].pos.z
        cut11 = 500.
        cut12 = -500.

        var2 = frame['cscdSBU_I3XYScale_noDC'].value
        cut2 = 1.0
        cut22 = 1.1

        var3 = frame[self.cscdllh_name].ReducedLlh
        cut3 = 7.6

        passed_cuts = ((var1<cut11)&(var1>cut12)&(var2<cut22))&((var2<cut2)|(var3<cut3))

        if passed_cuts:
                self.tags['LE_L3B']=True
         
        return


    def check_L3C(self, frame):
        '''
        https://wiki.icecube.wisc.edu/index.php/Multi_Year_Cascades/Low_Energy#L3C_.28Anti-Top-Bottom.29
        '''

        var3 = frame['cscdSBU_VetoMaxDomChargeOM'].value
        cut31 = 10
        cut32 = 56
        cut33 = 59

        var2 = frame[self.cscdllh_name].ReducedLlh
        cut22 = 7.5

        var1 = frame['cscdSBU_MonopodFit4_noDC'].pos.z
        cut11 = -450.
        cut12 = 360.

        passed_cuts = (var3<cut33)&((var3>cut31)&(var3<cut32)|(var2<cut22))&((var1>cut11)&(var1<cut12))
        
        if passed_cuts:
                self.tags['LE_L3C']=True

        return



    def check_L3D(self, frame):
        '''
        https://wiki.icecube.wisc.edu/index.php/Multi_Year_Cascades/Low_Energy#L3D_.28DelayTime.29
        '''

        var1 = frame['cscdSBU_MonopodFit4_noDC_Delay_ice'].value
        cut1 = -3000.
        cut12 = 125.
        cut13 = -5000.

        var2 = frame['cscdSBU_I3XYScale_noDC'].value
        cut21 = 0.35
        cut22 = 0.80

        passed_cuts = (var1<cut12)&((var1>cut1)|((var2>cut21)&(var2<cut22)))&(var1>cut13)
        
        if passed_cuts:
                self.tags['LE_L3D']=True
        
        return True

    def check_L3all(self, frame):

        self.check_L3A(frame)
        self.check_L3B(frame)
        self.check_L3C(frame)
        self.check_L3D(frame)
        if self.tags['LE_L3A'] and self.tags['LE_L3B'] \
        and self.tags['LE_L3C'] and self.tags['LE_L3D']:
                self.tags['LE_L3all']=True

    def check_L4A(self, frame):
        '''
        https://wiki.icecube.wisc.edu/index.php/Multi_Year_Cascades/Low_Energy#Level_4A_.28Further_Cleaning.29
        '''
        var1 = frame['cscdSBU_MonopodFit4'].pos.z
        cut11 = -135.
        cut12 = -85.
        
        is_dustlayer = (var1>cut11)&(var1<cut12)

        var2 = frame['cscdSBU_MonopodFit4'].energy
        cut2 = 3.e3 

        # want at least 4 strings above 3 TeV
        # official cscd-L3 ensures at least 3 strings

        var3 = frame['NString_OfflinePulsesHLC'].value
        cut3 = 3.0

        passed_strings = (var2<cut2)|((var2>=cut2)&(var3>cut3))

        # Qtot IC > 100 p.e.
        var4 = frame['cscdSBU_Qtot_HLC_IC'].value
        cut4 = 100.
        passed_qtot = var4 > cut4

        if passed_strings and (not is_dustlayer) and passed_qtot:
                self.tags['LE_L4A']=True

        return

    def check_neutrino(self, frame):
        '''
        https://wiki.icecube.wisc.edu/index.php/Multi_Year_Cascades/Low_Energy#Level_4_.28BDT_scores.29
        '''
        
        # https://wiki.icecube.wisc.edu/index.php/Multi_Year_Cascades/Low_Energy#Level_4B_.28BDT.hybrid.29
        cond1 = frame['cscdSBU_LE_bdt_hybrid'].value > 0.75
        
        
        # https://wiki.icecube.wisc.edu/index.php/Multi_Year_Cascades/Low_Energy#Level_4C_.28BDT.cascade.29
        cascade_cut = 1.-(0.25+1./(1.539+numpy.exp(-5.*(numpy.log10(frame['cscdSBU_MonopodFit4'].energy)-4.1))))
        cond2 = frame['cscdSBU_LE_bdt_cascade'].value > cascade_cut

        # https://wiki.icecube.wisc.edu/index.php/Multi_Year_Cascades/Low_Energy#Level_4D_.28BDT.track.29
        cond3 = frame['cscdSBU_LE_bdt_track'].value < 0.15

        if (cond1 or cond2 or cond3):
                self.tags['LE_neutrino'] = True        
                if frame['cscdSBU_LE_bdt_hybrid'].value >= 0.75:
                        self.tags['LE_hybrid'] = True
                else:
                        self.tags['LE_cascade'] = True
        return True

    def check_background(self, frame):
        '''
        https://wiki.icecube.wisc.edu/index.php/Multi_Year_Cascades/Low_Energy#Level_5_.28Muon_Background_Sample.29
        '''
        if (frame['cscdSBU_LE_bdt_cascade']>0.1) and (not self.tags['LE_neutrino']):
                self.tags['LE_muon']=True
        return True
 
    def check_final(self, frame):
        # check higher Level if all L3 has passed
        if self.tags['LE_L3all']:
                self.check_L4A(frame)

                # check classifier only if L4A passed        
                if self.tags['LE_L4A']:
                        self.check_neutrino(frame)
                        self.check_background(frame)

        # check whether event is above 60 TeV and should be excluded from this selection
        if frame['cscdSBU_MonopodFit4'].energy < 6.e4:
                self.tags['LE_below60TEV'] = True
        return 
    

    def Physics(self,frame):

        # clear all tags!
        for key in list(self.tags.keys()):
                self.tags[key]=False

        # check first if required recos are avail
        passed_reco = (frame['LineFit'].fit_status == dataclasses.I3Particle.FitStatus.OK)&(frame['cscdSBU_MonopodFit4_noDC'].fit_status == dataclasses.I3Particle.FitStatus.OK)
        if not passed_reco:
                # event can not pass anything. no need to check.
                self.PushFrame(frame)
                return True

        self.check_L3all(frame)
        self.check_final(frame)

        map = dataclasses.I3MapStringBool(self.tags)
        frame['cscdSBU_LE_tags']=map
        
        self.PushFrame(frame)
        return True

