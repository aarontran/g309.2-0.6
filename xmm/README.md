README for analysis of XMM obsids 0087940201, 0551000201
========================================================

SAS version `xmmsas_20160201_1833-15.0.0`
PyXSPEC version 1.1.0 (needs Parameter.index() function in particular)
Absorption model `tbabs_new` version 2.3.2
XSPEC version 12.9.0d

Setup and data reduction
------------------------

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


Spectrum extraction
-------------------

Inspect data, create appropriate regions in DS9 and save to

    regs/*.reg

Extract observation and FWC spectra with

    specextract.sh, which is a wrapper script for:
        reg2xmmdets.pl
        specbackgrp  # <- calls mos-spectra-mod, pn-spectra-mod, merge_exps.pl
        ff_fit.py

WARNING: specbackgrp calls modified versions of ESAS tasks mos/pn-spectra,
so if ESAS is updated, you need to sync these with new releases.

WARNING 2: do not run multiple specextract runs in parallel.
This goes for ESAS tasks generally.  HEASARC / SAS / ESAS tasks could collide
when modifying/reading _user_-specific parameter files.

Spectrum fits: you'll have to configure a lot of stuff by hand unfortunately.
Still working on it.
In short use `import * from g309_fits` in iPython and work in an interactive
environment.

    g309_models.py
    g309_fits.py

    # Dependencies:
    ExtractedSpectrum.py
    xspec_utils.py
    nice_tables.py

Alternative, background subtraction and fit (exploratory, not maintained):

    bin_unused/spec_subtract

Fit spectra, dump fitting results and make plots and tables:

    from g309_fits import *
    # run commands in interactive session

    xs_wdata_split.pl       # split qdp files into dat files, one per spectrum
    xs_replotter.py {x}.yaml    # create nice python spectrum plots
    latex_table_oneliner.sh


Image creation
--------------

Use ESAS tasks to prepare full FOV images (including soft proton and quiescent
particle backgrounds, derived from ESAS CALDB) in a standard way.
Then use homebrewed scripts to perform binning and smoothing, background
subtraction, and exposure correction.

Create full FOV images and spectra for ESAS use:

    # Custom run to create full FOV images for $SAS_OBSID.
    # Run 1x for each obsid.
    specbackprot_image  # <- calls {mos,pn}-spectra-mod-skip-rmfargen

WARNING: task `pn-spectra-mod-skip-rmfarfgen` is intended ONLY for full FOV
image creation.  It does not clobber existing RMFs, skips ARF creation, does
not create FWC spectra/RMF/ARF files, etc.

Create a `dir.dat` file in your `repro_merged/` directory; see ESAS cookbook
for explanation.

    vim repro_merged/dir.dat

For images without holes:

    mkdir repro_merged_no_holes
    cd repro_merged_no_holes
    ln -s ../repro_merged/dir.dat
    ln -s ../repro_merged/all-bkg_region-radec.fits

Now create a slew of images:

    # For each energy band mosaic you wish to create, point ESAS filenames to
    # either masked or unmasked files
    source sasinit {obsid}
    select_images_for_mosaicking.sh ${elow} ${ehigh} ${mask?}

    # Must run within repro_merged/
    image.sh

    # Dependencies:
    merge_comp_xmm (ESAS)
    fimgbin, fgauss, ftpixcalc, farith (HEASARC FTOOLS)
    hole_filler.py
    eq_width.py

Image display:

    load_g309.sh
    load_narrow_band_g309.sh
    make_ms_image.py



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

