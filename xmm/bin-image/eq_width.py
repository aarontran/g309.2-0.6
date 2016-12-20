#!/usr/local/bin/python
"""
Construct equivalent width image given (1) line-energy band image, and (2,3)
two adjacent continuum images.
"""

from __future__ import division

import argparse
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter

from astropy.io import fits

def main():
    """File modification I/O"""
    parser = argparse.ArgumentParser(description=("Create equivalent width"
                " or line flux images given line energy-band image"
                " and two adjacent continuum-band images"))
    parser.add_argument('line', metavar='LINE',
                        help=("line+continuum FITS image"))
    parser.add_argument('left', metavar='CONT1',
                        help=("left continuum FITS image"))
    parser.add_argument('right', metavar='CONT2',
                        help=("right continuum FITS image"))
    parser.add_argument('--bands', metavar='elow-ehigh,elow-ehigh,elow-ehigh',
                        help=("energy bands for each image"))
    parser.add_argument('--out', metavar='output.fits',
                        help=("Output filename, EW image"))
    parser.add_argument('--flux', action='store_true',
                        help=("Create line flux images instead of eq.width"))
    parser.add_argument('--clobber', action='store_true',
                        help=("Clobber any existing output file"))
    parser.add_argument('--out-interp-cont', metavar='output-interp-cont.fits',
                        help=("Output filename, interpolated continuum"))
    args = parser.parse_args()

    F_LINE = args.line
    F_LEFT = args.left
    F_RIGHT = args.right
    F_OUT = args.out
    BANDSTR = args.bands
    OPT_CLOBBER = args.clobber
    OPT_FLUX = args.flux
    OPT_OUT_INTERP_CONT = args.out_interp_cont

    bands = BANDSTR.split(",")
    pi_mins = [(band.split("-"))[0] for band in bands]
    pi_maxs = [(band.split("-"))[1] for band in bands]
    pi_mins = np.array(map(int, pi_mins))
    pi_maxs = np.array(map(int, pi_maxs))
    # Enforce band ordering
    for elow, ehigh in zip(pi_mins, pi_maxs):
        assert elow < ehigh
    for i in range(1, len(pi_maxs)):
        assert pi_maxs[i-1] <= pi_mins[i]

    left_ctr, line_ctr, right_ctr = (pi_maxs + pi_mins)/2
    left_de, line_de, right_de = pi_maxs - pi_mins
    print "Using band centers {}, {}, {}".format(left_ctr, line_ctr, right_ctr)
    print "Using band widths {}, {}, {}".format(left_de, line_de, right_de)

    fits_line = fits.open(F_LINE)
    fits_left = fits.open(F_LEFT)
    fits_right = fits.open(F_RIGHT)

    # Convert [cts / (deg^2 * second)] to [cts / (deg^2 * second * energy)]
    i_left = fits_left[0].data / left_de
    i_line = fits_line[0].data / line_de
    i_right = fits_right[0].data / right_de

    # LOG-interpolated continuum intensity @ center of line energy band...
    i_cont = (np.log(i_right) * (np.log(line_ctr) - np.log(left_ctr)) / (np.log(right_ctr) - np.log(left_ctr))
            + np.log(i_left) * (np.log(right_ctr) - np.log(line_ctr)) / (np.log(right_ctr) - np.log(left_ctr)))
    i_cont = np.exp(i_cont)

    if OPT_OUT_INTERP_CONT:
        fits_line[0].data = i_cont
        fits_line.writeto(OPT_OUT_INTERP_CONT, clobber=OPT_CLOBBER)

    if OPT_FLUX:
        output = (i_line - i_cont) * line_de
    else:
        output = (i_line - i_cont) * line_de / i_cont  # Units: eV
#    output[np.isinf(output)] = 0
#    output[np.isnan(output)] = 0
#    output[output < 0] = 0
    fits_line[0].data = output
    fits_line.writeto(F_OUT, clobber=OPT_CLOBBER)


if __name__ == '__main__':
    main()

