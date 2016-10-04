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

import matplotlib.pyplot as plt
import numpy as np
import os

import aplpy
from astropy.io import fits

XMMPATH = os.environ['XMM_PATH']

def main(fig_num, invert=False):

    if fig_num == '1':

        # Subplots: http://aplpy.readthedocs.io/en/stable/howto_subplot.html

        fig = plt.figure(figsize=(6,3.5))  # Play with this sizing?

        # Broadband X-ray image with sparse MOST contours to guide the eye
        f1 = aplpy.FITSFigure(XMMPATH + '/results_img/merged-im-sky-0.8-3.3kev-test.fits',
                              figure=fig, subplot=(1,2,1))
        f1.recenter(ra2deg(13,46,40), -62.87, width=18./60, height=18./60)

        # Weird bug:
        # vmin=9e-6,vmax=5e-5 works w/colorbar, but vmin=1e-5,vmax=5e-5 fails
        f1_cmap = 'cubehelix'
        if invert:
            f1_cmap += '_r'
        f1.show_colorscale(vmin=9e-6, vmax=5e-5, stretch='log',cmap=f1_cmap,smooth=5)

        # TODO get colorbars working for both subplots
        # https://github.com/aplpy/aplpy/issues/119
        #f1.add_colorbar()
        #f1.add_colorbar(log_format=True)
        #f1.colorbar.set_location('bottom')  # Warning: bottom colorbar not fully implemented =(

        most = fits.open(XMMPATH + '/../most/G309.2-0.6.fits')
        #lev = np.linspace(0.02, 0.2, 10)  # Lin MOST contours
        #lev = np.logspace(np.log10(0.01), np.log10(0.2), 10)  # Log MOST contours
        lev = [0.01, 0.01*np.sqrt(10), 0.1, 0.1*np.sqrt(10)]  # Sparse MOST contours
        f1.show_contour(data=most, levels=lev, colors='cyan', alpha=0.7)

        f1.tick_labels.set_xformat('hh:mm')
        f1.tick_labels.set_yformat('dd:mm')
        f1.axis_labels.set_ypad(-5)
        f1.refresh()

        # MOST image alone to show structure (varying dark/bright regions)
        f2 = aplpy.FITSFigure(XMMPATH + '/../most/G309.2-0.6.fits',
                              figure=fig, subplot=(1,2,2))
        f2.recenter(ra2deg(13,46,40), -62.87, width=18./60, height=18./60)
        f2_cmap = 'afmhot'
        if invert:
            f2_cmap += '_r'
        f2.show_colorscale(vmin=1e-3, vmax=1e-1, stretch='arcsinh',cmap=f2_cmap)

        f2.tick_labels.set_xformat('hh:mm')
        f2.tick_labels.hide_y()
        f2.axis_labels.hide_y()
        f2.refresh()

        fig.tight_layout()
        fig.canvas.draw()
        if invert:
            plt.savefig('fig_snr_xmm_most_invert.pdf', dpi=300)
        else:
            plt.savefig('fig_snr_xmm_most.pdf', dpi=300)

    elif fig_num == '2':
        # Broadband X-ray image with region and MOST overlay
        # Larger size to display background region clearly

        f = aplpy.FITSFigure(XMMPATH + '/results_img/merged-im-sky-0.8-3.3kev-test.fits',
                             figsize=(7,5))  # only height affects final size
        f.recenter(ra2deg(13,46,30), -62.9, width=28./60, height=28./60)
        f_cmap = 'afmhot'
        if invert:
            f_cmap += '_r'
        f.show_colorscale(vmin=1e-5, stretch='log',cmap=f_cmap)
        f.show_regions('regs/ann_000_100.reg')
        f.show_regions('regs-plot/circ_200.reg')
        f.show_regions('regs-plot/circ_300.reg')
        f.show_regions('regs/src.reg')  # Equivalent to circ_400, but changed color/width
        f.show_regions('regs-plot/circ_500.reg')
        f.show_regions('regs/bkg.reg')  # Yes, do show background

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
        if invert:
            f.save('fig_snr_regs-fiveann_invert.pdf', dpi=300)  # Drops into CWD
        else:
            f.save('fig_snr_regs-fiveann.pdf', dpi=300)  # Drops into CWD
    elif fig_num == '3':
        # Experimental -- abortive attempt to combine figures 1 and 2

        fig = plt.figure(figsize=(8,3.5))  # Play with this sizing?

        # Broadband X-ray image with sparse MOST contours to guide the eye
        f1 = aplpy.FITSFigure(XMMPATH + '/results_img/merged-im-sky-0.8-3.3kev-test.fits',
                              figure=fig, subplot=(1,3,1))
        f1.recenter(ra2deg(13,46,40), -62.87, width=18./60, height=18./60)

        # Weird bug:
        # vmin=9e-6,vmax=5e-5 works w/colorbar, but vmin=1e-5,vmax=5e-5 fails
        f1.show_colorscale(vmin=9e-6, vmax=5e-5, stretch='log',cmap='cubehelix',smooth=5)

        # TODO get colorbars working for both subplots
        # https://github.com/aplpy/aplpy/issues/119
        #f1.add_colorbar()
        #f1.add_colorbar(log_format=True)
        #f1.colorbar.set_location('bottom')  # Warning: bottom colorbar not fully implemented =(

        most = fits.open(XMMPATH + '/../most/G309.2-0.6.fits')
        lev = [0.01, 0.01*np.sqrt(10), 0.1, 0.1*np.sqrt(10)]  # Sparse MOST contours
        f1.show_contour(data=most, levels=lev, colors='cyan', alpha=0.7)

        f1.tick_labels.set_xformat('hh:mm')
        f1.tick_labels.set_yformat('dd:mm')
        f1.axis_labels.set_ypad(-5)
        f1.refresh()

        # MOST image alone to show structure (varying dark/bright regions)
        f2 = aplpy.FITSFigure(XMMPATH + '/../most/G309.2-0.6.fits',
                              figure=fig, subplot=(1,3,2))
        f2.recenter(ra2deg(13,46,40), -62.87, width=18./60, height=18./60)
        f2.show_colorscale(vmin=1e-3, vmax=1e-1, stretch='arcsinh',cmap='inferno')

        f2.tick_labels.set_xformat('hh:mm')
        f2.tick_labels.hide_y()
        f2.axis_labels.hide_y()
        f2.refresh()

        # Unsmoothed broadband XMM image with region, MOST overlays
        f3 = aplpy.FITSFigure(XMMPATH + '/results_img/merged-im-sky-0.8-3.3kev-test.fits',
                             figure=fig, subplot=(1,3,3))
        f3.recenter(ra2deg(13,46,30), -62.9, width=28./60, height=28./60)
        f3.show_colorscale(vmin=1e-5, stretch='log',cmap='hot')
        f3.show_regions('regs/ann_000_100.reg')
        f3.show_regions('regs/circ_200.reg')
        f3.show_regions('regs/circ_300.reg')
        f3.show_regions('regs/src.reg')  # Equivalent to circ_400, but changed color/width
        f3.show_regions('regs/circ_500.reg')
        f3.show_regions('regs/bkg.reg')  # Yes, do show background

        lev = np.logspace(np.log10(0.01), np.log10(0.2), 10)  # Log MOST contours
        f3.show_contour(data=most, levels=lev, colors='lime', alpha=0.5)

        f3.tick_labels.set_xformat('hh:mm')
        # Do need f3 tick labels; dec is not matched
        f3.tick_labels.set_yformat('dd:mm')
        f3.axis_labels.hide_y()
        f3.refresh()

        fig.tight_layout()
        fig.canvas.draw()
        plt.savefig('fig_snr_xmm_most_regs.pdf', dpi=300)
    else:
        raise Exception("Invalid figure number")


def ra2deg(h,m,s):
    """Convert RA specified in hh:mm:ss to degrees"""
    return (h+m/60.+s/3600.)/24.*360.


if __name__ == '__main__':
    main('1', invert=True)
    main('2', invert=True)
    #main('3')
