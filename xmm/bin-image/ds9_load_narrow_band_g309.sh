#!/bin/bash

ds9 -view layout vertical \
    -frame 1 -fits "results_img/merged-im-sky-1.3-1.4kev-test.fits" \
    -frame 2 -fits "results_img/merged-im-sky-1.8-1.9kev-test.fits" \
    -frame 3 -fits "results_img/merged-im-sky-2.4-2.5kev-test.fits" \
    -crop '+13:46:40.00' '-62:53:00.000' 0.3 0.3 wcs \
    -frame lock wcs -crosshair lock wcs -crop lock wcs -tile yes -zoom to fit \
    -tile column -colorbar no \
    -frame 1 \
      -scale asinh -cmap cubehelix1 \
      -scale limits 5e-7 7e-6 \
      -cmap value 1.46272 0.400604 \
      -cmap invert yes \
      -smooth yes -smooth function gaussian -smooth radius 12 \
      -contour load "../most/G309.2-0.6_log_sparse.con" wcs fk5 red 1 yes \
    -frame 2 \
      -scale asinh -cmap cubehelix1 \
      -scale limits 2e-7 1e-5 \
      -cmap value 1.21415 0.529909 \
      -cmap invert yes \
      -smooth yes -smooth function gaussian -smooth radius 12 \
      -contour load "../most/G309.2-0.6_log_sparse.con" wcs fk5 red 1 yes \
    -frame 3 \
      -scale asinh -cmap cubehelix1 \
      -scale limits 2e-7 4e-6 \
      -cmap value 1.24283 0.471903 \
      -cmap invert yes \
      -smooth yes -smooth function gaussian -smooth radius 12 \
      -contour load "../most/G309.2-0.6_log_sparse.con" wcs fk5 red 1 yes
