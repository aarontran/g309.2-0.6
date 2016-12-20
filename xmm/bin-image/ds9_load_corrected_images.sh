#!/bin/bash

# Usage: run script and check counts in DS9 to verify that
# we subtracted off approximately the right number of background counts.

ds9 -view layout vertical \
  -frame lock wcs -crosshair lock wcs -tile yes -zoom to fit \
  -frame  1 -fits "corrected-800-3300_bin16_gauss1.fits" \
  -frame  2 -fits "corrected-1150-1250_bin16_gauss1.fits" \
  -frame  3 -fits "corrected-1300-1400_bin16_gauss1.fits" \
  -frame  4 -fits "corrected-1600-1650_bin16_gauss1.fits" \
  -frame  5 -fits "corrected-1800-1900_bin16_gauss1.fits" \
  -frame  6 -fits "corrected-1980-2050_bin16_gauss1.fits" \
  -frame  7 -fits "corrected-2400-2500_bin16_gauss1.fits" \
  -frame  8 -fits "corrected-2600-2700_bin16_gauss1.fits" \
  -frame  9 -fits "exp-im-2600-2700.fits" \
  -frame 10 -fits "back-im-2600-2700.fits" \
  -frame 11 -fits "prot-im-2600-2700.fits" \
  -frame 12 -fits "obj-im-2600-2700.fits" \
  -frame 1 \
      -scale sqrt -cmap cubehelix1 \
      -lock smooth yes \
      -lock crosshair wcs \
      -lock crop wcs \
      -lock scale wcs \
      -lock colorbar yes \
  -regions load all "../regs/src.reg"
