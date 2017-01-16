#!/usr/local/bin/python
"""
Convert ASC-REGION-FITS file containing point sources with RA/dec coordinates
(!CIRCLE shape ONLY) to DS9 region file in RA/dec coordinates

RA/dec is not formally supported in ASC-REGION-FITS spec, but the format is
adopted for consistency...
(copy-paste code GALORE!)
"""

from __future__ import division

import argparse
#from datetime import datetime
#import numpy as np
#import os
import re
#import shutil
#import warnings
#from warnings import warn

#import astropy as ap
from astropy.io import fits
#from astropy.table import Table
from astropy import units as u
from astropy.coordinates import SkyCoord


DS9_V4_1_FK5_HEADER = [
    "# Region file format: DS9 version 4.1",
    ("global color=green dashlist=8 3 width=1 font='helvetica 10 normal roman'"
     " select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1"
     " source=1"),
    "fk5"
]


def main():
    """File conversion I/O"""
    parser = argparse.ArgumentParser(description=("Convert an"
                " ASC-REGION-FITS point source exclusion (!CIRCLE) file"
                " from RA/dec celestial coordinates with radii in arcmin."
                " to DS9 RA/dec region file"))
    parser.add_argument('input', metavar='input-radec.fits',
                        help=("ASC-REGION-FITS sources in un-projected RA/dec,"
                              " radii in arcmin."))
    parser.add_argument('--out', metavar='output.reg',
                        help=("Output filename, DS9 region file in fk5 RA/dec"))
    args = parser.parse_args()
    F_INPUT = args.input
    F_OUTPUT = args.out

    # Parse and validate input

    fits_input = fits.open(F_INPUT)

    t_in = fits_input[1]  # first BinTable

    assert t_in.header['HDUCLASS'] == 'ASC'
    assert t_in.header['HDUCLAS1'] == 'REGION'
    assert t_in.header['HDUCLAS2'] == 'STANDARD'
    assert t_in.header['MTYPE1'] == 'pos'
    assert t_in.header['MFORM1'] == 'RA,DEC'

    #radius = t_in.data['R'][:,0] / (abs(scale) * 60)  # scale*60 = arcmin/px

    assert t_in.header['TTYPE1'].lower() == "shape"
    assert t_in.header['TTYPE2'].lower() == "ra"
    assert t_in.header['TUNIT2'].lower() == "deg"
    assert t_in.header['TFORM2']         == "4E"
    assert t_in.header['TTYPE3'].lower() == "dec"
    assert t_in.header['TUNIT3'].lower() == "deg"
    assert t_in.header['TFORM3']         == "4E"
    assert t_in.header['TTYPE4'].lower() == "r"
    assert t_in.header['TUNIT4'].lower() == "arcmin"
    assert t_in.header['TFORM4']         == "4E"

    assert all(map(lambda x: x == '!CIRCLE', t_in.data['SHAPE']))

    ds9_regions = []

    for src in t_in.data:

        c = SkyCoord(ra=src['RA'][0]*u.degree,
                     dec=src['DEC'][0]*u.degree,
                     frame='fk5')

        radius = src['R'][0] * u.arcmin

        print "Parsed coordinate", c

        ds9_reg = "circle({},{},{}\")".format(
                c.ra.to_string(u.hour, sep=':'),
                c.dec.to_string(sep=':',alwayssign=True),
                radius.to(u.arcsec).value)

        ds9_regions.append(ds9_reg)

    with open(F_OUTPUT, 'w') as f:
        for h in DS9_V4_1_FK5_HEADER:
            f.write(h)
            f.write('\n')
        for ds9_reg in ds9_regions:
            f.write(ds9_reg)
            f.write('\n')


if __name__ == '__main__':
    main()

