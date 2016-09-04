#!/usr/local/bin/python
"""
Check light curves...
"""

import numpy as np
import matplotlib.pyplot as plt

import astropy as ap
from astropy.io import fits


for obsid in ["0087940201", "0551000201"]:

    subdir = "/data/gas2/atran/g309/xmm/{0}/repro/".format(obsid)
    exposures = ["mos1S001", "mos2S002", "pnS003"]

    fig, axes = plt.subplots(3, sharex=True, figsize=(16,10))

    for exp, ax in zip(exposures, axes):

        orig = fits.open(subdir + exp + "-clean-ori-lc.fits", memmap=True)
        final = fits.open(subdir + exp + "-clean-final-lc.fits", memmap=True)
        noclean=fits.open(subdir + exp + "-ori-lc.fits", memmap=True)

        ax.plot(noclean[1].data['TIME'], noclean[1].data['RATE'], 'og', alpha=0.4, markersize=8)
        ax.plot(orig[1].data['TIME'], orig[1].data['RATE'], 'ob-', alpha=0.4)
        ax.plot(final[1].data['TIME'], final[1].data['RATE'], '*r-', alpha=0.7)

        if exp == "pnS003":
            ax.set_xlabel('Time since XMM Epoch (Jan 1 1998 12:00:00TT)')
        ax.set_ylabel('Count rate (cts/sec)')
        ax.set_yscale('log')
        ax.set_title("Obsid {0}, exposure {1} lightcurve".format(obsid, exp))
        #plt.legend(loc='best')

    plt.tight_layout()
    #plt.savefig(obsid + "_lc.png", dpi=200)
    plt.show()

