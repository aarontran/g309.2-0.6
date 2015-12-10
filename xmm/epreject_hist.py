"""
compare PI and PHA distributions of epchain event lists
for 0551000201, with and without epreject run
"""

import numpy as np
import matplotlib.pyplot as plt

import astropy as ap
from astropy.io import fits

# Load data
norej = fits.open('0551000201/odf/repro/P0551000201PNS003PIEVLI0000.FIT', memmap=True)
eprej = fits.open('0551000201/odf/repro_epreject/P0551000201PNS003PIEVLI0000.FIT', memmap=True)

# Plot PHA histograms

plt.hist(norej[1].data['PHA'], bins=1024, range=(0,4096), color='blue',
        alpha=0.8, histtype='step', label='No epreject')
plt.hist(eprej[1].data['PHA'], bins=1024, range=(0,4096), color='red',
        alpha=0.8, histtype='step', label='With epreject offset correction')
plt.yscale('log')
plt.xlabel('PHA (channel)')
plt.ylabel('Binned counts')
plt.legend(loc='best')
plt.show()

# Plot PI histograms

# Non integer binning, say with bins=2048 and range= unspecified,
# will result in spurious features due to uneven sampling
# because the data only occur in integer values of PI.
plt.hist(eprej[1].data['PI'], bins=3300, range=(0,33000), color='red',
        alpha=0.8, histtype='step', label='No epreject')
plt.hist(norej[1].data['PI'], bins=3300, range=(0,33000), color='blue',
        alpha=0.8, histtype='step', label='With epreject offset correction')
plt.yscale('log')
plt.xlabel('PI (eV)')
plt.ylabel('(nicely) Binned counts')
plt.legend(loc='best')
plt.show()

# Print some nice information

print norej[1].columns
print norej[1].data
print "No epreject: ", norej[1].data.shape
print "With epreject: ", eprej[1].data.shape

