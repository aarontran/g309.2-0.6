#!/bin/bash

# submoment0_-80_to_-75_DHT36_Quad4_interp.fits \
# submoment0_-75_to_-70_DHT36_Quad4_interp.fits \
# submoment0_-70_to_-65_DHT36_Quad4_interp.fits \
# submoment0_-65_to_-60_DHT36_Quad4_interp.fits \
# submoment0_-60_to_-55_DHT36_Quad4_interp.fits \
# submoment0_-55_to_-50_DHT36_Quad4_interp.fits \
# submoment0_-50_to_-45_DHT36_Quad4_interp.fits \
# submoment0_-45_to_-40_DHT36_Quad4_interp.fits \
# submoment0_-40_to_-35_DHT36_Quad4_interp.fits \
# submoment0_-35_to_-30_DHT36_Quad4_interp.fits \
# submoment0_-30_to_-25_DHT36_Quad4_interp.fits \
# submoment0_-25_to_-20_DHT36_Quad4_interp.fits \
# submoment0_-20_to_-15_DHT36_Quad4_interp.fits \
# submoment0_-15_to_-10_DHT36_Quad4_interp.fits \
# submoment0_-10_to_-05_DHT36_Quad4_interp.fits \
# submoment0_-05_to_+00_DHT36_Quad4_interp.fits \

# submoment0_-80_to_-75_Th_IV_309.75_12CO.fits \
# submoment0_-75_to_-70_Th_IV_309.75_12CO.fits \
# submoment0_-70_to_-65_Th_IV_309.75_12CO.fits \
# submoment0_-65_to_-60_Th_IV_309.75_12CO.fits \
# submoment0_-60_to_-55_Th_IV_309.75_12CO.fits \
# submoment0_-55_to_-50_Th_IV_309.75_12CO.fits \
# submoment0_-50_to_-45_Th_IV_309.75_12CO.fits \
# submoment0_-45_to_-40_Th_IV_309.75_12CO.fits \
# submoment0_-40_to_-35_Th_IV_309.75_12CO.fits \
# submoment0_-35_to_-30_Th_IV_309.75_12CO.fits \
# submoment0_-30_to_-25_Th_IV_309.75_12CO.fits \
# submoment0_-25_to_-20_Th_IV_309.75_12CO.fits \
# submoment0_-20_to_-15_Th_IV_309.75_12CO.fits \
# submoment0_-15_to_-10_Th_IV_309.75_12CO.fits \
# submoment0_-10_to_-05_Th_IV_309.75_12CO.fits \
# submoment0_-05_to_+00_Th_IV_309.75_12CO.fits \

# Scale 0 to 10000 (0 to 10 K km/s) works well
# submoment0_+00_to_+05_Th_IV_309.75_12CO.fits \
# submoment0_+05_to_+10_Th_IV_309.75_12CO.fits \
# submoment0_+10_to_+15_Th_IV_309.75_12CO.fits \
# submoment0_+15_to_+20_Th_IV_309.75_12CO.fits \
# submoment0_+20_to_+25_Th_IV_309.75_12CO.fits \
# submoment0_+25_to_+30_Th_IV_309.75_12CO.fits \
# submoment0_+30_to_+35_Th_IV_309.75_12CO.fits \
# submoment0_+35_to_+40_Th_IV_309.75_12CO.fits \
# submoment0_+40_to_+45_Th_IV_309.75_12CO.fits \
# submoment0_+45_to_+50_Th_IV_309.75_12CO.fits \
# submoment0_+50_to_+55_Th_IV_309.75_12CO.fits \
# submoment0_+55_to_+60_Th_IV_309.75_12CO.fits \
# submoment0_+60_to_+65_Th_IV_309.75_12CO.fits \
# submoment0_+65_to_+70_Th_IV_309.75_12CO.fits \
# submoment0_+70_to_+75_Th_IV_309.75_12CO.fits \
# submoment0_+75_to_+80_Th_IV_309.75_12CO.fits \

ds9 \
  data_intgr/submoment0_+00_to_+05_Th_IV_309.75_12CO.fits \
  data_intgr/submoment0_+05_to_+10_Th_IV_309.75_12CO.fits \
  data_intgr/submoment0_+10_to_+15_Th_IV_309.75_12CO.fits \
  data_intgr/submoment0_+15_to_+20_Th_IV_309.75_12CO.fits \
  data_intgr/submoment0_+20_to_+25_Th_IV_309.75_12CO.fits \
  data_intgr/submoment0_+25_to_+30_Th_IV_309.75_12CO.fits \
  data_intgr/submoment0_+30_to_+35_Th_IV_309.75_12CO.fits \
  data_intgr/submoment0_+35_to_+40_Th_IV_309.75_12CO.fits \
  data_intgr/submoment0_+40_to_+45_Th_IV_309.75_12CO.fits \
  data_intgr/submoment0_+45_to_+50_Th_IV_309.75_12CO.fits \
  data_intgr/submoment0_+50_to_+55_Th_IV_309.75_12CO.fits \
  data_intgr/submoment0_+55_to_+60_Th_IV_309.75_12CO.fits \
  data_intgr/submoment0_+60_to_+65_Th_IV_309.75_12CO.fits \
  data_intgr/submoment0_+65_to_+70_Th_IV_309.75_12CO.fits \
  data_intgr/submoment0_+70_to_+75_Th_IV_309.75_12CO.fits \
  data_intgr/submoment0_+75_to_+80_Th_IV_309.75_12CO.fits \
  -frame lock wcs \
  -pan to 13:46:30 -62:53:00 wcs fk5 \
  -wcs galactic \
  -tile yes -tile grid mode manual -tile grid layout 4 4 \
  -scale lock yes -scale limits 0 20000 -scale lock no \
  -cmap lock yes -cmap Heat -cmap lock no \
  -regions load all "../xmm/regs/lobe_ne.reg" \
  -regions load all "../xmm/regs/lobe_sw.reg" \
  -frame 1 \
    -contour load "../most/G309.2-0.6_log_sparse.con" wcs fk5 cyan 1 yes \
  -frame 2 \
    -contour load "../most/G309.2-0.6_log_sparse.con" wcs fk5 cyan 1 yes \
  -frame 3 \
    -contour load "../most/G309.2-0.6_log_sparse.con" wcs fk5 cyan 1 yes \
  -frame 4 \
    -contour load "../most/G309.2-0.6_log_sparse.con" wcs fk5 cyan 1 yes \
  -frame 5 \
    -contour load "../most/G309.2-0.6_log_sparse.con" wcs fk5 cyan 1 yes \
  -frame 6 \
    -contour load "../most/G309.2-0.6_log_sparse.con" wcs fk5 cyan 1 yes \
  -frame 7 \
    -contour load "../most/G309.2-0.6_log_sparse.con" wcs fk5 cyan 1 yes \
  -frame 8 \
    -contour load "../most/G309.2-0.6_log_sparse.con" wcs fk5 cyan 1 yes \
  -frame 9 \
    -contour load "../most/G309.2-0.6_log_sparse.con" wcs fk5 cyan 1 yes \
  -frame 10 \
    -contour load "../most/G309.2-0.6_log_sparse.con" wcs fk5 cyan 1 yes \
  -frame 11 \
    -contour load "../most/G309.2-0.6_log_sparse.con" wcs fk5 cyan 1 yes \
  -frame 12 \
    -contour load "../most/G309.2-0.6_log_sparse.con" wcs fk5 cyan 1 yes \
  -frame 13 \
    -contour load "../most/G309.2-0.6_log_sparse.con" wcs fk5 cyan 1 yes \
  -frame 14 \
    -contour load "../most/G309.2-0.6_log_sparse.con" wcs fk5 cyan 1 yes \
  -frame 15 \
    -contour load "../most/G309.2-0.6_log_sparse.con" wcs fk5 cyan 1 yes \
  -frame 16 \
    -contour load "../most/G309.2-0.6_log_sparse.con" wcs fk5 cyan 1 yes

