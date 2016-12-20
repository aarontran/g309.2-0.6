README for analysis of XMM obsids 0087940201, 0551000201
========================================================

SAS version `xmmsas_20160201_1833-15.0.0`
PyXSPEC version 1.1.0 (needs Parameter.index() function in particular)
Absorption model `tbabs_new` version 2.3.2
XSPEC version 12.9.0d

Setup and data reduction / fitting
----------------------------------

Use Makefile to download and reprocess data for obsids 0087940201, 0551000201;
download ESAS CALDB with filter-wheel-closed data, diagonal RMFs:

    make all

To reprocess manually after downloading from XMM data archive, run
    
    source sasinit ${obsid}
    source sasrepro ${obsid}

To set an interactive environment for SAS/HEASOFT tools, run:

    source sasinit ${obsid}

Omitting obsid loads the SAS/HEASOFT environment but does not set environment
variables for SAS analysis (evselect works, odfingest will not).
Obsid is also required to use this pipeline (several environment variables read
by various scripts and tasks).
From here out, execution in a sasinit-executed environment is assumed.

Create filtered, OOT-event subtracted event lists and point source masks.
Repeat this for EACH obsid of interest.

    chainfilter
    # use lightcurve_check.py to inspect GTI filtering

Merge point source lists, replace __incorrect__ detector coordinate masks for
spectrum extraction:

    merge_point_source.sh

Inspect data, create appropriate regions in DS9 and save to

    regs/*.reg

Extract observation and FWC spectra with

    specextract.tcsh, which is a wrapper script for:
        reg2xmmdets.pl
        specbackgrp
        ff_fit.py

WARNING: specbackgrp calls modified versions of ESAS tasks mos/pn-spectra,
so if ESAS is updated, you need to sync these with new releases.

Spectrum fits: you'll have to configure a lot of stuff by hand unfortunately.
Still working on it.
In short use `import * from g309_fits` in iPython and work in an interactive
environment.

    g309_models.py
    g309_fits.py (replaces fitter.tcsh, but still in works), wrapper for
        xspec_fit_g309.py

    # Dependencies:
    ExtractedSpectrum.py
    xspec_utils.py
    nice_tables.py

Alternative, background subtraction and fit (exploratory, not maintained):

    bin_unused/spec_subtract

Images - crude, quick and dirty mosaic w/ many merging systematics

    quick_image.sh
    quick_image_merge.sh
    load_g309.sh
    load_narrow_band_g309.sh
    make_ms_image.py

Images - binned, smoothed, background-subtracted and exposure corrected:

    # Must run within repro_merged/
    image.sh

    # Dependencies:
    merge_comp_xmm (ESAS)
    fimgbin, fgauss, ftpixcalc, farith (HEASARC FTOOLS)
    hole_filler.py
    eq_width.py

Plotting and manipulation of spectrum fit results:

    from g309_fits import *  # Interactive use methods
    xs_wdata_split.pl
    xs_replotter.py {x}.yaml
    replot_*
    latex_table_oneliner.sh

Intermediate results dumped to:

    results_img
    results_spec


Image creation
--------------

WARNING: task `pn-spectra-mod-skip-rmfarfgen` is intended ONLY for full FOV
image creation.  It does not clobber existing RMFs, skips ARF creation, does
not create FWC spectra/RMF/ARF files, etc.



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

