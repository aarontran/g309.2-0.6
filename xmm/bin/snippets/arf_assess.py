#!/usr/local/bin/python
"""
Compare arfs. Yeah.
"""

import numpy as np
import matplotlib.pyplot as plt
import astropy as ap
from astropy.io import fits

for obsid in ["0087940201", "0551000201"]:

    subdir = "/data/gas2/atran/g309/xmm/{0}/odf/repro/".format(obsid)
    exposures = ["mos1S001", "mos2S002", "pnS003"]

    reg1 = "ann_000_100"
    reg2 = "bkg"

    for exp in exposures:

        arf_src = fits.open(subdir + "{}-{}.arf".format(exp,reg1))
        arf_bkg = fits.open(subdir + "{}-{}.arf".format(exp,reg2))

        plt.figure(figsize=(11,8))
        plt.loglog(arf_src[1].data['ENERG_LO'], arf_src[1].data['SPECRESP'],
            drawstyle='steps', color='red', label=reg1.replace('_', '-'))
        plt.loglog(arf_bkg[1].data['ENERG_LO'], arf_bkg[1].data['SPECRESP'], 'r',
            drawstyle='steps', color='blue', label=reg2.replace('_', '-'))
        plt.title("Obsid {0} {1} ARFs".format(obsid, exp))
        plt.legend(loc='best')
        plt.show()

        plt.plot(arf_bkg[1].data['ENERG_LO'],
                 arf_src[1].data['SPECRESP'] / arf_bkg[1].data['SPECRESP'],
                 'r', drawstyle='steps')
        plt.title("Obsid {0} {1} ARF ratio".format(obsid, exp))
        plt.show()
