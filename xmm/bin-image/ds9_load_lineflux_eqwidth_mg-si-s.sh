#!/bin/bash

# Show contours only on rightmost column
cd ${XMM_PATH}/repro_merged

mg_max="1e-6"
si_max="3e-6"
s_max="1e-6"
ew_max="1000"
ds9 -view layout vertical \
  mg_lineflux_bin* mg_eqwidth_bin* \
  si_lineflux_bin* si_eqwidth_bin* \
  s_lineflux_bin* s_eqwidth_bin* \
  -frame lock wcs -cmap lock yes -cmap Heat -cmap lock no \
  -crop +13:46:35.842 -62:53:18.641 0.4111085 0.3777754 wcs fk5 degrees \
  -crop match wcs \
  -crop lock wcs \
  -tile yes -tile grid mode manual -tile grid layout 5 6 \
  -zoom to fit \
  -scale lock yes -scale linear -scale lock no \
  -frame  1 \
    -scale limits 0 $mg_max \
  -frame  2 \
    -scale limits 0 $mg_max \
  -frame  3 \
    -scale limits 0 $mg_max \
  -frame  4 \
    -scale limits 0 $mg_max \
  -frame  5 \
    -scale limits 0 $mg_max \
    -contour load "../../most/G309.2-0.6_log_sparse.con" wcs fk5 green 1 yes \
  -frame  6 \
    -scale limits 0 $ew_max \
  -frame  7 \
    -scale limits 0 $ew_max \
  -frame  8 \
    -scale limits 0 $ew_max \
  -frame  9 \
    -scale limits 0 $ew_max \
  -frame 10 \
    -scale limits 0 $ew_max \
    -contour load "../../most/G309.2-0.6_log_sparse.con" wcs fk5 green 1 yes \
  -frame 11 \
    -scale limits 0 $si_max \
  -frame 12 \
    -scale limits 0 $si_max \
  -frame 13 \
    -scale limits 0 $si_max \
  -frame 14 \
    -scale limits 0 $si_max \
  -frame 15 \
    -scale limits 0 $si_max \
    -contour load "../../most/G309.2-0.6_log_sparse.con" wcs fk5 green 1 yes \
  -frame 16 \
    -scale limits 0 $ew_max \
  -frame 17 \
    -scale limits 0 $ew_max \
  -frame 18 \
    -scale limits 0 $ew_max \
  -frame 19 \
    -scale limits 0 $ew_max \
  -frame 20 \
    -scale limits 0 $ew_max \
    -contour load "../../most/G309.2-0.6_log_sparse.con" wcs fk5 green 1 yes \
  -frame 21 \
    -scale limits 0 $s_max \
  -frame 22 \
    -scale limits 0 $s_max \
  -frame 23 \
    -scale limits 0 $s_max \
  -frame 24 \
    -scale limits 0 $s_max \
  -frame 25 \
    -scale limits 0 $s_max \
    -contour load "../../most/G309.2-0.6_log_sparse.con" wcs fk5 green 1 yes \
  -frame 26 \
    -scale limits 0 $ew_max \
  -frame 27 \
    -scale limits 0 $ew_max \
  -frame 28 \
    -scale limits 0 $ew_max \
  -frame 29 \
    -scale limits 0 $ew_max \
  -frame 30 \
    -scale limits 0 $ew_max \
    -contour load "../../most/G309.2-0.6_log_sparse.con" wcs fk5 green 1 yes

#  -regions load all "../regs/bar.reg" \
#  -regions load all "../regs/ridge.reg" \
#  -regions load all "../regs/lobe.reg"
