Notes on X-ray background papers -- trying to figure out
sources / pointings


* de Luca and Molendi (2003) - XMM sample of various high |b| pointings, 5.5 sq. deg., 1.15 Msec
    photon index 1.41 +/- 0.06, norm ~ 11.6 photon cm^-2 s^-1 sr^-1 keV^-1 at 1 keV.
    Nice introduction -- 

* Hickox and Markevitch 2006, 2007 (661L), 2007 (671L)
2006 paper (absolute measurement of the CXB), CDF-N and CDF-S
    Use faint sources + unresolved flux + Vikhlinin+ (1995) 20 deg^2 ROSAT PSPC survey
    (to account for contribution of brighter sources not seen in CDFs)
    with gamma = 1.4, norm = 10.9 photons cm^-2 s^-1 sr^-1 keV^-1 at 1 keV
2007 (661L) paper -- further exclusions, not relevant as we care about total x-ray bkg

* Kim+ (2007) ChaMP X-ray sources + CDFs.  ChaMP = 149 Chandra pointings at high galactic latitude (|b| > 20 deg.)
    Attempt to bound resolved CXRB fractions
    Their estimates of total CXRB are <~ 10% of Hickox/Markevitch 2006 estimates
    (had to use similar procedure... take a bright-source contribution from other papers)

* Lehmer+ (2012), CDF-N 4 Megasec project! http://adsabs.harvard.edu/abs/2012ApJ...752...46L
    Doesn't tackle this question head on.

* Moretti+ (2003, 2009, 2012) Swift-XRT studies
http://adsabs.harvard.edu/abs/2003ApJ...588..696M
    2003 study uses multiple surveys -- ROSAT, ASCA, XMM, CDF-S, HDF-N
    Up to 2003 -- spread in estimates of flux density is ~10-20% (Figure 3).
    Mostly focused on log N -- log S results.
http://adsabs.harvard.edu/abs/2009A&A...493..501M
    Different approach (!)  Use GRB followups.
    Power law index 1.47 +/- 0.07, norm = 3.69e-3 keV^{-1} cm^{-2} s^{-1} deg^{-2}
        for fit in 1.5 - 7 keV range.  Error on norm is +/- 0.02 (stat 0.02).
    Sec. 7.1, Fig. 9 -- CXRB variance should be around 20% at 36 arcmin^2 (6' x 6')
    This is very useful.
    So in general expect flux measurements good to ~10%.

    "in the soft band the XRT measurement confirms Revnivtsev et al. (2005) conclusions: in the 2-10 keV band narrow-field focusing telescopes measure CXRB values which are significantly higher than the ones found by wide-field not focusing telescopes."

    Revnivtsev+ (2005) state that the discrepancy is ~10-15% (focusing/collimated vs. non-focusing).  Significant, but not worth worrying about for us.

http://www.aanda.org/articles/aa/pdf/2012/12/aa19921-12.pdf
    2012 study.
    Use Swift-XRT 0.5 Msec of CDF-S.
    Mostly trying to decompose to get at unresolved emission.
    They report photon index = 1.46 (+/-0.05 ish) from all stacked data

* Kushino+ (2002) -- ASCA GIS study of 91 fields, |b| > 10 deg., 50 deg.^2 and 5 Msec exposure
    Very nice coverage.
    Photon index = 1.41 +/- 0.03 ish
    Intensity = 8.61 +/- 0.07 photon keV^-1 s^-1 cm^-2 sr^-1 at 1 keV
    Intensity WITH bright sources (> 2e-13 erg cm^-2 s^-1)
    becomes = 9.66 +/- 0.07 photon keV^-1 s^-1 cm^-2 sr^-1 at 1 keV
    (consistent with ASCA SIS study, Gendreau+ 1995)

* Worsley+ (2005) -- chandra study of unresolved hard CXRB
   Mostly focused on teasing out the unresolved component.

Useful factoid -- it seems like the CXRB has some structure -- spectral change ~40 keV ish.

CDF-N counts 

* Civano+ (2016) COSMOS Legacy survey http://adsabs.harvard.edu/abs/2016ApJ...819...62C
    In brief skim I didn't see comments on X-ray extragalactic background.


Chen+ 1997 values: ok, useful, but based on a single field
    can we get a confirmation of how uniform the normalization is?
    
    used by Kavanagh+ 2015 straightforwardly
        (gamma = 1.46, norm 10.5 photons cm^-2 s^-1 sr^-1 at 1 keV)
        ( this is the "model A" of Chen)
    
    kuntz/snowden Chandra M101 Megasecond
      FOR ROSAT BKG
        gamma = 1.46 (Chen)
        norm 9.5 keV cm^-2 s^-1 sr^-1 keV^-1, kuntz 2001
      
      FIT? to ACIS/EPIC/ROSAT data -- clearly, not well constrained
      
      extragalactic norm:
        3.47e-7 (ACIS S3)
        3.74e-7 (ACIS S1)
        6.71e-7 (XMM)       --> ~7.93 keV cm^-2 s^-1 sr^-1 keV^-1
        9.13e-7 (ROSAT)     --> ~10.8 keV cm^-2 s^-1 sr^-1 keV^-1
        
        units: keV cm^-2 s^-1 arcmin^-2 keV^-1
        
        1 arcmin^2 = 8.461595e-8 sr
        
        4pi steradians in a sphere. 2pi = 360 deg.
        (180/pi)^2 = 3282.80635
        3282.80635 * 4*pi = 41,252.961249 sq degrees in the sky..
        = 148,510,660.5 arcmin^2 per 4*pi steradians





Moretti+ CXRB from Swift... arguing that signal/noise is better.
