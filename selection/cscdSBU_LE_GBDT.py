from icecube import icetray,dataclasses
import xgboost
import pickle
import numpy
import re
import glob

class LE_GBDT(icetray.I3Module):
    '''
    apply the GBDT classifier described here:
    https://wiki.icecube.wisc.edu/index.php/Multi_Year_Cascades/Low_Energy#Multi-Class_BDT
    '''

    def __init__(self,context):
        icetray.I3Module.__init__(self,context)
        self.AddOutBox("OutBox")
        #self.AddParameter("Year", "Specify what year's processing is used ('2011', '2012', etc). Need to anticipate variable names.", None)
         
        # access xgboost GBDT model
        if glob.glob("/data/user/hmniederhausen/mariola/test/models/bdt_full.xgb"):
            self.bdt = pickle.load( open( "/data/user/hmniederhausen/mariola/test/models/bdt_full.xgb", "rb" ) )
        elif glob.glob("./bdt_full.xgb"):
            self.bdt = pickle.load(open("./bdt_full.xgb"))
        elif glob.glob("/cvmfs/icecube.opensciencegrid.org/users/zzhang1/trained_bdt/bdt_full.xgb"):
            self.bdt = pickle.load(open("/cvmfs/icecube.opensciencegrid.org/users/zzhang1/trained_bdt/bdt_full.xgb"))
        else:
            print("missing trained bdt")
        '''

        if glob.glob("/data/user/zzhang1/pass2_GlobalFit/code/check_lowe_upgoing/trainning_selection_bdt/models/bdt_full_testing.xgb"):
            print("using new bdt model")
            self.bdt = pickle.load(open("/data/user/zzhang1/pass2_GlobalFit/code/check_lowe_upgoing/trainning_selection_bdt/models/bdt_full_testing.xgb"))
        elif glob.glob("./bdt_full_pass2.xgb"):
            self.bdt = pickle.load(open("./bdt_full_pass2.xgb"))
        elif glob.glob("/cvmfs/icecube.opensciencegrid.org/users/zzhang1/trained_bdt/bdt_full_pass2.xgb"):
            self.bdt = pickle.load(open("/cvmfs/icecube.opensciencegrid.org/users/zzhang1/trained_bdt/bdt_full_pass2.xgb"))
        else:
            print("missing trained bdt")
        '''
        
        # explicitlely use 2011 variable names for reference 
        self.variables = ['CascadeLlhVertexFitParams_rlogL', 'cscdSBU_MonopodFit4_noDC_Delay_ice_value', 'cscdSBU_MonopodFit4_noDC_z', 'cscdSBU_Qtot_HLC_log_value', 'cscdSBU_VertexRecoDist_CscdLLh', 'cscdSBU_I3XYScale_noDC_value', 'cscdSBU_L4StartingTrackHLC_cscdSBU_MonopodFit4_noDCVetoCharge_value', 'cscdSBU_L4VetoTrack_cscdSBU_MonopodFit4_noDCVetoCharge_value', 'cscdSBU_VetoDepthFirstHit_value', 'CscdL3_SPEFit16_zenith', 'LineFit_zenith', 'CscdL3_SPEFit16FitParams_rlogl', 'cscdSBU_MonopodFit4_noDC_zenith']

        # BDT only knows legacy variable names. Do not change!
        self.names = [re.sub(r'[^a-zA-Z0-9]','', name) for name in ['CascadeLlhVertexFitParams_rlogL', 'HMN_HMN_MonopodFit4_noDC_Delay_ice_value', 'HMN_MonopodFit4_noDC_z', 'HMN_Qtot_HLC_log_value', 'HMN_VertexRecoDist_CscdLLh', 'HMN_I3XYScale_noDC_value', 'HMN_L4StartingTrackHLC_HMN_MonopodFit4_noDCVetoCharge_value', 'HMN_L4VetoTrack_HMN_MonopodFit4_noDCVetoCharge_value', 'HMN_VetoDepthFirstHit_value', 'CscdL3_SPEFit16_zenith', 'LineFit_zenith', 'CscdL3_SPEFit16FitParams_rlogl', 'HMN_MonopodFit4_noDC_zenith']]

    def Configure(self):
        print("configured cascade multi-class BDT")
        '''
        self.year = self.GetParameter("Year")

        if self.year == "2011":
                self.cscdllh_name = "CascadeLlhVertexFitParams"
                
        elif (self.year == "2012") or (self.year == "2013") or (self.year == "2014") or (self.year == "2015"):
                self.cscdllh_name = "CascadeLlhVertexFit_L2Params"
                
        else:
                print("can not identify CascadeLlhVertexFitParams! please choose a year between 2011 and 2015!")
                self.cscdllh_name = None # cause crash downstream
        '''
        self.cscdllh_name = "CascadeLlhVertexFit_L2Params"
                
        
   
    def distanceXY(self, x1, x2, y1, y2):
        return numpy.sqrt((x2-x1)**2+(y2-y1)**2)

    def Physics(self,frame):

        # first check if fits are ok. otherwise set bdt.vars to nan and go to next frame
        if (not frame['LineFit'].fit_status==dataclasses.I3Particle.FitStatus.OK) or (not frame['cscdSBU_MonopodFit4_noDC'].fit_status==dataclasses.I3Particle.FitStatus.OK):
                frame['cscdSBU_LE_bdt_track'] = dataclasses.I3Double(numpy.nan)
                frame['cscdSBU_LE_bdt_cascade'] = dataclasses.I3Double(numpy.nan)
                frame['cscdSBU_LE_bdt_hybrid'] = dataclasses.I3Double(numpy.nan)
                self.PushFrame(frame)
                return True
                

        # need to calculate/retrieve variables 
        cscdrlogl = frame[self.cscdllh_name].ReducedLlh
        delaytime = frame['cscdSBU_MonopodFit4_noDC_Delay_ice'].value
        monopodz = frame['cscdSBU_MonopodFit4_noDC'].pos.z
        logqtot = numpy.log10(frame['cscdSBU_Qtot_HLC'].value)

        pos1 = frame['CscdL3_CascadeLlhVertexFit'].pos # needed to calculate vertexrecodist
        pos2 = frame['cscdSBU_MonopodFit4_noDC'].pos # needed to calculate vertexrecodist

        vertexrecodist = self.distanceXY(pos1.x, pos2.x, pos1.y, pos2.y)
        xyscale = frame['cscdSBU_I3XYScale_noDC'].value
        startingtrackcharge = frame['cscdSBU_L4StartingTrackHLC_cscdSBU_MonopodFit4_noDCVetoCharge'].value
        vetotrackcharge = frame['cscdSBU_L4VetoTrack_cscdSBU_MonopodFit4_noDCVetoCharge'].value
        depthfirsthit = frame['cscdSBU_VetoDepthFirstHit'].value
        spezenith = frame['CscdL3_SPEFit16'].dir.zenith
        linefitzenith = frame['LineFit'].dir.zenith
        sperlogl = frame['CscdL3_SPEFit16FitParams'].rlogl
        monopodzenith = frame['cscdSBU_MonopodFit4_noDC'].dir.zenith

        values = [cscdrlogl, delaytime, monopodz, logqtot, vertexrecodist, xyscale, startingtrackcharge, vetotrackcharge, depthfirsthit, spezenith, linefitzenith, sperlogl, monopodzenith]

        map = dict(list(zip(self.variables, values)))

        # store BDT input variables separately in frame
        frame['cscdSBU_LE_bdt_input']=dataclasses.I3MapStringDouble(map)
 
        inputdata = numpy.column_stack(values)

        xgmat_data = xgboost.DMatrix(inputdata, feature_names = self.names)
        scores = self.bdt.predict(xgmat_data)        

        frame['cscdSBU_LE_bdt_track']=dataclasses.I3Double(float(scores[:,0][0]))
        frame['cscdSBU_LE_bdt_cascade']=dataclasses.I3Double(float(scores[:,1][0]))
        frame['cscdSBU_LE_bdt_hybrid']=dataclasses.I3Double(float(scores[:,2][0]))
        #bdt_output = {'bdt_track': dataclasses.I3Double(float(scores[:,0][0])), 'bdt_cascade':dataclasses.I3Double(float(scores[:,1][0])), 'bdt_hybrid':dataclasses.I3Double(float(scores[:,2][0]))} 
        #frame['cscdSBU_LE_bdt_output']=dataclasses.I3MapStringDouble(bdt_output)  
 
        self.PushFrame(frame)
        return True

