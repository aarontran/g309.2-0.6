README for analysis of XMM obsids 0087940201, 0551000201
========================================================

Uses SAS build version: xmmsas_20141104_1833

Setup and data reduction / fitting
----------------------------------

To download data (including ESAS filterwheel closed data + diagonal RMFs for
MOS1, MOS2, PN), run from this top-level directory (xmm/):

    make all

This will download and unpackage data for obsids 0087940201 and 0551000201, and
run XMM-SAS odfingest and cifbuild (via script sasrepro).
To reprocess steps manually after downloading from XMM data archive, run
    
    source sasinit ${obsid}
    source sasrepro ${obsid}

To set-up an interactive environment for SAS/ESAS, run:

    source sasinit ${obsid}

which sets the environment variable ${XMM_PATH} to provide access to scripts
from deep within data directories.  Running `source sasinit` alone also sets up
the XMM SAS and HEASOFT environment, but does not set obsid-specific parameters
for SAS analysis (so evselect works, odfingest may not).

To pass data through the processing pipeline, run:

    source sasinit ${obsid}
    cd ${obsid}/odf/repro
    chainfilter_${obsid}
    specbackgrp_${obsid}

This will output a slew of spectra and files, which can be prepared for fitting
with the following XSPEC command chains (warning: as of 2016 Jan 13, many
parameters and commands must be hand-edited.  e.g. perform one fit, then copy
relevant parameters over to another fitting script)

Main fitting (model both source and background regions, separately):

    ff_pn.xcm
    ff_mos.xcm
    back_0087940201.xcm
    back_0551000201.xcm
    snr.xcm

Alternative, background subtraction and fit:

    specmeth
    snr_sqpb.xcm


Tools and scripts
-----------------

The chainfilter/specbackgrp scripts should be nearly the same, but have
variations for each dataset.  Some tools used in current pipeline, which can be
run independently as well:

    mos-spectra-mod, pn-spectra-mod
    make_xmmregions, reg2xmmdets.pl
    cheese_smell
    errcheck.sh
    arf_assess.py
    bkg2src_norm

Scripts to inspect pipeline files:

    epreject_hist.py
    lightcurve_check.py

Scripts for side analysis:

    chainfilter_0551000201_no-epreject      check effects of epreject run
    cheese_grater                           vary cheese (pt src removal) params
    tbabs_vnei.py                           make plots of absorbed NEI model
                                            (note: requires ARF/RMF files associated
                                             with some dummy spectrum)

