XMM-Newton data analysis notes
==============================

Log of commands run, files created.

Links:
    http://xmm.esac.esa.int/sas/current/documentation/threads/EPIC_filterbackground.shtml

Websites I'm looking at, to see what kind of filtering/cleaning can be done
* XMM SAS Inverse Index: http://xmm.esac.esa.int/sas/current/sas_inverse_index/sas_inverse_index_dataproc.shtml
* NASA XMM GOF ESAS cookbok: http://heasarc.gsfc.nasa.gov/docs/xmm/esas/cookbook/xmm-esas.html
* NASA XMM GOF ABC cookbook: http://heasarc.gsfc.nasa.gov/docs/xmm/abc/node8.html
* Threads: http://xmm.esac.esa.int/sas/current/documentation/threads/ (note ESAS image thread is same as cookbook...)
* Useful (look at more SAS workshop stuff): http://xmm.esa.int/external/xmm_data_analysis/sas_workshops/sas_ws9_files/presentations/Ignacio_EPIC_scientific_products_extraction.pdf


Thursday 2015 September 17
==========================
Initial meeting with Pat about this project.  See my notes.


Monday 2015 September 21
========================
Starting from the data analysis guide sent from Pat.
Run a number of commands, which I combine together in the script `xmm_repro`.
In simple script form, assuming you're in a directory with the folder ./$obsid

This first batch of commands ingests and prepares your data, creating level 1
event files for all detectors.
I have run these commands for all three XMM obsids with G309.2-0.6 data.

    # Contained in script, use `source sasinit`
    # -----------------------------------------
    heainit
    source /soft/XMM/xmmsas/setsas.csh
    setenv SAS_CCFPATH /proj/xmm/ccf


    # Contained in script, use `xmm_repro $obsid`
    # -------------------------------------------
    cd "$obsid/ODF"
    setenv SAS_ODF `pwd`
    gunzip *.gz
    mkdir "repro"
    cd "repro"

    cifbuild
    setenv SAS_CCF `pwd`/ccf.cif
    odfingest

    setenv SAS_ODF `pwd`/`ls -1 *SUM.SAS`
    emchain >& emchain.log
    epchain >& epchain.log

    ln -s P*M1*MIEV*.FIT m1_evt1.fits
    ln -s P*M2*MIEV*.FIT m2_evt1.fits
    ln -s P*PN*PIEV*.FIT pn_evt1.fits


    # When re-initializing sas environment
    # after having run ODF chain already
    # ------------------------------------
    setenv SAS_ODF `pwd`/$obsid/ODF
    setenv SAS_ODF `pwd`/`ls -1 $obsid/ODF/repro/*SUM.SAS`
    setenv SAS_CCF `pwd`/$obsid/ODF/repro/ccf.cif

Obsid 0087940901 does NOT have MOS or PN data, only RGS exposures, 2ks. Not sure why?
Therefore we're unable to run epchain as it errors out.  But emchain works, so
I guess that handles both MOS and RGS data.

Thursday 2015 September 24
==========================

Continuing with D. T. Reese's XMM cookbook (the data analysis PDF from Pat).
In what follows, I work with obsid 0087940201 in $obsid/ODF/repro/

First, make lightcurves: `mos1_ltcrv.fits, mos2_ltcrv.fits, pn_ltcrv.fits`.

    evselect table=m1_evt1.fits withrateset=yes rateset=mos1_ltcrv.fits maketimecolumn=yes timecolumn=TIME timebinsize=10 makeratecolumn=yes
    evselect table=m2_evt1.fits withrateset=yes rateset=mos2_ltcrv.fits maketimecolumn=yes timecolumn=TIME timebinsize=10 makeratecolumn=yes
    evselect table=pn_evt1.fits withrateset=yes rateset=pn_ltcrv.fits maketimecolumn=yes timecolumn=TIME timebinsize=10 makeratecolumn=yes

Inspect data with dsplot:

    dsplot table=mos1_ltcrv.fits x=TIME y=RATE &

MOS1 looks like lots of early flaring, maybe first 20-30% of obsid.  One flare at ~75% through.
First order fix would be to cut all before t = 1.5365e08, and excise t = 1.15384e08 to 1.15387e08
MOS2 looks like MOS1.
PN looks similar, but flares (and later flare) are shaped differently. Very clearly more counts.


Filter data by PATTERN and some standard set of flags (`#XMMEA_EM, #XMMEA_EP`).
Commands also set energy ranges, 0.2-12 keV for MOS and 0.2-15 keV for PN.
Note that PATTERN indicates types of event signals observed on the MOS or PN
CCDs, NOT the count rate.  See the links:
* [EPIC-mos event patterns](http://xmm.esac.esa.int/external/xmm_user_support/documentation/sas_usg/USG/MOSevtlist.html)
  "[Soft] X-rays mainly generate patterns 0 to 12 corresponding to compact
  regions of X-ray energy deposition... For imaging mode data patterns 0 to 12
  are the canonical set of valid X-ray events which are well calibrated.
  Selection of these patterns constitutes the best trade-off between detection
  efficiency and spectral resolution."
* [EPIC-pn event patterns](http://xmm.esac.esa.int/external/xmm_user_support/documentation/sas_usg/USG/pnevtlist.html)
  "For spectral analysis however, only single and double (pattern 0 to 4) should be used"

I got that confused at first and changed the PATTERN filters to <=11 (MOS) and
<=34 (PN), which subsequently messed up my attempts to generate RMF and ARF
files for spectral analysis!

    # Note change in the column #XMMEA_EM to #XMMEA_EP from MOS to PN
    evselect table=m1_evt1.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&#XMMEA_EM&&(PI in [200:12000])' filteredset=mos1-filt.fits filtertype=expression keepfilteroutput=yes
    evselect table=m2_evt1.fits:EVENTS withfilteredset=yes expression='(PATTERN<=12)&&#XMMEA_EM&&(PI in [200:12000])' filteredset=mos2-filt.fits filtertype=expression keepfilteroutput=yes
    evselect table=pn_evt1.fits:EVENTS withfilteredset=yes expression='(PATTERN<=4)&&#XMMEA_EP&&(PI in [200:15000])' filteredset=pn-filt.fits filtertype=expression keepfilteroutput=yes


Make binned images.  For Kes73...
On MOS1, Reese uses binsize=40.  One pixel = 1.1" x 1.1", compare to PSF HEW ~14".
On PN, Reese uses binsize=40 too. One pixel = 4.1", compare to PSF HEW ~15.2".
Ok let's do 40 for now, fiddle with it later.

    evselect table=mos1-filt.fits:EVENTS withimageset=yes imageset=mos1-filt-img.fits xcolumn=X ycolumn=Y imagebinning=binSize ximagebinsize=40 yimagebinsize=40
    evselect table=mos2-filt.fits:EVENTS withimageset=yes imageset=mos2-filt-img.fits xcolumn=X ycolumn=Y imagebinning=binSize ximagebinsize=40 yimagebinsize=40
    evselect table=pn-filt.fits:EVENTS withimageset=yes imageset=pn-filt-img.fits xcolumn=X ycolumn=Y imagebinning=binSize ximagebinsize=40 yimagebinsize=40

Looks pretty good!  Fuzzy blob...
Generate exposure maps as follows:

    atthkgen atthkset=atthk.fits  # Creates attitude information to get good time intervals (GTI)
    eexpmap imageset=mos1-filt-img.fits pimin=2000 pimax=8000 attitudeset=atthk.fits eventset=mos1-filt.fits expimageset=mos1_expmap.fits
    eexpmap imageset=mos2-filt-img.fits pimin=2000 pimax=8000 attitudeset=atthk.fits eventset=mos2-filt.fits expimageset=mos2_expmap.fits
    eexpmap imageset=pn-filt-img.fits pimin=2000 pimax=8000 attitudeset=atthk.fits eventset=pn-filt.fits expimageset=pn_expmap.fits

Select regions for spectral extraction.  Shapes selection is defined by XMM SAS
selectlib spec (http://xmm.esa.int/sas/current/doc/selectlib/node15.html).
It appears that DS9 physical/detector coordinates are the same (looking at
`mos1-filt-img.fits` and similar), and these coordinates correspond to straight
X/Y for XMM SAS.  Coordinates are:

    SNR ellipse:
	Center: 26260.5, 25100.5
	Radii: 6360, 4200
    Background ellipse:
	Center: 28604.5, 37740.5
	Radii: 6920, 3864

The resulting spectral extraction commands are:

    especget filestem=mos1src table=mos1-filt.fits srcexp='((X,Y) IN ellipse(26260.5, 25100.5, 6360, 42000, 0))' backexp='((X,Y) IN ellipse(28604.5, 37740.5, 6920, 3864, 0))' extendedsource=yes ;
    especget filestem=mos2src table=mos2-filt.fits srcexp='((X,Y) IN ellipse(26260.5, 25100.5, 6360, 42000, 0))' backexp='((X,Y) IN ellipse(28604.5, 37740.5, 6920, 3864, 0))' extendedsource=yes ;
    especget filestem=pnsrc table=pn-filt.fits srcexp='((X,Y) IN ellipse(26260.5, 25100.5, 6360, 42000, 0))' backexp='((X,Y) IN ellipse(28604.5, 37740.5, 6920, 3864, 0))' extendedsource=yes ;

NOTE: when I ran this (afternoon Thurs Sep 24) with filtered images that used weird PATTERN selections, I got errors:

    # MOS1, MOS2 run
    ** especget::rmfgen: warning (NonStandardPatterns), Non-standard pattern range - assuming energy pattern fraction = 1.0
    ... more logging ...
    ** especget::rmfgen: error (InvalidPatterns), An RMF cannot be produced for the pattern range in the DSS

which killed the MOS especget runs.  The PN run seemed to hang for about 1.5
hours creating the ARF, which isn't supposed to take that long.
It appears that tasks rmfgen, arfgen (which underly especget) cannot handle
non-standard patterns.  See the "NonStandardPattern" warning for arfgen:
[link](http://xmm.esac.esa.int/sas/current/doc/arfgen/node34.html).

I finally figured this out in the evening.  These output spectra will not be
usable for science, because we have not excised flares and made no attempt to
remove background etc.  So I need to figure out how to do that next.


Friday 2015 September 25 -- Weds 2015 September 30
==================================================

Inspect spectra in XSPEC with commands:

    XSPEC12>data mos1src_src.ds
    XSPEC12>setplot en
    XSPEC12>ignore **-0.2, 15.-**
    XSPEC12>cpd /xw
    XSPEC12>setplot rebin 5 5  # Pat recommends rebinning to 15 or 25
    XSPEC12>plot ldata

    XSPEC12>iplot
    PLT> rescale x 1.5 2.  # Zooming in on a faint Si line
    PLT> re y 0.01 .1

Good.  Now automatic flare filtering, to obtain GTIs:

    espfilt eventset=mos1-filt.fits method=histogram clobber=no -V 6
    espfilt eventset=mos2-filt.fits method=histogram clobber=no -V 6
    espfilt eventset=pn-filt.fits method=histogram clobber=no -V 6

PROBLEM: mos1 works but mos2 and pn fail... use verbose flag "-V 6" to explore.
Someone else had a similar error, occurring at same place in log.
RESOLUTION (much later, Weds 2015 Sep 30): tasks run successfully on statler, which has 8
GB RAM to treble's 4 GB.  Should have tried this earlier...

Output files from espfilt, where an example filestem is P0087940201M1S001 and XXX = 001, 002, 003:

    P{obsid}{M1,M2,PN}S{XXX}-objimg -- unfiltered "raw" image
    P{obsid}{M1,M2,PN}S{XXX}-objlc -- unfiltered light curve
    P{obsid}{M1,M2,PN}S{XXX}-corlc -- unfiltered corner light curve

    P{obsid}{M1,M2,PN}S{XXX}-hist.qdp -- histogram + lightcurves, qdp commands (very nice plots)
    P{obsid}{M1,M2,PN}S{XXX}-gti -- good time intervals in FITS and txt formats

    P{obsid}{M1,M2,PN}S{XXX}-objevlifilt -- filtered event list
    P{obsid}{M1,M2,PN}S{XXX}-objimgfilt -- image in det coords, pretty clean, SNR pops right out
    P{obsid}{M1,M2,PN}S{XXX}-corevlifilt  -- filtered corner event list
    P{obsid}{M1,M2,PN}S{XXX}-corimgfilt -- filtered corner image, looks empty?...

PROBLEM: I'm confused by the warning for PN that states data are in window
mode, so no corner files are generated.  XMM Archive states that the PN
exposure for this obsid is in extended full frame, not {large/small} window.
Why the discrepancy?
RESOLUTION: I had removed all the `OUT_OF_FOV` events because I'm operating on already-filtered data!
{mos1,mos2,pn}-filt.fits were generated with evselect using the `XMMEA_{EM,EP}` flags.

Generally Useful tools: fgui, fv, fhelp
Tools to manipulate spectra: mathpha, addrmf, addarf, dmhedit, grppha
(see scripts from Brian Williams, from Tycho project)

TODO: where do the exposure maps come into all this?


Monday 2015 October 5 -- Tuesday 2015 October 6
===============================================

Running ESAS and piecing together more about how things work...

Spectra after flare removal
---------------------------

Diversion (for mtg with Pat): created some spectra using espfilt-ered files
despite the fact that output from espfilt had some errors, due to lack of
corner pixels.  Should be OK for histogram method.  I suspect that especget
does NOT account for spatially varying / filterwheel background at all.

    especget filestem=mos1src_espfilt table=P0087940201M1S001-objevlifilt.FIT \
	srcexp='((X,Y) IN ellipse(26260.5, 25100.5, 6360, 42000, 0))' \
	backexp='((X,Y) IN ellipse(28604.5, 37740.5, 6920, 3864, 0))' \
	extendedsource=yes ;
    especget filestem=mos2src_espfilt table=P0087940201M2S002-objevlifilt.FIT \
	srcexp='((X,Y) IN ellipse(26260.5, 25100.5, 6360, 42000, 0))' \
	backexp='((X,Y) IN ellipse(28604.5, 37740.5, 6920, 3864, 0))' \
	extendedsource=yes ;
    especget filestem=pnsrc_espfilt table=P0087940201PNS003-objevlifilt.FIT \
	srcexp='((X,Y) IN ellipse(26260.5, 25100.5, 6360, 42000, 0))' \
	backexp='((X,Y) IN ellipse(28604.5, 37740.5, 6920, 3864, 0))' \
	extendedsource=yes ;

Result: these look almost the same as the very simply filtered spectra (no
explicit attempt to get GTIs without flares).
Yes, I looked at spectra, GTI ratios are something like (18.4 ks)/(30 ks) for
PN, and (27.3 ks)/(39.3 ks) for MOS1.  Nevertheless, main features are
unchanged.

Instrumental lines are removed, crudely, via background spectrum subtraction.
Since flares should affect FOV somewhat evenly, the background subtraction takes out flares as well.
The nice thing is that flares are removed, but photons from the source during flaring time are still kept.
But, subtracting as (flare + flare-epsilon1 + source) - (flare + flare-epsilon2) ~ source + flare-epsilon3
may heighten noise and assumes (1) clean sky background, and (2) flare affecting FOV uniformly.  These are not terrible assumptions by any means.

I ran a quick error analysis (see bottom) and it seems better to remove GTIs, in our case.


More on ESAS and pipeline/methodology layout
--------------------------------------------

Things to worry about (G309.2-0.6):
* Flares -- yes, about 25% of time (cut MOS 40ks to 27ks; PN 30ks to 18ks)
* Bad events -- yes, filtering the usual is fine.
* OOT events -- yes, problem for the bright O/B star
* Pileup -- ? unsure...

Current "chain" of ESAS commands I'm using (in script `esas_run`):

	epchain withoutoftime=true >& epchain_oot.log
	epchain >& epchain.log
	emchain >& emchain.log
	mos-filter >& mos-filter.log
	pn-filter >& pn-filter.log

	mos-spectra prefix=1S001 caldb=/data/mpofls/atran/research/xmm/caldb
		region=regm1.txt mask=0 elow=400 ehigh=1250 ccd1=1 ccd2=1 ccd3=1
		ccd4=1 ccd5=1 ccd6=1 ccd7=1 >& mos-spectra_1S001.log
	mos-spectra prefix=2S002 caldb=/data/mpofls/atran/research/xmm/caldb
		region=regm2.txt mask=0 elow=400 ehigh=1250 ccd1=1 ccd2=1 ccd3=1
		ccd4=1 ccd5=1 ccd6=1 ccd7=1 >& mos-spectra_2S002.log
	pn-spectra prefix=S003 caldb=/data/mpofls/atran/research/xmm/caldb
		region=regpn.txt mask=0 elow=400 ehigh=1250 quad1=1 quad2=1 quad3=1
		quad4=1 >& pn-spectra_S003.log

	mos_back prefix=1S001 caldb=/data/mpofls/atran/research/xmm/caldb
		diag=2 elow=400 ehigh=1250
		ccd1=1 ccd2=1 ccd3=1 ccd4=1 ccd5=1 ccd6=1 ccd7=1 >& mos_back_1S001.log
	mos_back prefix=2S002 caldb=/data/mpofls/atran/research/xmm/caldb
		diag=2 elow=400 ehigh=1250
		ccd1=1 ccd2=1 ccd3=1 ccd4=1 ccd5=1 ccd6=1 ccd7=1 >& mos_back_2S002.log
	pn_back prefix=S003 caldb=/data/mpofls/atran/research/xmm/caldb
		diag=2 elow=400 ehigh=1250
		quad1=1 quad2=1 quad3=1 quad4=1 >& pn_back_S003.log

NOTES learned the hard way (basically, how many times can Aaron fail to run ESAS correctly):

0. For quiescent particle background step (`{mos,pn}{-,_}{spectra,back}`),
   downloaded: esas-caldb-sasv13.tar.gz (1.5 GB) from the XMM SOC FTP
   `ftp://xmm.esac.esa.int/pub/ccf/constituents/extras/esas_caldb/`.
   DO NOT gunzip files; ESAS expects .gz files and will fail dramatically otherwise.
1. filter steps must run on statler or computer w/ more memory than treble, else evselect tasks in espfilt will fail.
   One sign of bad run is if mos-filter flags "anomalous" CCD state in all MOS2 CCDs because no files were produced.
2. If mos/pn-filter are re-run, need to move event files back to original place
   (3 files for MOS1, MOS2, PN event lists and 1 file for PN OOT event list)
   Here's a diff of ls -l output, before and after running {mos,pn}-filter, showing the emchain/epchain names:

	< -rw-r--r-- 1 atran mp  75M Oct  5 18:22 P0087940201PNS003OOEVLI0000.FIT
	---
	> -rw-r--r-- 1 atran mp   75M Oct  5 18:22 pnS003-oot.fits
	36c36
	< -rw-r--r-- 1 atran mp  73M Oct  5 18:30 P0087940201PNS003PIEVLI0000.FIT
	---
	> -rw-r--r-- 1 atran mp   73M Oct  5 18:30 pnS003-ori.fits
	42c42
	< -rw-r--r-- 1 atran mp  15M Oct  5 18:34 P0087940201M1S001MIEVLI0000.FIT
	---
	> -rw-r--r-- 1 atran mp   15M Oct  5 18:34 mos1S001-ori.fits
	44c44
	< -rw-r--r-- 1 atran mp  15M Oct  5 18:37 P0087940201M2S002MIEVLI0000.FIT
	---
	> -rw-r--r-- 1 atran mp   15M Oct  5 18:37 mos2S002-ori.fits

   Keep this diff, because you may need to re-locate these files...

3. I originally ran {mos,pn}-spectra with ellipses in (X,Y) coordinates,
   thinking that it's simply used for evselect so shouldn't break anything...
   Pat warned that XMM SAS (and definitely ESAS) doesn't like rectangular
   or square regions.
   So I created plaintext src/bgd files with the selections:

	src: &&((X,Y) IN ellipse(26260.5, 25100.5, 6360, 42000, 0))
	bgd: &&((X,Y) IN ellipse(28604.5, 37740.5, 6920, 3864, 0))

   But {mos,pn}-spectra runs failed.
   I gave up and created circular spectra in DETX,DETY coordinates, and cleared
   out ALL the files in my repro directory, to run ESAS with a clean slate.
   It seemed to work.
   So I haven't determined whether the region selections caused ESAS to fail.
   But it seems plausible.

4. {mos,pn}-spectra take a long time to run.  pn-spectra took 1hr 20min,
   mos-spectra took 50min. for each MOS camera.
   I think on treble mos-spectra was faster (20-30 min?) since I might be
   running less stuff, vs. Josh is using statler these days.

5. From source code: the event file should be cleaned of bad time intervals,
   bad pixels, and the like, but MUST include the corner pixels.  (So
   PATTERN<=12 is good, but FLAG==0 is not!).

5. I think the notion of using background/source region selections for ESAS
   is not correct.

> Our methodology for producing model QPB spectra (Kuntz & Snowden 2008) and
> other background components is based as much as possible on ``first
> principles''. We attempt to model as many of the aspects as possible using a
> wide range of inputs, e.g., filter-wheel-closed data, data from the unexposed
> corners of archived observations, and ROSAT All-Sky Survey data. We avoid the
> use of blank-sky data as they include to an unknown level the contributions
> of the cosmic background, residual SP contamination, and solar wind charge
> exchange contamination. This is in part due to the fact that a significant
> part of our scientific interest lies in the study of the diffuse background
> so we need a method that would not throw out our ``signal''. Other methods,
> such at that of Arnaud et al. (2001), Read & Ponman (2003), and Nevalainen,
> Markevitch, & Lumb (2005), have relied more on blank-field data for their
> subtractions.

I still don't know what exactly they do with the filterwheel spectra...

Anyways, result:
* use `mos1S001_obj.pi` with `mos1S001_back.pi` as background (BACKFILE).
  also manually link to RMF/ARF files.

Model the rest yourself!...

Monday 2015 October 5 (cont...)
===============================

Give up, just clear everything out and restart with clean slate.
Run the EXACT following commands, in order (following ESAS cookbook):

    # From the directory /data/mpofls/atran/research/xmm/
    # with subdirectory structure 0087940201_esas/{ODF,PPS}/
    cifbuild
    setenv SAS_CCF `pwd`/ccf.cif
    odfingest
    setenv SAS_ODF `pwd`/`ls -1 *SUM.SAS`

    ssh statler;

    epchain withoutoftime=true >& epchain_oot.log
    epchain >& epchain.log
    emchain >& emchain.log
    mos-filter >& mos-filter.log
    pn-filter >& pn-filter.log

    mos-spectra prefix=1S001 caldb=/data/mpofls/atran/research/xmm/caldb \
	region=regm1.txt mask=0 elow=400 ehigh=1250 ccd1=1 ccd2=1 ccd3=1 ccd4=1 ccd5=1 ccd6=1 ccd7=1 >& mos-spectra_1S001.log
    mos-spectra prefix=2S002 caldb=/data/mpofls/atran/research/xmm/caldb \
	region=regm2.txt mask=0 elow=400 ehigh=1250 ccd1=1 ccd2=1 ccd3=1 ccd4=1 ccd5=1 ccd6=1 ccd7=1 >& mos-spectra_2S002.log
    pn-spectra prefix=S003 caldb=/data/mpofls/atran/research/xmm/caldb \
	region=regpn.txt mask=0 elow=400 ehigh=1250 quad1=1 quad2=1 quad3=1 quad4=1 >& pn-spectra_S003.log

    mos_back prefix=1S001 caldb=/data/mpofls/atran/research/xmm/caldb \
	diag=2 elow=400 ehigh=1250 ccd1=1 ccd2=1 ccd3=1 ccd4=1 ccd5=1 ccd6=1 ccd7=1 >& mos_back_1S001.log
    mos_back prefix=2S002 caldb=/data/mpofls/atran/research/xmm/caldb \
	diag=2 elow=400 ehigh=1250 ccd1=1 ccd2=1 ccd3=1 ccd4=1 ccd5=1 ccd6=1 ccd7=1 >& mos_back_2S002.log
    pn_back prefix=S003 caldb=/data/mpofls/atran/research/xmm/caldb \
	diag=2 elow=400 ehigh=1250 quad1=1 quad2=1 quad3=1 quad4=1 >& pn_back_S003.log

Placed the following region expressions in regm1.txt, regm2.txt, and regpn.txt.
These are arbitrary selections, not exact same region of sky.

    &&((DETX,DETY) IN circle(-3417,-252.5,4233.03))  # MOS 1
    &&((DETX,DETY) IN circle(173.5,-3242,4391.91))  # MOS 2
    &&((DETX,DETY) IN circle(-51,3757.5,3035.48))  # PN

selected arbitrary regions for now.  Not the same area of sky.

Lots of exploration over Mon,Tues,Weds of Oct 5-7, trying to figure out ESAS
and getting kind of frustrated/stuck.  The useful notes are summarized below.

(note, revisiting this 2015 Nov 14: notes currenly pushed to appendices at the
bottom, and may eventually be reshuffled to other text files)


Monday 2015 October 12, Saturday 2015 October 17
================================================

Outstanding questions / things to check:
* epreject, epnoise

## What's REALLY in this quiescent particle background?

Here I CAREFULLY walk through the procedure traced out by Snowden and Kuntz, in
their 2008? A&A paper.

(snowden et al.'s) Motivation: analysis of diffuse emission that fills the FOV
(i.e., where there is no such thing as a "background" region)

Procedure:

1. extract spectra from all chip corners of your observation
   (`mos{pref}-*oc.pi`, where `*` indicates CCD 2-7)

2. extract spectra from all chip corners of all public observations (NOT FWC),
   IF the hardness ratio of other data matches your observation.  This is an
   "augmentation" of the `-oc.pi` data, NOT FWC data, to improve
   signal-to-noise.  Uses 42 Ms of public XMM data, since corners are always
   outside FOV.
   This appears to be carried out in the mos/pn-back stage, not in
   mos/pn-spectra.
   So I can't verify this, without going into the source code.
     The relevant file is {mos1,pn,mos2}-qpb.fits.gz

3. Assume "ratios of spectra from different regions of a chip are temporally
   invariant".
   - Extract `mos{pref}-*ff.pi` (FWC data for piece of region in chip `*`, 1-7)
   - Extract `mos{pref}-*fc.pi` (FWC data for corner of each chip, `*` is 2-7)

   Multiply -oc.pi (observation corner) by ratio of -ff.pi / -fc.pi
   To get ratio, smooth -ff.pi and -fc.pi slightly and then take the ratio.

   Maybe you can say, alternately, that we take -ff.pi * -oc.pi/-fc.pi (scale
   the FWC spectrum in your region, by the ratio of corner spectra) (although
   the smoothing/ratio operation means the operands don't commute)
   "This ''corrects'' the unexposed-region spectra to the shape of the spectrum
   in the region of interest."
   GOOD, this all makes sense.

4. Need to handle MOS1 CCD1 and MOS2 CCD1 specially.  Central CCD doesn't have
   any corner pixels!

   In MOS1, we empirically observe that total QPB spectrum in CCD1 is similar
   to CCDs 2,3,6,7.
   In MOS2, CCD1 is similar to CCDs 3,4,6.

   Take ratio of -1ff.pi / {-2fc.pi, -3fc.pi, -6fc.pi, -7fc.pi}
   (ratio of FWC region / FWC corners)
   Then, multiply by {-2oc.pi, -3oc.pi, -6oc.pi, -7oc.pi}.
   Basically, `-1ff.pi * {-*oc.pi/-*fc.pi}` takes the FWC data in our src
   region, then scales by the ratio of (corner obs)/(corner FWC) data for the
   chips w/ similar spectra to the central chip.

     (source FWC, ccd 1) * (corner obs)/(corner FWC)

   Assume the ratio of obs/FWC spectra is the same in corner, as it is in the
   region of interest (ROI).  Now, assume that ratio of obs/FWC spectra is same
   for MOS1-1 as it is for MOS1-{2,3,6,7}.  Then we can easily scale the FWC
   spectrum for ROI, to expected normalization for the actual observation.

   So that's what the code does.  I don't know precisely how it does the ratios
   for multiple CCDs, but hopefully there's some sensible weighting.

5. Now, combine the spectra from all these chips (`-ff.pi * -oc.pi/-fc.pi`),
   weighting appropriately by RMF/ARF/whatever, to form a single background
   region.

Note about ESAS CALDB fwc.fits.gz vs qpb.fits.gz.  The file sizes look wrong.
From Kuntz/Snowden Table 4, the augmentation data (qpb) should have ~1.5
million cts/ccd, vs. ~0.2 million cts/ccd for FWC data.  But, FWC data file is
123 MB to QPB's 34 MB.  Why?

1. Unzip files.  fwc.fits is 187M to qpb.fits 405M (ratio a bit above 2)
2. Look at qpb.fits file using `fv` tool.  There are six tables for each of
   CCDs 2-6.  Each CCD has data from 7202 observations with information on:
   - obsid, revolution, filter, instrument, RA/dec
   - total time, clean time
   - rate, rate err
   - hardness, hardness err
   - spectrum
   There are 1.4 million counts in MOS1 FWC vs. 9.7 million in MOS1 obs
   database, according to Table 4 of Kuntz/Snowden.  But QPB data are stored as
   spectra: ~500 channels x 7202 obsids = 3.6 million data points.

Everything checks out. Uncompressed file size ratios are about
right (bit above 2) and it makes sense that spectra (qpb) file compresses
better than the plain event list.

Resulting interpretation: the QPB is a correctly weighted (FWC to obs)
extraction of FWC data in the ROI.  Kuntz/Snowden 2008 claim that FWC data used
are only those with similar hardness ratios, as justified in their paper.
They explicitly exclude the Al/Si line region and apply a simple continuum fit.
"It is unwise merely to exclude the region containing these lines as the low
energy wings are quite extensive and so affect the lower energy data."


Possible concern: what if the incident particle background is different due to
the closed filterwheel (1.05 mm Al)?

* Corner spectrum should be the same regardless of filterwheel; energetic
  particles focused by mirrors wouldn't hit corners.

* The ROI may experience a different spectrum.  We ask,
  1. what is relative flux of particles via FOV, to particles outside FOV
  2. how does FWC attenuate that.  And, for particles incident on telescope
     structure causing K-alpha fluorescence:
  3. does FWC positioning affect incident flux or not?

  I don't know the answers to 1 and 2.  For 3, my hope is that it is
  negligible, being a small element; moreover, it most effectively impedes
  particles traveling down the boresight -- but these are should _not_ be the
  particles that cause instrumental line fluorescence.

  "Fourth, the mask protecting the unexposed pixels from cosmic X-rays also
  protects them from the softest and most highly temporally variable component
  of the particle background, the ''soft proton flares''."

  So, obviously, QPB cannot account for soft protons intrinsic to observation.
  What about stable background flux of soft protons / soft particles?

  I really do not know for sure.  But, I'll guess it's a small effect...


## Beyond the QPB

After the QPB, we must deal with instrumental lines + additional background (in
particular, sky X-ray background).

> The bulk of the quiescent particle background spectrum can be modeled and
> subtracted directly from the source spectrum. The remaining particle
> background components, the strong Al and Si instrumental lines, and the
> residual contamination by soft proton flares can be fitted simultaneously
> with the source spectrum. These multiple components lead to a multiplication
> of fit parameters, but we show that these components can be relatively simply
> parameterized. Note that these methods require summing large areas of the
> detector, so they are not useful for small extended objects; in these cases
> the traditional method of annular background subtraction is usually
> appropriate.  However, the background characterization developed here,
> particularly the division of the background between the quiescent component
> and the soft proton component where these components have significantly
> different spatial features, should be useful to those interested in the
> photometry of small regions. 

Instrumental background varies a lot.  Al line is bright over most of MOS with
some spots (CCD edges, seemingly random streaks/corners) not as bright.  Si
line is bright on edges of CCD1.  Au is concentrated near bottom of MOS (CCDs
7,2).  Fe,Cr are strong at far corners (CCDs 4,5,7,2).

We could get a ratio of lines in the ROI, from FWC closed data.  But we
wouldn't know how to scale it.
* The incident photon/particle spectrum causing K-alpha fluorescence could be
  different when the FW is removed.


Sunday 2015 October 18 -- Monday 2015 October 19
================================================

## Region selection + region files

Attempting to get consistent regions in all detectors by converting RA/dec to
XMM DETX/DETY.
NOTE: easiest to select regions from PPS processed image
P0087940201EPX000OIMAGE8000.fit
which I have done for these new src/bkg
regions.

In sky coords (fk5), here's a basic ds9 region covering most of the remnant:
 
	circle(13:46:47.553, -62:51:02.52, 239.76")

this region just butts up against the bright star HD11xxxx, trying to get as
much extended emission as possible.  It does miss extended emission to the west.
At least a few point sources are caught by this circle -- not much we can do
given the foreground star cluster.  Maybe we should run the point source
removal tool.

Two possible tools for coordinate conversion are ecoordconv and esky2det
Convert to XMM sky (X,Y) coordinates, and
then to individual detector coordinates:

    esky2det datastyle='user' ra='13h46m47.553s' dec='-62d51m02.52s' outunit='det' calinfoset='mos1S001-ori.fits'
    esky2det datastyle='user' ra='13h46m47.553s' dec='-62d51m02.52s' outunit='det' calinfoset='mos2S002-ori.fits'
    esky2det datastyle='user' ra='13h46m47.553s' dec='-62d51m02.52s' outunit='det' calinfoset='pnS003-ori.fits'

Outputs:

    # Instrument: EMOS1
    # Coord sytem of output is DETXY (CAMCOORD2 but in units of 0.05 arcsec).
    # Source RA = 206.698135 deg.
    # Source dec = -62.850700 deg.
    #
    # detX       detY
     -2055.2    -1690.2
    # ...
    # Instrument: EMOS2
    # detX       detY
      1509.3    -2280.0
    # ...
    # Instrument: EPN
    # detX       detY
     -1383.0     2121.9

    &&((DETX,DETY) IN circle(-2055.2, -1690.2, 4795.2))
    &&((DETX,DETY) IN circle(1509.3, -2280.0, 4795.2))
    &&((DETX,DETY) IN circle(-1383.0, 2121.9, 4795.2))

I updated files `0087940201_esas/ODF/repro/reg{m1,m2,pn}.txt` with new DETX/DETY regions.

Here are three circles around the remnant periphery that should capture a decent background...

    circle(13:47:42.885, -62:44:57.88, 125.41")
    circle(13:46:33.606, -62:42:02.47, 113.572")
    circle(13:47:32.693, -62:56:46.10, 125.41")

Radii are 2508.2, 2271.44, 2508.2.
These explicitly exclude stars, although remnant circle certainly contains lots of stars...

    esky2det datastyle='user' ra='13h47m42.885s' dec='-62d44m57.88s' outunit='det' calinfoset='mos1S001-ori.fits' withheader='no'
    esky2det datastyle='user' ra='13h47m42.885s' dec='-62d44m57.88s' outunit='det' calinfoset='mos2S002-ori.fits' withheader='no'
    esky2det datastyle='user' ra='13h47m42.885s' dec='-62d44m57.88s' outunit='det' calinfoset='pnS003-ori.fits' withheader='no'

    esky2det datastyle='user' ra='13h46m33.606s' dec='-62d42m02.47s' outunit='det' calinfoset='mos1S001-ori.fits' withheader='no'
    esky2det datastyle='user' ra='13h46m33.606s' dec='-62d42m02.47s' outunit='det' calinfoset='mos2S002-ori.fits' withheader='no'
    esky2det datastyle='user' ra='13h46m33.606s' dec='-62d42m02.47s' outunit='det' calinfoset='pnS003-ori.fits' withheader='no'

    esky2det datastyle='user' ra='13h47m32.693s' dec='-62d56m46.10s' outunit='det' calinfoset='mos1S001-ori.fits' withheader='no'
    esky2det datastyle='user' ra='13h47m32.693s' dec='-62d56m46.10s' outunit='det' calinfoset='mos2S002-ori.fits' withheader='no'
    esky2det datastyle='user' ra='13h47m32.693s' dec='-62d56m46.10s' outunit='det' calinfoset='pnS003-ori.fits' withheader='no'

Outputs:

    # Instrument: EMOS1
    # detX       detY
      8426.8    -2629.0
    # Instrument: EMOS2
    # detX       detY
      2501.6     8197.0
    # Instrument: EPN
    # detX       detY
     -2282.3    -8363.5
									      
    # Instrument: EMOS1
    # detX       detY
      4819.1     6857.7
    # Instrument: EMOS2
    # detX       detY
     -7003.4     4637.8
    # Instrument: EPN
    # detX       detY
      7190.8    -4720.2
									      
    # Instrument: EMOS1
    # detX       detY
     -3188.2   -10855.1
    # Instrument: EMOS2
    # detX       detY
     10668.3    -3459.8
    # Instrument: EPN
    # detX       detY
    -10552.1     3220.5

Resulting region expressions:

    Radii are 2508.2, 2271.44, 2508.2.

    circle(8426.8, -2629.0, 2508.2)
    circle(2501.6, 8197.0, 2508.2)
    circle(-2282.3, -8363.5, 2508.2)

    circle(4819.1, 6857.7, 2271.44)
    circle(-7003.4, 4637.8, 2271.44)
    circle(7190.8, -4720.2, 2271.44)

    circle(-3188.2, -10855.1, 2508.2)
    circle(10668.3, -3459.8, 2508.2)
    circle(-10552.1, 3220.5, 2508.2)

    &&(((DETX,DETY) IN circle(8426.8, -2629.0, 2508.2)) || ((DETX,DETY) IN circle(4819.1, 6857.7, 2271.44)) || ((DETX,DETY) IN circle(-3188.2, -10855.1, 2508.2)))
    &&(((DETX,DETY) IN circle(2501.6, 8197.0, 2508.2)) || ((DETX,DETY) IN circle(-7003.4, 4637.8, 2271.44)) || ((DETX,DETY) IN circle(10668.3, -3459.8, 2508.2)))
    &&(((DETX,DETY) IN circle(-2282.3, -8363.5, 2508.2)) || ((DETX,DETY) IN circle(7190.8, -4720.2, 2271.44)) || ((DETX,DETY) IN circle(-10552.1, 3220.5, 2508.2)))

OK, let's try generating some spectra!

Started around 12:33 pm.  Finished around 1:33pm.
Now group some spectra.

grppha

    atran(sas)@treble:/data/mpofls/atran/research/xmm/0087940201_esas/ODF/repro$ grppha
    Please enter PHA filename[] mos1S001-obj-src.pi
    Please enter output filename[] mos1S001-obj-src-grp.pi
    GRPPHA[] chkey BACKFILE mos1S001-back-src.pi
    GRPPHA[] chkey RESPFILE mos1S001-src.rmf
    GRPPHA[] chkey ANCRFILE mos1S001-src.arf
    GRPPHA[] group min 50
    GRPPHA[] exit
     ... written the PHA data Extension
     ...... exiting, changes written to file : mos1S001-obj-src-grp.pi
     ** grppha 3.0.1 completed successfully

OK!  Repeated this process for all spectra to obtain:

    mos1S001-obj-src-grp.pi
    mos1S001-obj-bkg-grp.pi
    pnS003-obj-src-grp.pi
    pnS003-obj-bkg-grp.pi

Now, attempt to model background (mos1S001-obj-bkg-grp.pi) and see how far I can get.
* Al K-alpha: 1.49 keV line with zero width
* Si K-alpha: 1.75 keV line with zero width
* galactic XRB: powerlaw
* extragalactic XRB: thermal (ray, apec)

Result: did not get very far...

Discussed some at group meeting.  Lots of discussion with Josh afterwards,
details about absorption, etc.

It turns out, looking at my unfolded spectrum, that it ticks way up, so as to
be not model-able by the components I'm working with.
Next logical step is to re-run pipeline on different observation and see if
same issue occurs.

## Regions for Motch obsid 0551000201

SOURCE REGIONS for MOTCH obsid 0551000201, using same regions on sky.

    # Eventually I will make a small shell script for this
    # Note that RADII are currently hardcoded..
    esky2det datastyle='user' ra='13h46m47.553s' dec='-62d51m02.52s' outunit='det' calinfoset='mos1S001-ori.fits' withheader='no' -V 0 \
	    | sed '/^\s*$/d' | sed -r 's/\s+([0-9.-]+)\s*([0-9.-]+)/\&\&((DETX,DETY) IN circle(\1, \2, 4795.2))/'
    esky2det datastyle='user' ra='13h46m47.553s' dec='-62d51m02.52s' outunit='det' calinfoset='mos2S002-ori.fits' withheader='no' -V 0 \
	    | sed '/^\s*$/d' | sed -r 's/\s+([0-9.-]+)\s*([0-9.-]+)/\&\&((DETX,DETY) IN circle(\1, \2, 4795.2))/'
    esky2det datastyle='user' ra='13h46m47.553s' dec='-62d51m02.52s' outunit='det' calinfoset='pnS003-ori.fits' withheader='no' -V 0 \
	    | sed '/^\s*$/d' | sed -r 's/\s+([0-9.-]+)\s*([0-9.-]+)/\&\&((DETX,DETY) IN circle(\1, \2, 4795.2))/'

    # Resulting regions.
    # Checked regions in DS9 (against the usual event lists, original files from em/epchain). Look good.
    &&((DETX,DETY) IN circle(-4650.2, -2784.3, 4795.2))
    &&((DETX,DETY) IN circle(2590.2, -4880.6, 4795.2))
    &&((DETX,DETY) IN circle(-2486.9, 4712.8, 4795.2))

    # GET BACKGROUND REGION EXPRESSION as follows
    # Radii are 2508.2, 2271.44, 2508.2.
    esky2det datastyle='user' ra='13h47m42.885s' dec='-62d44m57.88s' outunit='det' calinfoset='mos1S001-ori.fits' withheader='no' -V 0 > a.tmp
    esky2det datastyle='user' ra='13h46m33.606s' dec='-62d42m02.47s' outunit='det' calinfoset='mos1S001-ori.fits' withheader='no' -V 0 > b.tmp
    esky2det datastyle='user' ra='13h47m32.693s' dec='-62d56m46.10s' outunit='det' calinfoset='mos1S001-ori.fits' withheader='no' -V 0 > c.tmp
    cat a.tmp b.tmp c.tmp | sed '/^\s*$/d' | sed -r 's/\s*([0-9.-]+)\s*([0-9.-]+)/((DETX,DETY) IN circle(\1, \2, r))/'
    rm *.tmp

    esky2det datastyle='user' ra='13h47m42.885s' dec='-62d44m57.88s' outunit='det' calinfoset='mos2S002-ori.fits' withheader='no' -V 0 > a.tmp
    esky2det datastyle='user' ra='13h46m33.606s' dec='-62d42m02.47s' outunit='det' calinfoset='mos2S002-ori.fits' withheader='no' -V 0 > b.tmp
    esky2det datastyle='user' ra='13h47m32.693s' dec='-62d56m46.10s' outunit='det' calinfoset='mos2S002-ori.fits' withheader='no' -V 0 > c.tmp
    cat a.tmp b.tmp c.tmp | sed '/^\s*$/d' | sed -r 's/\s*([0-9.-]+)\s*([0-9.-]+)/((DETX,DETY) IN circle(\1, \2, r))/'
    rm *.tmp

    esky2det datastyle='user' ra='13h47m42.885s' dec='-62d44m57.88s' outunit='det' calinfoset='pnS003-ori.fits' withheader='no' -V 0 > a.tmp
    esky2det datastyle='user' ra='13h46m33.606s' dec='-62d42m02.47s' outunit='det' calinfoset='pnS003-ori.fits' withheader='no' -V 0 > b.tmp
    esky2det datastyle='user' ra='13h47m32.693s' dec='-62d56m46.10s' outunit='det' calinfoset='pnS003-ori.fits' withheader='no' -V 0 > c.tmp
    cat a.tmp b.tmp c.tmp | sed '/^\s*$/d' | sed -r 's/\s*([0-9.-]+)\s*([0-9.-]+)/((DETX,DETY) IN circle(\1, \2, r))/'
    rm *.tmp

    # Resulting background regions are:
    &&( ((DETX,DETY) IN circle(-15164.3, -3241.1, 2508.2)) || ((DETX,DETY) IN circle(-10332.7, -12167.0, 2271.44)) || ((DETX,DETY) IN circle(-4740.1, 6449.9, 2508.2)) )
    &&( ((DETX,DETY) IN circle(2993.3, -15396.8, 2508.2)) || ((DETX,DETY) IN circle(11943.7, -10610.9, 2271.44)) || ((DETX,DETY) IN circle(-6644.4, -4923.4, 2508.2)) )
    &&( ((DETX,DETY) IN circle(-2983.2, 15225.1, 2508.2)) || ((DETX,DETY) IN circle(-11890.8, 10360.0, 2271.44)) || ((DETX,DETY) IN circle(6747.0, 4837.4, 2508.2)) )

Created files:

    -rw-r--r-- 1 atran mp   52 Oct 20 02:21 regm1src.txt
    -rw-r--r-- 1 atran mp   51 Oct 20 02:21 regm2src.txt
    -rw-r--r-- 1 atran mp   51 Oct 20 02:21 regpnsrc.txt
    -rw-r--r-- 1 atran mp  165 Oct 20 02:21 regm1bkg.txt
    -rw-r--r-- 1 atran mp  164 Oct 20 02:21 regm2bkg.txt
    -rw-r--r-- 1 atran mp  162 Oct 20 02:21 regpnbkg.txt

AFTER A LOT OF FIDDLING, figured out how to use nohup and kill nohup processes...

    nohup perl -we '$| = 1 ; my $i = 0 ; while ( $i < 120 ) { my @lt = localtime ; print "hi! It is @lt!\n" ; sleep 1 ; $i++ ; }' > nohuptest.txt &

For spectra generation... I modified `esas_run` to run mos/pn-filter, then get spectra (mos/pn-spectra, mos/pn-back).
* sshed into statler
* sourced sasinit and sas_setpaths
* ran command:

    nohup source esas_run > nohup_esas_run_20151020.txt &

* PID is 1779  Started around 02:48am

    atran(sas)@statler:/data/mpofls/atran/research/xmm$ nohup source esas_run > nohup_esas_run_20151020.txt &
    [1] 1779

* Now running mos1S001 spectra... TIME TO SLEEP UGH


Tuesday 2015 October 20
=======================

Post-mortem: spectra finished running about an hour later, it turns out the runs for PN segfaulted?!
Grouped all the spectra and investigated further.  Same as before, assign
rmf/arf files, group min 50, and check out in XSPEC.

    mos1S001-obj-src-grp.pi
    mos1S001-obj-bkg-grp.pi
    grppha mos2S002-obj-src.pi mos2S002-obj-src-grp.pi 'chkey BACKFILE mos2S002-back-src.pi & chkey RESPFILE mos2S002-src.rmf & chkey ANCRFILE mos2S002-src.arf & group min 50 & exit' 
    grppha mos2S002-obj-bkg.pi mos2S002-obj-bkg-grp.pi 'chkey BACKFILE mos2S002-back-bkg.pi & chkey RESPFILE mos2S002-bkg.rmf & chkey ANCRFILE mos2S002-bkg.arf & group min 50 & exit' 

Observation: 
* mos1S001-obj-bkg-grp.pi from 0087940201 (Hughes) looks awful, extremely sharp rise at/above 5 keV.
* mos2S002-obj-bkg-grp.pi from 0087940201 (Hughes) looks awful, like MOS1
* pnS003-obj-bkg-grp.pi from 0087940201 (Hughes) looks awful, like MOS1.  Same extremely sharp rise above 5 keV. WHY?
* mos1S001-obj-bkg-grp.pi from 0551000201 (Motch) looks OK, appears to be a very slight trend up in the unfolded spectrum
* mos2S002-obj-bkg-grp.pi from 0551000201 (Motch) looks OK, similar to MOS1 

PLAN:
0. clean up all these damn notes.
1. re-run 00879... from scratch
2. re-run with epreject, epnoise on (see if that helps the low energy hump)


I deleted everything in `0087940201_esas/ODF/repro/` save for the DETX/DETY region selections.
Now I'll re-run `esas_run` from the very top.  Executing from the top on statler.
PID is 14938.
Started ~ 0100am

Wednesday 2015 October 21
=========================

Just playing around -- fitting the re-generated
`0087940201_esas/ODF/repro/mos1S001-obj-src-grp.pi`
using `mos1S001-obj-bkg-grp.pi` as the background (so I'm not subtracting out
instrumental).  This is a simple phabs x vrnei fit.  Confirms Rakowski's
results, to first order.

    ========================================================================
    Model phabs<1>*vrnei<2> Source No.: 1   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
       1    1   phabs      nH         10^22    0.881905     +/-  0.263328     
       2    2   vrnei      kT         keV      1.62262      +/-  0.351555     
       3    2   vrnei      kT_init    keV      0.541260     +/-  5.22617E-02  
       4    2   vrnei      H                   0.190000     +/-  29.4756      
       5    2   vrnei      He                  1.97384      +/-  67.0333      
       6    2   vrnei      C                   1.00000      frozen
       7    2   vrnei      N                   0.0          frozen
       8    2   vrnei      O                   7.33475      +/-  10.1127      
       9    2   vrnei      Ne                  0.0          frozen
      10    2   vrnei      Mg                  0.633630     +/-  0.164212     
      11    2   vrnei      Si                  3.91065      frozen
      12    2   vrnei      S                   4.98210      frozen
      13    2   vrnei      Ar                  3.17513      +/-  1.42175      
      14    2   vrnei      Ca                  7.39625      +/-  6.31153      
      15    2   vrnei      Fe                  0.165129     +/-  0.120787     
      16    2   vrnei      Ni                  1.07152      +/-  1.43786      
      17    2   vrnei      Tau        s/cm^3   1.00000E+08  +/-  1.42943E+10  
      18    2   vrnei      Redshift            0.0          frozen
      19    2   vrnei      norm                1.36767E-03  +/-  3.93857E-04  
    ________________________________________________________________________


    Fit statistic : Chi-Squared =         214.48 using 198 PHA bins.

    Test statistic : Chi-Squared =         214.48 using 198 PHA bins.
     Reduced chi-squared =         1.1594 for    185 degrees of freedom 
     Null hypothesis probability =   6.780013e-02

ANYWAYS, back to the main problem.

ALL of the data for 0087940201 show this problem.
The data for 0551000201 might show a small uptick, but it's subtle enough to
look like it's within error.  So for now I'll assume that this problem is
confined to 0087940201.

What's going on?

1. I use the same code for 0551000201 and re-ran the commands from scratch for
   0087940201.  So it's unlikely to be a (direct) bug in the data reduction.

   It's possible that the scripts being used are tripping up somehow.
   Run evselect and PATTERN filter by hand for spectra.
   I try successively more restrictive filters:
   - PATTERN <= 12, `#XMMEA_EM`
   - PATTERN <= 12, `#XMMEA_SM`
   - PATTERN <= 12, FLAG == 0
   Recalling that

	XMMEA_EM= '(FLAG & 0x766ba000) == 0' / Select good MOS events
	XMMEA_SM= '(FLAG & 0xfffffeff) == 0' / Select good MOS events for spectra
		compared to 'FLAG == 0', XMMEA_SM allows 0x00000100 (CLOSE_TO_DEADPIX) to pass through.

   with the following commands:

	evselect table=mos1S001-clean.fits:EVENTS filtertype=expression \
	    expression='(PATTERN<=12) && (PI in [200:12000]) && #XMMEA_EM' \
	    filtertype=expression withfilteredset=yes keepfilteroutput=yes \
	    filteredset='mos1S001-clean-XMMEA_EM-pattern12.fits'
	especget filestem='mos1src_especget_XMMEA_EM_pattern12' \
	    table='mos1S001-clean-XMMEA_EM-pattern12.fits' \
	    srcexp='((DETX,DETY) IN circle(-2055.2, -1690.2, 4795.2))' \
	    backexp='(((DETX,DETY) IN circle(8426.8, -2629.0, 2508.2)) \
		|| ((DETX,DETY) IN circle(4819.1, 6857.7, 2271.44)) \
		|| ((DETX,DETY) IN circle(-3188.2, -10855.1, 2508.2)))'

	evselect table=mos1S001-clean.fits:EVENTS filtertype=expression \
	    expression='(PATTERN<=12) && (PI in [200:12000]) && #XMMEA_SM' \
	    filtertype=expression withfilteredset=yes keepfilteroutput=yes \
	    filteredset='mos1S001-clean-XMMEA_SM-pattern12.fits'
	especget filestem='mos1src_especget_XMMEA_SM_pattern12' \
	    table='mos1S001-clean-XMMEA_SM-pattern12.fits' \
	    srcexp='((DETX,DETY) IN circle(-2055.2, -1690.2, 4795.2))' \
	    backexp='(((DETX,DETY) IN circle(8426.8, -2629.0, 2508.2)) \
		|| ((DETX,DETY) IN circle(4819.1, 6857.7, 2271.44)) \
		|| ((DETX,DETY) IN circle(-3188.2, -10855.1, 2508.2)))'

	evselect table=mos1S001-clean.fits:EVENTS filtertype=expression \
	    expression='(PATTERN<=0) && (PI in [200:12000]) && (FLAG == 0)' \
	    filtertype=expression withfilteredset=yes keepfilteroutput=yes \
	    filteredset='mos1S001-clean-perfect.fits'
	especget filestem='mos1src_especget_perfect' \
	    table='mos1S001-clean-perfect.fits' \
	    srcexp='((DETX,DETY) IN circle(-2055.2, -1690.2, 4795.2))' \
	    backexp='(((DETX,DETY) IN circle(8426.8, -2629.0, 2508.2)) \
		|| ((DETX,DETY) IN circle(4819.1, 6857.7, 2271.44)) \
		|| ((DETX,DETY) IN circle(-3188.2, -10855.1, 2508.2)))'

   Run as a nohup script, started around 19:10pm:

    atran(sas)@statler:/data/mpofls/atran/research/xmm$ nohup source spectrum_debug_20151022.tcsh > nohup_spectrum_debug_20151022.log &
    [1] 13285

Looking at spectra, after finishing:

	mos1src_especget_XMMEA_SM_pattern12_src.ds -- shows tail
	mos1src_especget_perfect_src.ds -- SAME PROBLEM?!

So it's not due to unfiltered events.

Even non-ESAS-processed data (from my walkthrough of Dan T. Reese's procedure)
show the same issue.

2. I use the right sky regions in all cases?
   * MOS1 hughes - yep (source)
   * MOS2 hughes - yep (source)
   * PN hughes - yep (source)
   Since this issue occurs for both source and bkg spectra I'll take this as being OK.
   Corroborated by the fact that spectra shows spectrum consistent w/ Rakowski+ paper.

3. soft proton flare filtering was OK?
   * Hughes (MOS1) looks OK
   * Motch (MOS1) looks OK, but definitely some contamination (needs a tighter cut)


Sunday 2015 October 25
======================

Reviewing this problem so far...

The final step I can take would be to download the data again, apply a very
basic proton-flare filter, and check simply extracted spectra (not worrying
about the filterwheel-extracted QPB).  Let's try this.
IF that doesn't work -- consider excising the affected data?

    # from /data/mpofls/atran/research/xmm/
    mkdir 0087940201_redl
    cd 0087940201_redl
    curl -o files.tar "http://nxsa.esac.esa.int/nxsa-sl/servlet/data-action-aio?obsno=0087940201"
    tar -xvf files.tar
    mv 0087940201/* .
    rmdir 0087940201/
    
    cd odf
    tar -xzvf 0087940201.tar.gz
    tar -xvf 0315_0087940201.TAR

The data so downloaded directly from ESAS contains a few different files.
Excluding the various tar/tar.gz files, the content changes from
`0087940201_esas/ODF/` to `0087940201_redl/odf/` are
(line numbers are wrong because I've removed some irrelevant changes)

    102a104
    >    887040 0315_0087940201_R1X00000OFX.FIT
    139a142
    >    887040 0315_0087940201_R2X00000OFX.FIT
    143c146
    <   743040 0315_0087940201_SCX00000ATS.FIT
    ---
    >    803520 0315_0087940201_SCX00000ATS.FIT
    152a156
    >  24170403 0315_0087940201_SCX00000RAS.ASC
    154c158
    <    63909 0315_0087940201_SCX00000SUM.ASC
    ---
    >     64475 0315_0087940201_SCX00000SUM.ASC
    156c160,164
    >    838080 0315_0087940201_SCX00000TCX.FIT
    >       411 MANIFEST.276294

New files:
* `0315_0087940201_R1X00000OFX.FIT`
* `0315_0087940201_R2X00000OFX.FIT`
* `0315_0087940201_SCX00000RAS.ASC`
* `0315_0087940201_SCX00000TCX.FIT`
* `MANIFEST.276294`
Larger files:
* `0315_0087940201_SCX00000ATS.FIT` (726K to 785K -- spacecraft attitude history file)
* `0315_0087940201_SCX00000SUM.ASC` (63909 to 64475 bytes)

(editorial note, 2015 Nov. 14: the new files are described in the MANIFEST.)

Looks OK to me.  Let's try re-rerunning the basic processing chain.
I run my `esas_run` script on statler, modified to execute all of:

    cifbuild
    odfingest
    epchain withoutoftime=true
    epchain
    emchain

and no more.  Started running around 16:48pm.

    atran(sas)@statler:~/rsch/xmm$ nohup source esas_run > nohup_esas_run_0087940201_redl_chains_20151025.log &
    [1] 18126

NOW, try generating spectra from unadulterated event list (NO proton flare filtering!)
Started around 17:32p.

    atran(sas)@statler:~/rsch/xmm$ nohup source spectrum_debug_redl.tcsh > spectrum_debug_redl.log &
    [1] 24226

Inspect "redl" spectra: answer, yep, same problem present...

When I return to the ESAS processed spectra, it seems like the spectra
from both obsids show the same problem!

    atran(sas)@treble:~/rsch/xmm/0087940201_esas/ODF/repro$ xspec
    ...
    XSPEC12>data 1:1 mos1S001-obj-src-grp.pi
    XSPEC12>data 2:2 ../../../0551000201_esas/ODF/repro/mos1S001-obj-src-grp.pi
    XSPEC12>setplot en
    XSPEC12>cpd /xw
    XSPEC12>ignore **:**-0.3,10.0-**
    XSPEC12>mo phabs*po

BUT, confusingly, when I plot data just for 0551000201 alone, it looks ok.  what the hell?
Hypothesis: both were using same rmf/arf files, in the 0087940201 folder, since the paths are not hardwired...
Quick test to confirm:

    atran(sas)@treble:~/rsch/xmm/0087940201_esas/ODF/repro$ xspec
    ...
    XSPEC12>data 1:1 mos1S001-obj-src-grp.pi
    XSPEC12>data 2:2 ../../../0551000201_esas/ODF/repro/mos1S001-obj-src-grp.pi 
    XSPEC12>response 2 ../../../0551000201_esas/ODF/repro/mos1S001-src.rmf 
    XSPEC12>arf 2 ../../../0551000201_esas/ODF/repro/mos1S001-src.arf 
    XSPEC12>cpd /xw
    XSPEC12>setplot en
    XSPEC12>ignore **:**-0.2,10.0-**
    XSPEC12>mo phabs*po
    XSPEC12>backgrnd 1 none
    XSPEC12>backgrnd 2 none
    XSPEC12>fit
    XSPEC12>plot ld
    XSPEC12>plot uf

This is extremely confusing.  Let's try again

    cd ../../../0551000201_esas/ODF/repro
    XSPEC12>data 1:1 mos1S001-obj-src-grp.pi 
    XSPEC12>data 2:2 ../../../0087940201_esas/ODF/repro/mos1S001-obj-src-grp.pi
    XSPEC12>response 2 ../../../0087940201_esas/ODF/repro/mos1S001-src.rmf 
    XSPEC12>arf 2 ../../../0087940201_esas/ODF/repro/mos1S001-src.arf
    XSPEC12>cpd /xw
    XSPEC12>setplot en
    XSPEC12>ignore **:**-0.2,10.0-**
    XSPEC12>mo phabs*po
    XSPEC12>fit
    XSPEC12>plot ld
    XSPEC12>plot uf

Looks the same.  OK...

    atran(sas)@treble:~/rsch/xmm/0551000201_esas/ODF/repro$ xspec
    XSPEC12>data 1:1 mos1S001-obj-src-grp.pi 
    XSPEC12>cpd /xw; setplot en; ignore **:**-0.2,10.0-**
    XSPEC12>backgrnd none
    XSPEC12>mo phabs*po
    XSPEC12>fit
    XSPEC12>plot ld
    XSPEC12>plot uf

OK, this (above) also looks the same!...
AHA.  One big difference is background subtraction.
If I do use QPB background spectra in the 0551000201 data, then the high energy tail looks OK
(essentially, subtraction noise)
If I do NOT use QPB background spectra, high energy tail does that sharp uptick in the unfolded spectra.
In channels (x-axis), it looks like flat noise, so after convolving with
arf/rmf it looks like an uptick in signal at increasing energy.  GREAT.  This makes sense.

Casual thought: any correlation with this warning message I've been getting?

    ***Warning: Detected response matrix energy bin value = 0 (or neg).
	     XSPEC will instead use small finite value (response file will not be altered).

if the RMF is negative maybe it's throwing XSPEC for a loop...


Monday 2015 October 26
======================

Continuing pursuit of this mysterious high energy tail.

Trick to make unfolded spectra physically meaningful/useful: set model to unity
(zero-slope power-law with unity normalization) before plotting unfolded
spectrum.  Unfolded data are model dependent in XSPEC:

    D-unfolded = D * (unfolded model) / (folded model);

unfolded model = theoretical model integrated over plot bin, folded model =
model times response).
[Source.](http://www.iucaa.ernet.in/~astrosat/MIT-IUCAA_workshop_presentations/IUCAA_Plotting_Spectra_Mon_Jan_20_2014.pdf)

Here are the relevant commands to generate some plots

    atran(sas)@treble:/data/mpofls/atran/research/xmm/0551000201_esas/ODF/repro$ xspec
    XSPEC12>data 1:1 mos1S001-obj-src-grp.pi
    XSPEC12>data 1:2 mos1S001-obj-src-grp.pi
    XSPEC12>setplot en ; cpd /xw; ignore **:**-0.2,10.0-**
    XSPEC12>mo po
    ========================================================================
    Model powerlaw<1> Source No.: 1   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
       1    1   powerlaw   PhoIndex            0.0          +/-  0.0          
       2    1   powerlaw   norm                1.00000      +/-  0.0          
    ________________________________________________________________________
    XSPEC12>backgrnd 2 none
    XSPEC12>setplot back
    XSPEC12>pl uf ld
    XSPEC12>cd ../../../0087940201_esas/ODF/repro
    XSPEC12>data 1:1 mos1S001-obj-src-grp.pi
    XSPEC12>data 1:2 mos1S001-obj-src-grp.pi
    XSPEC12>backgrnd 2 none
    XSPEC12>setplot en; ignore **:**-0.2,10.0-**
    XSPEC12>pl uf ld

and I save the plots to `20151026_unfolded_mos1S001_obs*.png`, in lieu of
printing them out or embedding them here (a rich document might be nice for
this).

I'm currently speculating that this is either
1. odd instrument signal
2. soft proton contamination
In either case, whatever the signal is, is probably not being filtered by
effective area function.  It might produce a flat signal in detector space;
when the (vague, unspecified) response is divided out then we get a rising
signal due to the steep effective area drop-off at high energies.


Tuesday 2015 October 27
=======================

Finally sat down with XSPEC manual and worked out details of how "responses",
"models", "datagroups", "spectra" work.  And hallelujah, it all works out.

A trial fit for background of 0551000201

    XSPEC12>show

    XSPEC version: 12.9.0d

    Tue Oct 27 18:53:03 2015
     Auto-saving is done after every command.
     Fit statistic in use: Chi-Squared
     Minimization technique: Levenberg-Marquardt
	    Convergence criterion = 0.01
	    Parameter fit deltas: 0.01 * parValue
     Always calculate parameter derivatives using full (slower) numerical differentiation: No
     Querying enabled.
     Prefit-renorming enabled.
     Solar abundance table: angr
     Photoionization Cross-Section Table:
	    bcmc:  Balucinska-Church and McCammon, 1998
     Cosmology in use: H0 = 70 q0 = 0 Lambda0 = 0.73
     Model data directory: /soft/lheasoft/headas/x86_64-pc-linux/../spectral/modelData/
     Plot settings:
       Showing of individual additive components is OFF.
       Showing of background spectra is OFF.
       Effective area normalization is OFF.
       Current unit settings:
	      Energy     = keV
	      Wavelength = angstrom, with Y-Axis displayed per Hz
       X-Axis data display mode: Energy
       Spectra plots will be shifted to source frame by redshift value z: 0
       Device: /xs
       Plotting of line IDs is OFF.
       Splashpage is ON.
       xlog for data plots is ON.
       ylog for data plots is OFF.

       Default plot rebin settings for all plot groups:
       Min. Signif.   Max. # Bins   Error Type
		    0.00000             1         quad

     Responses read: 
       ../../../mos1-diag.rsp associated with spectrum 1 source 2
	      energies: 2400 channels: 111
       mos1S001-bkg.rmf associated with spectrum 1 source 1
	      energies: 2400 channels: 111
     Distinct RMF files: 
	     ../../../mos1-diag.rsp     mos1S001-bkg.rmf

    1 file 1 spectrum 
    Spectrum 1  Spectral Data File: mos1S001-obj-bkg-grp.pi
    Net count rate (cts/s) for Spectrum:1  4.336e-02 +/- 1.894e-03 (52.6 % total)
     Assigned to Data Group 1 and Plot Group 1
      Noticed Channels:  5-41
      Telescope: XMM Instrument: EMOS1  Channel Type: PI
      Exposure Time: 2.302e+04 sec
     Using fit statistic: chi
     Using test statistic: chi
     Using Background File                mos1S001-back-bkg.pi
      Background Exposure Time: 2.302e+04 sec
     Using Response (RMF) File            mos1S001-bkg.rmf for Source 1
     Using Auxiliary Response (ARF) File  mos1S001-bkg.arf
     Using Response (RMF) File            ../../../mos1-diag.rsp for Source 2

     Spectral data counts: 1897
     Model predicted rate: 4.24538E-02


    Current model list:

    ========================================================================
    Model apec<1>   +   phabs<2>*apec<3>   +   phabs<4>*powerlaw<5>   +  gaussian<6>  + gaussian<7> + gaussian<8> Source No.: 1   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
       1    1   apec       kT         keV      8.03414E-03  +/-  1.93120E+05  
       2    1   apec       Abundanc            1.00000      frozen
       3    1   apec       Redshift            0.0          frozen
       4    1   apec       norm                5.00876E-04  +/-  3.51269E+05  
       5    2   phabs      nH         10^22    1.00000      frozen
       6    3   apec       kT         keV      0.963260     +/-  0.162959     
       7    3   apec       Abundanc            1.00000      frozen
       8    3   apec       Redshift            0.0          frozen
       9    3   apec       norm                2.01873E-04  +/-  4.01491E-05  
      10    4   phabs      nH         10^22    1.00000      frozen
      11    5   powerlaw   PhoIndex            1.46000      frozen
      12    5   powerlaw   norm                2.34497E-05  +/-  1.64495E-05  
      13    6   gaussian   LineE      keV      1.49000      frozen
      14    6   gaussian   Sigma      keV      0.0          frozen
      15    6   gaussian   norm                2.76225E-05  +/-  2.39728E-06  
      16    7   gaussian   LineE      keV      1.75000      frozen
      17    7   gaussian   Sigma      keV      0.0          frozen
      18    7   gaussian   norm                6.79513E-06  +/-  1.65755E-06  
      19    8   gaussian   LineE      keV      0.650000     frozen
      20    8   gaussian   Sigma      keV      0.0          frozen
      21    8   gaussian   norm                1.25548E-05  +/-  6.27539E-06  
    ________________________________________________________________________


    ========================================================================
    Model sp:powerlaw<1> Source No.: 2   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
       1    1   powerlaw   PhoIndex            0.820121     +/-  0.151480     
       2    1   powerlaw   norm                4.11614E-03  +/-  9.96526E-04  
    ________________________________________________________________________

       Using energies from responses.

    Fit statistic : Chi-Squared =          28.10 using 37 PHA bins.

    Test statistic : Chi-Squared =          28.10 using 37 PHA bins.
     Reduced chi-squared =          1.041 for     27 degrees of freedom 
     Null hypothesis probability =   4.057593e-01
     Weighting method: standard
    XSPEC12>

AND, a trial fit for the SNR in 0551000201 using the background parameters above!

    XSPEC12>show

    XSPEC version: 12.9.0d

    Tue Oct 27 18:54:27 2015
     Auto-saving is done after every command.
     Fit statistic in use: Chi-Squared
     Minimization technique: Levenberg-Marquardt
	    Convergence criterion = 0.01
	    Parameter fit deltas: 0.01 * parValue
     Always calculate parameter derivatives using full (slower) numerical differentiation: No
     Querying enabled.
     Prefit-renorming enabled.
     Solar abundance table: angr
     Photoionization Cross-Section Table:
	    bcmc:  Balucinska-Church and McCammon, 1998
     Cosmology in use: H0 = 70 q0 = 0 Lambda0 = 0.73
     Model data directory: /soft/lheasoft/headas/x86_64-pc-linux/../spectral/modelData/
     Plot settings:
       Showing of individual additive components is OFF.
       Showing of background spectra is OFF.
       Effective area normalization is OFF.
       Current unit settings:
	      Energy     = keV
	      Wavelength = angstrom, with Y-Axis displayed per Hz
       X-Axis data display mode: Energy
       Spectra plots will be shifted to source frame by redshift value z: 0
       Device: /xw
       Plotting of line IDs is OFF.
       Splashpage is ON.
       xlog for data plots is ON.
       ylog for data plots is OFF.

       Default plot rebin settings for all plot groups:
       Min. Signif.   Max. # Bins   Error Type
		    0.00000             1         quad

     Responses read: 
       ../../../mos1-diag.rsp associated with spectrum 1 source 2
	      energies: 2400 channels: 185
       mos1S001-src.rmf associated with spectrum 1 source 1
	      energies: 2400 channels: 185
       mos1S001-src.rmf associated with spectrum 1 source 3
	      energies: 2400 channels: 185
     Distinct RMF files: 
	     ../../../mos1-diag.rsp     mos1S001-src.rmf

    1 file 1 spectrum 
    Spectrum 1  Spectral Data File: mos1S001-obj-src-grp.pi
    Net count rate (cts/s) for Spectrum:1  2.681e-01 +/- 3.796e-03 (80.9 % total)
     Assigned to Data Group 1 and Plot Group 1
      Noticed Channels:  6-141
      Telescope: XMM Instrument: EMOS1  Channel Type: PI
      Exposure Time: 2.302e+04 sec
     Using fit statistic: chi
     Using test statistic: chi
     Using Background File                mos1S001-back-src.pi
      Background Exposure Time: 2.302e+04 sec
     Using Response (RMF) File            mos1S001-src.rmf for Source 1
     Using Auxiliary Response (ARF) File  mos1S001-src.arf
     Using Response (RMF) File            ../../../mos1-diag.rsp for Source 2
     Using Response (RMF) File            mos1S001-src.rmf for Source 3
     Using Auxiliary Response (ARF) File  mos1S001-src.arf

     Spectral data counts: 7627
     Model predicted rate: 0.253653


    Current model list:

    ========================================================================
    Model back:apec<1> + phabs<2>*apec<3> + phabs<4>*powerlaw<5> + gaussian<6> + gaussian<7> + gaussian<8> Source No.: 1   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
       1    1   apec       kT         keV      8.03414E-03  frozen
       2    1   apec       Abundanc            1.00000      frozen
       3    1   apec       Redshift            0.0          frozen
       4    1   apec       norm                5.00000E-04  frozen
       5    2   phabs      nH         10^22    1.00000      frozen
       6    3   apec       kT         keV      0.960000     frozen
       7    3   apec       Abundanc            1.00000      frozen
       8    3   apec       Redshift            0.0          frozen
       9    3   apec       norm                2.02000E-04  frozen
      10    4   phabs      nH         10^22    1.00000      frozen
      11    5   powerlaw   PhoIndex            1.46000      frozen
      12    5   powerlaw   norm                2.34000E-05  frozen
      13    6   gaussian   LineE      keV      1.49000      frozen
      14    6   gaussian   Sigma      keV      0.0          frozen
      15    6   gaussian   norm                2.76000E-05  frozen
      16    7   gaussian   LineE      keV      1.75000      frozen
      17    7   gaussian   Sigma      keV      0.0          frozen
      18    7   gaussian   norm                6.79500E-06  frozen
      19    8   gaussian   LineE      keV      0.650000     frozen
      20    8   gaussian   Sigma      keV      0.0          frozen
      21    8   gaussian   norm                1.25500E-05  frozen
    ________________________________________________________________________


    ========================================================================
    Model snr:phabs<1>*vnei<2> Source No.: 3   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
       1    1   phabs      nH         10^22    0.646077     +/-  3.73739E-02  
       2    2   vnei       kT         keV      4.59166      +/-  0.973791     
       3    2   vnei       H                   1.00000      frozen
       4    2   vnei       He                  1.00000      frozen
       5    2   vnei       C                   1.00000      frozen
       6    2   vnei       N                   1.00000      frozen
       7    2   vnei       O                   0.144388     frozen
       8    2   vnei       Ne                  1.11844E-02  +/-  3.03557E-02  
       9    2   vnei       Mg                  0.304664     +/-  5.38739E-02  
      10    2   vnei       Si                  2.00172      +/-  0.169084     
      11    2   vnei       S                   4.88936      +/-  0.647425     
      12    2   vnei       Ar                  3.88010      frozen
      13    2   vnei       Ca                  5.28715      frozen
      14    2   vnei       Fe                  7.12438E-02  frozen
      15    2   vnei       Ni                  0.957365     frozen
      16    2   vnei       Tau        s/cm^3   1.31766E+10  +/-  1.02414E+09  
      17    2   vnei       Redshift            0.0          frozen
      18    2   vnei       norm                1.18284E-03  +/-  1.40108E-04  
    ________________________________________________________________________


    ========================================================================
    Model sp:powerlaw<1> Source No.: 2   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
       1    1   powerlaw   PhoIndex            0.820000     frozen
       2    1   powerlaw   norm                4.12000E-03  frozen
    ________________________________________________________________________

       Using energies from responses.

    Fit statistic : Chi-Squared =         223.75 using 136 PHA bins.

    Test statistic : Chi-Squared =         223.75 using 136 PHA bins.
     Reduced chi-squared =         1.7480 for    128 degrees of freedom 
     Null hypothesis probability =   3.435070e-07
     Weighting method: standard
    XSPEC12>

Finally, I have some plots.  They (the plots) are NOT quite consistent with the
parameters I copied here.

BUT, they show the conceptual idea works.

    -rw-r--r--  1 atran mp  17K Oct 27 17:50 20151027_0551000201_mos1_src_phabsvnei.png
    -rw-r--r--  1 atran mp 9.8K Oct 27 18:55 20151027_0551000201_mos1_back.png

And I leave the links here, in lieu of using my paper lab notebook...

Please see also the necessary XSPEC commands in:

	-rw-r--r-- 1 atran mp 1.7K Oct 27 17:58 back.xcm
	-rw-r--r-- 1 atran mp 3.0K Oct 27 17:58 snr.xcm


Wednesday 2015 October 28
=========================

Now that I'm starting to see an end in sight, and how this will be structured,
I'm going to pause and set up a proper research directory

... work on this deferred for a while I was properly tackling the ACA
constraint.


Friday 2015 November 13 -- Saturday 2015 November 14
====================================================

Brief list of available data:
* XMM pointings 2x
* Chandra ptgs of src (not much of remnant) (4554, 8929)
* MOST radio, 0.83GHz, resolution 43"
* ATCA 1.34GHz (gaensler paper) + simultaneous HI 1.420GHz. ~24" resolution 

Way behind, been tied up with ACA constraint stuff.
Finished a short Makefile tutorial (software carpentry) yesterday.

Attempted to set up Makefile for XMM data reduction.  Spent most of day on
this.   Although I vacillate between doing this and wanting to throw my hands
up and admit defeat, I'm ultimately going for a Makefile approach.
These problems (tracking files in a pipeline, ensuring reproducibility in
projects) are not gonna get better, if I don't tackle them head on.

Also adding to Git and github for two reasons.
1. version control and branching
2. keep myself accountable and organized (ish).
3. ease of accessing / perusing revisions, distributing data / iPython
   notebooks, etc.

Comment: git push origin master, using https authentication, requires ssh -X on
my end.  Maybe change to using ssh instead of https for this?

## Reorganizing data

I am going to discard a lot of previous log files (from nohup runs, mid-October
etc.).
None of the previous data I generated were directly related to research, but
mostly were due to my fumbling around with XMM SAS and ESAS, and re-running
various chains.  None of the iterations were caused by scientific reasons,
so no information is concealed by deleting the records for these script
re-runs.

Files not deleted yet.

Have deleted first download of 087940201 (from late Sep/early Oct, when I was
messing around with Dan T. Reese's analysis manual).

Plan: start taking advantage of Git branches to organize ideas/code.
I think this is exactly what you need, to make things traceable.

Everything should be documented in a MASTER copy of notes, though.

NOTE: new "standard" prcedure for region selection.
1. use PPS processed and merged image P0087940201EPX000OIMAGE8000.fit
2. use MOST radio contours for overlay to help see SNR location.




Running notes
=============

Tentative plan:
- print regions overlaid on SNR (in detector coordinates)
- print plot of histogram filtering. maybe a second round would help.

* point source excision.
* readout streaks!



Before final-ish analysis, run evselect with `XMMEA_EM, XMMEA_SM, XMMEA_EP`, or simply flag==0 to reject all possibly bad events (maybe too restrictive)
where you set M1S001, M2S002, PNS003 etc. accordingly

	evselect table=P{obsid}M1S001PIEVLI0000.FIT expression='(PATTERN<=12) && (PI in [200:12000]) && #XMMEA_EM'
	evselect table=P{obsid}M2S002PIEVLI0000.FIT expression='(PATTERN<=12) && (PI in [200:12000]) && #XMMEA_EM'
	#evselect table=P{obsid}PNS003PIEVLI0000.FIT expression='(PATTERN<=4) && (PI in [200:15000]) && #XMMEA_EP'	# PN spectral analysis
	#evselect table=P{obsid}PNS003PIEVLI0000.FIT expression='(PATTERN<=12) && (PI in [200:15000]) && #XMMEA_EP'  # PN imaging analysis



Next step:
* merge data from two observations together -- total ~97ks before filtering.
Merge MOS data together, then attempt PN+MOS event merger.  This would not be
for quantitative analysis, but just to let human eyes get a gander at a richer
(if possibly more misleading) spectrum.
Note that Hughes and Motch observations were taken with different
filters (thick, medium respectively) -- so your model of the cosmic x-ray background will be slightly different in each case.

Sect. 9 of ESAS cookbook covers mosaics.


APPENDIX -- notes on pipeline tools and their functions
=======================================================

Files in ODF/repro after initial cifbuild/odfingest:

	atran@treble:/data/mpofls/atran/research/xmm/0087940201_esas/ODF/repro$ lsl
	total 632K
	-rw-r--r-- 1 atran mp  99K Oct  5 17:28 ccf.cif
	-rw-r--r-- 1 atran mp 522K Oct  5 17:28 0315_0087940201_SCX00000SUM.SAS

mos-filter, mos-spectra, pn-spectra output their commands to command.csh --
move and save this file after each call, to prevent from being clobbered (and
to have an easy to peruse log of commands run)
CURIOUSLY, pn-filter doesn't do this...  pn-filter does create an empty
../../catalogue file, I don't know why though?

## emchain synopsis, distilled from docs / outputs

	* Find and merge GTIs from attitude (spacecraft pointing), housekeeping, and (optionally) user-supplied GTI file
      - Many of these GTI files float around after the emchain run (ATTGTI, HK_GTI, FBKTSR, FBKGTI),
	    as well as the spacecraft attitude file generated by `atthkgen atthkset=P{obsid}OBX000ATTTSR0000.FIT`
	  - By default, _these are not actually applied to data_
	* Remove all bad events, except `OUT_OF_FOV` and `REJECTED_BY_GATTI`
	  - Flag: 0x762aa000; compare to XMMEA_EM 0x766ba000.  As claimed, this only
	    differs by allowing OUT_OF_FOV and REJECTED_BY_GATTI events which
	    correspond to 0x00010000 and 0x00400000 respectively)
	* Merge event lists from all CCDs, create a final event list w/ information for imaging.
      this includes, e.g., using attitude history to compute sky X/Y for each event;
	  identifying and applying GTIs for individual CCDs; etc.
	* Create flare time series and GTIs (for MOS1 and MOS2 both), but doesn't apply by default
	  - flare removal is conservative, uses high energy events and cuts, based on "flaremaxrate" and "flaretimebin".

	Result: a minimally processed event list for all CCDs, preserving events outside FOV and high energy (rejected by "GATTI") events.
	Most bad events are rejected, but for spectra further filtering may be desired (XMMEA_SM flag)

		-rw-r--r-- 1 atran mp   15M Sep 24 18:49 P0087940201M1S001MIEVLI0000.FIT
		-rw-r--r-- 1 atran mp   15M Sep 24 18:51 P0087940201M2S002MIEVLI0000.FIT

	* By default, HK, ATT, and flare filtering are NOT applied to data (filteratt, filterhk, applyflaregti)
	  You'll notice that there are no calls to gtimerge in emchain.log
	* Events are randomized within position, energy, time bins
	* Some intermediate files generated by emchain/epchain can be reused in subsequent calls

## epchain synopsis, distilled from docs / outputs

	* Process bad pixels, GTIs, etc. and get calibrated events for each CCD (option to remove low energy noise + soft flares via epreject, epnoise; off by default)
	* Combine into output events list.
	* Obtain background lightcurve + GTIs after applying indiv CCD masks (not applied to events list) (FBKTSR, FBKGTI)
	* OOT case: treat all events as OOT and randomly shuffle along RAWY column, to create "simulated readout streaks" that can be subtracted from images and spectra
	  Thread on how to subsequently subtract OOT events from images and spectra using FTOOLS, evselect, etc:

  	    http://xmm.esac.esa.int/sas/current/documentation/threads/EPIC_OoT.shtml

	Typically run as:
		withoutoftime=Y keepintermediate=raw
	then run a second time as:
		withoutoftime=N (is default and can thus be omitted) 

	Result:
		P0551000201OBX000ATTTSR0000.FIT		atthkgen output
		P0551000201PNS003BPXHMK00##.FIT		badpixfind, hard band pt src. mask?  for CCDs 1-12
		P0551000201PNS003BPXMSK00##.FIT		badpixfind, general mask?  for CCDs 1-12
		P0551000201PNS003OOEVLI0000.FIT		out-of-time events file
		P0551000201PNS003PIEVLI0000.FIT		imaging mode events file (if withoutoftime=Y)
		P0551000201PNS003FBKSPC0000.FIT		background spectrum (if withoutoftime=N)
		P0551000201PNS003FBKTSR0000.FIT		flare background rate set (lightcurve), for hard (7-15 keV) events with PATTERN<5, using source masks.
		P0551000201PNS003FBKGTI0000.FIT		flare background GTIs, computed from tabgtigen table=FBKTSR (rateset) gtiset=FBKGTI, imposing RATE < FLAREMAXRATE

	I haven't figured out what the badpixfind masks (BPXHMK, BPXMSK) are for, but oh well.

## Subtasks within epchain

	epnoise: "calculates the number of events per frame between 20 to 30 adu
		and removes those frames above a certain thershold defined by noisecut
		parameter. Once the noisy frames have been removed, the exposure time is
		updated accordingly."

		removes soft X-ray noisy frames (what is a frame? single readout event?)

		(how critical is this?  is this covered by our flare filtering?)

	epreject: offset map calculation may get distorted by particles

		Context: EPIC-pn computes an offset map just before the start of an
		exposure.  This map contains the energy offset for each pixel (in
		analog-to-digital units, adu). During the exposure, these offsets are
		subtracted onboard from the measured signals, and only events where the
		difference exceeds 20 adu (~100 eV) are transmitted to Earth.

		ALSO suppresses detector noise at low energies?  Depends on distance to readout node.
		http://xmm.esac.esa.int/sas/current/doc/epreject/node5.html

		 Compared to the sky background, the detector background is characterized by

			> a non-uniform spatial distribution: the detector background is not
			> vignetted, but rather increases toward the CAMEX chip (to the top and to the
			> bottom in figure 9 or figure 10) , with a steep rise in the rows closest to the
			> CAMEX

			> a non-uniform spectral distribution: noticeable detector background
			> is present only below a few hundred eV, with a steep rise toward the lowermost
			> energies This subtask is intended to simplify the background subtraction at low
			> energies. It makes use of the fact that the noise properties of EPIC pn vary
			> with position and energy, but are fairly stable in time.

		RESULTS:
		1. energy scale shift over entire spectral bandwidth
		2. detector noise because previously rejected events may be promoted to "valid" events

		See: http://xmm.esac.esa.int/external/xmm_user_support/documentation/sas_usg/USG/correpicimag.html
		http://xmm.esac.esa.int/sas/current/doc/epreject/node4.html

		(now, this sounds important, and relatively low impact correction, esp if you need line centroids.
		 But, why is it turned off in epchain by default?  It's enabled for timing/burst modes, though.)

## mos-filter synopsis

Review of mos-filter (any functionality I should incorporate?):

    $good=substep()
	...
	for each (event lists produced by emchain)

		espfilt eventset=mos".$rot_name.".fits  # Main filtering step

		rename the files (e.g., -objevlifilt.FIT to -clean.fits)

		print useful information from FITS file keywords. Notably, I can get livetime/ontime:

			atran(sas)@treble$ fkeypar mos1-filt.fits ONTIME ; pget fkeypar value ;
			3.96479230155498E+04
			atran(sas)@treble$ fkeypar mos1-filt.fits LIVETIME ; pget fkeypar value ;
			3.92745418829918E+04

			atran(sas)@treble$ fkeypar P0087940201M1S001-objevlifilt.FIT ONTIME ; pget fkeypar value ;
			2.76000000000000E+04
			atran(sas)@treble$ fkeypar P0087940201M1S001-objevlifilt.FIT LIVETIME ; pget fkeypar value ;
			2.72832182419300E+04

			Compare this to XMM archive stated duration of 40.463 ks.
			Unfiltered on/live time: 39.65 ks, 39.27 ks
			Filtered on/live time: 27.60 ks, 27.28 ks

			I assume on/live corresponds to some CCD downtime; difference is ~1%.
				ONTIME = sum of GTIs for the central CCD
				LIVETIME = live time for the central CCD

		create "diagnostic" images (line 125-166):
			image in DETX/DETY coords, unfiltered
			image in DETX/DETY coords, soft (0.2-0.9 keV) x-rays, mildly filtered
				(Snowden adds an additional filter flag if $ins_num==1 and $revl > 2383,
					(((FLAG & 0x766a0f63) == 0)||((FLAG & 0x766a0763) == 0))
				 vs. just
					((FLAG & 0x766a0f63) == 0)
				for the regular case)
				After very long exploration -- this is equivalent to just using 0x766a0763 alone.
				(0763 vs 0f63).  Special case appears to correspond to MOS1
			 	events taken after the CCD3 micrometeorite strike (in revolution 2382)

				Snowden's filter is actually LESS restrictive after rev 2383
				than before. Not sure why.

			image in DETX/DETY, filtered
			image in SKY X/Y, filtered

		create corner definition for MOS1 and MOS2 (different for each)
		manually extract corner-only events files, with mild filtering (like above, with 0x766a0{f,7}63)
		create image of corner-only events

		calculate count rate, hardness ratio??? for each chip.
			Very dense evselect expressions follow, selecting 0.3-10 keV, 0.5-0.8 keV, 2.5-5 keV.
			It looks like yes, for each CCD chip, Snowden computes some kind of spectrum info.
			I assume this helps filter on anomalous MOS CCDs.

			and then prints out the ones that look anomalous or potentially anomalous!

	AND THAT'S IT!

Basically a giant wrapper for espfilt, that generates a lot of diagnostic output.  Kind of useful.

## mos-spectra synopsis

mos-spectra extracts many spectra from varying regions (FOV, chip corners,
region of interest, etc.).  It filters with a lot of buried/embedded patterns.
But, the spectra are not actually manipulated.

mos-spectra handles the following:
* hardcodes CCD regions for MOS1 and MOS2
* removes bad edge of MOS1 CCD#4 (after loss of CCD#3 in 2012)
* obtains/applies hardcoded sky masks if specified (mask=1,2,3)
* extracts corner event file (mos1S001-corn.fits) if not already present.  would apply expression='pattern<=12, (flag & 0x766a0f63) == 0'
  (but, this file is already obtained from mos-filter (espfilt) by moving -corevlifilt.FIT to -corn.fits)
* anomalous CCD check, again.

Here are the output files, in approx. order of generation.  Substitute "1S001" with appropriate prefix.
Most of these files are independent of each other; exposure maps/masks go together; pi/rmf/arf go together.

	mos1S001-obj-im.fits					obs data img in sky coords, full FOV, all (selected) CCDs, all energies
	mos1S001-obj-im-sp-det.fits				obs data img in det coords, selected region (used for task proton-scale)
	mos1S001-obj-im-det-400-1250.fits		obs data img in det coords, selected region, all (selected) CCDs, 400-1250 eV
	atthk.fits								attitude data for exposure maps (atthkset=atthk.fits timestep=1)
	mos1S001-exp-im.fits					exposure map for full FOV (from mos1S001-obj-im.fits)
	mos1S001-mask-im.fits					exposure mask (essentially, full FOV minus deselected CCDs)

	mos1S001-obj.pi							obs data spectrum, selected region
	mos1S001.rmf							RMF for -obj.pi, computed using temporary detmaparray (detmap.ds, obs data img in det coords, FLAG==0 only)
	mos1S001.arf							ARF for -obj.pi, computed using same detmaparray and RMF as well (extendedsource flag enabled)

	mos1S001-obj-im-400-1250.fits			obs data img in sky coords, selected region, 400-1250 eV
	mos1S001-exp-im-400-1250.fits			exposure map for region and band
	mos1S001-mask-im-400-1250.fits			exposure mask for region and band

	mos1S001-1ff.pi							FWC data spectrum for intersection(selected region, CCD #1); FLAG == 0 required
	mos1S001-obj-im-400-1250-ccd1.fits		obs img for central chip, selected region, 400-1250 eV
	mos1S001-exp-im-400-1250-ccd1.fits		exposure map for obs central img
	mos1S001-mask-im-400-1250-ccd1.fits		exposure mask for obs central img
	mos1S001-im1-400-1250.fits				FWC img for central chip, selected region, 400-1250 eV; masked with "mos1S001-mask-im-400-1250-ccd1.fits"
	mos1S001-1obj.pi						obs spectrum for central chip

	mos1S001-2oc.pi							obs corner spectrum, CCD#2
	mos1S001-2obj.pi						obs data spectrum in intersection(CCD#2, selected region)
	mos1S001-2fc.pi							FWC corner spectrum, CCD#2
	mos1S001-2ff.pi							FWC spectrum in intersection(CCD#2, selected region)
	mos1S001-im2-400-1250.fits				FWC image in intersection(CCD#2, selected region, 400-1250 eV)

	... (repeat for CCDS 3-7)

Note that the FWC images/spectra (mos1S001-im1-400-1250.fits, mos1S001-2fc.pi,
mos1S001-im2-400-1250.fits, ...) are all extracted from mos1-fwc.fits.gz, part
of the ESAS CALDB.  This file looks like a bunch of FWC data all merged
together.

## mos\_back, pn\_back "synopsis"

Scripts mos\_back / pn\_back are compiled Fortran, unfortunately, so I can't
decipher what they do directly.  What do they output?

    mos{prefix}-aug.qdp - QDP plot showing the selected region of hardness/count rate distributions for the various ccds.
    mos{prefix}-back-im-det-elow-ehigh.fits - model particle background image, det coords,  for selected energy band (elow and ehigh) and selected region
    mos{prefix}-back.pi - model particle background spectrum for selected region.
    mos{prefix}-spec.qdp - QDP plot showing the observed spectrum and the model background spectrum.

    Additional output when diag=2:
    mos{prefix}-back.qdp - QDP plot showing the normalized model background spectrum.
    mos{prefix}-back-accum.qdp - QDP plot showing the accumulating background spectrum. Chip 1 at the bottom increasing upwards.
    mos{prefix}-bridge-fit.qdp - QDP plot showing the the fit for the Al-Si bridge.

SO, mos{prefix}-obj.pi (with arf,rmf) is to be used with mos{prefix}-back.pi.
You need to set BACKSCALE keyword and stuff appropriately.  After this, you're
supposed to fit instrumental lines + cosmic (galactic + extragalactic) X-ray
background yourself.



XMM event flags
===============

Handy dandy reference.

	XMMEA_EM= '(FLAG & 0x766ba000) == 0' / Select good MOS events
	XMMEA_SM= '(FLAG & 0xfffffeff) == 0' / Select good MOS events for spectra
		compared to 'FLAG == 0', XMMEA_SM allows 0x00000100 (CLOSE_TO_DEADPIX) to pass through.
	XMMEA_EP= '(FLAG & 0xcfa0000) == 0' / Select good PN events

	#MOS
	XMMEA_0 = '(FLAG & 0x1) != 0'  / DIAGONAL
	XMMEA_1 = '(FLAG & 0x2) != 0'  / CLOSE_TO_CCD_BORDER
	XMMEA_5 = '(FLAG & 0x20) != 0' / CLOSE_TO_ONBOARD_BADPIX
	XMMEA_6 = '(FLAG & 0x40) != 0' / CLOSE_TO_BRIGHTPIX
	XMMEA_8 = '(FLAG & 0x100) != 0' / CLOSE_TO_DEADPIX
	XMMEA_9 = '(FLAG & 0x200) != 0' / CLOSE_TO_BADCOL
	XMMEA_10= '(FLAG & 0x400) != 0' / CLOSE_TO_BADROW
	XMMEA_11= '(FLAG & 0x800) != 0' / IN_SPOILED_FRAME
	XMMEA_13= '(FLAG & 0x2000) != 0' / ON_BADOFFSET
	XMMEA_15= '(FLAG & 0x8000) != 0' / FLICKERING
	XMMEA_16= '(FLAG & 0x10000) != 0' / OUT_OF_FOV
	XMMEA_17= '(FLAG & 0x20000) != 0' / IN_BAD_FRAME
	XMMEA_19= '(FLAG & 0x80000) != 0' / COSMIC_RAY
	XMMEA_21= '(FLAG & 0x200000) != 0' / ON_BADPIX
	XMMEA_22= '(FLAG & 0x400000) != 0' / REJECTED_BY_GATTI
	XMMEA_25= '(FLAG & 0x2000000) != 0' / OUT_OF_CCD_WINDOW
	XMMEA_26= '(FLAG & 0x4000000) != 0' / OUTSIDE_THRESHOLDS
	XMMEA_28= '(FLAG & 0x10000000) != 0' / ON_BADROW
	XMMEA_29= '(FLAG & 0x20000000) != 0' / BAD_E3E4
	XMMEA_30= '(FLAG & 0x40000000) != 0' / UNDERSHOOT

	# PN
	XMMEA_0 = '(FLAG & 0x1) != 0'  / INVALID_PATTERN
	XMMEA_2 = '(FLAG & 0x4) != 0'  / CLOSE_TO_CCD_WINDOW
	XMMEA_3 = '(FLAG & 0x8) != 0'  / ON_OFFSET_COLUMN
	XMMEA_4 = '(FLAG & 0x10) != 0' / NEXT_TO_OFFSET_COLUMN
	XMMEA_5 = '(FLAG & 0x20) != 0' / CLOSE_TO_ONBOARD_BADPIX
	XMMEA_6 = '(FLAG & 0x40) != 0' / CLOSE_TO_BRIGHTPIX
	XMMEA_8 = '(FLAG & 0x100) != 0' / CLOSE_TO_DEADPIX
	XMMEA_11= '(FLAG & 0x800) != 0' / IN_SPOILED_FRAME
	XMMEA_16= '(FLAG & 0x10000) != 0' / OUT_OF_FOV
	XMMEA_17= '(FLAG & 0x20000) != 0' / IN_BAD_FRAME
	XMMEA_19= '(FLAG & 0x80000) != 0' / COSMIC_RAY
	XMMEA_20= '(FLAG & 0x100000) != 0' / MIP_ASSOCIATED
	XMMEA_21= '(FLAG & 0x200000) != 0' / ON_BADPIX
	XMMEA_22= '(FLAG & 0x400000) != 0' / SECONDARY
	XMMEA_23= '(FLAG & 0x800000) != 0' / TRAILING
	XMMEA_25= '(FLAG & 0x2000000) != 0' / OUT_OF_CCD_WINDOW


FAQ (things I was somewhat stumped on at some point)
====================================================

Q: What's the difference between epproc/emproc and epchain/emchain?
A: Same thing, script vs. compiled implementation.  Maybe chains are better?
> There are two types of tool available, the procs (epproc and emproc) and the
> chains (epchain and emchain) which do essentially the same job. However, the
> chains allow more user control, and can also be set to keep intermediate
> files (like the badpixel files) and can be stopped at certain points and
> restarted at others. An example of when this is useful is to stop the chain
> after bad pixel detection, add, or remove some pixels from the badpixel list,
> then complete the chain, if you're not happy with the bad pixels it detects
> by itself. The chains also appear to do a better job of detecting bad pixels
> and events than the procs, so I would recommend using them.
(from: http://www.sr.bham.ac.uk/xmm2/dataprep.html)


Q: What's in an obsid?
A: 10 digits (PPPPPPOOLL), where PPPPPP = proposal ID, OO = observation within proposal ID, and LL = "extended ID" (usually 1)

Flare removal by GTI cuts decreases error compared to blank sky subtraction
===========================================================================

Tuesday Oct 6 2015

What's the better way to remove flares from spectra: cutting time intervals of
significant flaring, or subtracting blank sky background?

Flares are ~10x the source count rate during flaring periods (note that MOS/PN
histogram of FOV count rate are likely dominated by the bright star HD119682,
and SNR is probably 2-10x fainter).

	Counts in filtered image (flares completely removed; original event list cleaned with XMMEA_EM and espfilt):
	- SNR: 0.077 cts/arcsec^2    / 27ks     -->  2.85e-3 ct/ks/arcsec^2
	- blank sky: 0.04 cts/arcsec^2  / 27ks  -->  1.48e-3 ct/ks/arcsec^2

	Counts in unfiltered image (original event list; no filtering for bad events, but there should be very few of those):
	- SNR: 0.217 cts/arcsec^2   / 40ks    	-->  5.43e-3 ct/ks/arcsec^2
	- blank sky: 0.165 cts/arcsec   / 40ks	-->  4.13e-3 ct/ks/arcsec^2

SNR is ~ 1.4e-3 ct/ks/arcsec, without blank sky background (instrumental, sky, etc. all in one)
Flaring is ~2.6e-3 ct/ks/arcsec^2, roughly 2x SNR brightness.  But flaring is concentrated in 13 of 40 ks.

	Estimated SNR counts (40 ks): 0.056 ct/arcsec^2
	Estimated flare counts (40 ks, but concentrated within 13 ks): 0.10 ct/arcsec^2
	Estimated SNR counts (13 ks): 0.018 ct/arcsec^2

Flares thus cause count rates ~10x brighter than actual SNR (after background removal), over the span of 13 ks.
But, what matters is the total error over 40ks.

	SNR alone (40 ks): 0.056*A +/- sqrt(0.056*A) ct

			relative error: sqrt(0.056*A) / (0.056*A) ~ 4.23 / sqrt(A)

	SNR alone (27 ks): 0.038*A +/- sqrt(0.038*A) ct

			relative error: sqrt(0.038*A) / (0.038*A) ~ 5.13 / sqrt(A)

	SNR (40 ks) - flare (13 ks): 0.056*A +/- sqrt(0.056*A) +/- sqrt(2*0.10*A) ct

			relative error: sqrt(0.256*A) / (0.056*A) ~ 9.04 / sqrt(A)

Adding errors in quadrature. flare subtraction using another region introduces sqrt(2 * flare cts) uncertainty.
This is a very rough estimate, but it looks like we almost double the relative error, as opposed to simply cutting out flare times.

Flares in different parts of FOV are definitely correlated.  So subtraction
process may not introduce that much error if the "actual" Poissonian error in
flare counts from one part of the FOV to another is similar (or, it doesn't
make sense to represent the counts as random discrete events).

So the error for blank sky subtraction is likely not as bad as I estimate.
Nevertheless, simply taking GTIs seems to be the safest approach.


