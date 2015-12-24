"""
Compare arfs. Yeah.
"""

import numpy as np
import matplotlib.pyplot as plt
import astropy as ap
from astropy.io import fits

for obsid in ["0087940201", "0551000201"]:

    subdir = "/data/mpofls/atran/research/g309/xmm/{0}/odf/repro/".format(obsid)
    exposures = ["mos1S001", "mos2S002", "pnS003"]

    for exp in exposures:

        arf_src = fits.open(subdir + exp + "-src.arf")
        arf_bkg = fits.open(subdir + exp + "-bkg.arf")

        plt.loglog(arf_src[1].data['ENERG_LO'], arf_src[1].data['SPECRESP'],
            drawstyle='steps')
        plt.loglog(arf_bkg[1].data['ENERG_LO'], arf_bkg[1].data['SPECRESP'], 'r',
            drawstyle='steps')
        plt.title("Obsid {0}, {1} src/bkg ARFs".format(obsid, exp))
        plt.show()

        plt.plot(arf_bkg[1].data['ENERG_LO'],
                 arf_src[1].data['SPECRESP'] / arf_bkg[1].data['SPECRESP'],
                 'r', drawstyle='steps')
        plt.title("Obsid {0}, {1} src/bkg ARF ratio".format(obsid, exp))
        plt.show()
