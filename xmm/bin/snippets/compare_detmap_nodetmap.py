#!/usr/local/bin/python
"""
Compare arfs. Makes mild difference, primarily at high energies.
"""

import matplotlib.pyplot as plt
import numpy as np
import os

import astropy as ap
from astropy.io import fits


XMM_PATH = os.environ['XMM_PATH']

regular = fits.open(XMM_PATH + "/0087940201/repro/mos1S001-src.arf")
flat = fits.open(XMM_PATH + "/0087940201/repro/mos1S001-src.flatarf")

plt.figure(figsize=(11,8))
plt.loglog(regular[1].data['ENERG_LO'], regular[1].data['SPECRESP'],
    drawstyle='steps', color='red', label="detmapped ARF")
plt.loglog(flat[1].data['ENERG_LO'], flat[1].data['SPECRESP'],
    drawstyle='steps', color='blue', label="flat ARF")
plt.title("Obsid 0087940201 src ARF detmap comparison")
plt.legend(loc='best')
plt.show()

plt.plot(regular[1].data['ENERG_LO'],
         regular[1].data['SPECRESP'] / flat[1].data['SPECRESP'],
         'r', drawstyle='steps')
plt.title("ARF ratio (Detmapped / flat)")
plt.show()
