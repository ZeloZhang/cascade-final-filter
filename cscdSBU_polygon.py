def ContainmentCut(tray, name, ic_config, Pulses="TWOfflinePulsesHLC", Vertex="CscdL3_Credo_SpiceMie"):
    """
    Tag reasonably contained events. Not actually a cut.
    """
    from icecube import icetray, dataclasses    
    if ic_config == "IC79":
        from mlb_CutParamsIC79 import ContainmentCut, RingClassifier
    elif ic_config == "IC86":
        from mlb_CutParamsIC86 import ContainmentCut, RingClassifier
 
    vertex_tag = Vertex+"Contained"
    pulse_tag = Pulses+"MaxQRing"
    final_tag = "cscdSBU_PolygonContTag_"+Vertex
    
    tray.AddModule(ContainmentCut, name+'_PolygonCut',
                       Vertex=Vertex, Output=vertex_tag)
   
   
    tray.AddModule(RingClassifier, name+"_RingClassifier",
                       Pulses=Pulses, Output=pulse_tag)
    
    def define_containment(frame):
        vertex = frame[vertex_tag]
        ring = frame[pulse_tag]
        inside = vertex.value and ring.value < 3
        frame[final_tag] = icetray.I3Bool(inside)
        return True
    
    tray.AddModule(define_containment, name+"_Combiner")
    

