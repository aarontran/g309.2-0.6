#!/bin/sh

ds9 -view layout vertical \
  -frame  1 -fits "regcheck_mos1S001_src_SE_ridge_dark.fits" \
    -bin to fit -zoom to fit \
  -frame  2 -fits "regcheck_mos2S002_src_SE_ridge_dark.fits" \
    -bin to fit -zoom to fit \
  -frame  3 -fits "regcheck_pnS003_src_SE_ridge_dark.fits" \
    -bin to fit -zoom to fit \
  -frame lock wcs -crosshair lock wcs -tile yes \
  -regions load all "regs/src_SE_ridge_dark.reg"
