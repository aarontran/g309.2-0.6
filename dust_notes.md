Constraining the column density and/or distance to the remnant is nontrivial.  In what follows, I label X-ray spectrum fit values as N_{H,fit}, to distinguish from the true N_H.
Aaron Tran, Mar 14--18 ish

1. Dust scattering provides a ~25% correction to column density fits

X-ray spectrum fits with a single absorption component overestimate the column density in relatively dense columns, due to unaccounted-for dust scattering.
(\textbf{note} this is stated without much background information in Reynolds et al., 2008)
E.g., Reynolds et al. (2009) find that a simple scattering model decreases their fitted N_H from 6.8e22 to 5.1e22 for G1.9-0.3 (Reynolds et al., 2009).

2. An empirical relationship links reddening to x-ray fitted absorption

For comparison, the Swift calculator gives E(B-V) = 23.0, then N_{H,fit,gal} = (2.2e21) * R_V * E(B-V) = 2.2e21 * 71.3 = 15e22 is extremely high.
This estimate should be compared to the un-corrected fit value ~7e22 (Reynolds et al., 2009; Zoglauer et al., 2015) because N_H ~ 2.2e21 A_V is an empirical relation derived from un-corrected X-ray spectrum fits.
Given that the remnant is probably not more than 8.5 kpc away (from Steve's arguments), the fit value of 7e22 towards the GC seems reasonable; the remaining 8e22 could appear in lines-of-sight traversing the other side of the galaxy.

For G309.2-0.6, the Swift calculator reports:
E(B-V) = 9.1  --> N_{H,fit,gal} = 2.2e21 * 28.2 = 6e22
N_H,tot = 1.8e22 (atomic and molecular)
For remnant distance of ~5-14 kpc, our fit column densities of 2-4e22 look pretty reasonable. especially since the remnant appears to lie beyond a very bright arm.

Stated another way, the empiricism N_{H,fit} = (2.2e21) * A_V (or, 2.87e21 from Foight+ 2015) folds absorption and extinction together into an "effective absorption" column density, which overestimates the true column density.  Because this relationship is calibrated from X-ray spectrum fits to SNRs and other objects, feeding in E(B-V) / A_V measurements gives results that are consistent with our X-ray spectrum fits.

3. Dust scattering is not enough to explain the mismatch between fitted absorptions and HI + CO survey derived columns

But, the N_H,tot values are from the Swift/HEASARC calculators from dust maps are far below what we are seeing in our fits, even after accounting for a ~25% correction from scattering (see Valencic+, Smith+, Corrales+ 2015/2016).

For galactic sightlines discussed above, "slightly" decreased values of N_H of ~5e22 (G1.9+0.3) or, say, 2e22 (G309.2-0.6) are still far higher than the gas map estimates.
Why is this?

4. Actionables?

(a) take the LAB spectrum and estimate a _minimum_ column towards remnant of (try limits -60 to -20, or -60 to 0 km/s):

    integral_{-60km/s}^{0km/s} HI
    ----------------------------------------  *  6e22 = estimate of "minimum" X-ray-fitted-column-density(-but-not-really) towards the remnant.
    integral_{all velocities} HI

Empricism yields: nH ~ 6e22 (using 2.2e21 * 28.2)
Ratio based on LAB spectrum is 4158 / 8229 = 0.505 * 6e22 ---> 3e22
   (integrating v_lsr from -100 to -20 km/s)
If integrating over -100 to 0 km/s, ratio is 5817/8229 = 0.707 * 6e22 ---> 4e22

Roughly speaking our fits would favor shorter distances as well...

    import numpy as np
    a = np.loadtxt('gass_spectrum.txt',comments='%')
    sel = np.logical_and(a[:,0] < 100, a[:,0] > -100) ; np.trapz(np.flipud(a[sel,2]), np.flipud(a[sel,0]))
    sel = np.logical_and(a[:,0] < 0, a[:,0] > -100) ; np.trapz(np.flipud(a[sel,2]), np.flipud(a[sel,0]))
    sel = np.logical_and(a[:,0] < -20, a[:,0] > -100) ; np.trapz(np.flipud(a[sel,2]), np.flipud(a[sel,0]))


(b) try to calibrate X-ray absorption using point sources in the field.
References:
   
N_H and E(B-V) calculators:
  http://www.swift.ac.uk/analysis/nhtot/index.php
  http://heasarc.gsfc.nasa.gov/cgi-bin/Tools/w3nh/w3nh.pl
  http://ned.ipac.caltech.edu/help/extinction_law_calc.html
  http://irsa.ipac.caltech.edu/applications/DUST/

E(B-V) based on Schlafly and Finkbeiner (2011) -- IRAS/ISSA, COBE/DIRBE, SDSS measurements of reddening
Skymaps:
    http://faun.rc.fas.harvard.edu/dfink/skymaps/

All-sky work:
Pan-STARRS 3-D dust mapping (no southern hemisphere coverage)  http://argonaut.skymaps.info/
IRAS 100 micron (how far can it probe?)
CO map (Dame et al.) -- molecular gas is concentrated at v_lsr < 0 km/s,
so whatever farther out arm is present has a higher ratio of HI / CO, or HI / HII.

Review of all-sky HI surveys: http://www.ifa.hawaii.edu/users/jpw/ism/reading/kalberla_mw_HI.pdf

SGPS (interferometric. ATCA beamwidth 2 arcmin., ~1 K sensitivity):
http://www.atnf.csiro.au/research/HI/sgps/queryForm.html (site doesn't work?)


