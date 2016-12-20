#!/usr/local/bin/python
"""
Plot Fe-K stuff

Note strong coupling, of course, w/ g309_fe_luminosity.py.
TRANSFERRED TO IPYTHON NOTEBOOK...
"""

from __future__ import division

import matplotlib.pyplot as plt
import numpy as np


def main():
    """Make a plot"""
    with np.load("fe-k-flux_grid_nH1e+22_fe1.npz") as data:
        Tau = data['Tau']
        kT = data['kT']
        erg_fluxes = data['erg_fluxes']
        phot_fluxes = data['phot_fluxes']

    plt.imshow(phot_fluxes.T, origin='lower', extent=(9, 13, -1, 1),
               aspect='auto', interpolation='none')

    xtick_vals = [1e9, 1e10, 1e11, 1e12, 1e13]
    ytick_vals = [0.1, 0.2, 0.5, 1, 2, 5, 10]
    plt.xticks(np.log10(xtick_vals),
               [r'$10^{9}$', r'$10^{10}$', r'$10^{11}$', r'$10^{12}$', r'$10^{13}$'])
    plt.yticks(np.log10(ytick_vals), ytick_vals)

    plt.viridis()
    plt.colorbar()
    plt.tight_layout()
    plt.show()

    BOUND = 5e-5  # crude upper bound on Fe-K photons/cm^2/sec

    norm_bound = BOUND / (phot_fluxes.T)
    norm_bound[norm_bound > 1e10] = np.nan  # Apply cap
#    norm_bound[np.logical_not(np.isfinite(norm_bound))] = 1  # Zero invalid numbers
    norm_bound = np.log10(norm_bound)

    # assume Fe = 1.  then,
    plt.imshow(norm_bound, origin='lower', extent=(9, 13, -1, 1),
               aspect='auto', interpolation='none')
    # Same stuff
    xtick_vals = [1e9, 1e10, 1e11, 1e12, 1e13]
    ytick_vals = [0.1, 0.2, 0.5, 1, 2, 5, 10]
    plt.xticks(np.log10(xtick_vals),
               [r'$10^{9}$', r'$10^{10}$', r'$10^{11}$', r'$10^{12}$', r'$10^{13}$'])
    plt.yticks(np.log10(ytick_vals), ytick_vals)
    plt.viridis()
    plt.colorbar()
    plt.tight_layout()
    plt.show()
    # result = upper bound on (norm x fe)


    # Next, apply our upper bound on flux to estimate the maximal Fe mass that
    # can be hiding at a given Tau & temperature.


if __name__ == '__main__':
    main()

