
## Summary of things to worry about

See: http://www.star.le.ac.uk/~amr30/BG/BGTable.html
I think we got them all...

* Flares (soft protons), evidenced in lightcurves
  Basic de-flare approach: espfilt uses corner (out of FOV) regions of CCDs to
  get lightcurve
  ESAS approach: mos-filter, pn-filter wrappers around espfilt.

  Methods (espfilt):
  - Histogram of count rates vs. finite time intervals; fit Gaussian to nominal
	count rate and apply threshold to cut high count rate time intervals
  - Ratio of high energy cts/pixel (8-12 keV), in annulus near FOV, to
    cts/pixel in unexposed corners.  Create GTI where FOV is below threshold
    for ratio (default, 1.2).  This seems to assume that:
      (1) flares/noise mostly affect FOV (at high energies)
      (2) FOV and corner signal at 8-12 keV is comparable, ignoring central
          sources and flares.
  Post-procedure checks:
  - Method 1: plot histograms to ensure gaussian and thresholding looks
    reasonable (OK)
  - Method 2: plot ratio of 8-12 keV counts, check that that also looks
    reasonable.
  - Both methods: check amount of good time (see FITS header keywords).

* Bad events, filtered by FLAG pattern (`XMMEA_EM, XMMEA_EP`)

* OOT events for PN data (evselect) -- photons registered during CCD readout
  (creates readout streaks) Results in incorrect RAWY value for XMM PN.

  Relevant for all CCDs (MOS, ACIS, PN), but PN has a relatively large
  fraction: 2.3% in ext. full frame mode (6.3% full frame), one order of
  magnitude larger than MOS (0.35% full frame).

  Compare CIAO acisreadcoor, which finds readout streak and removes all photons
  "above" user-input background spectrum.

* pile-up -- I think ok, but any readout streaks?  (pileup: use epatplot)
  Check instrument manuals for both PN and MOS.  Strongly suspect pileup is not
  an issue for us.

* MOS CCDs affected by soft x-ray noise in electronics (anomalous state)
  Addressed by {mos,pn}-filter and emtaglenoise.
  Most common in MOS 2, CCD 5.
  Note that XMM-SAS task emtaglenoise is due to Kuntz and Snowden, should use
  same approach as {mos,pn}-filter.
  Criterion for detecting elevated state does NOT work for central (#1) CCD,
  thus not checked!

* Point source removal -- (cheese, cheese-bands) -- skipping for now... I think ok.

  If I leave point sources in, I can argue that any individual source's flux is
  no more than (X), then perhaps argue, based on some distribution of pt
  sources in that area of the sky (higher due to intervening star cluster
  unfortunately), that effect is < some total flux.  Compare to total surface
  brightness of snr.  Maybe a problem given that SNR lies near star cluster.

* MOS1, CCD #4 is affected by the (apparent) destruction of CCD #3 and has
  higher background near its dead sibling CCD.
  Use evselect to pull this out.  Might be handled by ESAS already...

  > With xmmselect invoked for the emchain event list (e.g., mos1S001-ori.fits)
  > click on the circular button for DETX, add the selection criteria:
  >
  >     (CCDNR == 4)&&(PI in [100:1300])
  >
  > and click on the "Histogram" button. In the evselect GUI click on the
  > "Histogram" menu and 1) set the histogram bin size to 10, 2) check the
  > withhistoranges box, 3) set histogrammin=0 and histogrammax=13200, and 4)
  > click on the "Run" button. The histogram plot that is produced (e.g.,
  > Figure 14) can be used to determine the DETX cutoff for good data (in this
  > case $\sim9750$).

* Stray light -- mostly not a concern but can be extreme in some cases.
  Single reflections from outside FOV cause this (? per XMM background page)

## Summary of stable backgrounds/etc to worry about

* Quiescent particle background, which ESAS covers for us (also handles OOT stuff, crudely?)
  - electronic readout noise
  - high energy particles impacting mos/pn directly
  - high energy particles impacting telescope and causing instrumental K-alpha lines
  - thermal CCD noise (negligible, claims XMM)

* Residual soft proton background -- fit to power law? Spectrum different for MOS vs. PN (source?)

* SWCX background?


