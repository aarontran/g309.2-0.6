#!/usr/local/bin/python
"""
Make nice images!
For obvious reasons it's easier to find and test commands in interactive shell.
But save them here when done

See
https://github.com/aarontran/snr-filaments/blob/master/data-tycho/imgs/tycho_aplpy.py
for comparison

Using /usr/local/bin explicitly to resolve dependencies.
"""

from __future__ import division

import matplotlib as mpl
#mpl.use('Agg')  # For remote image creation over ssh
import matplotlib.pyplot as plt
import numpy as np
import os

import aplpy
from astropy import units as u
from astropy.io import fits

XMMPATH = os.environ['XMM_PATH']

def main(fig_num, invert=False):

    if fig_num == '1':

        # Subplots: http://aplpy.readthedocs.io/en/stable/howto_subplot.html
        fig = plt.figure(figsize=(7,5))  # height > optimal aspect ratio has no effect

        # MOST image alone to show structure (varying dark/bright regions)
        fmost = aplpy.FITSFigure(XMMPATH + '/../most/G309.2-0.6.fits',
                              figure=fig, subplot=(1,2,1))
        fmost.recenter(ra2deg(13,46,40), -62.87, width=18./60, height=18./60)
        fmost_cmap = 'afmhot'
        if invert:
            fmost_cmap += '_r'
        fmost.show_colorscale(vmin=1e-4, vmax=2e-1, stretch='arcsinh',cmap=fmost_cmap)

        # MOST beam notes:
        # - must specify parameters or else constructor will unsuccessfully
        #   search for FITS keywords BMAJ, BMIN, BPA.
        # - hatching is too sparse at our image size, and so has no effect
        # Reference: Whiteoak & Green, 1996A&AS..118..329W
        fmost.add_beam(major=42./np.sin(-62.9*np.pi/180) * u.arcsecond,
                    minor=42 * u.arcsecond,
                    angle=0,
                    corner='bottom left', hatch=None, pad=1, color='white')
        if invert:
            fmost.beam.set_edgecolor('black')
            fmost.beam.set_facecolor('gray')

        format_ticks_and_labels(fmost, invert=invert)
        #fmost.tick_labels.hide_y()
        #fmost.axis_labels.hide_y()


        # Broadband X-ray image with sparse MOST contours to guide the eye
        # Base image has 2.5" pixels and is smoothed with 2px Gaussian (5")
        fxmm = aplpy.FITSFigure(XMMPATH + '/repro_merged_no_holes/corrected-800-3300_bin0_gauss2.fits',
                              figure=fig, subplot=(1,2,2))
        fxmm.recenter(ra2deg(13,46,40), -62.87, width=18./60, height=18./60)

        # Weird bug:
        # vmin=9e-6,vmax=5e-5 works w/colorbar, but vmin=1e-5,vmax=5e-5 fails
        fxmm_cmap = 'cubehelix'
        if invert:
            fxmm_cmap += '_r'
        # Idea: log scale here to show faint emission; linear show in full fov
        # image to show sources
        #fxmm.show_colorscale(vmin=0.2e-5, vmax=2e-5, stretch='linear',cmap=fxmm_cmap)
        fxmm.show_colorscale(vmin=2e-6, vmax=4e-5, stretch='log',cmap=fxmm_cmap)

        # TODO get colorbars working for both subplots
        # https://github.com/aplpy/aplpy/issues/119
        # Warning: bottom colorbar not fully implemented =(
        #fxmm.add_colorbar(location='right', log_format=True)
        #fxmm.colorbar.set_font(size='small')
        ## TODO WARNING: tick labeling not good.
        ##fxmm.colorbar.set_axis_label_text(r'Counts $s^{-1}$')  # Give in text
        ##fxmm.colorbar.set_axis_label_font(size='small')

        most = fits.open(XMMPATH + '/../most/G309.2-0.6.fits')
        #lev = np.linspace(0.02, 0.2, 10)
        #lev = np.logspace(np.log10(0.01), np.log10(0.2), 10)
        lev = np.logspace(-2, -0.5, 4)  # Sparse log contours, 0.01 to 0.1*sqrt(10)
        lev_color = 'cyan'
        if invert:
            lev_color = 'gray'
        fxmm.show_contour(data=most, levels=lev, colors=lev_color, alpha=1)

        format_ticks_and_labels(fxmm, invert=invert)
        fxmm.tick_labels.hide_y()
        fxmm.axis_labels.hide_y()
        fxmm.refresh()

        fig.tight_layout()
        fig.canvas.draw()
        if invert:
            plt.savefig('fig_snr_xmm_most_invert.pdf', dpi=300)
        else:
            plt.savefig('fig_snr_xmm_most.pdf', dpi=300)

    elif fig_num == '2':

        # Subplots: http://aplpy.readthedocs.io/en/stable/howto_subplot.html
        fig = plt.figure(figsize=(8,10))  # height > optimal aspect ratio has no effect

        cmap = 'afmhot'
        if invert:
            cmap = 'cubehelix_r'
            #cmap += '_r'

        # Broadband X-ray image with point source extractions
        # and interpolation
        f = aplpy.FITSFigure(XMMPATH
                + '/repro_merged_no_holes/corrected-800-3300_bin0_gauss2.fits',
                figure=fig, subplot=(1,2,1))
        g = aplpy.FITSFigure(XMMPATH
                + '/repro_merged/corrected-800-3300_bin0_gauss2.fits',
                figure=fig, subplot=(1,2,2))

        for aplfig in [f, g]:
            aplfig.recenter(ra2deg(13,46,40), -62 - 52./60, width=30./60, height=36./60)
            #aplfig.show_colorscale(vmin=1e-6, vmax=4e-5, stretch='log',cmap=cmap)
            aplfig.show_colorscale(vmin=0.2e-5, vmax=3e-5, stretch='linear',cmap=cmap)
            format_ticks_and_labels(aplfig, invert=invert)
            aplfig.ticks.set_color('black')  # Because of FOV image

            if not invert:
                axleft_ticks = aplfig._ax1.yaxis.get_ticklines()
                axright_ticks = aplfig._ax2.yaxis.get_ticklines()
                axleft_minorticks = aplfig._ax1.yaxis.get_minorticklines()
                axright_minorticks = aplfig._ax2.yaxis.get_minorticklines()

                axleft_ticks[4].set_color('white')
                axleft_ticks[6].set_color('white')
                axright_ticks[5].set_color('white')
                for idx in [18,20,22,24,26,28,30,32,34,36]:
                    axleft_minorticks[idx].set_color('white')
                for idx in [17,19,21,23]:
                    axright_minorticks[idx].set_color('white')

        g.tick_labels.hide_y()
        g.axis_labels.hide_y()

        f.show_regions('regs-plot/all_point_sources.reg')
        #f.show_regions('regs/ann_000_100.reg')
        #f.show_regions('regs-plot/circ_200.reg')
        #f.show_regions('regs-plot/circ_300.reg')
        f.show_regions('regs/src.reg')  # Equivalent to circ_400, but changed color/width
        #f.show_regions('regs-plot/circ_500.reg')
        f.show_regions('regs/bkg.reg')  # Yes, do show background

        #f.image.figure.tight_layout()  # Use the matplotlib figure instance
        fig.tight_layout()
        fig.canvas.draw()
        if invert:
            plt.savefig('fig_snr_fullfov_invert.pdf', dpi=300)  # Drops into CWD
        else:
            plt.savefig('fig_snr_fullfov.pdf', dpi=300)  # Drops into CWD

    elif fig_num == '3':

        fig = plt.figure(figsize=(7,5))
        cmap_lf = 'cubehelix'
        if invert:
            cmap_lf += '_r'
        cmap_ew = 'afmhot'
        if invert:
            cmap_ew += '_r'

        mg_line = aplpy.FITSFigure(XMMPATH + '/repro_merged/mg_lineflux_bin8_gauss2.fits',
                                   figure=fig, subplot=(2,3,1))
        si_line = aplpy.FITSFigure(XMMPATH + '/repro_merged/si_lineflux_bin8_gauss2.fits',
                                   figure=fig, subplot=(2,3,2))
        s_line = aplpy.FITSFigure(XMMPATH + '/repro_merged/s_lineflux_bin8_gauss2.fits',
                                  figure=fig, subplot=(2,3,3))

        mg_eqw = aplpy.FITSFigure(XMMPATH + '/repro_merged/mg_eqwidth_bin16_gauss2.fits',
                                  figure=fig, subplot=(2,3,4))
        si_eqw = aplpy.FITSFigure(XMMPATH + '/repro_merged/si_eqwidth_bin16_gauss2.fits',
                                  figure=fig, subplot=(2,3,5))
        s_eqw = aplpy.FITSFigure(XMMPATH + '/repro_merged/s_eqwidth_bin16_gauss2.fits',
                                 figure=fig, subplot=(2,3,6))

        mg_line.show_colorscale(vmin=0, vmax=3e-6, stretch='arcsinh',cmap=cmap_lf)
        si_line.show_colorscale(vmin=0, vmax=3e-6, stretch='arcsinh',cmap=cmap_lf)
        s_line.show_colorscale( vmin=0, vmax=3e-6, stretch='arcsinh',cmap=cmap_lf)

        mg_eqw.show_colorscale(vmin=0, vmax=250, stretch='linear',cmap=cmap_ew)
        si_eqw.show_colorscale(vmin=0, vmax=1000, stretch='linear',cmap=cmap_ew)
        s_eqw.show_colorscale( vmin=0, vmax=1000, stretch='linear',cmap=cmap_ew)

        for im in [mg_line, si_line, s_line, mg_eqw, si_eqw, s_eqw]:
            im.recenter(ra2deg(13,46,40), -62.87, width=18./60, height=18./60)
            format_ticks_and_labels(im, invert=invert)
            im.ticks.hide()
            im.tick_labels.hide()
            im.axis_labels.hide()

        most = fits.open(XMMPATH + '/../most/G309.2-0.6.fits')
        lev = [1e-2]
        lev_color = 'cyan'
        if invert:
            lev_color = 'gray'
        for im in [mg_line, si_line, s_line, mg_eqw, si_eqw, s_eqw]:
            im.show_contour(data=most, levels=lev, colors=lev_color, alpha=0.7)

        text_color = 'white'
        if invert:
            text_color = 'black'

        if invert:
            mg_line.add_label(0.96, 0.92, '1.3--1.4 keV', relative=True, horizontalalignment='right', size='small', color='black')
            si_line.add_label(0.96, 0.92, '1.8--1.9 keV', relative=True, horizontalalignment='right', size='small', color='black')
            s_line.add_label( 0.96, 0.92, '2.4--2.5 keV', relative=True, horizontalalignment='right', size='small', color='black')
        else:
            mg_line.add_label(0.96, 0.92, '1.3--1.4 keV', relative=True, horizontalalignment='right', size='small', color='black', backgroundcolor='white')
            si_line.add_label(0.96, 0.92, '1.8--1.9 keV', relative=True, horizontalalignment='right', size='small', color='black', backgroundcolor='white')
            s_line.add_label( 0.96, 0.92, '2.4--2.5 keV', relative=True, horizontalalignment='right', size='small', color='black', backgroundcolor='white')

        # MEH -- too awkward.
#        mg_line.add_label(0.96, 0.78, '1.3--1.4 keV', relative=True, horizontalalignment='right', size='small', color=text_color)
#        si_line.add_label(0.96, 0.78, '1.8--1.9 keV', relative=True, horizontalalignment='right', size='small', color=text_color)
#        s_line.add_label( 0.96, 0.78, '2.4--2.5 keV', relative=True, horizontalalignment='right', size='small', color=text_color)

        mg_eqw.add_label(0.96, 0.92, 'Mg EW', relative=True, horizontalalignment='right', size='small', color=text_color)
        si_eqw.add_label(0.96, 0.92, 'Si EW', relative=True, horizontalalignment='right', size='small', color=text_color)
        s_eqw.add_label( 0.96, 0.92, 'S EW',  relative=True, horizontalalignment='right', size='small', color=text_color)

        mg_eqw.add_colorbar(location='bottom')
        mg_eqw.colorbar.set_font(size='small')
        #mg_eqw.colorbar.set_axis_label_text(r'Equivalent width, eV')
        #mg_eqw.colorbar.set_axis_label_font(size='small')
        mg_eqw.colorbar.set_ticks([0,50,100,150,200,250])

        si_eqw.add_colorbar(location='bottom')
        si_eqw.colorbar.set_font(size='small')
        #si_eqw.colorbar.set_axis_label_text(r'Equivalent width, eV')
        #si_eqw.colorbar.set_axis_label_font(size='small')
        si_eqw.colorbar.set_ticks([0,200,400,600,800,1000])

        s_eqw.add_colorbar(location='bottom')
        s_eqw.colorbar.set_font(size='small')
        #s_eqw.colorbar.set_axis_label_text(r'Equivalent width, eV')
        #s_eqw.colorbar.set_axis_label_font(size='small')
        s_eqw.colorbar.set_ticks([0,200,400,600,800,1000])

        # Scalebar label commanding does not work :(
        #s_eqw.add_scalebar(1 * u.arcmin)  # 1 arcminute scalebar
        #s_eqw.scalebar.set_label('1 arcmin.')
        #s_eqw.scalebar.set_corner('top right')
        #s_eqw.scalebar.set_font(size='small')
        #if invert:
        #    s_eqw.scalebar.set_color('black')
        #else:
        #    s_eqw.scalebar.set_color('white')

        fig.tight_layout()
        fig.canvas.draw()
        if invert:
            plt.savefig('fig_lineflux_eqwidth_invert.pdf', dpi=300)
        else:
            plt.savefig('fig_lineflux_eqwidth.pdf', dpi=300)

    elif fig_num == '4':
        # RGB image of Mg line flux, Si/S eq width

        aplpy.make_rgb_image([XMMPATH + '/repro_merged/mg_lineflux_bin16_gauss2.fits',
                              XMMPATH + '/repro_merged/si_eqwidth_bin16_gauss2.fits',
                              XMMPATH + '/repro_merged/s_eqwidth_bin16_gauss2.fits'],
                             'fig_rgb_soft_eqwidth.png',
                             vmin_r=1e-7, vmax_r=1e-6, stretch_r='log',
                             vmin_g=0, vmax_g=800, stretch_g='linear',
                             vmin_b=0, vmax_b=800, stretch_b='linear',
                             make_nans_transparent=True)

        fig = plt.figure(figsize=(3, 5))
        f = aplpy.FITSFigure(XMMPATH + '/repro_merged/mg_lineflux_bin16_gauss2.fits',
                             figure=fig)
        f.recenter(ra2deg(13,46,40), -62.87, width=18./60, height=18./60)
        f.show_rgb('fig_rgb_soft_eqwidth.png')
        format_ticks_and_labels(f, invert=False)
        f.ticks.hide()
        f.tick_labels.hide()
        f.axis_labels.hide()

        most = fits.open(XMMPATH + '/../most/G309.2-0.6.fits')
        lev = [1e-2]
        lev_color = 'magenta'
        f.show_contour(data=most, levels=lev, colors=lev_color, alpha=0.7)

        f.show_regions('regs/core.reg')
        f.show_regions('regs/lobe_ne.reg')
        f.show_regions('regs/lobe_sw.reg')
        f.show_regions('regs/ridge_nw.reg')
        f.show_regions('regs/ridge_se.reg')

        f.add_label(0.52, 0.34, 'Core', relative=True, size=8, color='white')
        f.add_label(0.09, 0.74, 'Lobe NE', relative=True, size=8, color='white')
        f.add_label(0.87, 0.75, 'Ridge NW', relative=True, size=8, color='white')
        f.add_label(0.10, 0.22, 'Ridge SE', relative=True, size=8, color='white')
        f.add_label(0.55, 0.05, 'Lobe SW', relative=True, size=8, color='white')

        fig.tight_layout()
        fig.canvas.draw()
        plt.savefig('fig_rgb_soft_eqwidth.pdf', dpi=300)

    else:
        raise Exception("Invalid figure number")

def format_ticks_and_labels(aplfig, invert=False):
    """Common tick setup code"""
    aplfig.tick_labels.set_yformat('dd:mm')
    aplfig.tick_labels.set_xformat('hh:mm')
    aplfig.axis_labels.set_ypad(-5)
    if invert:
        aplfig.ticks.set_color('black')


def ra2deg(h,m,s):
    """Convert RA specified in hh:mm:ss to degrees"""
    return (h+m/60.+s/3600.)/24.*360.


if __name__ == '__main__':
    #main('1', invert=False)
    #main('1', invert=True)
    #main('2', invert=False)
    #main('2', invert=True)
    #main('3', invert=False)
    #main('3', invert=True)
    main('4', invert=False)
