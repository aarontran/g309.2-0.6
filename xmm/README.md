README for analysis of XMM obsids 0087940201, 0551000201
========================================================

SAS build version `xmmsas_20160201_1833-15.0.0`
PyXSPEC version 1.1.0 (needs Parameter.index() function in particular)
Absorption model `tbabs_new` version 2.3.2
XSPEC version 12.9.0d

Setup and data reduction / fitting
----------------------------------

To download data (including ESAS filterwheel closed data + diagonal RMFs for
MOS1, MOS2, PN), run from this top-level directory (xmm/):

    make all

to download and reprocess data for obsids 0087940201, 0551000201; 
download ESAS filter-wheel-closed data, diagonal RMFs for MOS1, MOS2, and PN.
To reprocess manually after downloading from XMM data archive, run
    
    source sasinit ${obsid}
    source sasrepro ${obsid}

To set an interactive environment for SAS/HEASOFT tools, run:

    source sasinit ${obsid}

`sasinit` sets environment variable `$XMM_PATH` which is referenced
extensively.
Running `source sasinit` alone loads the SAS/HEASOFT environment but does not
set obsid-specific parameters for SAS analysis (so evselect works, odfingest
may not).

All working files should reside in:

    ${XMM_PATH}/${OBSID}/odf/repro

Create filtered, OOT-event subtracted event lists and point source masks:

    source sasinit ${obsid}
    chainfilter_0551000201
    chainfilter_0087940201

Inspect data, create regions in DS9, and create corresponding XMM detector
regions with:

    make_xmmregions (calls reg2xmmdets.pl)
    check_xmmregions

Extract observation and FWC spectra with

    specextract.tcsh, which is a wrapper script for:
        make_xmmregions
        specbackgrp $obsid $region
        ff_fit.py

Spectrum fits: you'll have to configure a lot of stuff by hand unfortunately.
Still working on it.

    g309_models.py
    g309_fits.py (replaces fitter.tcsh, but still in works), wrapper for
        xspec_fit_g309.py

    # Dependencies:
    ExtractedSpectrum.py
    xspec_utils.py
    nice_tables.py

Alternative, background subtraction and fit (not well-tested or explored):

    spec_subtract
    snr_sbkg.xcm

Image creation (not too tidy yet):

    load_g309.sh
    quick_image.sh
    quick_image_merge.sh
    make_ms_image.py

Plotting and manipulation spectrum fit results:

    from g309_fits import *  # Interactive use methods
    xs_wdata_split.pl
    xs_replotter.pl
    replot_*
    latex_table_oneliner.sh

Intermediate results dumped to:

    results_img
    results_spec




Tools and scripts
-----------------

The chainfilter/specbackgrp scripts should be nearly the same, but have
variations for each dataset.  Some tools used in current pipeline, which can be
run independently as well:

    get_header_keyword {keyword}

        obtain keyword values from spectrum fits files for all exposures

    cheese_smell

        DS9 call to inspect cheese_grater outputs

    errcheck.sh

        Scan logfiles for pipeline (glorified grep)

    arf_assess.py

        Compare ARF files across obsids/exposures

Scripts to inspect pipeline files:

    epreject_hist.py

        See the effect of epreject on output spectra counts (channel space)

    lightcurve_check.py

        Check your lightcurves, please.

Scripts for side analysis:

    chainfilter_0551000201_no-epreject

        check effects of epreject run on epchain process
        irrelevant since we are not using PN data from this obsid anyways

    cheese_grater

        vary cheese (pt src removal) params

    tbabs_vnei.py

        make plots of absorbed NEI model (note: requires ARF/RMF files
        associated with some dummy spectrum, so doesn't work out of the box)

