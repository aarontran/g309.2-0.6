#!/bin/bash

ds9 -view layout vertical \
    -fits "0087940201/pps/P0087940201EPX000OIMAGE8000.FTZ" \
    -scale asinh -cmap cubehelix1 \
    -scale limits 0 50 \
    -smooth yes -smooth function gaussian -smooth radius 3 \
    -regions load all "regs/src.reg" \
    -regions load all "regs/bkg.reg" \
    -regions load all "regs/ann_000_100.reg" \
    -regions load all "regs/ann_100_200.reg" \
    -regions load all "regs/ann_200_300.reg" \
    -regions load all "regs/ann_300_400.reg" \
    -regions load all "regs/ann_400_500.reg" \
    -contour load "../most/G309.2-0.6_linear.con" wcs fk5 green 1 yes
