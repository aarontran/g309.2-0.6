#!/usr/local/bin/python
"""
Fill in point source holes in an image with counts drawn from a Poisson
distribution, based on #counts in surrounding annulus.
Idea taken from Randall+ (2015, ApJ 805:112).
"""

from __future__ import division

import argparse
#from datetime import datetime
import numpy as np

from astropy.io import fits

from tanproj import radec2tanproj

def main():
    """File modification I/O"""
    parser = argparse.ArgumentParser(description=("Given an image"
                " in tangent-projected sky coordinates and"
                " an ASC-REGION-FITS list of point source exclusions in"
                " celestial RA/dec coordinates,"
                " fill in the image gaps by drawing counts from a"
                " Poisson distribution with mean count rate derived from"
                " an annulus surrounding each point source"))
    parser.add_argument('image', metavar='FITS',
                        help=("FITS image in tangent-projected sky coords"))
    parser.add_argument('exposure', metavar='FITS',
                        help=("FITS exposure image in tangent-projected sky coords"))
    parser.add_argument('--annulus-width', metavar='pixels', type=float,
                        help=("Width (pixels) of sampling annulus around each"
                              " point source."))
    parser.add_argument('--mask', metavar='FITS',
                        help=("ASC-REGION-FITS sources in un-projected RA/DEC,"
                            " radii in arcmin."))
    parser.add_argument('--debug', action='store_true',
                        help=("Create debugging output w/ sources and annuli"
                              " highlighted by artificially high/low values"))
    parser.add_argument('--clobber', action='store_true',
                        help=("Clobber any existing output file"))
    parser.add_argument('--out', metavar='output.fits',
                        help=("Output filename, image w/ filled holes"))
    args = parser.parse_args()

    F_INPUT = args.image
    F_EXPOSURE = args.exposure
    F_MASK = args.mask
    F_OUTPUT = args.out
    ANNULUS_WIDTH = args.annulus_width
    OPT_DEBUG = args.debug
    OPT_CLOBBER = args.clobber

    R_EPSILON = 0.5  # Radius error (pixels) for each point source

    unit_tests()
    assert F_INPUT != F_OUTPUT

    fits_mask = fits.open(F_MASK)
    mask = fits_mask[1]
    assert mask.header['HDUCLASS'] == 'ASC'
    assert mask.header['HDUCLAS1'] == 'REGION'
    assert mask.header['HDUCLAS2'] == 'STANDARD'
    assert mask.header['MTYPE1'] == 'pos'
    assert mask.header['MFORM1'] == 'RA,DEC'
    assert all(map(lambda x: x == '!CIRCLE', mask.data['SHAPE']))

    fits_image = fits.open(F_INPUT)
    phdu = fits_image[0]
    assert phdu.is_image
    assert phdu.header['CTYPE1'] == 'RA---TAN'
    assert phdu.header['CUNIT1'] == 'deg'
    assert phdu.header['CTYPE2'] == 'DEC--TAN'
    assert phdu.header['CUNIT2'] == 'deg'
    assert phdu.header['CDELT1'] == -1 * phdu.header['CDELT2']
    assert phdu.header['CDELT2'] > 0
    # XMM ESAS image convention: X scales inversely w/ RA, Y increases w/ dec.
    # X,Y pixel sizes are equal in deg.; the projection transformation accounts
    # for RA "compression" at high declination

    dat = phdu.data
    x0 = phdu.header['CRPIX1']
    y0 = phdu.header['CRPIX2']
    ra0 = phdu.header['CRVAL1']
    dec0 = phdu.header['CRVAL2']
    scale = phdu.header['CDELT2']  # pixel size == deg./pixel

    fits_exposure = fits.open(F_EXPOSURE)
    exposure = fits_exposure[0]
    for key in ['CTYPE1', 'CUNIT1', 'CTYPE2', 'CUNIT2', 'CDELT1', 'CDELT2']:
        assert exposure.header[key] == phdu.header[key]

    dat_exp = exposure.data

    # Convert point sources to current image projection
    x_srcs, y_srcs = radec2tanproj(mask.data['RA'][:,0], mask.data['DEC'][:,0],
                                 ra0, dec0, x0, y0, 1/scale)
    r_srcs = mask.data['R'][:,0] / (abs(scale) * 60)  # scale*60 = arcmin/px

    n_overlaps = any_sources_overlap(x_srcs, y_srcs, r_srcs)
    if n_overlaps:
        print "\nWARNING: {} pairwise overlap(s), source filling may be inconsistent!\n".format(n_overlaps)

    dat_filled = np.copy(dat)
    max_abs_dat = np.max(np.abs(dat))

    # Get all pixels in annulus of radii (r_pt + 0.5, r_pt + 0.5 + ANN_WIDTH)
    # centered on each point source.
    for x_pt, y_pt, r_pt in zip(x_srcs, y_srcs, r_srcs):

        ann_r1 = r_pt + R_EPSILON  # Excise extra edge pixels
        ann_r2 = r_pt + R_EPSILON + ANNULUS_WIDTH

        # Inspect all pixels in a box around source + annulus
        # Bounds for x, y search: either annulus edge or image boundary
        search_x = (max(1, np.floor(x_pt - ann_r2)),
                    min(dat.shape[0], np.ceil(x_pt + ann_r2)))
        search_y = (max(1, np.floor(y_pt - ann_r2)),
                    min(dat.shape[1], np.ceil(y_pt + ann_r2)))
        search_x = map(int, search_x)
        search_y = map(int, search_y)

        ann_count_rate = 0
        ann_px = 0
        mean_exp = 0

        for x in range(search_x[0], search_x[1] + 1):
            for y in range(search_y[0], search_y[1] + 1):
                # Order of conditionals matters for short-circuiting:
                # distance check is O(1)
                # vs. overlapping source check is O(n_sources)
                d = distance((x, y), (x_pt, y_pt))
                if d > ann_r1 and d < ann_r2 and (not point_overlaps_sources(x, y, x_srcs, y_srcs, r_srcs + R_EPSILON)):
                    # Prevent division by zero.  Counts should be zero in these pixels anyways.
                    if dat_exp[y-1, x-1] <= 0:
                        continue
                    ann_count_rate += (dat[y-1, x-1] / dat_exp[y-1, x-1])  # shift 1- to 0-based indices
                    ann_px += 1
                    mean_exp += dat_exp[y-1, x-1]

        mean_exp = mean_exp / ann_px  # Average exposure for a given pixel

        print "Source at ({:g},{:g}), r = {:g}. Search X in {}, Y in {}.".format(
                x_pt, y_pt, r_pt, search_x, search_y)
        print "  Annulus count rate: {:g} cts/s".format(ann_count_rate)
        print "       usable pixels: {:g} px".format(ann_px)
        print "          count flux: {:g} cts/px/s".format(ann_count_rate/ann_px)
        print "  Total cts mean exp: {:g}".format(ann_count_rate * mean_exp)
        if ann_px < 100:
            print "\n  ***WARNING: <100 pixels sampled; adjust --annulus-width***\n"
        if ann_count_rate * mean_exp < 1:
            print "\n  ***WARNING: <1 count in annulus for mean exposure***\n"

        flux = ann_count_rate/ann_px  # counts / sec / pixel
        if flux < 0:
            print "\n  ***WARNING: negative count rate, forcing to zero!***\n"
            flux = 0

        # Insert new values into image

        for x in range(search_x[0], search_x[1] + 1):
            for y in range(search_y[0], search_y[1] + 1):
                d = distance((x, y), (x_pt, y_pt))
                if OPT_DEBUG:
                    if d <= ann_r1:
                        dat_filled[y-1, x-1] = 10 * max_abs_dat
                    elif d > ann_r1 and d < ann_r2:
                        dat_filled[y-1, x-1] = -10 * max_abs_dat
                else:
                    if d <= ann_r1:
                        # Scale flux to counts/px for current pixel's exposure
                        dat_filled[y-1, x-1] = np.random.poisson(flux * dat_exp[y-1, x-1])

    phdu.data = dat_filled
    fits_image.writeto(F_OUTPUT, clobber=OPT_CLOBBER)

    print "\nWrote output to {:s}.  Check image for reasonable annuli".format(F_OUTPUT)
    print "(e.g., overlapping sources OK; annuli not sampling beyond sky FOV)."


def any_sources_overlap(x_srcs, y_srcs, r_srcs):
    """Return the number of 2-source overlaps in a list of point sources
    I.e., the # of pairwise collisions.  Does not account for multiple overlap
    or other funky things (e.g., a triple Venn diagram counts as 3 overlaps).
    """
    overlaps = 0
    assert len(x_srcs) == len(y_srcs)
    assert len(x_srcs) == len(r_srcs)

    for i in range(len(x_srcs)):

        x_a = x_srcs[i]
        y_a = y_srcs[i]
        r_a = r_srcs[i]

        for j in range(i+1, len(x_srcs)):

            x_b = x_srcs[j]
            y_b = y_srcs[j]
            r_b = r_srcs[j]

            # If circular point sources overlap
            if distance((x_a, y_a), (x_b, y_b)) <= (r_a + r_b):
                overlaps += 1

    return overlaps


def point_overlaps_sources(x, y, x_srcs, y_srcs, r_srcs):
    """
    Check whether a given point lies within a list of sources.
    Points on a source boundary are taken to be included.
    """
    # If speed from exponent/sqrt evaluation is a concern:
    #   sort list by x_pt, then
    #     keep only those with abs(x - x_pt) < r_src
    #   sort list by y_pt, then
    #     keep only those with abs(x - x_pt) < r_src
    #   check all remaining
    # Can also do better by vectorizing.
    # Run time would be: ~ O(n log n) + ~O(n_nearby) * t_math
    # (n_nearby ~ 1 if few collisions)
    # Current approach: O(n) * t_math, regardless of # collisions
    for x_pt, y_pt, r_pt in zip(x_srcs, y_srcs, r_srcs):
        if distance((x, y), (x_pt, y_pt)) <= r_pt:
            return True
    return False


def distance(point_a, point_b):
    """Euclidean distance between cartesian 2-tuples"""
    assert len(point_a) == len(point_b)
    quad = 0
    for (a_i, b_i) in zip(point_a, point_b):
        quad = quad + (b_i - a_i)**2
    return np.sqrt(quad)


def unit_tests():
    """Crude and not-comprehensive sanity checks"""
    assert distance((0,0), (10,0)) == 10
    assert distance((0,0), (-10,0)) == 10
    assert distance((0,-10), (0,0)) == 10
    assert np.abs(distance((5,10), (8,14)) - 5) < 1e-10

    assert not point_overlaps_sources(1, 2.1, [1], [1], [1])
    assert point_overlaps_sources(1, 2, [1], [1], [1])
    assert point_overlaps_sources(1.2, 1.2, [1], [1], [1])

    # 4 sources on x-axis, exactly touching --> 3 pairwise overlaps
    assert any_sources_overlap([1, 2, 3, 4], [0, 0, 0, 0], [0.5, 0.5, 0.5, 0.5]) == 3

    # 4 disjoint sources
    assert any_sources_overlap([-1, 2, 3.1, 4.2], [-1, 0, 0, 0], [1, 0.5, 0.5, 0.5]) == 0


if __name__ == '__main__':
    main()

