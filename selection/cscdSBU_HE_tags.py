from icecube import icetray,dataclasses
import numpy


class HE_tags(icetray.I3Module):

    '''
    This module applies the selection described in
    https://wiki.icecube.wisc.edu/index.php/Multi_Year_Cascades#High_Energy_Sample 
    
    Note: no cuts are applied. the cut decisions are stored as flags!
    '''

    def __init__(self,context):
        icetray.I3Module.__init__(self,context)
        self.AddOutBox("OutBox")
        #self.AddParameter("Year", "Specify what year's processing is used ('2011', '2012', etc). Need to anticipate variable names.", None)
        self.tags = {'HE_vars':False, 'HE_above60TEV':False,\
                     'L4_A':False,'L4_B':False,'L4_C':False,'L4_D':False,'L4_E':False,\
                     'L4_F':False,'L4_G':False}

         
    def Configure(self):
        print("configured cscdSBU HE tagging")

        #self.year = self.GetParameter("Year")

        '''
        if self.year == "2011":
                self.cscdllh_name = "CascadeLlhVertexFitParams"
               
        elif (self.year == "2012") or (self.year == "2013") or (self.year == "2014") or (self.year == "2015"):
                self.cscdllh_name = "CascadeLlhVertexFit_L2Params"
              
        else:
                print("can not identify year! please choose a year between 2011 and 2015!")
        '''
        self.cscdllh_name = "CascadeLlhVertexFit_L2Params"
        
    def distance(self, x1, x2, y1, y2, z1, z2):
        return numpy.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)
             

    def check_cuts(self, frame):
        '''
        https://wiki.icecube.wisc.edu/index.php/Multi_Year_Cascades/High_Energy#Level4_Cuts 
        ''' 

        # L4A (PolygonTag)
        if not frame['cscdSBU_PolygonContTag_cscdSBU_MonopodFit4'].value:
                return
        self.tags['L4_A']=True

        # L4B (Monopod.Z)
        if not numpy.abs(frame['cscdSBU_MonopodFit4'].pos.z) < 450.:
                return
        self.tags['L4_B']=True


        # L4C (QtotHLC)
        passed_qtot1 = frame['cscdSBU_Qtot_HLC_IC'].value > 1000.
        passed_qtot2 = numpy.log10(frame['cscdSBU_MonopodFit4'].energy) < numpy.log10(frame['cscdSBU_Qtot_HLC_IC'].value)+1.6
        if not (passed_qtot1 or passed_qtot2):
                return

        self.tags['L4_C']=True

        # L4D (TimeSplitPosition)
        pos1 = frame['TimeSplit_CascadeLlhVertexFit_0'].pos
        pos2 = frame['TimeSplit_CascadeLlhVertexFit_1'].pos
        timesplit = self.distance(pos1.x, pos2.x, pos1.y, pos2.y, pos1.z, pos2.z)
        
        passed_ts1 = timesplit <= 60
        passed_ts2 = numpy.log10(frame['cscdSBU_MonopodFit4'].energy) < -0.01 * timesplit + 5.0
        if not (passed_ts1 or passed_ts2):
                return

        self.tags['L4_D']=True

        # L4E (DelayTime)
        diff = numpy.abs(frame['cscdSBU_MonopodFit4'].pos.z - frame['cscdSBU_VetoDepthFirstHit'].value)
        if diff<15.:
                # assume cascade
                zenith = frame['cscdSBU_MonopodFit4'].dir.zenith
        else:
                # assume track
                zenith = frame['CscdL3_SPEFit16'].dir.zenith

        #passed_highE_upgoing = (frame['cscdSBU_MonopodFit4'].energy >= 600000.) or (numpy.cos(zenith) < 0.2)
        passed_highE_upgoing = (frame['cscdSBU_MonopodFit4'].energy > 600000.) or (numpy.cos(zenith) < 0.2) #correction

        con_a = frame[self.cscdllh_name].ReducedLlh > 7.5
        con_b = timesplit > 40.
        con_c = diff >= 15
        con_d = frame['cscdSBU_L4StartingTrackHLC_cscdSBU_MonopodFit4_OfflinePulsesHLC_noDCVetoCharge'].value >= 4.

        conditions = (con_a&con_b)|(con_a&con_c)|(con_a&con_d)|(con_b&con_c)|(con_b&con_d)|(con_c&con_d)
        passed_delay = (not conditions) or (conditions and (frame['cscdSBU_MonopodFit4_Delay_ice'].value > -200. or numpy.log10(frame['cscdSBU_MonopodFit4'].energy)<4e-3*frame['cscdSBU_MonopodFit4_Delay_ice'].value+5.6)) #correction

        if not (passed_highE_upgoing or passed_delay):
                return

        self.tags['L4_E']=True

        # L4F (MaxDomChargeOM)
        max_dom = frame['cscdSBU_VetoMaxDomChargeOM'].value
        max_string = frame['cscdSBU_VetoMaxDomChargeString'].value

        cond1 = ((max_dom >= 5) and (max_dom < 58)) and (frame['cscdSBU_MonopodFit4'].energy >= 50.e3) and (max_string < 79)
        cond2 = ((max_dom > 8) and (max_dom < 58)) and (frame['cscdSBU_MonopodFit4'].energy < 50.e3) and (max_string < 79)
        
        # don't cut the DeepCore cap!
        cond3 = (max_dom < 58) and (max_string >= 79)

        if not ((cond1 or cond2) or cond3):
                return

        self.tags['L4_F']=True

        # L4G (StartingTrackCharge)        
        cond1 = (frame['cscdSBU_L4StartingTrackHLC_cscdSBU_MonopodFit4_OfflinePulsesHLC_noDCVetoCharge'].value <= 4.) or (frame['cscdSBU_MonopodFit4'].energy > 6.e5)
        cond2 = numpy.log10(frame['cscdSBU_MonopodFit4'].energy) > (frame['cscdSBU_L4StartingTrackHLC_cscdSBU_MonopodFit4_OfflinePulsesHLC_noDCVetoCharge'].value * 0.1 + 4.4)
        if not (cond1 or cond2):
                return

        self.tags['L4_G']=True

        # if the event survives all cuts it makes it into the sample ;-)
        self.tags['HE_vars']=True        
        
        return


    def Physics(self,frame):

        # clear all tags!
        for key in list(self.tags.keys()):
                self.tags[key]=False

        # check first if required recos are avail
        passed_reco = frame['cscdSBU_MonopodFit4'].fit_status == dataclasses.I3Particle.FitStatus.OK
        if not passed_reco:
                # event can not pass anything. no need to check.
                self.PushFrame(frame)
                return True

        self.check_cuts(frame)
        if frame['cscdSBU_MonopodFit4'].energy >= 6.e4:
                self.tags['HE_above60TEV'] = True        

        map = dataclasses.I3MapStringBool(self.tags)
        frame['cscdSBU_HE_tags']=map
        
        self.PushFrame(frame)
        return True

