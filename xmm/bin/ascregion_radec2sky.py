#!/usr/local/bin/python
"""
Convert ASC-REGION-FITS file containing point sources with RA/dec coordinates
(either !CIRCLE or CIRCLE shapes) to ASC-REGION-FITS files in sky coordinates,
applying gnomonic tangent projection.

To specify projection center and scale, you must either
1. provide an existing ASC-REGION-FITS file with the required coordinate system
information,
2. provide coordinates in keyword argument form

Warning: this is a fairly specialized task intended for usage in ESAS
framework.

RA/dec is not formally supported in ASC-REGION-FITS spec, but the format is
adopted for consistency...
"""

from __future__ import division

import argparse
from datetime import datetime
import numpy as np
import os
import re
#import shutil
#import warnings
from warnings import warn

import astropy as ap
from astropy.io import fits
from astropy.table import Table

from tanproj import radec2tanproj


def main():
    """File conversion I/O"""
    parser = argparse.ArgumentParser(description=("Convert an"
                " ASC-REGION-FITS point source exclusion (!CIRCLE) file"
                " from RA/dec celestial coordinates with radii in arcmin."
                " to tangent-projected sky coordinates (xy)"))
    parser.add_argument('input', metavar='input-radec.fits',
                        help=("ASC-REGION-FITS sources in un-projected RA/dec,"
                              " radii in arcmin."))
    parser.add_argument('--template', metavar='reference.fits',
                        help=("Reference ASC-REGION-FITS file (with desired"
                              " projection and header keywords"))
    parser.add_argument('--out', metavar='output-sky.fits',
                        help=("Output filename, converted ASC-REGION-FITS in"
                              " tangent-projected sky coordinates"))
    args = parser.parse_args()
    F_INPUT = args.input
    F_TEMPLATE = args.template
    F_OUTPUT = args.out

    # Parse and validate input

    if not re.match(".*bkg_region-sky.*\.fits", F_TEMPLATE):
        warn(("--template {:s} doesn't follow ESAS naming").format(F_TEMPLATE))
    if not re.match(".*bkg_region-sky.*\.fits", F_OUTPUT):
        warn(("--out {:s} doesn't follow ESAS naming").format(F_OUTPUT))

    #shutil.copy(F_TEMPLATE, F_OUT)

    fits_input = fits.open(F_INPUT)
    fits_template = fits.open(F_TEMPLATE)

    t_in = fits_input[1]  # first BinTable
    t_template = fits_template[1]

    for t in [t_in, t_template]:
        assert t.header['HDUCLASS'] == 'ASC'
        assert t.header['HDUCLAS1'] == 'REGION'
        assert t.header['HDUCLAS2'] == 'STANDARD'
    assert t_in.header['MTYPE1'] == 'pos'
    assert t_in.header['MFORM1'] == 'RA,DEC'
    assert all(map(lambda x: x == '!CIRCLE', t_in.data['SHAPE']))

    # Set up projection center
    assert t_template.header['TCTYP2'] == "RA---TAN"
    assert t_template.header['TCUNI2'] == "deg"
    x0 = t_template.header['TCRPX2']
    ra0 = t_template.header['TCRVL2']

    assert t_template.header['TCTYP3'] == "DEC--TAN"
    assert t_template.header['TCUNI3'] == "deg"
    y0 = t_template.header['TCRPX3']
    dec0 = t_template.header['TCRVL3']

    # Square coordinates
    assert t_template.header['TCDLT2'] == -1 * t_template.header['TCDLT3']
    assert t_template.header['TCDLT3'] > 0
    scale = t_template.header['TCDLT3']

    # Perform the coordinate conversion (vectorized)
    x, y = radec2tanproj(t_in.data['RA'][:,0], t_in.data['DEC'][:,0],
                         ra0, dec0, x0, y0, 1/scale)
    # 1/scale needed to get pixel/deg., as FITS sky coords records deg./pixel

    radius = t_in.data['R'][:,0] / (abs(scale) * 60)  # scale*60 = arcmin/px

    # Construct output FITS file in same format as output by SAS task region
    # (except use 'E' instead of '4E' for X, Y, R, ROTANG)
    x_pad = pad_E_to_4E(x)
    y_pad = pad_E_to_4E(y)
    radius_pad = pad_E_to_4E(radius)

    bhdu = fits.BinTableHDU.from_columns(
        [fits.Column(name='SHAPE', format=t_in.columns['SHAPE'].format,
                     array=t_in.data['SHAPE']),
         fits.Column(name='X', format='4E', array=x_pad),
         fits.Column(name='Y', format='4E', array=y_pad),
         fits.Column(name='R', format='4E', array=radius_pad),
         fits.Column(name='ROTANG', format='4E', array=t_in.data['ROTANG']),
         fits.Column(name='COMPONENT', format='J', array=t_in.data['COMPONENT'])
         ]
        )
    bhdu.name = 'REGION'

    # Loosely following ASC-REGION-FITS spec
    bhdu.header['HDUVERS'] = '1.2.0'
    bhdu.header['HDUCLASS'] = 'ASC'
    bhdu.header['HDUCLAS1'] = 'REGION'
    bhdu.header['HDUCLAS2'] = 'STANDARD'
    bhdu.header['HDUDOC'] = 'ASC-FITS-REGION-1.2: Rots, McDowell'

    bhdu.header['MTYPE1'] = 'pos'
    bhdu.header['MFORM1'] = 'X,Y'
    for kw in ['TCTYP2', 'TCRPX2', 'TCRVL2', 'TCUNI2', 'TCDLT2',
               'TCTYP3', 'TCRPX3', 'TCRVL3', 'TCUNI3', 'TCDLT3']:
        # Coordinate transformation parameters already validated above
        if ("TCRPX" in kw) or ("TCRVL" in kw) or ("TCDLT" in kw):
            bhdu.header[kw] = "{:.14e}".format(t_template.header[kw]).upper()
        else:
            bhdu.header[kw] = t_template.header[kw]


    phdu = fits_template[0]  # Work off of template header
    phdu.header['HISTORY'] = ('Rewritten by {} (atran@cfa)'
                             ' using RA/dec list {} on date {}').format(
                            os.path.basename(__file__),
                            os.path.basename(F_INPUT),
                            datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%Sz'))
    # RFC3339/ISO8601 date as used by XMM tools; add 'Z' to indicate timezone

    f_out = fits.HDUList([phdu, bhdu])
    f_out.writeto(F_OUTPUT, clobber=True)


def pad_E_to_4E(column, **kwargs):
    """Expand 1-D numpy array (E) to column of zero-padded 4E vectors"""
    column_padded = np.zeros((len(column), 4), **kwargs)
    column_padded[:,0] = column
    return column_padded


if __name__ == '__main__':
    main()

