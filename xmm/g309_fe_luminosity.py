#!/usr/local/bin/python
"""
Estimate Fe-K stuff
"""

from __future__ import division

from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import os

import xspec as xs

from g309_fits import prep_xs, stopwatch
import g309_models as g309
import xspec_utils as xs_utils
from ExtractedSpectrum import ExtractedSpectrum


def main():
    """Get 6-7 keV flux due to Iron for XMM MOS1/2 (merged)"""
    # "Low"-level load of only one spectrum
    prep_xs(with_xs=False, statMethod='pgstat')  # Standard setup
    extr = ExtractedSpectrum("0087940201", "mosmerge", "src",
                             suffix='grp01', marfrmf=True)
    spec = xs_utils.load_spec(1, extr.pha(), background=extr.qpb(),
                              default_dir=extr.repro_dir())
    extr.spec = spec  # Required for model loaders.  Rather ugly but works...
    g309.load_remnant_model(1, "snr_src", [extr], case='vnei')

    xs.AllData.ignore("**-5.0, 8.0-**")
    xs.AllData.ignore("bad")

    # Must address two issues:
    # 1. verify that nH had minimal impact (< some %)
    # 2. check degeneracy between norm/Fe. step over range and confirm
    #    how well they correlate
#    print "Gridding Fe-K flux with nH=1e22, Fe=1"
#    grid_fe_k_flux(base_nH=1, base_fe=1)
#
#    print "Gridding Fe-K flux with nH=10e22, Fe=1"
#    grid_fe_k_flux(base_nH=10, base_fe=1)

    # NOT yet run...
    print "Gridding Fe-K flux with nH=0.1e22, Fe=1"
    grid_fe_k_flux(base_nH=0.1, base_fe=1)
    print "Gridding Fe-K flux with nH=1e22, Fe=0.1"
    grid_fe_k_flux(base_nH=1, base_fe=0.1)
    print "Gridding Fe-K flux with nH=1e22, Fe=10"
    grid_fe_k_flux(base_nH=1, base_fe=10)


def grid_fe_k_flux(base_nH=1, base_fe=1, out=None):
    """Make a grid """

    # Make it shut up
    xs.Xset.chatter = 9

    # Ensure "standard" normalization
    snr = xs.AllModels(1, 'snr_src')
    snr.tbnew_gas.nH = base_nH
    snr.vnei.Fe = base_fe
    snr.vnei.norm = 1

    # Temporarily unshutup to affirm baseline parameters
    xs.Xset.chatter = 10
    snr.show()
    xs.Xset.chatter = 9

    # First compute flux w/ "standard" norm (effectively, fix mass & distance)
    range_Tau = np.logspace(9, 13, 100)  # Spans 1e9 to 1e13
    range_kT  = np.logspace(-1, 1, 100)  # Spans 0.1 to 10 keV

    # Outputs
    erg_fluxes  = np.zeros((len(range_Tau), len(range_kT)))
    phot_fluxes = np.zeros((len(range_Tau), len(range_kT)))

    # Time: ~50 minutes for 100x100 pts (1e9 to 1e13 s cm^{-3}, 0.1 to 10 keV)
    # for only one spectrum (0087940201 MOS merged)
    for i in range(len(range_Tau)):

        print "Tau = {:g}".format(range_Tau[i]), datetime.now()
        snr.vnei.Tau = range_Tau[i]

        for j in range(len(range_kT)):

            if j % 5 == 0:
                print "  kT = {:g} ...".format(range_kT[j])
            snr.vnei.kT = range_kT[j]

            snr.vnei.Fe = 0
            xs.AllModels.calcFlux("6 7")

            continuum_erg  = xs.AllData(1).flux[0]
            continuum_phot = xs.AllData(1).flux[3]

            snr.vnei.Fe = base_fe
            xs.AllModels.calcFlux("6 7")

            erg_fluxes[i,j]  = (xs.AllData(1).flux[0] - continuum_erg) / snr.constant.factor.values[0]
            phot_fluxes[i,j] = (xs.AllData(1).flux[3] - continuum_phot) / snr.constant.factor.values[0]

    # Reset
    xs.Xset.chatter = 10

    if out is None:
        out = "fe-k-flux_grid_nH{:g}_fe{:g}.npz".format(base_nH * 1e22, base_fe)

    np.savez(out, Tau=range_Tau, kT=range_kT, erg_fluxes=erg_fluxes,
             phot_fluxes=phot_fluxes)



if __name__ == '__main__':
    main()

