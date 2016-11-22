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
import warnings
from warnings import warn

import astropy as ap
from astropy.io import fits
from astropy.table import Table

def main():
    """File conversion I/O"""
    parser = argparse.ArgumentParser(description=("Convert an"
                " ASC-REGION-FITS point source exclusion (!CIRCLE) file"
                " from RA/dec celestial coordinates with radii in arcmin."
                " to tangent-projected sky coordinates (xy)"))
    parser.add_argument('input', metavar='input-radec.fits',
                        help=("ASC-REGION-FITS sources in un-projected RA/dec,"
                              " radii in arcmin."))
    parser.add_argument('--projection-reference', metavar='reference.fits',
                        help="Reference ASC-REGION-FITS file")
    parser.add_argument('--out', metavar='output-sky.fits',
                        help=("Output filename, converted ASC-REGION-FITS in"
                              " tangent-projected sky coordinates"))
    args = parser.parse_args()
    F_INPUT = args.input
    F_PROJ_REF = args.projection_reference
    F_OUTPUT = args.out

    # Parse and validate input

    if not re.match(".*bkg_region-sky.*\.fits", F_PROJ_REF):
        warn(("--proj-ref {:s} doesn't follow ESAS naming").format(F_PROJ_REF))

    if not re.match(".*bkg_region-sky.*\.fits", F_OUTPUT):
        warn(("--out {:s} doesn't follow ESAS naming").format(F_OUTPUT))

    fits_input = fits.open(F_INPUT)
    fits_proj_ref = fits.open(F_PROJ_REF)
    t_in = fits_input[1]  # first BinTable
    t_proj_ref = fits_proj_ref[1]

    for t in [t_in, t_proj_ref]:
        assert t.header['HDUCLASS'] == 'ASC'
        assert t.header['HDUCLAS1'] == 'REGION'
        assert t.header['HDUCLAS2'] == 'STANDARD'
    assert t_in.header['MTYPE1'] == 'pos'
    assert t_in.header['MFORM1'] == 'RA,DEC'
    assert all(map(lambda x: x == '!CIRCLE', t_in.data['SHAPE']))

    # Set up projection center
    assert t_proj_ref.header['TCTYP2'] == "RA---TAN"
    assert t_proj_ref.header['TCUNI2'] == "deg"
    x0 = t_proj_ref.header['TCRPX2']
    ra0 = t_proj_ref.header['TCRVL2']

    assert t_proj_ref.header['TCTYP3'] == "DEC--TAN"
    assert t_proj_ref.header['TCUNI3'] == "deg"
    y0 = t_proj_ref.header['TCRPX3']
    dec0 = t_proj_ref.header['TCRVL3']

    # Square coordinates
    assert t_proj_ref.header['TCDLT2'] == -1 * t_proj_ref.header['TCDLT3']
    assert t_proj_ref.header['TCDLT3'] > 0
    scale = t_proj_ref.header['TCDLT3']


    # Perform the coordinate conversion (vectorized)
    x, y = radec2tanproj(t_in.data['RA'], t_in.data['DEC'],
                         ra0, dec0, x0, y0, 1/scale)
    # 1/scale needed to get pixel/deg., as FITS sky coords records deg./pixel

    radius = t_in.data['R'] / (abs(scale) * 60)  # scale*60 = arcmin/px

    # Construct output FITS file in same format as output by SAS task region
    # (except use 'E' instead of '4E' for X, Y, R, ROTANG)
    bhdu = fits.BinTableHDU.from_columns(
        [fits.Column(name='SHAPE', format=t_in.columns['SHAPE'].format,
                     array=t_in.data['SHAPE']),
         fits.Column(name='X', format='E', array=x),
         fits.Column(name='Y', format='E', array=y),
         fits.Column(name='R', format='E', array=radius),
         fits.Column(name='ROTANG', format='E', array=t_in.data['ROTANG']),
         fits.Column(name='COMPONENT', format='I', array=t_in.data['COMPONENT'])
         ]
        )
    bhdu.name = 'REGION'
    bhdu.header['MTYPE1'] = 'pos'
    bhdu.header['MFORM1'] = 'X,Y'
    for kw in ['TCTYP2', 'TCUNI2', 'TCRPX2', 'TCRVL2', 'TCDLT2',
               'TCTYP3', 'TCUNI3', 'TCRPX3', 'TCRVL3', 'TCDLT3']:
        # Coordinate transformation parameters already validated above
        bhdu.header[kw] = t_proj_ref.header[kw]

    # Loosely following ASC-REGION-FITS spec
    bhdu.header['HDUCLASS'] = 'ASC'
    bhdu.header['HDUCLAS1'] = 'REGION'
    bhdu.header['HDUCLAS2'] = 'STANDARD'
    bhdu.header['HDUVERS'] = '1.2.0'
    bhdu.header['HDUDOC'] = 'ASC-FITS-REGION-1.2: Rots, McDowell'

    phdu = fits.PrimaryHDU()
    # RFC3339/ISO8601 date as used by XMM tools; add 'Z' to indicate timezone
    phdu.header['DATE'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%m:%Sz')
    # Convenient way to get program name
    phdu.header['CREATOR'] = '{} (atran@cfa)'.format(os.path.basename(__file__))
    phdu.header['HISTORY'] = 'Created by {} at {}'.format(
                    phdu.header['CREATOR'], phdu.header['DATE'])

    f_out = fits.HDUList([phdu, bhdu])
    f_out.writeto(F_OUTPUT, clobber=True)


def radec2tanproj(ra, dec, ra0, dec0, x0, y0, scale):
    """Convert RA/dec (decimal deg.) to gnomonic tangent projection (pixels)

    Transform from: http://lambda.gsfc.nasa.gov/product/iras/coordproj.cfm

    Input:
      ra (deg.), coordinate
      dec (deg.), coordinate
      ra0 (deg.), projection center
      dec0 (deg.), projection center
      x0 (px), projection center in pixels
      y0 (px), projection center in pixels
      scale (pixel/deg.) - ASSUMED POSITIVE.  Inverted from tanproj2radec
    Output:
      x, y (tuple) in pixels
    """
    # Convert to radians
    ra_tan = ra * np.pi/180
    dec_tan = dec * np.pi/180
    ra0_tan = ra0 * np.pi/180
    dec0_tan = dec0 * np.pi/180

    a = np.cos(dec_tan) * np.cos(ra_tan - ra0_tan)
    f = scale * (180/np.pi) / (np.sin(dec0_tan) * np.sin(dec_tan)
                               + a * np.cos(dec0_tan))

    # RA varies inversely with XMM sky coordinate x
    # (i.e., XMM sky coords use "standard" x-y axes;
    # y increases up, x increases right)
    # But, transformation equations seem to apply an inversion already (need to
    # re-derive these myself), so I add the -1x factor to y rather than x
    dy = -1 * -f * ( np.cos(dec0_tan) * np.sin(dec_tan) - a * np.sin(dec0_tan))
    dx = -f * np.cos(dec_tan) * np.sin(ra_tan - ra0_tan)

    return dx + x0, dy + y0


if __name__ == '__main__':
    main()

