from icecube import icetray,dataclasses
from I3Tray import *

@icetray.traysegment
def addvars(tray, name, ic_config, pulses='OfflinePulses'):

    # add Qtot/MaxQtotRatio calculations
    from cscdSBU_misc import misc
    tray.AddSegment(misc, 'misc', pulses=pulses)
    
    # add outer layer veto related variables  
    from icecube import CascadeVariables
    from icecube import phys_services
    load("CascadeVariables")
    tray.AddModule("I3VetoModule", "Veto_Common_Off",
                   HitmapName=pulses,
                   OutputName="cscdSBU_Veto_OfflinePulses",
                   DetectorGeometry=int(ic_config[-2:]),
                   useAMANDA=False,
                   FullOutput=True,
                   ) 

    def veto(frame):
            if frame.Has('Veto_SRTOfflinePulses'):
               veto = frame['Veto_SRTOfflinePulses']
            else:
               veto = frame['Veto_SRTInIcePulses']
            frame['cscdSBU_VetoDepthFirstHit'] = dataclasses.I3Double(veto.depthFirstHit)
            frame['cscdSBU_VetoEarliestLayer'] = dataclasses.I3Double(veto.earliestLayer) 
            
            vetoOff = frame['cscdSBU_Veto_OfflinePulses']
            frame['cscdSBU_VetoMaxDomChargeOM'] = dataclasses.I3Double(vetoOff.maxDomChargeOM)
            frame['cscdSBU_VetoMaxDomChargeString'] = dataclasses.I3Double(vetoOff.maxDomChargeString)
  
            return True

    tray.AddModule(veto, "veto")

    # add Achim's I3Scale Variable
    from cscdSBU_I3Scale import I3Scale
    tray.AddModule(I3Scale,"icecubescale",
                   vertex        = "cscdSBU_MonopodFit4",
                   geometry      = "I3Geometry",
                   ic_config     = ic_config,
                   outputname    = "cscdSBU_I3XYScale"
                   )
   
    tray.AddModule(I3Scale,"icecubescale2",
                   vertex        = "cscdSBU_MonopodFit4_noDC",
                   geometry      = "I3Geometry",
                   ic_config     = ic_config,
                   outputname    = "cscdSBU_I3XYScale_noDC"
                   )

    # add Jakobs Track Charges
    sys.path.append(os.path.expandvars('$I3_BUILD/CascadeL3_IC79/resources/level4'))
    import common 
    tray.AddSegment(common.TrackVetoes, "pulses_all", vertex='cscdSBU_MonopodFit4')
    tray.AddSegment(common.TrackVetoes_noDC, "pulses_noDC", vertex='cscdSBU_MonopodFit4')
    #tray.AddSegment(common.TrackVetoes_noDC, "pulses_noDC", vertex='cscdSBU_MonopodFit4',safety_margin=60)
    tray.AddSegment(common.TrackVetoes, "pulses_all_monopod_noDC", vertex='cscdSBU_MonopodFit4_noDC')

    # add Mariola variables
    from cscdSBU_polygon import ContainmentCut
    tray.AddSegment(ContainmentCut, 'Containment_Monopod4', Vertex="cscdSBU_MonopodFit4", ic_config=ic_config)
    from cscdSBU_polygon import ContainmentCut
    tray.AddSegment(ContainmentCut, 'Containment_Monopod4_noDC', Vertex="cscdSBU_MonopodFit4_noDC", ic_config=ic_config)
    
    from mlb_DelayTime_noNoise import calc_dt_nearly_ice 
    # calculate delay time with new monopod
    tray.AddModule(calc_dt_nearly_ice,'delaytime_monopod',name='cscdSBU_MonopodFit4',
                   reconame='cscdSBU_MonopodFit4',pulsemapname='OfflinePulsesHLC_noSaturDOMs')
    tray.AddModule(calc_dt_nearly_ice,'delaytime_monopod_noDC',name='cscdSBU_MonopodFit4_noDC',
                   reconame='cscdSBU_MonopodFit4_noDC',pulsemapname='OfflinePulsesHLC_noSaturDOMs')
