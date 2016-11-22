#!/usr/local/bin/python
"""
What it says on the tin.
"""

from __future__ import division

import argparse
import matplotlib.pyplot as plt
import numpy as np

from astropy.io import fits


def main():
    """Read in two files and print report to stdout"""
    parser = argparse.ArgumentParser(description=("Compare coordinates of two"
                " ASC-REGION-FITS point source exclusion (!CIRCLE) files"
                " line by line.  Plot and report on typical errors."))
    parser.add_argument('file_a', metavar='FILE_A',
                        help=("ASC-REGION-FITS file"
                              " (tangent-projected sky coordinates)"))
    parser.add_argument('file_b', metavar='FILE_B',
                        help=("ASC-REGION-FITS file"
                              " (tangent-projected sky coordinates)"))
    parser.add_argument('--plot', action='store_true',
                        help=("Display quiver plot of coordinate errors"))
    args = parser.parse_args()

    a = fits.open(args.file_a)
    b = fits.open(args.file_b)

    x_a, y_a = get_xy(args.file_a)
    x_b, y_b = get_xy(args.file_b)
    x_err = x_b - x_a
    y_err = y_b - y_a

    # Confirm matched coordinate transform (string keywords)
    for kw in ['TCTYP2', 'TCUNI2',
               'TCTYP3', 'TCUNI3']:
        assert str(a[1].header[kw]) == str(b[1].header[kw])
    # Confirm matched coordinate transform (float keywords)
    for kw in ['TCRPX2', 'TCRVL2', 'TCDLT2',
               'TCRPX3', 'TCRVL3', 'TCDLT3']:
        assert abs(a[1].header[kw] - b[1].header[kw]) / (a[1].header[kw]) < 1e-10

    TCTYP2 = a[1].header['TCTYP2']  # Type (RA---TAN, DEC--TAN)
    TCUNI2 = a[1].header['TCUNI2']  # Unit (deg)
    TCRPX2 = a[1].header['TCRPX2']  # Reference pixel
    TCRVL2 = a[1].header['TCRVL2']  # Reference celestial coordinate
    TCDLT2 = a[1].header['TCDLT2']  # Pixel-coordinate scale
    TCTYP3 = a[1].header['TCTYP3']
    TCUNI3 = a[1].header['TCUNI3']
    TCRPX3 = a[1].header['TCRPX3']
    TCRVL3 = a[1].header['TCRVL3']
    TCDLT3 = a[1].header['TCDLT3']

    print "X pixel scale = {:g} {:s} at {:s} = {:g} {:s}".format(TCDLT2, TCUNI2, TCTYP2, TCRVL2, TCUNI2)
    print "Y pixel scale = {:g} {:s} at {:s} = {:g} {:s}".format(TCDLT3, TCUNI3, TCTYP3, TCRVL3, TCUNI3)
    print
    print "X error (px): range [{:g}, {:g}], median {:g}, mean {:g}".format(
            min(x_err), max(x_err), np.median(x_err), np.mean(x_err))
    print "    RMS X error {:g}".format(np.sqrt(np.mean(x_err**2)))
    print "Y error (px): range [{:g}, {:g}], median {:g}, mean {:g}".format(
            min(y_err), max(y_err), np.median(y_err), np.mean(y_err))
    print "    RMS Y error {:g}".format(np.sqrt(np.mean(y_err**2)))

    abs_err = np.sqrt((x_b - x_a)**2 + (y_b - y_a)**2)
    print "Total error (px): range [{:g}, {:g}], median {:g}, mean {:g}".format(
            min(abs_err), max(abs_err), np.median(abs_err), np.mean(abs_err))
    print "    RMS tot. error {:g}".format(np.sqrt(np.mean(abs_err**2)))
    print "    (n.b. because delta(RA) != delta(dec), tot. pixel error is not"
    print "     equivalent to true arclength error)"

    if args.plot:
        plt.quiver(x_a, y_a, x_err, y_err, width=4e-3)
        plt.title("{:s} coordinate error w.r.t. {:s}".format(
                args.file_b, args.file_a))
        plt.tight_layout()
        plt.show()


def get_xy(fname):
    """Get X, Y coordinates from ASC-REGION-FITS file"""
    f = fits.open(fname)
    table = f[1]  # first BinTable
    assert table.header['HDUCLASS'] == 'ASC'
    assert table.header['HDUCLAS1'] == 'REGION'
    assert table.header['HDUCLAS2'] == 'STANDARD'
    assert table.header['MTYPE1'] == 'pos'
    assert table.header['MFORM1'] == 'X,Y'

    if table.data['X'].ndim == 1:
        x = table.data['X']
    elif table.data['X'].ndim == 2:
        x = table.data['X'][:,0]
    else:
        raise ValueError("X column format has incorrect dimension (0 or >2)")

    if table.data['Y'].ndim == 1:
        y = table.data['Y']
    elif table.data['Y'].ndim == 2:
        y = table.data['Y'][:,0]
    else:
        raise ValueError("Y column format has incorrect dimension (0 or >2)")

    return x, y


if __name__ == '__main__':
    main()
