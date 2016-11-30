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
    parser.add_argument('--annulus-width', metavar='pixels', type=float,
                        help=("Width (pixels) of sampling annulus around each"
                              " point source."))
    parser.add_argument('--mask', metavar='FITS',
                        help=("ASC-REGION-FITS sources in un-projected RA/DEC,"
                            " radii in arcmin."))
    parser.add_argument('--out', metavar='output.fits',
                        help=("Output filename, image w/ filled holes"))
    args = parser.parse_args()

    F_INPUT = args.image
    F_MASK = args.mask
    F_OUTPUT = args.out
    ANNULUS_WIDTH = args.annulus_width

    R_EPSILON = 0.5  # Radius error (pixels) for each point source

    assert F_INPUT != F_OUTPUT

    # Some unit tests
    assert distance((0,0), (10,0)) == 10
    assert distance((0,0), (-10,0)) == 10
    assert distance((0,-10), (0,0)) == 10
    assert np.abs(distance((5,10), (8,14)) - 5) < 1e-10

    # A few considerations when estimating annulus count rate
    # 1. must include zero count pixels in annulus
    # 2. must deal w/ circle edges (w/ conversion uncertainty ~0.5px, masking
    #    differs subtly between each obsid.  So, merged image may have
    #    some pixels within source circle > 0 (not fully sampled),
    #    some pixels outside source circle dimmer than truth)
    # 3. deal w/ overlap with any other circles
    # TODO dealt with 1./2., but not 3.

    # Alternative: we could create images w/ NO masking, then apply masks @
    # merging step only.  But, this requires:
    # 1. SEPARATELY extracted full FOV spectra for proton image creation
    # 2. creating new MASKS for merger stage
    # (cannot use exclusion lists for ESAS tasks - need actual image)
    # Pro: simplifies spectrum/image extraction (only one step needed)
    #      simplifies source edge masking (know exactly which pixels masked)
    # Con: more work, more scripts affected for relatively little gain
    #      trade unneeded mos/pn-spectra intermediate files (useless but
    #      auto-generated) for another intermediate mask file (needs new tool)
    # For now, more work for somewhat small gain.  So, NO (for now).

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
    # XMM ESAS image convention: X scales inversely w/ RA, Y increases w/ dec.
    # X,Y pixel sizes are equal in deg.; the projection transformation accounts
    # for RA "compression" at high declination
    assert phdu.header['CDELT1'] == -1 * phdu.header['CDELT2']
    assert phdu.header['CDELT2'] > 0

    dat = phdu.data
    x0 = phdu.header['CRPIX1']
    y0 = phdu.header['CRPIX2']
    ra0 = phdu.header['CRVAL1']
    dec0 = phdu.header['CRVAL2']
    scale = phdu.header['CDELT2']  # pixel size == deg./pixel

    # Convert point sources to current image projection
    x_srcs, y_srcs = radec2tanproj(mask.data['RA'][:,0], mask.data['DEC'][:,0],
                                 ra0, dec0, x0, y0, 1/scale)
    r_srcs = mask.data['R'][:,0] / (abs(scale) * 60)  # scale*60 = arcmin/px

    dat_filled = np.copy(dat)

    # Get all pixels in annulus of radii (r_pt + 0.5, r_pt + 0.5 + ANN_WIDTH)
    # centered on each point source.
    for x_pt, y_pt, r_pt in zip(x_srcs, y_srcs, r_srcs):

        ann_r1 = r_pt + R_EPSILON  # Excise extra edge pixels
        ann_r2 = r_pt + R_EPSILON + ANNULUS_WIDTH

        # Bounds for x, y search: either annulus edge or image boundary
        search_x = (max(1, np.floor(x_pt - ann_r2)),
                    min(dat.shape[0], np.ceil(x_pt + ann_r2)))

        search_y = (max(1, np.floor(y_pt - ann_r2)),
                    min(dat.shape[1], np.ceil(y_pt + ann_r2)))
        # Deal with type issues to please Python range function
        search_x = map(int, search_x)
        search_y = map(int, search_y)

        # Inspect all pixels in a box around current point source
        ann_counts = 0
        ann_px = 0

        print "Source {}, {}; r = {}. Search X in {}, Y in {}".format(
                x_pt, y_pt, r_pt, search_x, search_y)

        for x in range(search_x[0], search_x[1] + 1):
            for y in range(search_y[0], search_y[1] + 1):
                # Order of conditionals matters for short-circuiting:
                # distance check is O(1)
                # vs. overlapping source check is O(n_sources)
                d = distance((x, y), (x_pt, y_pt))
                if d > ann_r1 and d < ann_r2:
                    if not overlap_sources(x, y, x_srcs, y_srcs, r_srcs + R_EPSILON):
#                        print "    Got pt ({},{}) at d={}, {} counts".format(x, y, d, dat[x-1, y-1])
                        ann_counts += dat[y-1, x-1]  # shift 1- to 0-based indices
                        ann_px += 1

        print "  got {:.2f}/{:d} = {:.3f} counts/px around source".format(ann_counts,
                ann_px, ann_counts/ann_px)
        if ann_px < 100:
            print "  WARNING: not enough pixels sampled"

        # MODIFY ARRAY COPY

        for x in range(search_x[0], search_x[1] + 1):
            for y in range(search_y[0], search_y[1] + 1):
                d = distance((x, y), (x_pt, y_pt))
                if d < ann_r1:
                    dat_filled[y-1, x-1] = np.random.poisson(ann_counts/ann_px)
                elif d > ann_r1 and d < ann_r2:
                    dat_filled[y-1, x-1] = +999  # FOR TESTING

    phdu.data = dat_filled
    fits_image.writeto(F_OUTPUT)


def overlap_sources(x, y, x_srcs, y_srcs, r_srcs):
    """
    Check whether a given point lies within a list of sources
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
        if distance((x, y), (x_pt, y_pt)) < r_pt:
            return True
    return False


def distance(point_a, point_b):
    """Euclidean distance between cartesian 2-tuples"""
    assert len(point_a) == len(point_b)
    quad = 0
    for (a_i, b_i) in zip(point_a, point_b):
        quad = quad + (b_i - a_i)**2
    return np.sqrt(quad)


if __name__ == '__main__':
    main()

