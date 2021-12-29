from icecube import icetray,dataclasses,phys_services,dataio
from icecube.icetray import traysegment

from icecube import MuonGun, simclasses
from icecube.weighting import weighting
from icecube.weighting.fluxes import GaisserH3a,GaisserH4a, Hoerandel5
from icecube.weighting.weighting import Hoerandel, I3Units
from icecube.weighting.weighting import from_simprod
from icecube.weighting.__init__ import get_weighted_primary
import math
import numpy 

from icecube import NewNuFlux
from icecube.weighting import fluxes, get_weighted_primary


@icetray.traysegment
def weights(tray, name, nfile, infiles, datatype, year):
    # datatype = 'cors', 'muongun', 'nugen'

    if datatype == 'nugen':
        # regenerate different SV assumptions, conventional kaon fractions
        kaon_fracs = [0.8, 0.9, 1.0, 1.1, 1.2]
        hondas = [NewNuFlux.makeFlux('honda2006') for kaon_frac in kaon_fracs]

        # sv thresholds
        sv_muon_thresholds = [1.e2, 1.5e2, 2.e2, 2.5e2, 3.e2, 3.5e2, 4.e2, 4.5e2, 5.e2, 6.e2, 7.e2, 1.e3, 2.e3, 5.e3] # in GeV
        
        for obj in zip(kaon_fracs, hondas):
            kaon_frac, honda = obj
            honda.knee_reweighting_model = 'gaisserH3a_elbert'
            honda.relative_kaon_contribution = kaon_frac

        def saveAtmWeight(frame): 
            p = frame['cscdSBU_MCPrimary']

            honda_weights = [honda.getFlux(p.type, p.energy, math.cos(p.dir.zenith)) for honda in hondas]
            
            for obj in zip(kaon_fracs, honda_weights):
                kaon_frac, conv = obj
                frame["cscdSBU_AtmWeight_Conv_kaon%d" %(kaon_frac * 100.)]=dataclasses.I3Double(conv)

            # passing rate calculation
            from icecube.AtmosphericSelfVeto import AnalyticPassingFraction
            particleType = p.pdg_encoding
            conventional_vetos = [AnalyticPassingFraction('conventional', veto_threshold=muon_thresh) for muon_thresh in sv_muon_thresholds]
            prompt_vetos = [AnalyticPassingFraction('charm', veto_threshold=muon_thresh) for muon_thresh in sv_muon_thresholds]

            # add penetrating depth dependence
            from icecube import MuonGun, simclasses
            surface = MuonGun.Cylinder(1000, 500)
            d = surface.intersection(p.pos, p.dir)
            getDepth=p.pos + d.first*p.dir
            impactDepth = MuonGun.depth((p.pos + d.first*p.dir).z)*1.e3
            conv_passing_fractions = [conv_veto(particleType, enu=p.energy, ct=math.cos(p.dir.zenith), depth=impactDepth) for conv_veto in conventional_vetos]
            prompt_passing_fractions = [prompt_veto(particleType, enu=p.energy, ct=math.cos(p.dir.zenith), depth=impactDepth) for prompt_veto in prompt_vetos]
            for obj in zip(sv_muon_thresholds, conv_passing_fractions, prompt_passing_fractions):
                sv_muon_threshold, conv_passing_fraction, prompt_passing_fraction = obj
                frame["cscdSBU_AtmWeight_Conv_PassRate_muon%d" %(sv_muon_threshold)] = dataclasses.I3Double(conv_passing_fraction.item(0))
                frame["cscdSBU_AtmWeight_Prompt_PassRate_muon%d" %(sv_muon_threshold)] = dataclasses.I3Double(prompt_passing_fraction.item(0))

        tray.AddModule(saveAtmWeight,'saveAFlux')

    if datatype == 'cors':
        if year=='2011':
                s9622=weighting.from_simprod(9622)
                s10309=weighting.from_simprod(10309)
                s10282=weighting.from_simprod(10282)
                s10475=weighting.from_simprod(10475)
                s10651=weighting.from_simprod(10651)
                s10784=weighting.from_simprod(10784)
                s10899=weighting.from_simprod(10899)        
                gensum=s9622*99000+s10309*10000+s10282*10000+s10475*19435+s10651*19996+s10784*19992+s10899*19883        

        elif year=='2012':
                # need to first process 2012 CORSIKA
                s11057=weighting.from_simprod(11057)
                s11362=weighting.from_simprod(11362)
                s11499=weighting.from_simprod(11499)
                s11637=weighting.from_simprod(11637)
                s11808=weighting.from_simprod(11808)
                s11865=weighting.from_simprod(11865)
                s11905=weighting.from_simprod(11905)
                s11926=weighting.from_simprod(11926)
                s11937=weighting.from_simprod(11937)
                s11943=weighting.from_simprod(11943)
                gensum=s11057*99979+s11362*49762+s11499*99495+s11637*99677+s11808*99821+s11865*99895+s11905*99941+s11926*99940+s11937*99941+s11943*99951

        else:
                print("YEAR NOT SUPPORTED YET!")
       
      
        def getMergedWeight(frame):
            flux=GaisserH3a()
            flux2=GaisserH4a()

            get_weighted_primary(frame,"cscdSBU_MCPrimary")
            energy=frame['cscdSBU_MCPrimary'].energy
            ptype=frame['cscdSBU_MCPrimary'].type

            if math.isnan(flux(energy, ptype)) or math.isnan(gensum(energy,ptype)) or gensum(energy,ptype)==0:
                print("Flux: %f Generator: %f " % (flux(energy, ptype), gensum(energy,ptype)))

            weight = flux(energy,ptype)/gensum(energy,ptype)
            weight2 = flux2(energy,ptype)/gensum(energy,ptype)


            frame['cscdSBU_mergedGaisserH3a'] = dataclasses.I3Double(weight)
            frame['cscdSBU_mergedGaisserH4a'] = dataclasses.I3Double(weight2)

            return True

        tray.AddModule(getMergedWeight,'getMerged')

        def bundle_multiplicity(frame):
                deep_bundle = MuonGun.muons_at_surface(frame, MuonGun.Cylinder(1000, 500))
                frame['cscdSBU_BundleMultiplicity_depth'] = icetray.I3Int(len(deep_bundle))
                return True

        #tray.AddModule(bundle_multiplicity, "bundles_counter")

        def bundle_surface(frame):
                frame['cscdSBU_BundleMultiplicity_surface'] = icetray.I3Int(len([track for track in frame['MMCTrackList'] if track.Ei>0]))
                track_energies = [track.Ei for track in frame['MMCTrackList']]
                frame['cscdSBU_BundleInelasticity_surface'] = dataclasses.I3Double(numpy.amax(track_energies) / numpy.sum(track_energies))
                frame['cscdSBU_TrackEnergy'] = dataclasses.I3Double(numpy.amax(track_energies))
                return True

        tray.AddModule(bundle_surface, "bundles_counter2")

        def max_brems(frame):
                maxE = 0
                energies = [p.energy for p in frame['I3MCTree'] if (str(p.type)=="Brems" and p.is_cascade==True)]
                if(len(energies)>0):
                        maxE = numpy.amax(energies)
                frame.Put("cscdSBU_MaxBrems_energy", dataclasses.I3Double(maxE))
                return True

        tray.AddModule(max_brems, "bundles_counter3")
                

        
    
    if datatype == 'muongun':
        # do not calculate muongun weight here, calculate the weight when we create hd5 files later.
        return True
        def put_muon(frame):
            if not 'Muon' in frame:
                tree = frame['I3MCTree']
                muons = [p for p in tree if (p.type == dataclasses.I3Particle.MuMinus or p.type == dataclasses.I3Particle.MuPlus)]
                maxmuon = muons[numpy.argmax([p.energy for p in muons])] # get most energetic one
                frame['cscdSBU_MCMuon'] = maxmuon

        tray.AddModule(put_muon)

        def harvest_generator(infiles):
            generator = None
            fname = infiles[1]
            f = dataio.I3File(fname)
            fr = f.pop_frame(icetray.I3Frame.Stream('S'))
            for k in list(fr.keys()):
                if not (k == 'InIceErrataKeys' or k == 'I3TriggerHierarchy'): # I add I3TriggerHierarchy to sovle deserialization problem on IC86_2012 medium energy muongun dataset.
                    v = fr[k]
                    if isinstance(v, MuonGun.GenerationProbability):
                        generator = v

            f.close()
            return generator


        generator = harvest_generator(infiles)*nfile


        tray.AddModule('I3MuonGun::WeightCalculatorModule', 'cscdSBU_MuonWeight_GaisserH4a',
                Model=MuonGun.load_model('GaisserH4a_atmod12_SIBYLL'),
                Generator=generator)
        
        tray.AddModule('I3MuonGun::WeightCalculatorModule', 'cscdSBU_MuonWeight_GaisserH4a_charm',
                Model=MuonGun.load_model('GaisserH4a_atmod12_DPMJET-C'),
                Generator=generator) 
