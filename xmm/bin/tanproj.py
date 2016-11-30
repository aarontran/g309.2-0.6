"""
Utility methods for tangent projection conversion
"""

from __future__ import division

import numpy as np


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
