from icecube import icetray

from nugen import nugen_weights, nugen_truth

@icetray.traysegment
def weights(tray, name, datatype='data'):
    # datatype = 'nugen', 'cors', 'data'

    if datatype == 'nugen':
        print ("... adding atm. neutrino weights.")
        # add atmospheric neutrino weights
        from nugen import nugen_weights
        tray.AddSegment(nugen_weights,'atm_flux')

        from nugen import nugen_truth
        tray.AddSegment(nugen_truth,'visible_truth')

    if datatype == 'cors':
        print ("this is corsika. weights need to be calculated later.")
    if datatype == 'muongun':
        print ("this is muongun. weights need to be calculated later.")
    if datatype == 'data':
        print ("this is data. no weights needed.")
