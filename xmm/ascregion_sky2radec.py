#!/usr/local/bin/python
"""
Convert XMM SAS "region" task run outputs from sky to RA/dec coordinates

Warning: this is a fairly specialized task intended for usage in ESAS
framework.
"""

from __future__ import division

import argparse
from datetime import datetime
import numpy as np
import re
import warnings
from warnings import warn

import astropy as ap
from astropy.io import fits
from astropy.table import Table

def main():
    """Merge and Convert ASC-REGION-FITS coordinate conversion"""

    parser = argparse.ArgumentParser(description=("Merge and convert"
                " ASC-REGION-FITS files output by SAS 'region' / ESAS 'cheese'"
                " from tangent-projected sky coordinates (xy) to celestial"
                " sky coordinates (RA/dec) with radii in arcmin."
                " All shapes must be '!CIRCLE'; point source catalogs must be"
                " sparse-ish (e.g. cheese default 40\" separation)."))
    parser.add_argument('files', nargs='+', metavar='FILE',
                        help="ASC-REGION-FITS table(s), tangent-projected sky coordinates")
    parser.add_argument('--out', metavar='FILE',
                        default="merged-bkg_region-radec.fits",
                        help="output ASC-REGION table in deprojected RA/dec")
    parser.add_argument('--merge-dist', type=float, default=2, metavar='ARCSEC',
                        help="merger separation threshold between pt sources")
    args = parser.parse_args()
    MERGE_DIST = args.merge_dist
    FILES = args.files
    F_OUT = args.out

    # Parse and validate input

    srcs = {}

    for fname in FILES:

        if not re.match(".*bkg_region-sky.*\.fits", fname):
            warn("Input file {:s} does not match ESAS naming convention".format(fname))

        f_in = fits.open(fname)
        table = f_in[1]  # first BinTable

        assert all(map(lambda x: x == '!CIRCLE', table.data['SHAPE']))

        assert table.header['MFORM1'] == 'X,Y'
        x = table.data['X'][:,0]
        y = table.data['Y'][:,0]

        assert table.header['TCTYP2'] == "RA---TAN"
        assert table.header['TCUNI2'] == "deg"
        x0 = table.header['TCRPX2']
        ra0 = table.header['TCRVL2']

        assert table.header['TCTYP3'] == "DEC--TAN"
        assert table.header['TCUNI3'] == "deg"
        y0 = table.header['TCRPX3']
        dec0 = table.header['TCRVL3']

        scale = table.header['TCDLT3']

        ra, dec = tanproj2radec(x, y, x0, y0, ra0, dec0, scale)
        radius = table.data['R'][:,0] * abs(scale) * 60  # arcminutes

        srcs[fname] = {}
        srcs[fname]['shape'] = table.data['SHAPE']
        srcs[fname]['ra'] = ra
        srcs[fname]['dec'] = dec
        srcs[fname]['radius'] = radius

    shape_merged = srcs[FILES[0]]['shape']
    ra_merged = srcs[FILES[0]]['ra']
    dec_merged = srcs[FILES[0]]['dec']
    radius_merged = srcs[FILES[0]]['radius']

    for fname in FILES[1:]:

        print "Merging {} sources from {}".format(len(srcs[fname]['ra']), fname)

        # for each candidate source, there can only be at most 1 existing
        # source within MERGE_DIST. And, the mapping from candidate sources
        # to matched existing sources must be injective.
        # Generally enforced by ESAS cheese task (default minimum separation 40
        # arcsec) with use of reasonable MERGE_DIST (say, 2-5 arcsec)

        # Candidate sources to append
        for i_add in range(len(srcs[fname]['ra'])):

            ra_add = srcs[fname]['ra'][i_add]
            dec_add = srcs[fname]['dec'][i_add]
            radius_add = srcs[fname]['radius'][i_add]
            shape_add = srcs[fname]['radius'][i_add]

            j_match = None
            sep_match = None

            # Look for a matching source in the current merged list
            for j in range(len(ra_merged)):
                sep = arcdegsep(ra_merged[j], dec_merged[j], ra_add, dec_add)
                if sep < MERGE_DIST / 3600:
                    assert j_match is None
                    j_match = j
                    sep_match = sep

            # Add or merge the current candidate source
            if j_match is None:

                ra_merged = np.append(ra_merged, ra_add)
                dec_merged = np.append(dec_merged, dec_add)
                radius_merged = np.append(radius_merged, radius_add)
                shape_merged = np.append(shape_merged, shape_add)

                print "    New source: RA, dec ({}, {}), r = {} arcmin".format(
                            ra_add, dec_add, radius_add)

            else:

                r2 = max(radius_add, radius_merged[j_match])
                r1 = min(radius_add, radius_merged[j_match])

                diag = "    Matched existing src (sep {:.2f}\")".format(sep_match * 3600)

                if (r2 == radius_add):
                    ra_merged[j_match] = ra_add
                    dec_merged[j_match] = dec_add
                    radius_merged[j_match] = radius_add
                    shape_merged[j_match] = shape_add
                    diag += "; replacing (r_old {:.2f}\", r_new {:.2f}\")".format(r1 * 60, r2 * 60)
                else:  # note change in order of r1,r2
                    diag += "; no change (r_old {:.2f}\", r_new {:.2f}\")".format(r2 * 60, r1 * 60)
                # else, existing source subsumes new candidate source

                print diag

                # Edge case wherein neither source fully encloses the other
                if sep_match*60 + r1 > r2:
                    # Extend exactly enough to subsume smaller source
                    radius_merged[j_match] = sep_match*60 + r1
                    print "\tMatched sources do not fully overlap; merged radius is {:.2f}\"".format(radius_merged[j_match] * 60)


    # Construct output FITS file
    # ESAS task conv-region expects: SHAPE, RA, Dec, R, ROTANG, COMPONENT
    # then converts stuff.
    celestial_bhdu = fits.BinTableHDU.from_columns(
        [fits.Column(name='SHAPE', format=table.columns['SHAPE'].format,
                     array=shape_merged),
         fits.Column(name='RA', format='E', array=ra_merged, unit="deg"),
         fits.Column(name='Dec', format='E', array=dec_merged, unit="deg"),
         fits.Column(name='R', format='E', array=radius_merged, unit="arcmin"),
         fits.Column(name='ROTANG', format=table.columns['ROTANG'].format,
                     array=table.data['ROTANG'], unit="deg"),
         fits.Column(name='COMPONENT', format=table.columns['COMPONENT'].format,
                     array=table.data['COMPONENT'])
         ]
        )
    celestial_bhdu.name = 'REGION'
    celestial_bhdu.header['MTYPE1'] = 'pos'
    celestial_bhdu.header['MFORM1'] = 'RA,DEC'

    # Loosely following ASC-REGION-FITS spec
    celestial_bhdu.header['HDUCLASS'] = 'ASC'
    celestial_bhdu.header['HDUCLAS1'] = 'REGION'
    celestial_bhdu.header['HDUCLAS2'] = 'STANDARD'
    celestial_bhdu.header['HDUVERS'] = '1.2.0'
    celestial_bhdu.header['HDUDOC'] = 'ASC-FITS-REGION-1.2: Rots, McDowell'

    celestial_phdu = fits.PrimaryHDU()
    # RFC3339/ISO8601 date as used by XMM tools; add 'Z' to indicate timezone
    celestial_phdu.header['DATE'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%m:%Sz')
    celestial_phdu.header['CREATOR'] = 'ascregion_sky2radec.py (atran@cfa)'
    celestial_phdu.header['HISTORY'] = ('Created by ascregion_sky2radec.py at '
                                        + celestial_phdu.header['DATE'])

    f_out = fits.HDUList([celestial_phdu, celestial_bhdu])
    f_out.writeto(F_OUT, clobber=True)


def arcdegsep(ra1, dec1, ra2, dec2):
    """Distance (deg.) separating two points on sky, specified by RA and dec.

    Uses haversine formula in lieu of numerically-vulnerable
    cosine law formula.
    See: https://en.wikipedia.org/wiki/Great-circle_distance

    Input:
        ra1, dec1   first point, RA/dec in decimal degrees
        ra2, dec2   second point, RA/dec in decimal degrees
    Output:
        distance between two points in decimal degrees
    """
    ra1  =  ra1 * np.pi/180
    dec1 = dec1 * np.pi/180
    ra2  =  ra2 * np.pi/180
    dec2 = dec2 * np.pi/180

    # Prevent antipodal points - warn if distance > 1 deg.
    # (i.e. outside intended use case of simple point-source merging)
    # because I'm too lazy to build more sophisticated check
    # or use an unconditionally stable formula (Vincenty or whatever)
    test = np.sqrt((dec1 - dec2)**2 + ((ra1 - ra2) * np.cos((dec2+dec1)/2))**2)
    if test * 180/np.pi > 1:
        warn("arcdegsep arguments >~1 deg apart! ({}, {}, {}, {})".format(ra1, dec1, ra2, dec2))

    def hav(theta):
        """Haversine function"""
        return (np.sin(theta/2))**2

    radicand = hav(dec2 - dec1) + np.cos(dec1) * np.cos(dec2) * hav(ra2 - ra1)
    return 2 * np.arcsin(np.sqrt(radicand)) * 180/np.pi  # archav(radicand)


def tanproj2radec(x, y, x0, y0, ra0, dec0, scale):
    """Convert gnomonic tangent projection to RA/dec
    Operate in pixels / degrees.

    Transform from: http://lambda.gsfc.nasa.gov/product/iras/coordproj.cfm

    Input:
      x (px), distance from ra0
      y (px), distance from dec0
      x0 (px), projection center in pixels
      y0 (px), projection center in pixels
      ra0 (deg.), projection center
      dec0 (deg.), projection center
      scale (deg./pixel) - ASSUMED POSITIVE
    Output:
      RA, dec (tuple) in decimal degrees
    """
    # Convert to radians
    ra_tan = ra0 * np.pi/180
    dec_tan = dec0 * np.pi/180

    # RA varies inversely with XMM sky coordinate x
    # (i.e., XMM sky coords use "standard" x-y axes;
    # y increases up, x increases right)
    # But, transformation equations seem to apply an inversion already (need to
    # re-derive these myself), so I add the -1x factor to y rather than x
    dx = (x - x0) * scale * np.pi/180
    dy = -1 * (y - y0) * scale * np.pi/180
    d = np.arctan(np.sqrt(dx**2 + dy**2))

    b = np.arctan2(-dx, dy)
    xx = np.sin(dec_tan) * np.sin(d) * np.cos(b) + np.cos(dec_tan) * np.cos(d)
    yy = np.sin(d) * np.sin(b)

    ra = ra_tan + np.arctan2(yy, xx)
    dec = np.arcsin( np.sin(dec_tan) * np.cos(d)
                     - np.cos(dec_tan) * np.sin(d) * np.cos(b) )

    return ra * 180/np.pi, dec * 180/np.pi


if __name__ == '__main__':
    main()

