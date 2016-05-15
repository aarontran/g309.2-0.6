#!/usr/local/bin/python
"""
Make nice images!
For obvious reasons it's easier to find and test commands in interactive shell.
But save them here when done

See
https://github.com/aarontran/snr-filaments/blob/master/data-tycho/imgs/tycho_aplpy.py
for comparison

Using /usr/local/bin explicitly to resolve dependencies.
Dependencies: aplpy, pyregion
"""

import numpy as np
import os

import aplpy
from astropy.io import fits
#import matplotlib.pyplot as

XMMPATH = os.environ['XMM_PATH']

def main(fig_num):

    if fig_num == '1a':
        # Broadband X-ray image with sparse MOST contours to guide the eye
        # TODO this should be RGB instead of broadband -- TBD
        f = aplpy.FITSFigure(XMMPATH + '/results_img/merged-im-sky-0.8-3.3kev-test.fits',
                             figsize=(8,6))
        f.recenter(ra2deg(13,46,40), -62.87, width=18./60, height=18./60)

        # Weird bug:
        # vmin=9e-6, vmax=5e-5 works with colorbar
        # vmin=1e-5, vmax=5e-5 fails
        f.show_colorscale(vmin=9e-6, vmax=5e-5, stretch='log',cmap='cubehelix',smooth=5)
        #f.add_colorbar()
        #f.add_colorbar(log_format=True)
        #f.colorbar.set_location('bottom')  # Warning: bottom colorbar not fully implemented =(

        most = fits.open(XMMPATH + '/../most/G309.2-0.6.fits')
        #lev = np.linspace(0.02, 0.2, 10)  # Lin MOST contours
        #lev = np.logspace(np.log10(0.01), np.log10(0.2), 10)  # Log MOST contours
        lev = [0.01, 0.01*np.sqrt(10), 0.1, 0.1*np.sqrt(10)]  # Sparse MOST contours
        f.show_contour(data=most, levels=lev, colors='cyan', alpha=0.5)

        f.tick_labels.set_yformat('dd:mm')
        f.tick_labels.set_xformat('hh:mm')
        f.axis_labels.set_ypad(-5)
        f.refresh()
        f.image.figure.tight_layout()  # Use the matplotlib figure instance
        f.save('fig_snr_xmm-broadband_most-sparse.pdf', dpi=300)  # Drops into CWD

    elif fig_num == '1b':
        # MOST image alone to show structure (varying dark/bright regions)
        # TODO make this into a subplot figure, merging 1a/1b
        f = aplpy.FITSFigure(XMMPATH + '/../most/G309.2-0.6.fits',
                             figsize=(8,6))
        f.recenter(ra2deg(13,46,40), -62.87, width=18./60, height=18./60)
        f.show_colorscale(vmin=1e-3, vmax=1e-1, stretch='arcsinh',cmap='inferno')

        f.tick_labels.set_yformat('dd:mm')
        f.tick_labels.set_xformat('hh:mm')
        f.axis_labels.set_ypad(-5)
        f.refresh()
        f.image.figure.tight_layout()  # Use the matplotlib figure instance
        f.save('fig_snr_most.pdf', dpi=300)  # Drops into CWD

    elif fig_num == '2':
        # Broadband X-ray image with region and MOST overlay
        # Larger size to display background region clearly

        f = aplpy.FITSFigure(XMMPATH + '/results_img/merged-im-sky-0.8-3.3kev-test.fits',
                             figsize=(10,8))
        f.recenter(ra2deg(13,46,30), -62.9, width=30./60, height=24./60)
        f.show_colorscale(vmin=1e-5, stretch='log',cmap='hot')
        f.show_regions('regs/bkg.reg')
        f.show_regions('regs/src.reg')

        most = fits.open(XMMPATH + '/../most/G309.2-0.6.fits')
        #lev = np.linspace(0.02, 0.2, 10)  # Lin MOST contours
        lev = np.logspace(np.log10(0.01), np.log10(0.2), 10)  # Log MOST contours
        #lev = [0.01, 0.01*np.sqrt(10), 0.1, 0.1*np.sqrt(10)]  # Sparse MOST contours
        f.show_contour(data=most, levels=lev, colors='lime', alpha=0.5)

        f.tick_labels.set_yformat('dd:mm')
        f.tick_labels.set_xformat('hh:mm')
        f.axis_labels.set_ypad(-5)
        f.refresh()
        f.image.figure.tight_layout()  # Use the matplotlib figure instance
        f.save('fig_snr_regs-src-bkg.pdf', dpi=300)  # Drops into CWD


def ra2deg(h,m,s):
    """Convert RA specified in hh:mm:ss to degrees"""
    return (h+m/60.+s/3600.)/24.*360.


if __name__ == '__main__':
    main('1a')
    main('1b')
    main('2')
