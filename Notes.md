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
Initial meeting with Pat about this project.  See my (paper) notes.


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


Friday 2015 November 13 -- Sunday 2015 November 15
==================================================

Brief list of available data:
* XMM pointings 2x
* Chandra ptgs of src (not much of remnant) (4554, 8929)
  Obsid 4554 does overlap the remnant, no grating.  Not likely to contribute much
  (short 15ks exposure, XMM-Newton effective area >> Chandra)
* MOST radio, 0.83GHz, resolution 43"
* ATCA 1.34GHz (gaensler paper) + simultaneous HI 1.420GHz. ~24" resolution

Way behind, been tied up with ACA constraint stuff.

## Repo organization

Finished a short Makefile tutorial (software carpentry) yesterday.

Attempted to set up Makefile for XMM data reduction.  Spent most of Friday on
this.  Although I vacillate between doing this and wanting to throw my hands
up and admit defeat, I'll stick to implementing a Makefile approach.
These problems (keeping files consistent in a pipeline, ensuring scientific
reproducibility) won't improve, if I don't tackle them head on.

Initialized git repo and pushed to Github to:
1. version control and branching
2. keep myself accountable and organized (ish).
3. ease of accessing / perusing revisions, distributing data / iPython
   notebooks, etc.

Comment: git push origin master, using https authentication, requires ssh -X on
my end.  Maybe change to using ssh instead of https for this?

## Reorganizing data

I discard some previous log files and data (mid-October nohup runs etc.).
None of the previous data I generated were directly related to research, but
mostly were due to my fumbling around with XMM SAS and ESAS, and re-running
various chains.  None of the iterations were for scientific exploration,
so no information is concealed by deleting the records for these script
re-runs.

Basically start with a clean slate.

    specbackgrp src  started 14:24 monday nov 16

May start using Git branches to organize ideas, and trace exploratory analyses.
Depends on the needs at hand.  Use git tag to annotate branch tips or
something, maybe.


Monday 2015 November 16
=======================

Continued organizing up workflow.  Started adding and running new scripts,
selected new regions.

## Scripting

Re-running specbackgrp script (spectrum extraction script). Script successfully
runs `mos_back` and `pn_back`, and renames some files.  But, then this appears
on my terminal:

    atran(sas)@statler:~/rsch/g309/xmm/0087940201/odf/repro$ specbackgrp src
    You should not see this!

And, pressing enter creates more "You should not see this!" messages.
Cause: line breaks in commands being passed to grppha.
In addition, I need to escape exclamation points in tcsh for some reason...

Easiest solution: just use bash.  bash correctly inherits environment variables
($PATH) from calling tcsh, so that's OK.

## Region selection

NOTE: new "standard" procedure for region selection.
1. use PPS processed and merged image P0087940201EPX000OIMAGE8000.FTZ
2. use MOST radio contours for overlay to help see SNR location.

Created image of remnant with radio contours.
(missing: coordinates, scalebar, radio beam and x-ray PSF.  For now OK though.)

Loaded regions (see notes from Oct 18/19).  They were:

    # Source:
    circle(13:46:47.553, -62:51:02.52, 239.76")

    # Background:
    circle(13:47:42.885, -62:44:57.88, 125.41")
    circle(13:46:33.606, -62:42:02.47, 113.572")
    circle(13:47:32.693, -62:56:46.10, 125.41")

I made a few changes:
* moved one background circle that overlapped the SNR's radio contour
* change circle sizes to 120" (radius = 2 arcminutes), nice clean number
* move one background circle off a faint radio contour, that might trace some
  sort of gas / other emission not related to the remnant.
and the new background comprises six small circles around the remnant.

Saved image of:
* XMM 0087940201 merged PPS image, log scale, heat map
  (fits file is P0087940201EPX000OIMAGE8000.FTZ, and I symlink to this file)
* linear most contours (0.01, 0.02, 0.03, ..., 0.2 Jy/beam)
* src.reg, bkg.reg selections created today
to `20151116_xmm0087940201pps_mostlinear_src_bkg.png`.

And, added procedure for creating and regenerating MOST contours.  Pretty
straightforward.

## Minor coordinate mismatch

Adding new script to convert DS9 regions to XMM detector region expressions.
Using same source region as before with newly reprocessed data,
I'm getting VERY slightly different DETX/Y coordinates.
Here's an example for MOS1 detector.

    DS9 fk5:
    0087940201: &&((DETX,DETY) IN circle(-2056.3, -1681.7, 4795.2))
    0551000201: &&((DETX,DETY) IN circle(-4649.7, -2786.9, 4795.2))()


    0087940201 (old): &&((DETX,DETY) IN circle(-2055.2, -1690.2, 4795.2))
    0551000201 (old): &&((DETX,DETY) IN circle(-4650.2, -2784.3, 4795.2))

The difference is ~1-2 detector units, i.e. ~0.1 arcsec, except for DETY
in 0087940201 MOS1 (~9 detector units is ~0.45 arcsec).
These differences are minute given the large region size (~8 arcmin diam),
XMM-Newton PSF, etc.

Working hypothesis: data from XMM SOC archive differs slightly from data
available via NASA HEASARC w3browse.  I test this by getting w3browse data for
these obsids to compare event lists again (rerun cifbuild, odfingest, emchain).

Result (working in `/data/mpofls/atran/research/g309/xmm`):

    > setenv SAS_ODF $XMM_PATH/0087940201/odf/repro/0315_0087940201_SCX00000SUM.SAS
    > setenv SAS_CCF $XMM_PATH/0087940201/odf/repro/ccf.cif
    > reg2xmmdets.pl regs/src.reg 0087940201/odf/repro/mos1S001-ori.fits
    &&((DETX,DETY) IN circle(-2056.3, -1681.7, 4795.2))

    > setenv SAS_ODF $XMM_PATH/w3browse/0087940201/ODF/repro/0315_0087940201_SCX00000SUM.SAS
    > setenv SAS_CCF $XMM_PATH/w3browse/0087940201/ODF/repro/ccf.cif
    > reg2xmmdets.pl regs/src.reg w3browse/0087940201/ODF/repro/P0087940201M1S001MIEVLI0000.FIT
    &&((DETX,DETY) IN circle(-2054.8, -1689.5, 4795.2))

    > setenv SAS_ODF $XMM_PATH/0551000201/odf/repro/1692_0551000201_SCX00000SUM.SAS
    > setenv SAS_CCF $XMM_PATH/0551000201/odf/repro/ccf.cif
    > reg2xmmdets.pl regs/src.reg 0551000201/odf/repro/mos1S001-ori.fits
    &&((DETX,DETY) IN circle(-4649.7, -2786.9, 4795.2))

    > setenv SAS_ODF $XMM_PATH/w3browse/0551000201/ODF/repro/1692_0551000201_SCX00000SUM.SAS
    > setenv SAS_CCF $XMM_PATH/w3browse/0551000201/ODF/repro/ccf.cif
    > reg2xmmdets.pl regs/src.reg w3browse/0551000201/ODF/repro/P0551000201M1S001MIEVLI0000.FIT
    &&((DETX,DETY) IN circle(-4649.7, -2786.9, 4795.2))

OK.  So, my script returns the same result as claimed.
* For 0551000201, w3browse data match XMM-SAS data; no difference.
* For 0087940201, w3browse data still disagree.  But, strangely, it disagrees
  slightly with the data from the first time I computed these regions (by 0.4
  in detx and 0.7 in dety).  Both sets of w3browse data disagree more
  substantially w/ the XMM-SAS downloaded data (~1 in detx and ~8 in dety).

This is curious, and my bet is that it's related to updated calibration files
being passed between XMM SOC and NASA HEASARC.  But, for our analysis, the
discrepancy is extremely unimportant, so don't pursue this further.

## New regions for XMM detectors produced

Quick comparison of source regions being produced (because the source circle is
unchanged from mid-October):

    Old, 0087940201:
	&&((DETX,DETY) IN circle(-2055.2, -1690.2, 4795.2))
	&&((DETX,DETY) IN circle(1509.3, -2280.0, 4795.2))
	&&((DETX,DETY) IN circle(-1383.0, 2121.9, 4795.2))
    New, 0087940201:
	&&((DETX,DETY) IN circle(-2056.3, -1681.7, 4795.2))
	&&((DETX,DETY) IN circle(1500.8, -2281.1, 4795.2))
	&&((DETX,DETY) IN circle(-1374.4, 2123.1, 4795.2))
    Old, 0551000201:
	&&((DETX,DETY) IN circle(-4650.2, -2784.3, 4795.2))
	&&((DETX,DETY) IN circle(2590.2, -4880.6, 4795.2))
	&&((DETX,DETY) IN circle(-2486.9, 4712.8, 4795.2))
    New, 0551000201:
	&&((DETX,DETY) IN circle(-4649.7, -2786.9, 4795.2))
	&&((DETX,DETY) IN circle(2592.7, -4880.1, 4795.2))
	&&((DETX,DETY) IN circle(-2489.4, 4712.3, 4795.2))

All show some very slight changes, order of <10 detector units (which is <0.5
arcsec, so OK).  Changes look smaller for old vs. new 0551000201, maybe because
it is a more recent obsid?  I'm not sure.

Anyways, I'm ok with this, so I will overwrite the old region files.
If needed, they can be salvaged from my old notes anyways.

Remark: to make Makefile work, perhaps the right approach is to build modular
scripts that help hide hard-to-manipulate filename patterns.
Low priority, but can revisit this later...

## Walkthrough of data:

TODO: walk-through data carefully, documenting all possible changes/etc.

0551000201: inspect soft X-ray images
* MOS1 CCD4 appears to have an oddly bright edge, in the file
    0551000201/odf/repro$ ds9 mos1S001-obj-image-det-soft.fits
  I'm not sure if this is removed in the cleaned event list.
  Other CCDs look ok.
* MOS2 CCD5 is very obviously in anomolous state, matching the mos-filter
  flagging.  Other CCDs look ok.
* PN image, presumably without OOT events, looks good.

0087940201:
* MOS1 looks ok (obj-image-det-soft.fits)
* MOS2 looks ok (obj-image-det-soft.fits)
* PN (obj-image-det.fits), presumably without OOT events, looks good.

I re-run spectrum extraction for all the data now, with new background regions.
After some wrestling with the precise nohup command...

    atran(sas)@statler:/data/mpofls/atran/research/g309/xmm/0087940201/odf/repro$ nohup /bin/tcsh -c 'source /data/mpofls/atran/research/g309/xmm/sasinit 0087940201; specbackgrp_0087940201 src; specbackgrp_0087940201 bkg' > &
    nohup_specbackgrp_20151116.log &
    [1] 31479

    atran(sas)@cooper:/data/mpofls/atran/research/g309/xmm/0551000201/odf/repro$ nohup /bin/tcsh -c 'source /data/mpofls/atran/research/g309/xmm/sasinit 0551000201; specbackgrp_0551000201 src; specbackgrp_0551000201 bkg' > &
    nohup_specbackgrp_20151116.log &
    [1] 19068


Friday 2015 November 20
=======================

## Looking at pn-spectra results

pn-spectra failed on 0551000201 because pnS003-clean.fits has unexpected
SUBMODE keyword 'PrimeLargeWindow', but pn-spectra only accepts
* 'PrimeFullWindowExtended' (the PN mode for 0087940201)
  (it also checks for frame time FRMTIME, and treats files w/ FRMTIME <210
   or >210 differently)
* 'PrimeFullWindow'
and it can't handle anything else.  I don't really understand why.

Weird issue: grppha log shows errors reading "infile" for `mos1S001_bkg`,
for BOTH 0551000201 and 0087940201.  Why?
Issue does not occur for either `mos1S001_src` or `mos2S002_bkg`, so this is
quite unusual.

Another issue: I should have grouped the "-os.pi" spectra.  Added a thing into
my scripts to do so, and ran the grppha command by hand for 0087940201 (no
point in doing this for 0551000201).

I do not think it's worth my time to try to reproduce what pn-spectra is doing
from scratch.  If I can't use the ESAS QPB, maybe I can sacrifice some low
energy counts (where soft proton spectrum seems to curve) and just model the
soft proton contamination outright in the PN background.

## More XSPEC fitting discussion

Chatted more with Josh about XSPEC today -- see notebook for some remarks.
Tools Josh noted: Sherpa has a nice Python interface; J. Buchner has created a
package BXA for Bayesian sampling to drive model fits of X-ray spectra, through
XSPEC or Sherpa.

I think I now get what's up with these identifiers.
It's easiest for me to think about folding models through RMF/ARF files.

The functions for response/arf are the most critical, even though in the
default (simplest case) they're normally hidden from the user.
RMF and ARF files, with identifier "x:y", map model/source x --> spectrum y.
In XSPEC, this makes the __spectrum__ "show up" for the given __model__.

    Model params
        params for spectrum x
        params for spectrum y
        ...

Main point of confusion: if two models fold through different RMFs to produce
an output signal, counts(channel), how does XSPEC fit two models, folded
through distinct RMFs, to data that was ALREADY passed through an RMF to
convert channels --> energy ? (when using setplot en).  We must have assumed an
RMF to get to energy, but different counts are parameterized by different RMFs
in our mode.

Changing rmf/arf has no apparent effect on data, in either energy or channel
space (but obviously affects model).
But, removing rmf entirely kills our ability to move to energy space.
Hypothesis: XSPEC makes some assumption on the RMF to show it in energy space,
say, making it diagonal.
I'm not sure how they send the model to energy -- I would assume that
it's folded through rmf/arf, then passed through the assumed RMF (undoing the
RMF step), something like

    M(I) = integral[ M(E) * rmf(I,E) * arf(E) dE ]
    M'(E) = rmf^{-1}(I,E) * M(I)

Apparent answer: XSPEC is fitting in channel space.  See
    http://heasarc.gsfc.nasa.gov/xanadu/xspec/manual/XspecSpectralFitting.html
for the chi^2 formula being minimized -- specified strictly in channel space.
This seems completely logical.

Another thing: remember, BACKSCAL does account for ARF in calculation.
I would think the spatial variation of the RMF matters too, but I guess that's
probably much smaller.

For PRACTICE: walk through ALL XSPEC commands used to get spectra.
rmfgen, arfgen, detmap, etc.

    # source 1 (model 1) folds through resp/arf 1:1 to fit data (:1)
    # source 2 (model 2) folds through resp/arf 2:1 to fit data (:1)
    # (ignoring datagroup "1" for now)

    data 1:1 mos1S001-bkg.pi
    data 1:1 mos1S001-bkg-grp50.pi
    response 1:1 mos1S001-bkg.rmf
    arf 1:1 mos1S001-bkg.arf
    resp 2:1 ../../../caldb/mos1-diag.rsp
    arf 2:1 none

    # source 1 (model 1) folds through resp/arf 1:2 to fit data (:2)
    #   this is the default setting; model 1 always goes through
    #   the rmf/arf attached to the spectrum
    # source 2 (model 2) folds through resp/arf 2:2 to fit data (:2)
    # (ignoring datagroup "1" for now)
    # source 3 (model 3) folds through resp/arf 3:2 to fit data (:2)

    data 2:2 mos1S001-src.pi
    data 2:2 mos1S001-src-grp50.pi
    resp 2:2 ../../../caldb/mos1-diag.rsp
    arf 2:2 none
    resp 3:2 mos1S001-src.rmf
    arf 3:2 mos1S001-src.arf

    # Only now do you specify the models

    model 1:xrb apec + phabs*(po+apec)
    model 2:sp po
    model 3:snr phabs*vnei


Saturday -- Sunday 2015 November 21-22
======================================

Current list of procedure changes (not yet executed):
1. remove enhanced signal in MOS #1, CCD #4.
   script mos-spectra takes cflim parameter to specify where to cut, manually
2. fix PN spectrum extraction for 0551000201
3. explore effects of changing a few epchain parameters
4. explore effect of removing point sources w/ automated algorithm


First attempt to fit backgrounds from 3 instruments simultaneously.
Looks pretty good, I'd say.
* Background regions from 0087940201 only
* 1.49, 1.75 keV line intensities same for both MOS1/MOS2
  (woops, forgot to freeze)
* 1.49, 7.49, 7.11, 8.05, 8.62, 8.90 keV for PN
* Soft proton power law ~ 0.5 for MOS1/MOS2, ~0.76 for PN
* X-ray background - allow a constant term for MOS1/MOS2/PN
  but otherwise use same model
  unabsorbed 1 keV apec, phabs x (power + apec) with 1.4 power law, 0.3 keV
  apec; nH = 1 x 10^22.


    ========================================================================
    Model instr:gaussian<1> + gaussian<2> + gaussian<3> + gaussian<4> + gaussian<5> + gaussian<6> + gaussian<7> + gaussian<8> Source No.: 2   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
                               Data group: 1
       1    1   gaussian   LineE      keV      1.49016      +/-  1.85407E-03
       2    1   gaussian   Sigma      keV      0.0          frozen
       3    1   gaussian   norm                5.81723E-05  +/-  2.45807E-06
       4    2   gaussian   LineE      keV      1.85002      +/-  1.07660E-02
       5    2   gaussian   Sigma      keV      0.0          frozen
       6    2   gaussian   norm                1.07773E-05  +/-  2.73666E-06
       7    3   gaussian   LineE      keV      1.48910      +/-  1.04283E-02
       8    3   gaussian   Sigma      keV      0.0          frozen
       9    3   gaussian   norm                0.0          frozen
      10    4   gaussian   LineE      keV      7.45584      +/-  2.40032E-02
      11    4   gaussian   Sigma      keV      0.0          frozen
      12    4   gaussian   norm                0.0          frozen
      13    5   gaussian   LineE      keV      5.34317      +/-  4.50433E-02
      14    5   gaussian   Sigma      keV      0.0          frozen
      15    5   gaussian   norm                0.0          frozen
      16    6   gaussian   LineE      keV      8.04000      +/-  4.60735E-03
      17    6   gaussian   Sigma      keV      0.0          frozen
      18    6   gaussian   norm                0.0          frozen
      19    7   gaussian   LineE      keV      8.58980      +/-  3.91053E-02
      20    7   gaussian   Sigma      keV      0.0          frozen
      21    7   gaussian   norm                0.0          frozen
      22    8   gaussian   LineE      keV      8.85013      +/-  2.37674E-02
      23    8   gaussian   Sigma      keV      0.0          frozen
      24    8   gaussian   norm                0.0          frozen
                               Data group: 2
      25    1   gaussian   LineE      keV      1.49016      = instr:p1
      26    1   gaussian   Sigma      keV      0.0          = instr:p2
      27    1   gaussian   norm                5.81723E-05  = instr:p3
      28    2   gaussian   LineE      keV      1.85002      = instr:p4
      29    2   gaussian   Sigma      keV      0.0          = instr:p5
      30    2   gaussian   norm                1.07773E-05  = instr:p6
      31    3   gaussian   LineE      keV      1.48910      = instr:p7
      32    3   gaussian   Sigma      keV      0.0          = instr:p8
      33    3   gaussian   norm                0.0          = instr:p9
      34    4   gaussian   LineE      keV      7.45584      = instr:p10
      35    4   gaussian   Sigma      keV      0.0          = instr:p11
      36    4   gaussian   norm                0.0          = instr:p12
      37    5   gaussian   LineE      keV      5.34317      = instr:p13
      38    5   gaussian   Sigma      keV      0.0          = instr:p14
      39    5   gaussian   norm                0.0          = instr:p15
      40    6   gaussian   LineE      keV      8.04000      = instr:p16
      41    6   gaussian   Sigma      keV      0.0          = instr:p17
      42    6   gaussian   norm                0.0          = instr:p18
      43    7   gaussian   LineE      keV      8.58980      = instr:p19
      44    7   gaussian   Sigma      keV      0.0          = instr:p20
      45    7   gaussian   norm                0.0          = instr:p21
      46    8   gaussian   LineE      keV      8.85013      = instr:p22
      47    8   gaussian   Sigma      keV      0.0          = instr:p23
      48    8   gaussian   norm                0.0          = instr:p24
                               Data group: 3
      49    1   gaussian   LineE      keV      1.49016      = instr:p1
      50    1   gaussian   Sigma      keV      0.0          = instr:p2
      51    1   gaussian   norm                0.0          frozen
      52    2   gaussian   LineE      keV      1.85002      = instr:p4
      53    2   gaussian   Sigma      keV      0.0          = instr:p5
      54    2   gaussian   norm                0.0          frozen
      55    3   gaussian   LineE      keV      1.48910      = instr:p7
      56    3   gaussian   Sigma      keV      0.0          = instr:p8
      57    3   gaussian   norm                8.83618E-06  +/-  1.30864E-06
      58    4   gaussian   LineE      keV      7.45584      = instr:p10
      59    4   gaussian   Sigma      keV      0.0          = instr:p11
      60    4   gaussian   norm                1.05592E-05  +/-  2.01838E-06
      61    5   gaussian   LineE      keV      5.34317      = instr:p13
      62    5   gaussian   Sigma      keV      0.0          = instr:p14
      63    5   gaussian   norm                3.52263E-06  +/-  1.36904E-06
      64    6   gaussian   LineE      keV      8.04000      = instr:p16
      65    6   gaussian   Sigma      keV      0.0          = instr:p17
      66    6   gaussian   norm                9.86675E-05  +/-  4.10001E-06
      67    7   gaussian   LineE      keV      8.58980      = instr:p19
      68    7   gaussian   Sigma      keV      0.0          = instr:p20
      69    7   gaussian   norm                1.22391E-05  +/-  3.08128E-06
      70    8   gaussian   LineE      keV      8.85013      = instr:p22
      71    8   gaussian   Sigma      keV      0.0          = instr:p23
      72    8   gaussian   norm                2.50312E-05  +/-  3.63480E-06
    ________________________________________________________________________


    ========================================================================
    Model spm1:powerlaw<1> Source No.: 3   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
                               Data group: 1
       1    1   powerlaw   PhoIndex            0.519159     +/-  1.80841E-02
       2    1   powerlaw   norm                4.25692E-02  +/-  1.30967E-03
    ________________________________________________________________________


    ========================================================================
    Model spm2:powerlaw<1> Source No.: 4   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
                               Data group: 2
       1    1   powerlaw   PhoIndex            0.507269     +/-  1.78046E-02
       2    1   powerlaw   norm                4.05707E-02  +/-  1.25785E-03
    ________________________________________________________________________


    ========================================================================
    Model sppn:powerlaw<1> Source No.: 5   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
                               Data group: 3
       1    1   powerlaw   PhoIndex            0.762193     +/-  2.69742E-02
       2    1   powerlaw   norm                7.68172E-02  +/-  2.86196E-03
    ________________________________________________________________________


    ========================================================================
    Model xrb:constant<1>*constant<2>(apec<3> + phabs<4>(powerlaw<5> + apec<6>)) Source No.: 1   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
                               Data group: 1
       1    1   constant   factor              1.00000      frozen
       2    2   constant   factor              1.00000      frozen
       3    3   apec       kT         keV      1.00000      frozen
       4    3   apec       Abundanc            1.00000      frozen
       5    3   apec       Redshift            0.0          frozen
       6    3   apec       norm                1.57651E-05  +/-  6.96728E-06
       7    4   phabs      nH         10^22    1.00000      frozen
       8    5   powerlaw   PhoIndex            1.40000      frozen
       9    5   powerlaw   norm                7.99979E-15  +/-  1.56934E-05
      10    6   apec       kT         keV      0.300000     frozen
      11    6   apec       Abundanc            1.00000      frozen
      12    6   apec       Redshift            0.0          frozen
      13    6   apec       norm                1.58997E-03  +/-  4.04653E-04
                               Data group: 2
      14    1   constant   factor              1.11725      +/-  0.228343
      15    2   constant   factor              1.00000      frozen
      16    3   apec       kT         keV      1.00000      = xrb:p3
      17    3   apec       Abundanc            1.00000      = xrb:p4
      18    3   apec       Redshift            0.0          = xrb:p5
      19    3   apec       norm                1.57651E-05  = xrb:p6
      20    4   phabs      nH         10^22    1.00000      = xrb:p7
      21    5   powerlaw   PhoIndex            1.40000      = xrb:p8
      22    5   powerlaw   norm                7.99979E-15  = xrb:p9
      23    6   apec       kT         keV      0.300000     = xrb:p10
      24    6   apec       Abundanc            1.00000      = xrb:p11
      25    6   apec       Redshift            0.0          = xrb:p12
      26    6   apec       norm                1.58997E-03  = xrb:p13
                               Data group: 3
      27    1   constant   factor              0.411642     +/-  9.18809E-02
      28    2   constant   factor              1.00000      frozen
      29    3   apec       kT         keV      1.00000      = xrb:p3
      30    3   apec       Abundanc            1.00000      = xrb:p4
      31    3   apec       Redshift            0.0          = xrb:p5
      32    3   apec       norm                1.57651E-05  = xrb:p6
      33    4   phabs      nH         10^22    1.00000      = xrb:p7
      34    5   powerlaw   PhoIndex            1.40000      = xrb:p8
      35    5   powerlaw   norm                7.99979E-15  = xrb:p9
      36    6   apec       kT         keV      0.300000     = xrb:p10
      37    6   apec       Abundanc            1.00000      = xrb:p11
      38    6   apec       Redshift            0.0          = xrb:p12
      39    6   apec       norm                1.58997E-03  = xrb:p13
    ________________________________________________________________________


    Fit statistic : Chi-Squared =         664.01 using 593 PHA bins.

    Test statistic : Chi-Squared =         664.01 using 593 PHA bins.
     Reduced chi-squared =         1.1732 for    566 degrees of freedom
     Null hypothesis probability =   2.720152e-03
    XSPEC12>pl ld


Monday 2015 November 23
=======================

Current list of procedure changes (not yet executed, copied from Sat/Sun 2015
Nov 21-22):
1. remove enhanced signal in MOS #1, CCD #4.
   script mos-spectra takes cflim parameter to specify where to cut, manually
2. fix PN spectrum extraction for 0551000201
3. explore effects of changing a few epchain parameters
4. explore effect of removing point sources w/ automated algorithm

Early morning of Monday (~1:30am) I was trying to apply the "good" background
fit to the SNR fit.

__Observation:__ the instrumental line fit from background regions is
over-eager -- we actually have negative residual.  Modeled PN lines shoot way
above the actual signal when I import the background parameters unchanged from
my fit to bkg region (back.xcm).

__Simple mistake:__ I did not account for ratio of src/bkg areas (normally
automatically done by XSPEC, by taking BACKSCAL ratio and applying to the
BACKGRND spectrum).

QUESTION: Is taking ratio of areas OK (well, integral arf(x,y) dxdy)?
Tentatively, yes.  Difference in RMF/ARF is accounted for by folding through
SOURCE RMF/ARF instead of BKG RMF/ARF.

QUESTION: ARF/RMF account for extended sources by weighting over the source
region.  Are they always "normalized" to 1, so that I should be multiplying my
background model normalizations by the ratio BACKSCAL(src)/BACKSCAL(bkg)??
As ESAS is intended to work with XSPEC, I'm going to assume this is OK.

QUESTION: what about energy dependence of ARF/RMF?
This should be fine.  Again as long as source/bkg arf/rmf are weighted
correctly to handle this, that's OK.  All we have to do is pass model
parameters through the arf/rmf.
Now, of course, XMM-SAS's backend implementation is WAY easier if we can assume
that arf (or, rmf) is separable as arf(x,y,E) = phi(x,y) * psi(E).  That is,
the spectral response/gain of the detector is spatially invariant.
But that's a question for another day...

__Adapting background fit parameters to source fit__:

I created a one-off script (`xmm/bkg2src_norm`) that gives me the ratio of
src/bkg areas for each instrument in obsid 0087940201, by simply inspecting
BACKSCAL keywords inserted by `mos-spectra`.

    atran(sas)@treble:~/rsch/g309/xmm$ ./bkg2src_norm

    MOS1 BACKSCAL calculation
    src: 7.098143E+07
    bkg: 8.421573E+07
    (7.098143E+07) / (8.421573E+07)
    src/bkg: 0.842852398239616

    MOS2 BACKSCAL calculation
    src: 6.927987E+07
    bkg: 1.012479E+08
    (6.927987E+07) / (1.012479E+08)
    src/bkg: 0.684259821685191

    PN BACKSCAL calculation
    src: 6.433184E+07
    bkg: 9.177010E+07
    (6.433184E+07) / (9.177010E+07)
    src/bkg: 0.701010895705682

Now, I need to apply the normalization to my background fits.  Unfortunately
this is non-trivial because neither bash nor xspec can do math (every day I am
inching closer to PyXSPEC or Sherpa or something better than this).
Simple fix conceptually, even if a hassle to implement (TBD).

NOW, are there any background regions we need to twiddle?
Comparing line emission from source and background... yes, more adjustments
needed.  Intensities, and ratios of lines, are definitely not the same.

* XRB -- I will assume constant over detector region

* Instrumental lines vary.

  Across MOS1/MOS2 the spatial distribution of line strengths is similar.
  BUT, rotation of detectors + different regions means there is no reason to
  expect the normalizations, in either absolute intensity or ratio of
  intensities, to be linked.  All we can say is that absolute intensities
  should be comparable and should follow the map of line emission from Kuntz
  and Snowden (2008).

  TODO: can we use the database of FWC observations to estimate the line
  strength and/or ratio of line strengths?

  TODO: what is the physical mechanism that causes the fluorescent emission, in both
  FWC and non-FWC observations?

  TODO: why does ESAS doc consistently assert that Si line is at 1.75 keV?
  They're probably right, but I want to know what line this is that is
  different than the normal 1.85 heavily ionized Si line.
  Probably, similar line but energy adjusted due to presence of remaining
  electrons or something...

  IF the photons/particles that induce fluorescent emission are predominantly
  NOT focused down the telescope boresight, then it should be easy to
  characterize lines regardless of sky position (barring obscenely bright
  things like Cyg X-1 or whatever).

* Misc. point sources -- need to test out cheese

* Soft proton, I have no fucking idea. ESAS creates soft proton images based on
  the spectral fit -- I don't know if this lets us consider spatial variation,
  or if it's just based on a semi-random event list cut based on our model soft
  proton spectrum (if so we'd HAVE to either get a global fit, or specify the
  extraction region -- only a global fit makes sense, and that might not be
  possible for all observations).

  TODO: physical mechanism for soft proton contamination.  Any spatial
  dependence?!

* SWCX (solar wind charge exchange) -- ok, this ought to be invariant.
  But inspect the data.  Be suspicious of oxygen abundance from vnei fitting.


## Adjusting toy SNR fit (0087940201)

allowing various components in vnei model to float, I can get down to
chi-squared = 1022.  Keeps going to 0 neon, and 0 iron.  Numbers are wonky
(some places asking for 20,40x solar for Ar/Ca/O/Ne or w/e).

Freeing oxygen helps handle low-energy excess (would be hard to distinguish
from SWCX usually, but if we assume SWCX + XRB from background regions is
representative, then this is OK).

I'm tempted to let SWCX float for PN, but that's no good because our estimate
of SWCX is inferred from a fit to real data

Add two more lines to SWCX.  I think the residual in soft PN/MOS emission is
part of what's getting us, and it's not well modeled by either O or Fe emission
in the SNR vnei.

## NASA XMM-GOF tool to estimate SWCX

Looking at trend plot for revolution 0315, obsid 0087940201:

    https://heasarc.gsfc.nasa.gov/docs/xmm/scripts/xmm_trend.html

Start,stop for 0087940201 are 1.15354e8 and 1.15394e8 seconds
Note: these are seconds measured from January 01, 1998, 00:00:00 UTC
The calculation

    January 01 1998 00:00:00utc + 1.15354430246723e8 seconds

yields 2001 August 28, 02:53:50am UTC, which is just one minute off from the
stated observation start time (02:52:50, I don't know what happened).

It looks like our observation is fine with basic flare filtering (matches my
experience so far), but shows evidence for SWCX contamination.  I don't know
how much, from the plot, but certainly above baseline.

Taking the epoch (01/01/98) and adding 1.15354
It aligns to the observation start time...

## OK I need to stop, step backward, and retrace a few details of my work so far.


Tuesday 2015 November 24
========================

Current list of pending procedure changes (copied from Mon 2015 Nov 23):
1. remove enhanced signal in MOS #1, CCD #4.
   script mos-spectra takes cflim parameter to specify where to cut, manually
2. fix PN spectrum extraction for 0551000201
3. explore effects of changing a few epchain parameters
4. explore effect of removing point sources w/ automated algorithm

Spoke with Pat.  OK to go ahead with procedures I'm considering:
1. estimating line strengths and ratios based on FWC spectra
2. applying data cut to estimate SWCX contamination between start and end of observation!
3. didn't ask explicitly, but maybe use ESAS proton task to back out a model
   spectrum in central region... assuming the soft proton vignetting function
   IS included in ESAS, as claimed by snowden's presentation

   http://web.mit.edu/iachec/meetings/2014/Presentations/Kuntz.pdf

Stuff from Pat:
1. just do a simple background subtraction, compare your results
2. good to have numbers.  preliminary, but use for comparisons and to guide
   direction of work
3. temperature kT ~ 2 keV is really high! check your methods
4. proton vignetting, interesting..
5. ay253 sounds worthwhile.
6. yeah, no reason not to expect spectral variation with position on detector
   (proton reflectivity on mirrors varies with energy too, right?)
   so it does make sense that soft proton power law should vary.
   tricky problem to deal with, but oh well.


Wednesday 2015 November 25
==========================

Playing with fakeit and vnei, to help intuit effect of changing elemental
abundances, kT, and tau.  No notable results produced.

Paused to work more on ACA stuff, after MP meeting.


Wednesday-Thursday 2015 December 2,3
====================================

Resumed after Thanksgiving + a few more MP script things over Mon/Tues/Weds.

Current list of pending procedure changes (copied from Mon 2015 Nov 23):
2. fix PN spectrum extraction for 0551000201
3. explore effects of changing a few epchain parameters
4. explore effect of removing point sources w/ automated algorithm
5. check what/where filter flags are applied, and add comments to scripts.
   (flag and pattern rejections)
   see if we need to evselect anywhere to remove these bad events.
6. double check plots of histogram filtering, see if 2nd round is needed.
7. add mosaicking step.

MOS1 CCD4 noise band removal
----------------------------
Per 2015 November 16 notes, where I inspected soft X-ray images produced by a
"standard chain", remove MOS1 CCD4 edge noise in 0551000201 as follows:

Generate DETX histogram using xmmselect on mos1S001-ori.fits (emchain
output) with selection `(CCDNR == 4)&&(PI in [100:1300])`,
histogram binning 10, and histogram min/max of 0,13200.

    Histogram: img-notes/20151202_histogram.png

The noise doesn't appear too enhanced, peaks around 26 counts and is
fairly narrow, compared to the ESAS example.  But it is clearly a strong
feature.  From visual inspection, we can cut events with DETX >= 12000.

I double check with 0551000201/odf/repro/mos1S001-obj-image-det-soft.fits
and confirm, by eye, that a cut at DETX = 12000 looks good.
Note that to help visually pull out the feature, you need to smooth or bin
the data in ds9.

Modified script `specbackgrp_0551000201` to use cflim=12000 for MOS1 spectrum
processing.  I did not generate new spectra immediately.
Quick visual inspection of current regions in MOS1S001 sky coords suggests that
none are near the chip edges, so we should be ok.

Get PN spectrum extraction working for 0551000201
-------------------------------------------------
See 2015 Nov. 20 notes. I need to inspect how pn-spectra works.

    Depending on SUBMODE and FRMTIME, set values for
        $scale
            $scale is used in two places:
            1. compute $rate based on NAXIS2 keyword in corner OOT events?!
               PI in 600:1300, 1650:7200 (both hard and soft)
               * $rate in turn is used printed with "Corner rate/corner hardness"
                 as part of pn-spectra terminal output.
            2. compute $hard based on NAXIS2 keyword in corner OOT events
               PI in 1650:7200 (hard only)
            PrimeFullWindowExtended (frametime < 210)
            uses scale 0.0232 (2.32%?)
            PrimeFullWindowExtended (frametime > 210)
            uses scale 0.0163 (1.63% sensible, larger frametime -> less OOT)
            PrimeFullWindow
            uses scale 0.063 (6.3%?).  Again about right, almost 3x faster
            readout means 3x more OOT events.

            Neither $rate nor $hard have any effect on final output.
        $submode (split on PrimeFullWindowExtended, depending on frame time)
            Doesn't seem to be used anywhere, except in printing output.
        $mode
            Again isn't used anywhere except in diagnostic output

    Look into how OOT event %s are computed.
    Based on SPIE paper on PN operations (1997?).
    PN operations:
        NL (regular shift+read) = 23.04 microsec
        FS (fast shift) = 0.72 microsec

    Full frame:
        readout time ~ 23.04*200 microsec = 4.608 ms
        integration time ~ 73.4 ms
        % OOT = 6.28%

    Ext full frame:
        readout time ~ 4.608 ms (same as full frame)
        integration time ~ 199.1 ms (accomplished by adding 52.4ms delay
        between quadrant readout -- not sure how, diff between 199.1ms and
        73.4ms is 31.425*4 ms)
        % OOT = 2.31%

    Large window: only use 1/2 CCD.
        rapidly read and discard lines 0-99 ~ 0.72 * 100 microsec
        read remaining lines (100-199) normally ~ 23.04 * 100 microsec
        read/dump 100 lines, fast ~ 0.72 * 100 microsec
            (this discards OOTs from preceding readout; fast shift still has OOTs but much fewer)
        integration time ~ 47.7ms
        % OOT = 0.072/(47.7ms * 0.949) = 0.159%

        total time: 2.448ms * 11 + twait,twarm,etc
        not sure how they got 47.7ms integration time, but I guess it works
        out.  The OOT% I'm getting is consistent with XMM user's guide.

Note, OOT events are NOT incorporated anywhere until the final spectra are
extracted (and this is done in `pn_back`).  In `pn-filter` the regular and OOT
files are processed separately.  The log from `pn_back` notes the observation
mode and OOT scaling to use.

After further reading, I realized that large window observations can't be
processed by ESAS because there are no corner observation data
available.  Thus we can't get a QPB.  This was all stated in the ESAS cookbook
up front.  OK, that makes sense.

At some point (Dec. 3), I attempted to run a modified version of pn-spectra.
This obviously failed; even after setting the scale parameter for large window,
it couldn't extract corner count rates and hit a divide-by-zero error when
calculating a hardness ratio.

So how do we deal with this dataset specially?

What if we just fit the background without QPB?

Fit 0087940201 MOS1S001 background spectrum, using `back.xcm` and then invoking
`data 2 none` in XSPEC to discard the MOS2S002 and PNS003 spectra.

    -> chisqr changes marginally (1.0846 to 1.1164)

Inspect residuals from model fit, then background remove (so compare to data
w/o QPB to model w/QPB).  By eye, maybe MOS could get away with it.  But, PN
has a huge excess in soft band (<0.5 keV).

Fit 0087940201, all 3 instruments, background spectrum, using `back.xcm` then
invoking back 1 none, back 2 none, back 3 none to discard QPBs.

    Test statistic : Chi-Squared =         696.33 using 612 PHA bins.
     Reduced chi-squared =         1.1883 for    586 degrees of freedom
     Null hypothesis probability =   1.109445e-03

    Test statistic : Chi-Squared =         647.76 using 612 PHA bins.
     Reduced chi-squared =         1.1054 for    586 degrees of freedom
     Null hypothesis probability =   3.890180e-02


1. Fit with background (QPB) present

    Test statistic : Chi-Squared =         170.29 using 169 PHA bins.
     Reduced chi-squared =         1.0846 for    157 degrees of freedom
     Null hypothesis probability =   2.215537e-01

    ========================================================================
    Model instr:gaussian<1> + gaussian<2> + gaussian<3> + gaussian<4> + gaussian<5> + gaussian<6> + gaussian<7> + gaussian<8> Source No.: 2   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
       1    1   gaussian   LineE      keV      1.49000      frozen
       2    1   gaussian   Sigma      keV      0.0          frozen
       3    1   gaussian   norm                5.45958E-05  +/-  3.57696E-06
       4    2   gaussian   LineE      keV      1.75000      frozen
       5    2   gaussian   Sigma      keV      0.0          frozen
       6    2   gaussian   norm                2.71880E-06  +/-  2.37192E-06

    ========================================================================
    Model spm1:powerlaw<1> Source No.: 3   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
       1    1   powerlaw   PhoIndex            0.472479     +/-  2.52238E-02
       2    1   powerlaw   norm                3.93902E-02  +/-  2.12869E-03

    ========================================================================
    Model swcx:gaussian<1> + gaussian<2> Source No.: 6   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
       1    1   gaussian   LineE      keV      0.560000     frozen
       2    1   gaussian   Sigma      keV      0.0          frozen
       3    1   gaussian   norm                4.23113E-05  +/-  1.88449E-05
       4    2   gaussian   LineE      keV      0.650000     frozen
       5    2   gaussian   Sigma      keV      0.0          frozen
       6    2   gaussian   norm                7.37661E-06  +/-  9.13970E-06

    ========================================================================
    Model xrb:constant<1>*constant<2>(apec<3> + phabs<4>(powerlaw<5> + apec<6>)) Source No.: 1   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
       1    1   constant   factor              1.00000      frozen
       2    2   constant   factor              1.00000      frozen
       3    3   apec       kT         keV      0.800876     +/-  9.67488E-02
       4    3   apec       Abundanc            1.00000      frozen
       5    3   apec       Redshift            0.0          frozen
       6    3   apec       norm                2.71665E-05  +/-  8.04079E-06
       7    4   phabs      nH         10^22    1.85473      +/-  0.601081
       8    5   powerlaw   PhoIndex            1.40000      frozen
       9    5   powerlaw   norm                1.49479E-08  +/-  3.56009E-05
      10    6   apec       kT         keV      0.344765     +/-  0.106170
      11    6   apec       Abundanc            1.00000      frozen
      12    6   apec       Redshift            0.0          frozen
      13    6   apec       norm                5.40461E-03  +/-  7.67162E-03


2. Fit after calling `back none` to remove QPB.

    Test statistic : Chi-Squared =         175.28 using 169 PHA bins.
     Reduced chi-squared =         1.1164 for    157 degrees of freedom
     Null hypothesis probability =   1.512035e-01

    ========================================================================
    Model instr:gaussian<1> + gaussian<2> + gaussian<3> + gaussian<4> + gaussian<5> + gaussian<6> + gaussian<7> + gaussian<8> Source No.: 2   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
       1    1   gaussian   LineE      keV      1.49000      frozen
       2    1   gaussian   Sigma      keV      0.0          frozen
       3    1   gaussian   norm                5.41860E-05  +/-  3.63455E-06
       4    2   gaussian   LineE      keV      1.75000      frozen
       5    2   gaussian   Sigma      keV      0.0          frozen
       6    2   gaussian   norm                2.58837E-06  +/-  2.37059E-06
    ...

    Model spm1:powerlaw<1> Source No.: 3   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
       1    1   powerlaw   PhoIndex            0.439894     +/-  2.13021E-02
       2    1   powerlaw   norm                4.75057E-02  +/-  2.18412E-03

    Model swcx:gaussian<1> + gaussian<2> Source No.: 6   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
       1    1   gaussian   LineE      keV      0.560000     frozen
       2    1   gaussian   Sigma      keV      0.0          frozen
       3    1   gaussian   norm                4.18679E-05  +/-  1.88575E-05
       4    2   gaussian   LineE      keV      0.650000     frozen
       5    2   gaussian   Sigma      keV      0.0          frozen
       6    2   gaussian   norm                6.96550E-06  +/-  9.14624E-06

    Model xrb:constant<1>*constant<2>(apec<3> + phabs<4>(powerlaw<5> + apec<6>)) Source No.: 1   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
       1    1   constant   factor              1.00000      frozen
       2    2   constant   factor              1.00000      frozen
       3    3   apec       kT         keV      0.805529     +/-  0.103846
       4    3   apec       Abundanc            1.00000      frozen
       5    3   apec       Redshift            0.0          frozen
       6    3   apec       norm                2.53347E-05  +/-  8.01923E-06
       7    4   phabs      nH         10^22    1.85336      +/-  0.638269
       8    5   powerlaw   PhoIndex            1.40000      frozen
       9    5   powerlaw   norm                1.04421E-17  +/-  3.59608E-05
      10    6   apec       kT         keV      0.341441     +/-  0.182041
      11    6   apec       Abundanc            1.00000      frozen
      12    6   apec       Redshift            0.0          frozen
      13    6   apec       norm                5.18351E-03  +/-  1.03722E-02


Maybe we can find an alternate way to work around this...


Friday 2015 December 4
======================

0087940201 pnS003 exposure QPB from ESAS -- looks good, compared in XSPEC and
the QDP plot from `pn_back`.

But, 0551000201 QPBs for both MOS1 and MOS2 look like utter crap.
They look ok in the QDP plot file, but in XSPEC they look really bad.  What
happened??

I looked through logs for MOS1S001 src with mos_back and didn't see any obvious
issues.


Monday 2015 December 7 -- epreject exploration
==============================================

Current list of pending procedure changes (copied from Weds 2015 Dec 2):
2. fix PN spectrum extraction for 0551000201
    -- in works, deciding how to work without QPB, we'd need different
    procedure.  Defer temporarily, I will work out a few more things on
    0087940201 first.

    Remark: epchain doc claims that its runbackground=Y mode is able to create
    background spectrum for LW imaging mode.  But, looking at XMM-Newton sky
    FOV in DS9, this seems impossible...

3. explore effects of changing a few epchain parameters
    epreject, epnoise
4. explore effect of removing point sources w/ automated algorithm
5. check what/where filter flags are applied, and add comments to scripts.
   (flag and pattern rejections)
   see if we need to evselect anywhere to remove these bad events.
6. double check plots of histogram filtering, see if 2nd round is needed.
7. add mosaicking step.
8. is it necessary to run filtering step 2x?
   re-run espfilt, see what happens.

Investigating effect of epchain run: epreject, epnoise
------------------------------------------------------

* epreject -- only a small number of pixels should be affected by the high
  energy strikes.  (why is it disabled by default?)
* epnoise -- seems unnecessary, procedure is just to remove frames with too
  many soft x-ray counts.  This should be covered by pn-filter task.
  I will skip this.

Parameter settings via epchain to epreject.  epchain's call to epreject does
NOT screen soft flares by default in xmmsas_20141104.  This is OK to me.

    withsoftflarescreening=N hardcoded in epchain
    withoffsetmap=Y by default in epchain, but not in SAS doc...
    withnoisehandling='N' by default, user cannot set through epchain
        (I don't even know what it does)
    sigma=4 for offset correction (default)
    noiseparameters=... (default)
    withxrlcorrection=N (default, imaging mode so no need)

I set sigma=5 for finding bright spots, per recommendation of epreject doc:

    Tests indicate that setting this parameter to $\sim4\,\sigma$ is a good choice
    for short ( $\sim5\mbox{ ks}$) exposures; for longer exposures this parameter
    can be increased (to $\sim5$-$6\,\sigma$ for more than 20 ks).

And I use adu=20 and adu<20 (PHA column in FITS files) to look at actual data.

    It is recommended to control the results by accumulating an image below
    20 adu after this task: this image shows the pixels where an offset shift
    was applied (Fig.5).

Running epchain with runepreject=Y for 0087940201 PNS003, but epreject failed
for both OOT and regular runs.

    ** epreject: warning (NoOffsetMap), No offset map found; using 20 ADU image
    instead
    [...]
    ** epreject: warning (notCalibrated),  no offset calibration for submode
    PrimeFullWindowExtended, skipping rest of the task

No offset map is available, OK, where should that be found?  epreject calls the
function:

    OAL_hasAssociatedSet(OFFSET_DATA)  looking in ODF (ODF access layer)

Which, I assume (but did not verify), seeks the following files according to
online ODF guide:

    files of form {RRRR}_{obsidentif}_PN{U}{EEE}{CC}ODI.FIT
        {U} = observation scheduled (S) or unscheduled (U), I don't know what that means
        {EEE} = exposure number within observation
        {CC} = PN CCD
    correspond to EPIC PN offset data.

0087940201 has no such offset files, so I guess offset maps were not computed
early in the mission.
But, 0551000201 has these offset files!

Now, what about the offset calibration map?
From SAS source (packages/cal/f90/cal.f90) it looks like pnMedianMap
access interface was only added in November 2003.

    epreject attempts to read pnMedianMap from CCF.

        call CAL_pnMedianMap(r4med)

    In the source for CAL library ( packages/cal/f90/CalF90cxxGlue.cc ),
    inspect function CAL_pnMedianMap.  CalServer is used to instantiate a
    LowEnergyNoiseServer, which has method medianMap to read in the medianMap
    for a given mode and CCD.

    LowEnergyNoiseServer appears to read this in by creating

        CcfConstituentTable ccftab(dataSet, "MEDIAN_MAP_INDEX");
        const Table * medianMapTab = ccftab.block();

    And I can't easily figure out where the code for CcfConstituentTable comes
    from

        epreject:- reading from CCF: pnMedianMap
        epreject:- Opening CCF CIF /data/mpofls/atran/research/g309/xmm/0087940201/odf/repro/ccf.cif

        [....
        many calls of form:]

        epreject:- Attempting to access block with name 'MEDIAN_MAP_DUMMY' in dataset with name '/proj/xmm/ccf/EPN_REJECT_0006.CCF'.

        [so I'm not sure what the role of the CCF file is, in all this.
         Actually, why should anything be in the CIF file if this is a standard
         reference offset image for all observations?]

OK, I'm not going further than this.  Don't want to spend another hour or two
wading through source + logging output to figure it out.

(edit: I guess I changed my mind...)

0087940201 won't have epreject run; the offset map is not available in the ODF,
and the reference offset map (count images from many observations) was not
found in the CIF.  I don't know what file is missing, and I don't know why it's
missing.

BUT, 0551000201 does have offset map available; I run this accordingly.

    Histogram binning on PHA is indeed slightly different, fewer events at
    lower energy.  Consistent with epchain log which claims that many events
    were offset corrected, but I don't see any events below 20 ADU in evselect

I'm really confused.  Keywords in `EXPOS{ccd#}` tables of pnS003-ori.fits
indicate offset maps changed, but there are no ADU<20 events in EVENTS table.

events01.dat ->cleanevents01.dat filters on PI > 150, AFTER epreject step.
We normally expect ADU=20 to correspond to 100 eV, so I'm surprised that any
events with ADU=20 exist at all.  I guess these are events with different
offsets, such that ADU=20 corresponds to PI > 150.

This seems like a plausible explanation.  So, how can I look at the energy
shift?  I'm worried that so many events were affected by this procedure
(depends on the chip), so we DO need to inspect the result of the filtering.

Try running epchain with parameter screenlowthresh=0.  Tested, still observe no
ADU < 20 events.  Try again keeping intermediate products..

    epchain runepreject=Y sigma=5 screenlowthresh=0 keepintermediate=all >& epchain_rerun_nocut_interm.log
    evselect table=P0551000201PNS003PIEVLI0000.FIT expression='(PHA<20)' filteredset=pnS003-ori-rerun_nocut_lt20adu.fits

Inspect rawevents01.dat.  From the epchain logging output:

        epreject:-    576802 of  1008425 events selected for offset correction
        epreject:-    101285 events shifted below threshold of    20 [adu]

    evselect table=rawevents01.dat expression='(PHA<20)' filteredset=rawevents01_lt20adu.fits

        evselect:- selected 101285 rows from the input table.

    evselect table=events01.dat expression='(PHA<20)' filteredset=events01_lt20adu.fits

        evselect:- selected 101285 rows from the input table.

    evselect table=cleanevents01.dat expression='(PHA<20)' filteredset=cleanevents01_lt20adu.fits

        evselect:- selected 0 rows from the input table.

BINGO.
Aside: after epevents call (converts rawevents01.dat to events01.dat),
epchain calls attcalc on events01.dat; this just adds X/Y columns to FITS event
list and has no effect on ADU<20 events.

Let's deconstruct the culprit evselect call in epchain, which is:

    evselect table=events01.dat:EVENTS withfilteredset=Y \
        filteredset=cleanevents01.dat
        destruct=Y
        expression='(PI>0 && RAWY>0 )' \
        writedss=Y
        updateexposure=Y
        keepfilteroutput=Y
        -w 10

Why is this destroying the ADU<20 events?

    Many of these have FLAG field 134217728 = 0x07FF FDAE
        0000 0111 1111 1111 ... 1111 1101 1010 1110
    I see one example of 134217732 = 0x08000004
        0x4 -> close to CCD window
        0x0800,0000 -> no idea... not listed in pn flag attributes...
    But evselect call is not filtering on FLAG.

    Flag: -w 10 forces only first 10 of each warning type to be shown.
    Flags: filteredset, keepfilteroutput --> set output as usual
    Flag: writedss=Y is normally on by default
    Flag: updateexposure=Y writes new keywords (LIVETIME, ONTIME, etc)
    Flag: withfilteredset=Y this is NO LONGER in the SAS documentation...

AH, PI value = NULL for these events.
    (creating a histogram on PI value in 'fv' causes fv to segfault and die)


The raw events list (after epreject, before epevents) has PHA w/offset applied,
FLAG, OFF_COR; no PI value is assigned.

Inspecting the ADU<20 events in DS9, I note
* spread due to epframes randomizing position of events within pixel
  (if you count blocks, comes out about right, nearly 64 pixels)
* a lot more events than I would expect.  Could be associated with
  flaring in this observation?!...
  (do we need to run soft flare filtering first?)

After epevents is run, events list has added:
    DETX, DETY, PHA_CTI, PI, PATTERN,

OK, try running process without epreject, as:

    epchain screenlowthresh=0 keepintermediate=all >& epchain_rerun.log

    evselect table=rawevents01.dat expression='(PHA==20)' filteredset=rawevents01_eq20adu.fits
        evselect:- selected 228915 rows from the input table.
    evselect table=events01.dat expression='(PHA==20)' filteredset=events01_eq20adu.fits
        evselect:- selected 228915 rows from the input table.
    evselect table=cleanevents01.dat expression='(PHA==20)' filteredset=cleanevents01_eq20adu.fits
        evselect:- selected 220002 rows from the input table.

    evselect table=P0551000201PNS003PIEVLI0000.FIT expression='(PHA==20)' filteredset=P0551000201PNS003PIEVLI0000.FIT_eq20adu.fits
        evselect:- selected 3577095 rows from the input table.

That is a LOT of events at ADU=20.  Inspecting the uncleaned events file:
    ds9 events01_eq20adu.fits
I see basically what looks like signal, no obvious cosmic ray strikes (or, hard
to differentiate from point sources in FOV).

I'm strongly leaning towards ignoring this shift.
The correction is order of a few ADU ~ 10-15 eV = 0.010-0.015 keV
This should be pretty negligible, I think -- especially since it's just
isolated to a few pixels, and is thus a ~1% effect.

We have much bigger fish to fry.



Tuesday 2015 December 8 -- more on epreject
===========================================

Current list of pending procedure changes (copied from Mon 2015 Dec 7):
2. fix PN spectrum extraction for 0551000201
    -- in works, deciding how to work without QPB, we'd need different
    procedure.  Defer temporarily, I will work out a few more things on
    0087940201 first.

    Remark: epchain doc claims that its runbackground=Y mode is able to create
    background spectrum for LW imaging mode.  But, looking at XMM-Newton sky
    FOV in DS9, this seems impossible...

3. explore effects of changing a few epchain parameters
    epreject, epnoise
    (epreject -- changing sigma?)
    (epnoise -- ??)
4. explore effect of removing point sources w/ automated algorithm
5. check what/where filter flags are applied, and add comments to scripts.
   (flag and pattern rejections)
   see if we need to evselect anywhere to remove these bad events.
6. double check plots of histogram filtering, see if 2nd round is needed.
7. add mosaicking step.
8. is it necessary to run filtering step 2x?
   re-run espfilt, see what happens.


0087940201: no offset maps to use with epreject
0551000201: epreject run, I can't tell whether good or not.  The number of
events down-shifted at 5 sigma is surprisingly large.  And the map of adu=20
events seems to cover the entire CCD.

I compare the histograms from running epchain with and without epreject (in
both cases, without filtering events < 0.150 keV).

Use fv to generate two histograms of PHA, bin size 4 (channel range 0-4095),
and export to plaintext as CSV.  Manually edit file to remove quotation marks;
in Vim, `:%s/"//g` will do.

    cd ${XMM_PATH}/xmm/0551000201/odf/repro_epreject/
    epchain runepreject=Y sigma=5 screenlowthresh=0 keepintermediate=all
    fv P0551000201PNS003PIEVLI0000.FIT
    cd ../../repro
    epchain screenlowthresh=0 keepintermediate=all
    fv P0551000201PNS003PIEVLI0000.FIT

Inspected further by generating histograms from FITS files in Python.

Diverted for part of afternoon to clean up some public doc on flags + epreject,
XMM data reduction.  Maybe this will clarify things.

    ocf.io/atran/useful_xmm.html

Try looking in a specific energy (PI) band vs. just PHA-selected image, per
SAS User Guide 4.3.2.1.1 example.  Note that PHA>=20 should not have any
effect.

    # in odf/repro_epreject/
    evselect table=P0551000201PNS003PIEVLI0000.FIT \
            filteredset=P0551000201PNS003PIEVLI0000_PI_120_200.fits \
            expression='(PHA>=20)&&(PI>=120)&&(PI<200)'
        evselect:- selected 968705 rows from the input table.
    # in odf/repro/
    evselect table=P0551000201PNS003PIEVLI0000.FIT \
            filteredset=P0551000201PNS003PIEVLI0000_PI_120_200.fits \
            expression='(PHA>=20)&&(PI>=120)&&(PI<200)'
        evselect:- selected 1013560 rows from the input table.

This is actually great -- the noise reduction pops out to the eyes,
I've saved the image to `img-notes/20151208_epreject_0551000201_soft.png`.

One mistake, my Python histograms were generated with OOT file vs. regular event
files, no wonder... massive difference mostly accounted for by discrepancy at
lowest energies, interestingly.

After epchain, run with epreject ends up throwing away ~2 million rows
I don't know how many of those rows are really good, though. I'll re-run things
and find out.

I throw out ALL the processed data for 0551000201, and start over again.
Accidentally threw out CIF file and ODF summary.
Re-building now, then going to set up chainfilter runs at home.

    atran(sas)@cooper:~/rsch/g309/xmm$ nohup /bin/tcsh -c \
        'source sasinit 0551000201; chainfilter_0551000201;' \
        >& 20151208_nohup_chainfilter_0551000201.log &
    [1] 30394

Next call is:

    atran(sas)@cooper:~/rsch/g309/xmm$ nohup /bin/tcsh -c \
        'source sasinit 0551000201; chainfilter_0551000201_no-epreject;' \
        >& 20151209_nohup_chainfilter_0551000201_no-epreject.log &
    [1] 25946


Wednesday 2015 December 9 -- epreject results
=============================================

## epreject results and diffing

Compared and subtracted very soft X-ray images to see results of epreject.

    farith '0551000201/odf/repro_no-epreject/pnS003-ori_vsoft-img.fits' \
        '0551000201/odf/repro/pnS003-ori_vsoft-img.fits' 'asdf.fits' SUB

Printed and annotated image (hints: use diverging color map `h5_dkbluered`and
set symmetric limits about the Gaussian-ish distribution centered on 0).

I observe a fair amount of noise subtraction (positive delta, red spots),
especially on "left" CCDs (2, 3, 11, 12).  There is one REALLY bright spot on
CCD 10, where epreject results in net addition of +200 counts.
On some modified columns, a lot of shifting (alternating add/substract)
(look like they could be readout streaks, but are not)

Yes, epreject removes some noise in very soft images (0.12 to 0.20 keV), when
comparing the two images side-by-side.  So that looks promising.

Now, I also compare 0.5-2 keV images and do a subtraction.

    # Run 1x in each directory, repro/ and repro_no-epreject/
    evselect table=pnS003-ori.fits filteredset=pnS003-ori_0.5_to_2_kev.fits expression='(PI>=500)&&(PI<2000)' -V 0
    evselect table='pnS003-ori_0.5_to_2_kev.fits' withimageset=true \
        imageset='pnS003-ori_0.5_to_2_kev_img.fits' xcolumn=DETX ycolumn=DETY \
        imagebinning=binSize ximagebinsize=50 yimagebinsize=50

    farith \
        '0551000201/odf/repro_no-epreject/pnS003-ori_0.5_to_2_kev_img.fits' \
        '0551000201/odf/repro/pnS003-ori_0.5_to_2_kev_img.fits' \
        'epreject_diff_0.5_to_2_kev_img.fits' SUB

The characteristics are completely different.  Here, image is almost all faint
noise (within +/- 15).
* At bright star HD119682, there is a smattering of signal in subtracted image;
  when smoothed, there is bipolar structure to the delta counts (+/- 12 ish).
  I don't know why.  Likely not physical because it is confined to the center
  of the star, and doesn't extend through the PSF.
* One very bright streak along right (+DETX) edge of CCD11, increasing in
  intensity down towards readout.  Strongly negative delta means that
  epreject correction ADDED a lot of counts to this CCD edge, peaking around
  +100 or so (doubling strength of this signal).  This is really weird.

In both image subtractions, noise disappears as I increase smoothing in ds9,
indicating that some signal is likely random (e.g., due to uneven binning, true
signal scatter, etc.).  This is especially dramatic in the 0.5-2 keV image,
indicating that epreject had no effect for almost all of the image.


Verdict:
--> epreject: OK.  Keep an eye on instrumental noise / bright
column streaks etc as usual.
--> epnoise: "The purpose of this subtask is to suppress the detector noise at
    energies below ~250 eV and should be used for qualitative imaging purposes
    only."
    Yeah, we can skip this.

## Point source detection and removal

Note there are at least two tools in SAS: `edetect_chain` and `cheese`.  I
don't know the difference between them, so will stick to cheese just to be
consistent in ESAS framework...

First testing with ESAS cheese call on `0551000201/odf/repro` (this has had
epreject run already).

    cheese prefixm="1S001 2S002" prefixp="S003" scale=0.25 rate=1.0 dist=40.0 clobber=0 elow=400 ehigh=7200

It seems like the algorithm works well outside the SNR, but inside it snags on
spurious features.  Let's try two further calls with stricter thresholds:
rate=2, dist=40.

    nohup /bin/tcsh -c 'source sasinit 0551000201; cd 0551000201/odf/repro; cheese prefixm="1S001 2S002" prefixp="S003" scale=0.25 rate=2.0 dist=60.0 clobber=1 elow=400 ehigh=7200'
        >& 20151209_nohup_cheese_0551000201_rate_2_dist_60.log &

        # Ran at 19:50p ish? on statler
        # Forgot to run in background with & at end.

    nohup /bin/tcsh -c 'source sasinit 0087940201; cd 0087940201/odf/repro; cheese prefixm="1S001 2S002" prefixp="S003" scale=0.25 rate=2.0 dist=60.0 clobber=1 elow=400 ehigh=7200'
        >& 20151209_nohup_cheese_0087940201_rate_2_dist_60.log &

        # Ran at 19:54p
        atran@cooper:~/rsch/g309/xmm$ nohup /bin/tcsh -c '...' >& ... &
        [1] 28827

After the fact, I moved `command.csh` files to `cheese_command.csh`


Thursday 2015 December 10 -- iterate on point source removal (cheese)
=====================================================================

## Look at cheese from yesterday

How do the cheese masks look? (scale=0.25, rate=2, dist=60)
Easy way to check -- set up 6 tiled images in DS9 and link frames.

* 0087940201 -- looks good, I think that all sources are real.  PNS003 in
  particular brings out some sources that are more questionable in MOS images.
  But, the bright star HD 119682 is NOT masked.

* 0551000201 -- also looks good.  Two stars that are masked successfully here
  are NOT not masked in 0087940201 (near CCD edges, and off PN entirely in one
  case). Again, the bright star HD 119682 is NOT masked.

It would be nice to use both obsids for source detection.  I could homebrew it
by correcting for exposure and merging, then running wavdetect or similar.  I
don't know what cheese is doing.

Saved DS9 session screenshot to `img-notes/20151210_cheese_assess.png`.

## Make more cheese!

Create and run the script `cheese_grater` to figure out best parameters.
Variant cheese files are named by source detection parameters.
All use the default 0.4-7.2 keV energy band (elow=400, ehigh=7200).

NOTE: some time is consumed by computing exposure maps with:

    eexpmap attitudeset=atthk.fits eventset=mos2S002-clean.fits:EVENTS
        expimageset=mos2S002-exp-im.fits imageset=mos2S002-obj-im.fits
        pimax=7200 pimin=400 withdetcoords=no verbosity=1

To save time, set clobber=0.  Clobber allows us to skip evselect, eexpmask, and
emask creation for all exposures (-obj-im.fits, -exp-im.fits, -mask-im.fits).
The source detection/removal parameters (rate, dist, scale) are first used
around line 520 of cheese to call SAS (ESAS?) task "region".

Detection still takes a while, calls to eboxdetect and esplinemap necessary.

## Histogram (flare filtering checks)

When I try to investigate SWPC emission, filtering may mess up the distribution
of time / spectra somewhat.  Just be aware of this later.

### 0087940201 soft flare filtering

Inspect `*-hist.qdp` files from {mos,pn}-filter.  I'm satisfied with the
filtering, but would make one more edit to cut out events near the start of the
observation (also simplifies the GTIs).
No need to adjust the Gaussian cut.

* MOS1S001: looks OK. I might tighten upper count rate bound to 2.2 cts/sec (fitted
  Gaussian width), but would make little difference based on lightcurve.
  In lightcurve, I would just cut all data from first 10ks of observation;
  a smattering of points are selected, but surrounded by noise.

* MOS2S002: looks OK. Same comments as MOS1S001, basically.

* PNS003: looks OK. I might tighten upper count rate bound to 5.8 cts/sec
  (fitted Gaussian width) vs. ~6.2 cts/s, noise tail more pronounced than in
  MOS plots.  Again, adjustment would make little difference.

  Cut from 0 to 6000 seconds looks good.
  Time from start of observation disagrees with MOS lightcurve, I suspect that
  PN started taking data after MOS, maybe due to a radzone or something.

I'm unsure of the point of the OOT histogram, it looks the same as the
regular PNS003 data (as expected, since they should be the same data...).

In fact, it may be better to have more residual counts, because background
fitting for soft proton power law might be more robust.  I'm not really sure if
we want to go that route though...

### 0551000201 soft flare filtering

Brief noise at very start of observation (0-2ks), decent-ish data in first 20ks
of observation.  Increased noise 20-30ks, some ok data 30-35 ks.  After ~38ks,
flaring increases dramatically and is obviously unusable.
There will definitely be residual contamination.

* MOS1S001: looks ok.  I would tighten upper count rate bound to 1.4 cts/sec
  (vs. 1.7 cts/sec), about 20% correction.
  Cut small bits of data between 19-32ks (from start of MOS time).

* MOS2S002: same deal as MOS1.  Interestingly, lightcurve and count rate
  histogram look subtly better than MOS1, I dunno why.
  Here I'd tighten upper count rate bound to 1.5 cts/sec (from ~1.7 cts/sec)

* PNS003: wow PN looks bad.  Early observation is ok, but after ~20ks the
  flaring is just way too strong.
  Here, I might cut upper count rate bound to 3.3 cts/sec, well below current
  cut at 3.9 cts/sec.
  Similar ratio as my suggested MOS cuts though.
  But that will reduce our already sparse counts further.


Friday 2015 December 11 -- inspect point source removal tests
=============================================================

## Cheese results inspection

NOTE: I have been looking exclusively at 0087940201 masks, to save time.

ESAS Cookbook defaults (already done)
scale=0.25 rate=1 dist=40

    Successfully removes bright star HD119682, but it looks like there's a
    number of false positives.  Holes are pretty big.
    Lots of speckle holes (a few pixels apiece) on MOS2.
    REJECT.

Increase dist alone from default
scale=0.25 rate=1 dist=60

    Mostly the same.  Does NOT remove bright star HD119682.
    More speckle, for some reason.
    Maybe two putative stars, other than the really bright one, are not masked
    as compared to default.
    REJECT.

Increase rate alone from default
scale=0.25 rate=2 dist=40

    Better, much more conservative.
    Holes are same size as default.
    DOES get bright star HD119682.
    This one looks almost optimal, but compare to scale=0.25/rate=2/dist=60 too

Decrease scale from default
scale=0.1 rate=1.0 dist=40.0 clobber=0 elow=400 ehigh=7200

    Exactly as you'd expect, bigger holes...
    REJECT.

Increase scale from default
scale=0.5 rate=1.0 dist=40.0 clobber=0 elow=400 ehigh=7200

    Holes shrink.  Actually, the holes still look pretty good to me,
    but the difference is pretty marginal.
    Looking at DS9 projection of bright star, the cheese mask still looks
    reasonably conservative.
    I would be ok with adopting these smaller holes.

Increase rate and dist from default (already done)
scale=0.25 rate=2 dist=60

    See notes above (Thurs Dec 10)

Increase rate alone, further, from default
scale=0.25 rate=4 dist=40

    As expected. Only some 4-5 stars are masked (includes bright star).
    About two objects that look like stars are not masked.
    A little too conservative, but OK.

Verdict: scale=0.5, rate=2.0, dist=40 seems like a good set of parameters.
scale=0.5 rate=2 dist=40

    I inspect images for both 0087940201 and 0551000201
    0087940201 -- broadly, looks good.  basically same as
      scale=0.25,rate=2,dist=60 assessment from yesterday.
    0551000201 -- the holes are bigger.
      Again, looks like assessment from yesterday, which was positive.
      There's one object being masked in top right
      (RA 13:44:51.036, dec -62:48:46.53) that I'm not sure actually is a point
      source, at least it's not obvious in image.
      But it's completely irrelevant to our work, so I'll leave it in.

I think this is done, I've settled on a set of parameters with which I'm
satisfied.  Very unscientific, but I hope it's OK.


## Next steps

RA/dec for point sources are available in emllist.fits, output by cheese.  Use
this to create simple region masks for any figures necessary.

cheese also outputs emllistout.fits -- this is the original output from
emldetect.  cheese runs task fill_list to fill in null values for something?
so emllist.fits is the correct output file to inspect...
It could be worth inspecting outputs from SAS eboxdetect boxlist.fits and
boxlist-f.fits, but... eh...



Thursday 2015 December 17 -- manual GTI filtering
=================================================

Diverted by planning for JAN1116 load.  Back to work on this.

GTI filtering, following assessment from last Thurs (Dec 10).  I defer from
count rate filtering; just apply some obvious time interval cuts.
- based on lightcurve, not obvious that further count rate filtering has
  obvious effects
- lose more photons, which may be meaningful esp. at high energy
- somewhat tricky to reproduce. we'd have to create binned light curve files
  from evselect, then use tabgtigen to make new GTIs.
  Not hard, but figuring out the lightcurves generated by espfilt is a bit of
  trouble.
- more eyeballing.
- may be helpful to have residual photons since we are subtracting or fitting
  background anyways.

For all these, I take the start times to be TSTART in the FITS headers of
mos1S001-ori.fits, mos2S002-ori.fits, pnS003-ori.fits

From XMM-SAS selectlib doc page (and corroborated by hand):
> In an arithmetic context all given times evaluate to the number of elapsed
> seconds since the fixed time 1998-01-01T00:00:00 TT.

## 0087940201 GTIs

* 0087940201 MOS1S001 -- cut all intervals before 10000 sec
    = 1.15354430246723E+08 + 10,000 sec
    --> Cut times before 115,364,430 sec
* 0087940201 MOS2S002 -- same as for MOS1
    = 1.15354431376978E+08 + 10,000 sec
    MOS2 first frame ~1.1 sec. after MOS1, according to TSTART.
    --> Cut times before 115,364,431 sec
* 0087940201 PNS003 -- cut all intervals before 6000 sec
    = 1.15358540104471E+08 + 6,000 sec
    PN first frame ~ 4.11ks after MOS1/MOS2 started, per TSTART
    --> Cut times before 115,364,540 sec

For 0087940201, filter event lists to use ONLY events after 115,364,540 sec;
simply taking the maximum of the cut time estimates.

## 0551000201 GTIs

* 0551000201 MOS1S001 -- cut between 19-32ks of MOS time.
* 0551000201 MOS2S002 -- cut between 19.5-32ks of MOS time.
* 0551000201 PNS003 -- cut everything after 30ks.  There's a snippet of signal,
  but surrounded by flaring noise.

    atran(sas)@treble$ fkeypar mos1S001-ori.fits TSTART ; pget fkeypar value
    3.52724237093625E+08
    atran(sas)@treble$ fkeypar mos2S002-ori.fits TSTART ; pget fkeypar value
    3.52724235780930E+08
    atran(sas)@treble$ fkeypar pnS003-ori.fits TSTART ; pget fkeypar value
    3.52725946564511E+08

Let's adopt: MOS, cut 19.5-32ks; PN cut >30ks
    MOS1 TSTART = 352,724,237 seconds; cut between 352,743,736 and 352,756,237 sec.
    MOS2 TSTART = 352,724,236 seconds; as above
    PN TSTART = 352,725,947 seconds; cut all after 352,755,947 sec.

## Implementation

NASA's XMM GOF "ABC guide" describes a few implementations:
    http://heasarc.gsfc.nasa.gov/docs/xmm/abc/node8.html#SECTION00850000000000000000

I move some files around and run evselect to apply filters
(long diversion finagling with details of evselect parameters, and determining
why withfilteredset is not a documented parameter...)

Run evselect to generate NEW light curves for comparison.  A few points don't
quite agree; from looking at plot, this appears to occur at edge of GTIs
(though I didn't formally verify this).  If I change binning (timebinsize) to 1
second, this problem seems to go away.

In this process, I turned up an error in my notes.  Both PN and MOS exposures
are filtered with flag 0x766a0f63, for both 0551000201 AND 0087940201.
Steve Snowden uses 0x766a0763 for unfiltered detector images for REVL > 2383,
for both MOS and PN; but, espfilt has already filtered on 0x766a0f63 to create
the cleaned events file.

Anyways, I made the new light curves.  Maybe the GTIs can be adjusted, in
particular for the latter half of 0551000201 (where I accept about 8ks of MOS
time, but reject all the PN time).

But for now it seems OK.

Quick check on exposure times:
0087940201 mos2S002-clean.fits ONTIME = 25.891 ks, LIVETIME = 25.621 ks (central CCD)
0087940201 mos2S002-clean-ori.fits ONTIME = 28.440 ks, LIVETIME = 28.119 ks (central CCD)
    OK, as expected, a fair bit of time was trimmed; lost ~3ks (10%).


Rerunning pipeline:

    atran(sas)@statler:/data/mpofls/atran/research/g309/xmm$ nohup /bin/tcsh -c 'source sasinit 0087940201; minchainfilt_0087940201;' >& 20151218_nohup_minchainfilt_0087940201 &
    [1] 18552

    atran(sas)@cooper:/data/mpofls/atran/research/g309/xmm$ nohup /bin/tcsh -c 'source sasinit 0551000201; minchainfilt_0551000201;' >& 20151218_nohup_minchainfilt_0551000201 &
    [1] 17150

Friday 2015 December 18 -- continued pipeline fixes
===================================================

Errored out because I made some mistakes in string quotation.
Fixed and started re-running again around 10:20am.

    atran@statler$ nohup /bin/tcsh -c 'source sasinit 0087940201; minchainfilt_0087940201;' >& 20151218_nohup_minchainfilt_0087940201 &
    [1] 15222

    atran@cooper$ nohup /bin/tcsh -c 'source sasinit 0551000201; minchainfilt_0551000201;' >& 20151218_nohup_minchainfilt_0551000201 &
    [1] 15316

OK, I think it worked successfully.

Realized that my final filtering was removing corner pixels; added corners back
in to event lists for spectrum extraction.

    atran@cooper:~/rsch/g309/xmm$ nohup /bin/tcsh -c 'source sasinit 0087940201; minchainfilt_0087940201;' >& 20151218_nohup_minchainfilt_0087940201 &
    [1] 15485

    atran@statler:~/rsch/g309/xmm$ nohup /bin/tcsh -c 'source sasinit 0551000201; minchainfilt_0551000201;' >& 20151218_nohup_minchainfilt_0551000201 &
    [1] 12128

Current list of pending procedure changes (copied from Mon 2015 Dec 7):
2. fix PN spectrum extraction for 0551000201
    -- in works, deciding how to work without QPB, we'd need different
    procedure.  Defer temporarily, I will work out a few more things on
    0087940201 first.

    Remark: epchain doc claims that its runbackground=Y mode is able to create
    background spectrum for LW imaging mode.  But, looking at XMM-Newton sky
    FOV in DS9, this seems impossible...


Monday 2015 December 21 -- spectrum extraction pipeline
=======================================================

We have a few different steps.
Let's start with the easiest, which is to just pull out spectra from
source/background regions and do a simplistic subtraction.

I prepare some event lists without corner events for manual extraction.

    atran(sas)@treble$ evselect table=mos1S001-clean2.fits filteredset=mos1S001-clean-fov.fits expression="(PATTERN<=12)&&(#XMMEA_EM)" updateexposure=no filterexposure=no keepfilteroutput=yes withfilteredset=yes filtertype=expression
        evselect:- selected 90778 rows from the input table.
    atran(sas)@treble$ evselect table=mos2S002-clean2.fits filteredset=mos2S002-clean-fov.fits expression="(PATTERN<=12)&&(#XMMEA_EM)" updateexposure=no filterexposure=no keepfilteroutput=yes withfilteredset=yes filtertype=expression
        evselect:- selected 95265 rows from the input table.
    atran(sas)@treble$ evselect table=pnS003-clean2.fits filteredset=pnS003-clean-fov.fits expression="(PATTERN<=4)&&(FLAG==0)" updateexposure=no filterexposure=no keepfilteroutput=yes withfilteredset=yes filtertype=expression
        evselect:- selected 264393 rows from the input table.
    atran(sas)@treble$ cd ../../../0551000201/odf/repro
    atran(sas)@treble$ source ../../../sasinit 0551000201
        XMM SAS ready for 0551000201
    atran(sas)@treble$ evselect table=mos1S001-clean2.fits filteredset=mos1S001-clean-fov.fits expression="(PATTERN<=12)&&(#XMMEA_EM)" updateexposure=no filterexposure=no keepfilteroutput=yes withfilteredset=yes filtertype=expression
        evselect:- selected 63365 rows from the input table.
    atran(sas)@treble$ evselect table=mos2S002-clean2.fits filteredset=mos2S002-clean-fov.fits expression="(PATTERN<=12)&&(#XMMEA_EM)" updateexposure=no filterexposure=no keepfilteroutput=yes withfilteredset=yes filtertype=expression
        evselect:- selected 74420 rows from the input table.
    atran(sas)@treble$ evselect table=pnS003-clean2.fits filteredset=pnS003-clean-fov.fits expression="(PATTERN<=4)&&(FLAG==0)" updateexposure=no filterexposure=no keepfilteroutput=yes withfilteredset=yes filtertype=expression
        evselect:- selected 71843 rows from the input table.
    atran(sas)@treble$

Woops, actually, that wasn't really necessary.  Oh well.

Return modified version of ESAS `pn-spectra` to usage, just for sheer
convenience in extracting the object and background spectra; restores file
added in commit `e7c4cfb1b5aef5c0749ab1c64b1919b49b32c937`.

I use OOT event ratio 0.0016 for PrimeLargeWindow mode, and add elsif
statements to that block to make life easier (see my notes from earlier in Dec
2015 regarding spectrum extraction for Large Window mode observations; see this link too:
http://xmm.esac.esa.int/external/xmm_user_support/documentation/uhb/epicoot.html
Otherwise, identical to SAS 2014 version of pn-spectra.

    atran@treble:/data/mpofls/atran/research/g309/xmm/0087940201/odf/repro$ cp *grp50.pi spec_backup/.
    atran@treble:/data/mpofls/atran/research/g309/xmm/0087940201/odf/repro$ cp *src* spec_backup/.
    atran@treble:/data/mpofls/atran/research/g309/xmm/0087940201/odf/repro$ cp *bkg* spec_backup/.

    atran(sas)@cooper:~/rsch/g309/xmm$ nohup /bin/tcsh -c 'source sasinit 0551000201; specbackgrp_0551000201 src; specbackgrp_0551000201 bkg' > & 20151221_nohup_specbackgrp_0551000201.log &
    [1] 10674

    atran(sas)@statler:~/rsch/g309/xmm$ nohup /bin/tcsh -c 'source sasinit 0087940201; specbackgrp_0087940201 src; specbackgrp_0087940201 bkg' >& 20151221_nohup_specbackgrp_0087940201.log &
    [1] 28792

NOTE this failed on 0551000201 src at a call to:
    backscale spectrumset=mos1S001-7ff.pi badpixlocation=mos1S001-clean.fits withbadpixcorr=yes
but worked fine on bkg.  Not sure why.  Re-running mos-spectra with identical
(old) parameters worked fine.  Very odd.

Re-run the pipeline with using (1) new cheese masks, (2) new source/bkg
regions.  Notably, both bkg and src regions are a bit larger (esp. for
0551000201) so we should have somewhat better statistics.

    atran@cooper:/data/mpofls/atran/research/g309/xmm$ nohup /bin/tcsh -c 'source sasinit 0551000201; specbackgrp_0551000201 src; specbackgrp_0551000201 bkg' > & 20151221_nohup_specbackgrp_0551000201.log &
    [1] 7895
    atran@statler:/data/mpofls/atran/research/g309/xmm$ nohup /bin/tcsh -c 'source sasinit 0087940201; specbackgrp_0087940201 src; specbackgrp_0087940201 bkg' > & 20151221_nohup_specbackgrp_0087940201.log &
    [1] 29343

As part of this process, I also fixed a bug in `reg2xmmdet.pl` where regions
outside detector FOV would cause error and return invalid regions.
I confirm that I don't get that weird failure for call to mos-spectra on obsid
0551000201 with exposure mos1S001 and src region, so everything looks good.

It's possible that I forgot to kill some child processes, earlier.
My current procedure is just to inspect output of `ps aux` if I'm killing and
restarting these nohup calls.

morning: looks ok, runs completed successfully.  No obvious errors yet (haven't
inspected all log files), some warnings that should be double checked.  From
first glance they look benign (datasubspace too complex for background region,
etc...)


Tuesday 2015 December 22
========================

A few remarks on spectrum extraction runs:
* Log messages "Spectrum file already exists" are OK.  These only occur for
  files that aren't affected by user input (observation corner data, FWC corner
  data, attitude file atthk.fits,

  I'm worried that quadrant/chip observation files, which I am not destroying
  or updating, are getting re-used without my knowledge, which would result in
  subtly incorrect data...
  Answer: quadrant/chip data are OK, not being reused.
  I am renaming `pnS003-obj.{pi,arf,rmf}` files, so they are not being reused.
  So all is good.
  Scanning mos-spectra code I see the same behavior.  So, data are a-OK.

  Modified pn-spectra-mod to output slightly more helpful logging messages
  (notify me precisely which files are being re-used).
  Create mos-spectra-mod to, again, output slightly more helpful logging
  messages.  Otherwise identical to original ESAS version.

  AHA.  0551000201, mos-spectra for exposures 1S001 and 2S002 needs to be re-run.
  The files mos1S001-obj.pi, mos1S001-obj.rmf, mos1S001-obj.arf were NOT moved
  prior to my script run, therefore they didn't get overwritten...
  Same for 0087940201... argh `-_-`.

  Check the files for:

    corner event file already exists: mos1S001-corn.fits
    image file already exists: mos1S001-obj-im.fits
    image file already exists: mos1S001-obj-im-sp-det.fits
    attitude file already exists
    exposure image file already exists: mos1S001-exp-im.fits
    spectrum file already exists: mos1S001-obj.pi
    rmf file already exists: mos1S001.rmf
    arf file already exists: mos1S001.arf

  and see if they need to be re-run.
  * -obj.pi, .rmf, .arf must to be recomputed
  * attitude file atthk.fits is fine
  * -exp-im.fits is fine, no region selection
  * -im-sp-det is NOT fine, needs to be regenerated -- depends on region
  * -obj-im is fine, but risk that you need to regenerate if you change the ccd
     selection...
  * -corn same problem, if you change CCD selection you may need to re-compute
    this

  Visually confirm this in ds9 tomorrow
  I think best to set clobber parameter to 1...
  note that -corn.fits file is NOT subject to clobber parameter.

* Data Subspace issue.

    From: http://xmm.esac.esa.int/sas/current/doc/arfgen/node16.html
    "arfgen extracts spatial information from the Data Sub-Space (DSS) stored in the
    spectral dataset"

  OK, need to re-run this.  I'm just going to select an annulus region for
  background now, and modify my scripts to make it work.

Sat down today and hashed out a lot more details about ARF/RMF computation and
background subtraction.  I might have gone over some before, but still hadn't
completely ingrained (e.g., why we need to compute ARF using an image map taken
to represent the true source distribution -- neglecting PSF effects even, which
I'm not thinking about now).

Wondering whether the simple first order correction of ratio of effective
areas, integrated over energy, should be made when doing a basic (XSPEC/Sherpa
style) background subtraction...
Of course this is irrelevant for QPB, which is indeed a straight subtraction,
and the "generating spectrum" is not completely understood nor can it be
modeled as a source spectrum, since it's tied to detector electronics etc.  In
practice it will obey different RMFs/ARFs than for x-ray photons.


Wednesday 2015 December 23
==========================

Today I addressed the following issues:
* overly complex data subspace expression breaks BACKSCAL calculation
  - make new background region for this
* more aggressive pt source masking to improve new larger regions
* inconsistent file clobbering leads to incorrect spectra, (1) incorrect object
  spectra when files aren't moved after manual run of {mos,pn}-spectra, and (2)
  incorrect QPB caused by non-clobbering of corner file, so that -4oc.pi
  includes MOS1 CCD4 noise that should have been removed
* confirmed that using clobber parameter with mos-spectra is safe
* fixed clobber behavior for pn-spectra to my liking
* restored missing pnS003-clean-oot.fits file (bug in chainfilter scripts)

## New background regions

Created new background region (annulus), r1 = 510" and r2 = 700".
Adjusted source region; circle with r = 400".
Both have same center: ra 13:46:35.381, dec -62:54:01.44,510.
Ratio of areas is 229900 / 160000 ~ 1.44.  Conveniently, background annulus is
entirely within 2x the source region radius.

Source region is large (r = 6.67 arcmin); it encloses main shell of MOST radio
contours.

Modified region conversion (ds9->xmm) code to parse annuli.  Tested resulting
expressions with evselect by hand and it looks good.


## Change pt source masking

Use merged PPS image to assess pt source masking (change `cheese_smell`).
Use more aggressive source masking, so we can use the larger regions safely.
With current (scale=0.5, rate=2, dist=40) mask, I'm missing a few (1-2ish)
point sources in the new regions.  Not a big difference, but I think it helps,
and I erred in not looking at merged images before.

For both 0087940201 and 0551000201, return to masks with default parameters:
scale=0.25, rate=1, dist=40.  On the merged PPS image with much better SNR, it
becomes apparent that most sources are real.
Unfortunately, mask for 0551000201 also removes a few small pt-like sources in
the SNR; I'm not sure if these are real pt sources or not.

For now, accept the loss of some data and slightly inconsistent masking.
A todo is to improve this masking slightly.  Only marginal improvement
expected.


## More spectrum extraction pipeline fixes -- clobbering behavior

Modified `mos-spectra-mod` to clobber old files.

This might not be safe, since clobber parameter is not officially documented.
The code triggered by clobber=1 could be out of date or wrong.  I walk through
the script briefly and check by eye that clobber commands are identical to
commands without clobber.  Not a guarantee but at least a cursory check.

* [OK] -obj-im.fits
* [OK] -obj-im-sp-det.fits
* [OK] -exp-im-det.fits
* [OK] -obj-im-det-$elow-$ehigh.fits
* [OK] -exp-im.fits

Also add clobber=1 to `mos_back` and `pn_back` calls.  Again, I don't know what
clobber does here -- `mos_back_mod.f90` is not as easy to decipher.  But I
think this is safe, it's semi-documented, and it's a simple parameter...

## Apparent error in mos-spectra clobbering behavior, tied to cflim usage

### Reading of situation

-corn file isn't be overwritten by default.  Scripts {mos,pn}-filter don't
apply CCD cuts when creating -corn, but {mos,pn}-spectra do.  Is this OK for
our spectrum extraction and QPB calculation?  We use -corn file to:
* extract -oc.pi spectra.
* compute hardness ratios
If corn.fits file does not have MOS1 CCD4 cut applied, the extracted -4oc.pi
spectrum will still include enhanced edge counts that should have been cut.

This is a dangerous error!  What happens, a little closer to code:
1. cflim cut is applied to ccddef for MOS1.
2. If corner file doesn't already exist, generate corner event list
   with user-selected CCDs and cflim cut
3. use -corn.fits file to extract -oc.pi spectra for all CCDs.

I see two issues
1. the corner file MUST be re-generated here, at least to incorporate the
   cflim cut.
2. if we change the CCD definitions or cflim, it often happens that files are
   NOT clobbered.  This risks leaving the user with old files that DON'T
   reflect the selected excisions.
   For CCD omissions, this is fine; we don't care about that CCD anyways.
   (I havent checked that all-detector images/etc are OK)

   For cflim, we must update the files.
   If we changed our mind and re-included a CCD, this would also be a problem.

3. I rely on renaming files to regenerate spectra, and non-clobbering behavior
   works fine.  But this is not always a safe assumption when I'm running the
   script by hand, quickly.

I confirmed this by looking at select expression in FITS header for
mos1S001-4oc.pi, running a select on PI=[200:900] and the selected CCD box on
mos1S001-corn.fits, and inspecting the resulting image.  Very obvious band of
bright emission at CCD4 edge, that would not have been removed from corner
spectrum.

This is not a concern for PN because I'm not omitting quadrants, and there is
no manual excision of CCD regions here.  But, it could become an issue if PN
ever sustains damage to one CCD or a subpart of a CCD.

### Take evasive action (mos-spectra)

__Change script to clobber:__
* -corn.pi
* -obj.pi
* .rmf
* .arf
* -[1-7]oc.pi
Because these need to be recomputed if CCD selections change, if cflim
changes, if cheese masks change, etc.
If I only change regions (and rename -obj.pi, .rmf, .arf in between calls),
these files wouldn't need to be clobbered (cflim bug aside)

__Files that are NOT clobbered:__
* atthk.fits is always the same
* -[1-7]fc.pi will not change unless CALDB is updated
does NOT include cflim cut, this is OK

__Files already always clobbered (region-dependent):__
* -[1-7]ff.pi  <- includes ccddef and cflim cut correctly
* -[1-7]obj.pi <- includes ccddef and cflim cut correctly

__Files clobbered by clobber=1 parameter listed above and already addressed__

Because I clobber -corn.pi and regenerate the file with user-specified ccddef,
we won't be able to compute the hardness ratio for omitted chips.  I think
that's OK, as long as either:
1. user runs mos-spectra first with all CCDs enabled
2. mos-filter suffices to identify anomalous state chips

Other possible issue, we could hit divide by zero errors.
Eh.
Run and fix if needed.

### (pn-spectra) stick close to holding sector MV-7

__Files that are NOT clobbered:__
* atthk.fits            <- ok, this never changes
* -corn.pi
* -corn-oot.pi
* -obj-im.fits
* -exp-im.fits (and -mask-im.fits)
* -obj-im-oot.fits
* -obj-im-sp-det.fits
* -obj-im-det-$elow-$ehigh.fits
* -obj-im-det-$elow-$ehigh-oot.fits
* -obj.pi
* -obj-oot.pi
* .rmf
* .arf
* -[1-4]oc.pi
* -[1-4]oc-oot.pi
* -[1-4]fc.pi           <- ok, this doesn't change unless CALDB is updated
* -[1-4]fc-oot.pi       <- ok, this doesn't change unless CALDB is updated

__Files that are always clobbered (region-dependent):__
* -[1-4]obj.pi
* -[1-4]obj-oot.pi
* -[1-4]ff.pi

changed all 14 checks to clobber the files.

I go ahead and clobber the rest of them to be totally safe...
changes to GTI, masks, etc would necessitate updates

Concern: -corn file created by pn-filter does NOT use the same (more
conservative) flags as used by pn-spectra.  This is OK because pn-filter does
NOT create corner lists/images anymore; the code has been disabled internally
(via hardcoded cornproc parameter, same as commenting out).


## Restore missing pnS003-clean-oot.fits (cause of errors in pn-spectra runs)

Error in pn-spectra call -- could not find pnS003-clean-oot.fits.  What
happened?!  Related to my ad hoc modifications.
I had moved the -oot file, but not applied the new GTI filtering and replaced
it.  Fixed in chainfilter scripts.


## Change final manual filtering step

{mos,pn}-spectra already apply correct flags when making object spectra.
I quickly check (see output below) that corner spectra are OK even if we don't
apply strictest filtering.

So I change this behavior and remove it from the (direct) pipeline.
This is more consistent with nominal ESAS run.


First just get corner counts, no filtering beyond mos-filter selections:

    atran(sas)@treble:/data/mpofls/atran/research/g309/xmm/0087940201/odf/repro$ evselect table=mos1S001-clean2.fits filteredset=asdf.fits expression='!(CIRCLE(100,-200,17700,DETX,DETY)||CIRCLE(834,135,17100,DETX,DETY)||CIRCLE(770,-803,17100,DETX,DETY)||BOX(-20,-17000,6500,500,0,DETX,DETY)||BOX(5880,-20500,7500,1500,10,DETX,DETY)||BOX(-5920,-20500,7500,1500,350,DETX,DETY)||BOX(-20,-20000,5500,500,0,DETX,DETY)||BOX(-12900,16000,250,4000,0,DETX,DETY)||BOX(80,18600,150,1300,0,DETX,DETY)||BOX(-10,-18800,125,1500,0,DETX,DETY))'
    ...
    evselect:- evselect (evselect-3.62)  [xmmsas_20141104_1833-14.0.0] started:  2015-12-23T22:42:30.000
    evselect:- selected 5452 rows from the input table.
    evselect:- evselect (evselect-3.62)  [xmmsas_20141104_1833-14.0.0] ended:    2015-12-23T22:42:31.000

Now, get corner counts using mos-{filter,spectra} selections for -corn.fits

    atran(sas)@treble:/data/mpofls/atran/research/g309/xmm/0087940201/odf/repro$ evselect table=mos1S001-clean2.fits filteredset=asdf.fits expression='(PATTERN<=12)&&((FLAG & 0x766a0f63) == 0)&&!(CIRCLE(100,-200,17700,DETX,DETY)||CIRCLE(834,135,17100,DETX,DETY)||CIRCLE(770,-803,17100,DETX,DETY)||BOX(-20,-17000,6500,500,0,DETX,DETY)||BOX(5880,-20500,7500,1500,10,DETX,DETY)||BOX(-5920,-20500,7500,1500,350,DETX,DETY)||BOX(-20,-20000,5500,500,0,DETX,DETY)||BOX(-12900,16000,250,4000,0,DETX,DETY)||BOX(80,18600,150,1300,0,DETX,DETY)||BOX(-10,-18800,125,1500,0,DETX,DETY))'
    ...
    evselect:- evselect (evselect-3.62)  [xmmsas_20141104_1833-14.0.0] started:  2015-12-23T22:43:15.000
    evselect:- selected 5452 rows from the input table.
    evselect:- evselect (evselect-3.62)  [xmmsas_20141104_1833-14.0.0] ended:    2015-12-23T22:43:16.000

Now, get corner counts using manual filters.  First `#XMMEA_EM` or corner:

    atran(sas)@treble:/data/mpofls/atran/research/g309/xmm/0087940201/odf/repro$ evselect table=mos1S001-clean2.fits filteredset=asdf.fits expression='(PATTERN<=12)&&(#XMMEA_EM||(FLAG==0x10000))&&!(CIRCLE(100,-200,17700,DETX,DETY)||CIRCLE(834,135,17100,DETX,DETY)||CIRCLE(770,-803,17100,DETX,DETY)||BOX(-20,-17000,6500,500,0,DETX,DETY)||BOX(5880,-20500,7500,1500,10,DETX,DETY)||BOX(-5920,-20500,7500,1500,350,DETX,DETY)||BOX(-20,-20000,5500,500,0,DETX,DETY)||BOX(-12900,16000,250,4000,0,DETX,DETY)||BOX(80,18600,150,1300,0,DETX,DETY)||BOX(-10,-18800,125,1500,0,DETX,DETY))'
    evselect:- evselect (evselect-3.62)  [xmmsas_20141104_1833-14.0.0] started:  2015-12-23T22:45:42.000
    evselect:- selected 5452 rows from the input table.
    evselect:- evselect (evselect-3.62)  [xmmsas_20141104_1833-14.0.0] ended:    2015-12-23T22:45:42.000

Then `FLAG==0` or corner:

    atran(sas)@treble:/data/mpofls/atran/research/g309/xmm/0087940201/odf/repro$ evselect table=mos1S001-clean2.fits filteredset=asdf.fits expression='(PATTERN<=12)&&((FLAG==0)||(FLAG==0x10000))&&!(CIRCLE(100,-200,17700,DETX,DETY)||CIRCLE(834,135,17100,DETX,DETY)||CIRCLE(770,-803,17100,DETX,DETY)||BOX(-20,-17000,6500,500,0,DETX,DETY)||BOX(5880,-20500,7500,1500,10,DETX,DETY)||BOX(-5920,-20500,7500,1500,350,DETX,DETY)||BOX(-20,-20000,5500,500,0,DETX,DETY)||BOX(-12900,16000,250,4000,0,DETX,DETY)||BOX(80,18600,150,1300,0,DETX,DETY)||BOX(-10,-18800,125,1500,0,DETX,DETY))'
    evselect:- evselect (evselect-3.62)  [xmmsas_20141104_1833-14.0.0] started:  2015-12-23T22:45:59.000
    evselect:- selected 5452 rows from the input table.
    evselect:- evselect (evselect-3.62)  [xmmsas_20141104_1833-14.0.0] ended:    2015-12-23T22:45:59.000

Looks like no difference, so that's good.  Note, this is important to check for
-corn because the -corn event list is fed directly into -[1-7]oc.pi.


## Massive pipeline rerun

Started around 6:07pm Weds Dec 23

    atran@cooper:~/rsch/g309/xmm$ nohup /bin/tcsh -c 'source sasinit 0551000201; chainfilter_0551000201; specbackgrp_0551000201 src; specbackgrp_0551000201 bkg' > & 20151223_pipeline_0551000201.log &
    [1] 2382

    atran@statler:~/rsch/g309/xmm$ nohup /bin/tcsh -c 'source sasinit 0087940201; chainfilter_0087940201; specbackgrp_0087940201 src; specbackgrp_0087940201 bkg' > & 20151223_pipeline_0087940201.log &
    [1] 31415

Thursday 2015 December 24
=========================

## Pipeline re-run and review of errors

Amateur mistake was made.  In pn-spectra-mod, added messages that I was
regenerating files, but forgot to actually remove else {...} blocks.

    atran@cooper:~/rsch/g309/xmm$ nohup /bin/tcsh -c 'source sasinit 0551000201; chainfilter_0551000201; specbackgrp_0551000201 src; specbackgrp_0551000201 bkg' >& 20151224_pipeline_0551000201.log &
    [1] 502

    atran@statler:~/rsch/g309/xmm$ nohup /bin/tcsh -c 'source sasinit 0087940201; chainfilter_0087940201; specbackgrp_0087940201 src; specbackgrp_0087940201 bkg' >& 20151224_pipeline_0087940201.log &
    [1] 28979

Anyways, re-run, it only takes about 1.5 hrs

Checking for errors in logs.  nohup logs (`20151224_pipeline_*`) are OK.
Use the following commands:

    cat *.log | grep -in error > errcheck.log
    (in vim) :g/^\d\+:evselect.*/d

In logs for both obsids:
* epevents errors related to CTI correction are OK
* grppha logs look good.
* Error related to -obj-im.fits regeneration in
  `mos-spectra_{mos1S001,mos2S002}_{src,bkg}.log` files.
  which I believe is caused by an extra parenthesis in the selection
  expression.  This is line 445 of the original mos-spectra script
  (`xmmsas_20141104_1833`); you can contrast to the version for rev>2382, which
  does have the correct parenthesis setup.

  Normally, -obj-im.fits is already created by cheese; mos-spectra would not
  run this command.

  In this case, I won't re-run the pipeline.  It's an error, but doesn't affect
  our work.

In mos-filter log for 0551000201 only: error creating a temp file with command:
    evselect table=mos1S001-corn.fits:EVENTS withfilteredset=yes
        expression='(PATTERN<=12)&&((FLAG & 0x766a0f63)==0)&&(CCDNR==6)&&(PI in [300:10000])'
        ...
MOS1 CCD6 is the (first) missing CCD.  The script tries to get the number of
corner counts (NAXIS2 = number of rows) but fails.  This is OK, and mos-filter
proceeds from the error normally.

## Checking normalization of effective area

The src/bkg arfs for 0087940201 mos1S001 differ by ~1.24x at low energies;
starting from ~5 keV, the ratio increases almost linearly to ~1.7x at 12 keV.

Similar effect for 0551000201 mos2S002, except increasing from ~1.7x to 3.1x
at 12 keV.  Quite a substantial correction is needed.

So this basically captures vignetting at different energies, where vignetting
is worst at around 12 keV (PN shows some of the interesting response to 15 keV)
depending on the region/detector positioning.

Straight subtraction makes the background look dimmer than it really is.
It would be good to apply this correction.

(src - qpb_src) - (bkg - qpb_bkg), then model accordingly.

## Set up script for background subtraction

specmeth, to be renamed.

(edit, jan 7 2016: while setting this up, I was uncertain exactly how to
propagate errors in bkg subtraction -- revisit this)


Tuesday-Wednesday 2016 January 5-6 -- plan corrections, get FWC spectra
=======================================================================

## Address lingering questions about ARF/RMF corrections

* Adding ARF correction (first order effect) before XSPEC bkg subtraction?

  YES, but note that this may further mess up instrumental line subtraction.
  Assuming ARF is flatter for instrumental lines than sky background (due to no
  mirror vignetting), then background instrumental lines will be
  over-estimated.

  Quantify effect of change by generating spectra with/without correction.

  Checked BACKSCAL ratios against manually computed ratios from ESAS cheese
  images, they look ok (ratio is right to ~ a few %; worse if we don't account
  for pt src mask. Trying to reproduce absolute BACKSCAL values by computing
  area in (arcsec^2) from cheese images is worse, off by ~10%. I don't know
  where the discrepancy comes from.

* Adjust ARF/RMF to reflect weighting of (estimated) "true source", rather than
  use weighting based on source + x-ray background + detector background + ...

  DEFER or SKIP.

  Maybe possible, but requires (background, soft proton, SWCX) subtracted
  images to generate a new detector map.

  Only necessary for "straight" background subtraction.  If modeling both
  SNR and background separately, ARF/RMF should be weighted with background.
  (but ideally without QPB).  Background subtraction already implicitly assumes
  uniform RMF/ARF across detector, so we can't remove this systematic error
  entirely.

* Addressing vignetting in instrumental lines?

  YES -- approach as follows:

  1. extract spectra from FWC data -- fit with arf none, since we care only
     about the channel space signal, not how it's produced.
     (alternative: generate custom arf without vignetting/filters.
      ARF's energy dependence subtly alters shape of modeled lines -- most
      important for PN, due to high energy instrumental lines.)
  2. from FWC spectrum fit, compute line ratios + normalizations.  Rescale
     by exposure times.
  3. use ratios/normalizations in instrumental line fits.  Note that QPB +
     lines may differ from (all FWC QPB) + lines, as ESAS extracts QPB spectra
     that are specifically matched to indiv observation.

  If I am NOT using FWC data, and NOT propagating normalizations across
  different fits (background -> source region), no issue.  Free normalizations
  will account for this.

  But, if this works, will help remove 1-2 parameters from fits.
  Could be very useful, esp. in constraining Al/Si lines.

  Low priority: check temporal variations in instrumental lines in FWC data, or
  corner data from DB of public observations.

## Implement FWC spectrum extraction to get instrumental lines

Modify "mos-spectra-mod" and "pn-spectra-mod" to extract spectrum, RMF, ARF
from FWC data.  Copy basic parameters from elsewhere in script
(spectralbinsize, specchannel{min,max}; use standard $ccddef, $maskitdet,
$fulldef, $FOVdef).  Modify specbackgrp scripts to copy resulting fwc files.

Remarks:
* __Explicitly remove effective area + filter from ARF for FWC data__

* backscale correction requires bad pixel locations, taken from BADPIX
  extensions in an event list FITS file.  I would have guessed better to use
  FWC data for badpix, but the corner spectra use -clean.fits for this.  So I
  just imitate ESAS behavior here.  Don't think it really matters; I'm not
  using FWC spectrum BACKSCAL for anything anyways

* (MOS) detmap for ARF and RMF are the same; I omit duplicate command in my
  modification (when creating rmf/arf for -obj.pi, same detmap gets created
  twice)

* (PN) Why doesn't RMF for PN use a detector map???
  For now, I imitate ESAS and do NOT use detmap for PN RMF.  But this should be
  investigated and fixed.  I don't know how much difference it makes...

## Test new FWC spectrum extraction

    atran@statler:/data/mpofls/atran/research/g309/xmm$ source sasinit 0087940201
    atran(sas)@statler$ cd 0087940201/odf/repro
    atran(sas)@statler$ make_xmmregions 0087940201
    ...
    atran(sas)@statler$ mos-spectra-mod prefix=1S001 caldb="${XMM_PATH}/caldb" region="/data/mpofls/atran/research/g309/xmm/regs/0087940201/reg_mos1S001_src.txt" mask=1 elow=0 ehigh=0 ccd1=1 ccd2=1 ccd3=1 ccd4=1 ccd5=1 ccd7=1 ccd6=0 cflim=12000 >& mos-spectra_mos1S001_src.log

Running nominally.
Result: cannot extract RMF and ARF for FWC-extracted spectra

    ** rmfgen: error (blockNotFound), Could not find block with qualified name
    '/proj/xmm/ccf/EMOS1_FILTERTRANSX_0014.CCF:FILTER-CLOSED' in dataset with name
    '/proj/xmm/ccf/EMOS1_FILTERTRANSX_0014.CCF'

Identical error for arfgen, despite the fact that I set "modeleffarea=no" and
"modelfiltertrans=no".  I cannot fit the FWC data without a response matrix.

Can I create a response matrix using the spectrumset for the current
observation?  It should depend only on the region (in detector coordinates) and
the detector map weighting.  From a quick look at XSPEC, this seems reasonable.

It doesn't have to be perfect, and it won't be perfect, because we're using
these files to estimate ratios in order to better fit backgrounds to be
subtracted from / modeled out of the actual data.

Try again using the actual observation spectrumset...

    atran@statler:~/rsch/g309/xmm$ nohup /bin/tcsh -c 'source sasinit 0551000201; specbackgrp_0551000201 src; specbackgrp_0551000201 bkg' >& 20160107_specfwctest_0551000201.log &
    [1] 6409

    atran@cooper:~/rsch/g309/xmm$ nohup /bin/tcsh -c 'source sasinit 0087940201; specbackgrp_0087940201 src; specbackgrp_0087940201 bkg' >& 20160107_specfwctest_0087940201.log &
    [1] 14673

Failed 2x more due to bugs in pn-spectra-mod, fixed and re-ran as needed.


Thursday 2016 January 7 -- more changes to fit/pipeline procedure
=================================================================

Inspect new logs for mos-spectra/pn-spectra and mos_back/pn_back.
Added error check script, and found yet another bug in pn-spectra-mod.  Made
fix, re-run script (just before leaving):

    atran@statler:~/rsch/g309/xmm$ nohup /bin/tcsh -c 'source sasinit 0551000201; specbackgrp_0551000201 src; specbackgrp_0551000201 bkg' >& 20160108_specfwctest_0551000201.log &
    [1] 31583
    atran@cooper:~/rsch/g309/xmm$ nohup /bin/tcsh -c 'source sasinit 0087940201; specbackgrp_0087940201 src; specbackgrp_0087940201 bkg' >& 20160108_specfwctest_0087940201.log &
    [1] 11585

## Preliminary test of FWC line fitting procedure

All done on 0087940201 mos1S001 exposure.

Fit FWC in bkg region with a broken power law + 2 gaussians (ignore <0.3keV),
using FWC-weighted RMF, no ARF.  This yields...
    Al line (1.49 keV): norm=3.89662E-02
    Si line (1.75 keV): norm=7.31105E-03
with FWC ARF on INSTR LINES ONLY:
    Al line (1.49 keV): norm=4.67590E-02
    Si line (1.75 keV): norm=8.68996E-03
    (note that ARF actually requires LARGER normalization; I assume this is
     because ARF without vignetting/filter only models detector QE, basically)
The fit with FWC arf looks kind of weird -- makes it more troublesome to model
the QPB continuum (used only to get the lines, so we discard broken power law
parameters after)

Now, fit the observation background spectrum.  NOTE: remember to remove ARF for
instrumental lines.
with default ARF (mos1S001-bkg.arf):
    Al line (1.49 keV): norm=9.34806E-05
    Si line (1.75 keV): norm=1.41575E-05
    (obviously leads to incorrect normalizations)
no ARF:
    Al line (1.49 keV): norm=2.75227E-02
    Si line (1.75 keV): norm=3.78328E-03
WITH FWC ARF (mos1S001-bkg-ff.arf):
    Al line (1.49 keV): norm=3.29999E-02
    Si line (1.75 keV): norm=4.48052E-03

Compare ratios:
    FWC fitted line ratio (without ARF): 5.33
    FWC fitted line ratio (with ARF on lines only): 5.38  <- not much difference, I'll just use FWC ARF because it is physically motivated
    Obs fitted line ratio (without ARF): 6.60
    Obs fitted line ratio (with FWC ARF): 7.36
Lots of variation.  Unsurprising, given lots of APEC and soft proton emission.

What happens if we fix the line ratio to FWC value of 5.33?
  without ARF: Resulting chi-squared (334 vs. 333) is basically the same!
    If we fix this ratio, the fit "adjusts".  Clear residual at Al line peak in
    either case, regardless of fixing ratio or not.
  with FWC ARF: chi-squared jumps from 333.7 to 335.8.  Basically no
  difference!

  Note I am letting the following parameters float:
  * apec kT (both cool and hot components)
  * phabs nH
  * soft proton power law index
  * normalizations for all components (instr lines, swpc, sp,
    apec/powerlaw/apec)
  Total: 11 free parameters, if instr line ratio is fixed.

  With instr line ratio fixed, with FWC ARF, and some parameter twiddling,
  adding further SWCX components only marginally improves fit.
  E.g., dropping chi-squared to 327 after adding two C VI lines at 0.37/0.48
  keV and allowing SWCX line energies to float.
  Really marginal, not physically meaningful.

What happens if we fix the absolute normalizations (ARF none)?
  Fit worsens significantly (chi-squared jumps to ~400?).
  We simply overshoot the line; no amount of adjustment can fix this except for
  decreasing soft proton power law norm, which would cause fit to fail from
  above 2 keV, so that's not an option.

Now, fit FWC in src region
    Al line (1.49 keV): norm=2.24813E-02
    Si line (1.75 keV): norm=8.14144E-03
    Ratio is: 2.7612
Yep, big difference.

Verdict: yes, use line ratios to inform fits.  Use FWC-weighted ARF.
Don't use normalizations; I think the PN lines + MOS Al lines are strong enough
to be better determined from actual data.  But consider:
1. maybe let line ratios float, parameterized by constant term
2. maybe use and freeze normalizations (also freezing ratio), then allow
   absolute normalization to vary via constant term.


## Skip OOT subtraction / count rate scaling for FWC data

OOT subtraction is normally done in pn_back
(see `xmmsas_20141104_1833/packages/esas/src/pn_back_mod.f90`).
This would be necessary to correctly estimate instrumental line normalizations.

But, quickly comparing spectra, including those not processed by pn_back,
suggests that spectra are already correctly scaled.
This confuses me, because `pn_back` scales "-os" spectra to per-second and
per-arcminute, but I don't see any reason that the spectra extracted from
evselect calls in `pn-spectra` should be scaled this way.

  -obj.pi in pn-spectra is created normally, typical call to evselect and
    backscale.  File has 4096 channels (0-4095) with counts column.
    BACKSCAL = 183399504
    EXPOSURE = 1.7959E+04 (weighted live time of CCDs)
  -obj-oot.pi in pn-spectra is basically the same.
    4096 channels
    BACKSCAL = 183399504
    EXPOSURE = 1.92951073607287E+04 (weighted live time of CCDs)
        (differs from non-oot file by ~6.9%)
  -obj-os.pi from `pn_back` is markedly NOT the same.  Data stored as count
    rate (counts/second) + stat err for 4096 channels.
    BACKSCAL = 1.8340E+08
    EXPOSURE = 1.7959E+04  (same as -obj.pi)

OK.  Now, why do the counts appear fairly consistent in XSPEC?
Review source code `pn_back_mod.f90`.

    obj_cnts = spec - [ ootsca * spec_oot * (obj_expo / expo_oot)
                            * (obj_back / back_oot) ]
    obj_cnts *= obj_cnts / obj_expo

    resulting formula is:

        spec/obj_expo - [ootsca * (spec_oot /expo_oot) * (obj_back / back_oot)]

        (i.e., take spectrum counts and subtract OOT counts, scaled by
        exposure/backscal AND OOT scaling factor.  Result is still counts.)

    then convert obj_cnts to a count rate. (scale both cnts + stat-err by
        obj_expo)

ANSWER: amsca factor is ONLY used for the per-quadrant OOT subtraction.  OK.


Upon some reflection, OOT subtraction doesn't matter, because we're looking at:
1. 1% to 6% correction
2. uniform shift across energies, which would not affect line ratios.

The normalizations will be slightly off.  But we are tacking on a constant
factor to deal even larger discrepancies between observation/FWC data, and it's
not likely we're going to report or use this constant anywhere.  So as long as
we are internally aware that the normalizations from FWC data are not OOT
corrected, that's OK.

So, completely skip this to save time (a few hours mucking with FTOOLs).


## Implement ARF correction by taking mean ARF ratio in some energy band

NOW, before doing this, you should actually perform fits and see if they make
any difference.  Compare using a set of background-subtracted fits as follows.

### fit without "ARF correction" to bkg-subtracted spectra

    data 1:1 mos1S001_src_sqpb.pi
    data 1:2 mos2S002_src_sqpb.pi
    data 1:3 pnS003_src_os_sqpb.pi
    # backgrounds are _bkg_sqpb.pi (and _bkg_os_sqpb.pi)

    cpd /xw
    setplot en

    # ignore 1:1-22,398-414 2:1-24,413-431 3:1-29,545-673
    ignore 1:**-0.3,11.0-**
    ignore 2:**-0.3,11.0-**
    ignore 3:**-0.4,11.0-**

    abund wilm
    model TBabs*vnei

yielding parameters:

    ========================================================================
    Model TBabs<1>*vnei<2> Source No.: 1   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
       1    1   TBabs      nH         10^22    1.76700      +/-  3.11133E-02
       2    2   vnei       kT         keV      3.96000      +/-  0.252459
       3    2   vnei       H                   1.00000      frozen
       4    2   vnei       He                  1.00000      frozen
       5    2   vnei       C                   1.00000      frozen
       6    2   vnei       N                   1.00000      frozen
       7    2   vnei       O                   1.00000      frozen
       8    2   vnei       Ne                  1.00000      frozen
       9    2   vnei       Mg                  1.00000      frozen
      10    2   vnei       Si                  3.80658      +/-  0.104544
      11    2   vnei       S                   3.97469      +/-  0.205606
      12    2   vnei       Ar                  1.00000      frozen
      13    2   vnei       Ca                  1.00000      frozen
      14    2   vnei       Fe                  1.00000      frozen
      15    2   vnei       Ni                  1.00000      frozen
      16    2   vnei       Tau        s/cm^3   1.58020E+10  +/-  5.18094E+08
      17    2   vnei       Redshift            0.0          frozen
      18    2   vnei       norm                3.22627E-03  +/-  1.35549E-04
    ________________________________________________________________________


    Fit statistic : Chi-Squared =        2197.05 using 1278 PHA bins.

    Test statistic : Chi-Squared =        2197.05 using 1278 PHA bins.
     Reduced chi-squared =        1.72724 for   1272 degrees of freedom
     Null hypothesis probability =   2.628829e-52

Remarks:
* from the manual fitting, both Si and S must be free to achieve a good fit.
* the kT value is still quite high, which Pat was surprised by before
* significant residual at soft energies for both MOS and PN (<0.8 keV)
* large absolute residuals in MOS and PN associated w/instrumental line subtraction

### fit with "ARF correction" to bkg-subtracted spectra

NOW, try again by applying arf factor to backgrounds via mathpha, before
fitting.

From my script `arf_assess.py`, I estimate the ratios of data between 0-5keV
by eyeballing plots.  (that is, ratio of src-region ARF / bkg-region ARF)
    MOS1: 1.25
    MOS2: 1.32
    PN: 1.27
ARF discrepancy increases further at high energies, but we have almost no
signal there anyways due to the really high background.  So I expect ARF
correction for <5keV to suffice.

    # Only set backscal and exposure, since these are the only two that matter
    # for XSPEC backgrounds
    # Careful; exposure=CALC is incorrect here.

    mathpha expr="1.25 * mos1S001_bkg_sqpb.pi" outfil="mos1S001_bkg_sqpb_arfcorr.pi" \
        units=C exposure="mos1S001_bkg_sqpb.pi" backscal='%' areascal='%' \
        properr='yes' ncomments=0

    mathpha expr="1.32 * mos2S002_bkg_sqpb.pi" outfil="mos2S002_bkg_sqpb_arfcorr.pi" \
        units=C exposure="mos2S002_bkg_sqpb.pi" backscal='%' areascal='%' \
        properr='yes' ncomments=0

    mathpha expr="1.27 * pnS003_bkg_os_sqpb.pi" outfil="pnS003_bkg_os_sqpb_arfcorr.pi" \
        units=R exposure="pnS003_bkg_os_sqpb.pi" backscal='%' areascal='%' \
        properr='yes' ncomments=0

UNCOVERED minor bug in spectrum subtraction script (specmeth); set units=R for
PN exposures!  Don't fix immediately, because it will require me to restart
this short analysis (probably affects error calculation though, which does
affect fits).

    XSPEC12>back 1 mos1S001_bkg_sqpb.pi
    Net count rate (cts/s) for Spectrum:1  3.605e-01 +/- 8.075e-03 (36.2 % total)
    XSPEC12>back 1 mos1S001_bkg_sqpb_arfcorr.pi
    Net count rate (cts/s) for Spectrum:1  1.898e-01 +/- 8.487e-03 (19.1 % total)
    XSPEC12>back 2 mos2S002_bkg_sqpb.pi
    Net count rate (cts/s) for Spectrum:2  4.106e-01 +/- 8.121e-03 (39.1 % total)
    XSPEC12>back 2 mos2S002_bkg_sqpb_arfcorr.pi
    Net count rate (cts/s) for Spectrum:2  2.011e-01 +/- 8.610e-03 (19.1 % total)
    XSPEC12>back 3 pnS003_bkg_os_sqpb.pi
    Net count rate (cts/s) for Spectrum:3  7.945e-01 +/- 1.615e-02 (29.6 % total)
    XSPEC12>back 3 pnS003_bkg_os_sqpb_arfcorr.pi
    Net count rate (cts/s) for Spectrum:3  2.855e-01 +/- 1.705e-02 (10.7 % total)

OK, much less dramatic change after applying energy ranges
(MOS 0.3-11 keV, PN 0.4-11keV as above)

    XSPEC12>back 1 mos1S001_bkg_sqpb.pi
    Net count rate (cts/s) for Spectrum:1  3.831e-01 +/- 7.583e-03 (42.1 % total)
    XSPEC12>back 1 mos1S001_bkg_sqpb_arfcorr.pi
    Net count rate (cts/s) for Spectrum:1  2.408e-01 +/- 7.949e-03 (26.4 % total)
    XSPEC12>back 2 mos2S002_bkg_sqpb.pi
    Net count rate (cts/s) for Spectrum:2  3.988e-01 +/- 7.656e-03 (42.0 % total)
    XSPEC12>back 2 mos2S002_bkg_sqpb_arfcorr.pi
    Net count rate (cts/s) for Spectrum:2  2.180e-01 +/- 8.104e-03 (22.9 % total)
    XSPEC12>back 3 pnS003_bkg_os_sqpb.pi
    Net count rate (cts/s) for Spectrum:3  1.068e+00 +/- 1.265e-02 (54.4 % total)
    XSPEC12>back 3 pnS003_bkg_os_sqpb_arfcorr.pi
    Net count rate (cts/s) for Spectrum:3  8.262e-01 +/- 1.318e-02 (42.0 % total)

First fit, abund=1 (solar) for all.

    ========================================================================
    Model TBabs<1>*vnei<2> Source No.: 1   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
       1    1   TBabs      nH         10^22    2.20476      +/-  5.30039E-02
       2    2   vnei       kT         keV      1.35985      +/-  9.08687E-02
       3    2   vnei       H                   1.00000      frozen
       4    2   vnei       He                  1.00000      frozen
       5    2   vnei       C                   1.00000      frozen
       6    2   vnei       N                   1.00000      frozen
       7    2   vnei       O                   1.00000      frozen
       8    2   vnei       Ne                  1.00000      frozen
       9    2   vnei       Mg                  1.00000      frozen
      10    2   vnei       Si                  4.23944      +/-  0.152323
      11    2   vnei       S                   4.69722      +/-  0.313183
      12    2   vnei       Ar                  1.00000      frozen
      13    2   vnei       Ca                  1.00000      frozen
      14    2   vnei       Fe                  1.00000      frozen
      15    2   vnei       Ni                  1.00000      frozen
      16    2   vnei       Tau        s/cm^3   2.24616E+10  +/-  1.89956E+09
      17    2   vnei       Redshift            0.0          frozen
      18    2   vnei       norm                6.08443E-03  +/-  5.94876E-04
    ________________________________________________________________________


    Fit statistic : Chi-Squared =        2680.18 using 1278 PHA bins.

    Test statistic : Chi-Squared =        2680.18 using 1278 PHA bins.
     Reduced chi-squared =        2.10706 for   1272 degrees of freedom
     Null hypothesis probability =  1.695962e-102

BIG difference!
* chi-squared is worse (2200 -> 2700); red chi-squared (1.73 -> 2.11)
  But, they're both bad enough that I'm willing to live with this.
  In any case, the arf-correction is physically motivated.
  And I think a large effect is the high-energy residuals, which are basically
  consistent with the signal being totally washed by background.
  IF I change fit to exclude all data above 8 keV, chi-squared improves significantly!
  (without arf correction: chisqr = 1903, redchisqr = 1.69;
   with arf correction: chisqr = 2055, redchisqr = 1.83)
* Higher absorption (nH 1.77 -> 2.20)
* Lower temperature (kT 3.96 -> 1.36)
* Increased Si/S abundance (~3.8/4.0 to 4.2/4.7)
* Slightly larger ionization age (tau 1.58E+10 -> 2.25E+10)
* 2x larger norm for vnei (3.2E-03 -> 6.1E-03)
  I assume this helps offset the temperature/absorption changes.

Verdict: yes, this is an important correction; in fact I wish I could apply
this correction as a function of energy/channel space.
And, why not?  If I'm making such a crude correction, I can take it one step
further by using the EBOUNDS table in the RMF file !!

OK -- defer implementing this correction until discussion with Pat.


Friday 2016 January 8 -- spectrum fitting setup
===============================================

## Error propagation with mathpha

properr=yes sums the errors on inputs in quadrature (ok for Gaussian errors)
properr=no sums counts, then treats errors as poisson in different ways.
    POISS-0 default, sqrt(n); POISS-1,2,3 uses Gehrels approximations
Note that Gaussian errors, for counts (n1+n2) with initially Poisson errors,
are just sqrt(n), same as POISS-0.

    initial MOS/PN spectrum from evselect is just counts, no error column.
        POISSERR=T is set in spectrum header.

    QPB spectrum from {mos,pn}-back is counts and STAT-ERR, much smaller than
        Poissonian errors.  Counts are fractional + derived from Megasec. of
        FWC data, scaled down to our observation.
        E.g., mos1S001-bkg-qpb.pi channel 56 has 6.04 +/- 0.36 counts.
        The continuum bridge fit around channels 250-375 has ZERO errors.

We MUST use properr=yes if subtracted spectrum can have negative counts
(everything else takes sqrt(n) stuff).  Propagated Gaussian errors will reflect
relatively high confidence in the QPB background that ESAS produces.  Because
we're subtracting two spectra, Gaussian errors will be larger than POISS-0
errors, which is desirable.

May not matter, since XSPEC will recompute errors when fitting grppha-binned
data anyways.

Bug fix: auxfiles keyword was not working -- I think because i/p spectum was
missing many keywords besides BACKSCAL, it failed and defaulted to null values.
So BACKSCAL was not set correctly.  Fixed this and kept re-running background
subtraction script.

## Double check scaling for transferring background model to SNR

Currently scaling by backscal value.  Because XSPEC already divides out
EXPOSURE before fitting spectrum (see manual), we don't need to adjust for
that.

## Mess around with models in XSPEC

To get a sense of tbabs, vnei behavior as viewed through XMM-Newton ARF/RMF.
Inspect and prepare some plots.  Most conceptually tricky may be getting a feel
for behavior of model w/ varying ionization timescale tau.
1e8 - 1e13 sec ~ 3.2yrs to 32,000 yr
So we might expect order 1e10 to 1e11 sec (300-3000yr) for young-mid age SNRs.

This about matches what we're seeing (1e10 to 2e10) -- actually a little on the
young side, given our guess of remnant age (Gaensler: ~1000 - 20000 yr based on
HI absorption -> dist -> age).  With stated errors it could be as close as 3.8
kpc, which may help account for the large inferred values of kT.
Rakowski+ (2001) also report similar values of kT ~ 1-2, and favor a closer
distance.


Saturday - Wednesday 2016 January 9-13 -- pipelining (manual work) to SNR fit
==============================================================================

Most work done over Jan 9-11, numbers and results assembled; notes cleaned up
over Jan 12-13.

List of section headers:
* Fix PN FWC extraction for LargeWindow submode
* XSPEC fit of instrumental lines in FWC data (+)
* Observation bkg fit, RMF/ARF handling for instrumental lines?
* Observation bkg fit, notes and results
  - 0087940201 bkg fit (+)
  - 0551000201 bkg fit (+)
* SNR fitting results
  - Fit with ionization timescale tied to default 1e+11
  - Fit with ionization timescale free
* SNR fitting with (crude) straight background subtraction
  - Fitting progression
  - Investigate fit discrepancy w.r.t 2016 Jan 07 bkg-sub fits
  - Investigate why bkg subtraction fits are so bad
* Images to accompany notes
* Notes from Pat meeting, Tues Jan 12

(+) indicates sections with fit numbers used in downstream fits (currently by
hand-copying, though this could be improved)

Key results are also summarized in the file: `results_20160112.txt`
(the results file contains some comments not given in notes, and vice
versa; neither strictly supersedes the other's information content)


Fix PN FWC extraction for LargeWindow submode
---------------------------------------------

MAJOR ERROR discovered: PN FWC extraction for 0551000201 must account for large
frame window.  By itself, pn-spectra{-mod} selections don't include this.

Try getting BOX for large window in DS9:
  center = -3691.5, -1111.5
  SIZE = 19648 x 16320
Thus we need: -9271 < DETY < 7049, roughly.
In pn-spectra-mod I add the definition

  $halfdef="&&((DETX,DETY) in BOX(-2196,-1110,16060,8160,0))";

NOTE: for current fitting process, this doesn't change anything since I'm not
using 0551000201 PNS003 data at the moment.  I made script change, then
proceeded with fits (need to re-run extraction pipeline, if we return to
0551000201 PNS003 data).


XSPEC fit of instrumental lines in FWC data
-------------------------------------------

Do this the stupidest possible way to save time.  Fit by hand with XSPEC
"scripts" `ff_mos.xcm` and `ff_pn.xcm`, modifying the filenames in scripts and
inspecting plots.  Almost certainly faster than writing a real script.

MOS: fit Al 1.49 keV and Si 1.75 keV lines.
PN: ESAS cookbook recommends lines at: 1.49, 7.49, 7.11, 8.05, 8.62, 8.90 keV.
    Looking at 0551000201 src, four main lines in ~7-9 keV range:
      weak-ish 7.49 (Ni K-alpha?)
      strong 8.05 (Copper K-alpha?)
      strong 8.62 (Zinc K-alpha?)
      medium 8.90 (Copper K-beta?)

Observations for PN fits:
* faint forward-modeled lines around 6-7 keV appear to be channel-energy
  redistribution effects.
* Two small bumps not modeled (Mn, Cr lines)
* fits to 0551000201, 0087940201 PN SRC __and__ background both show no need
  for 7.11 keV line as recommended by ESAS.
    0551000201 pnS003-bkg-ff: widen 1.49, 8.05 lines; then 8.62, 8.90
  Fit normalizations are ~1e-4 or smaller (basically zero); so in practice we
  can just ignore.  There are definitely more prominent features that I am NOT
  modeling.
* PN lines are generally wider than the Gaussians with sigma=0, especially in
  0551000201 spectra.  To fix this, allow line widths to vary.

Removed 7.11 keV line in background region fit script as a result.  I wonder if
it's a typo.

For MOS, parameters 3/6 indicate Al and Si line normalizations
respectively.  Using custom FWC ARF (no filter/vignetting) for instrumental
lines; no ARF for continuum background modeled by power law.  For PN, do a
two-step fit: 1st fit normalizations, 2nd time let line widths float.

0087940201 mos1 src
   3    1   gaussian   norm                4.14609E-02  +/-  1.86937E-04
   6    2   gaussian   norm                1.28250E-02  +/-  1.13420E-04
0087940201 mos1 bkg
   3    1   gaussian   norm                4.66742E-02  +/-  1.83855E-04
   6    2   gaussian   norm                8.89327E-03  +/-  9.41538E-05
0087940201 mos2 src
   3    1   gaussian   norm                4.53064E-02  +/-  1.84964E-04
   6    2   gaussian   norm                1.18173E-02  +/-  1.06179E-04
0087940201 mos2 bkg
   3    1   gaussian   norm                4.97471E-02  +/-  1.93144E-04
   6    2   gaussian   norm                9.34134E-03  +/-  9.81577E-05
0087940201 pn src
   1    1   gaussian   LineE      keV      1.49000      frozen
   2    1   gaussian   Sigma      keV      0.0          +/-  2.59243E-03
   3    1   gaussian   norm                3.34797E-02  +/-  2.78617E-04
   4    2   gaussian   LineE      keV      7.49000      frozen
   5    2   gaussian   Sigma      keV      2.75955E-05  +/-  -1.00000
   6    2   gaussian   norm                1.23563E-02  +/-  1.86121E-04
   7    3   gaussian   LineE      keV      8.05000      frozen
   8    3   gaussian   Sigma      keV      4.64571E-04  +/-  -1.00000
   9    3   gaussian   norm                8.81967E-02  +/-  3.69142E-04
  10    4   gaussian   LineE      keV      8.62000      frozen
  11    4   gaussian   Sigma      keV      6.15888E-02  +/-  2.98145E-03
  12    4   gaussian   norm                1.85035E-02  +/-  2.69025E-04
  13    5   gaussian   LineE      keV      8.90000      frozen
  14    5   gaussian   Sigma      keV      8.93654E-03  +/-  1.91152E-02
  15    5   gaussian   norm                1.09118E-02  +/-  2.38250E-04
0087940201 pn bkg
   1    1   gaussian   LineE      keV      1.49000      frozen
   2    1   gaussian   Sigma      keV      1.81761E-02  +/-  1.09565E-03
   3    1   gaussian   norm                3.43531E-02  +/-  2.68424E-04
   4    2   gaussian   LineE      keV      7.49000      frozen
   5    2   gaussian   Sigma      keV      4.34900E-02  +/-  2.95195E-03
   6    2   gaussian   norm                1.51056E-02  +/-  2.16095E-04
   7    3   gaussian   LineE      keV      8.05000      frozen
   8    3   gaussian   Sigma      keV      4.86598E-02  +/-  6.01155E-04
   9    3   gaussian   norm                0.126220     +/-  4.39045E-04
  10    4   gaussian   LineE      keV      8.62000      frozen
  11    4   gaussian   Sigma      keV      8.53148E-02  +/-  2.69867E-03
  12    4   gaussian   norm                2.03146E-02  +/-  2.93500E-04
  13    5   gaussian   LineE      keV      8.90000      frozen
  14    5   gaussian   Sigma      keV      3.23556E-02  +/-  3.91492E-03
  15    5   gaussian   norm                1.65277E-02  +/-  2.62839E-04

0551000201 mos1 src
   3    1   gaussian   norm                3.33970E-02  +/-  1.53464E-04
   6    2   gaussian   norm                2.00385E-02  +/-  1.25056E-04
0551000201 mos1 bkg <- Si line is quite faint here w.r.t. QPB
   3    1   gaussian   norm                6.04617E-02  +/-  2.02562E-04
   6    2   gaussian   norm                3.38640E-03  +/-  7.56750E-05
0551000201 mos2 src <- lines are pretty equal here
   3    1   gaussian   norm                3.86562E-02  +/-  1.70168E-04
   6    2   gaussian   norm                2.02123E-02  +/-  1.30830E-04
0551000201 mos2 bkg <- reduced chi-squared a bit large; residuals a bit large
   3    1   gaussian   norm                6.42723E-02  +/-  2.16655E-04
   6    2   gaussian   norm                5.21779E-03  +/-  8.65451E-05
0551000201 pn src
  (invalid due to wrong FWC region selection -- must be redone)
0551000201 pn bkg
  (invalid due to wrong FWC region selection -- must be redone)


Observation bkg fit, RMF/ARF handling for instrumental lines?
-------------------------------------------------------------

When we fit our observation background regions, should we use
mos1S001-bkg.rmf/arf for the instrumental line model?  Both RMF and ARF are
weighted by a FWC detector map rather than the actual image weighting. Does it
make more sense to use the regular RMF already weighted?
    - Assume that incorrect detector map weighting of instr lines doesn't
      matter much (not possible to separate anyways)
    - Use different ARF for instrumental lines
    - Use same RMF for instrumental lines

We can either say:

    [f_{instr} * A_{fwc-instr} + f_{sky} * A_{qpb + instr + sky weighted}]
        * R_{qpb + instr + sky}

or:

    f_{instr + sky} * R_{qpb + instr + sky}
        * A_{qpb + instr + sky weighted}

Neither of these are precisely correct.
Case 1: `f_{sky}` should not include instr line emission in its weighting
Case 2: `f_{instr...}` should not be forward-modeled through an ARF that
  includes mirror effective area and filter transmission.  Doesn't matter for
  two entirely free Gaussians, but does matter if we are trying to track
  normalization as a sanity check.
In both cases we should not include the QPB emission in the detector map, but
that's more hassle than its worth to try to remove.  Anyways that should be
fairly uniform across the detector; actual emission in our regions of interest
should be pretty smooth-ish anyways (no sharp structure; point sources masked).

We could test this by changing the ARF and seeing how the fit changes.
But, remember that weighting is a lower order effect (1st order: distance from
aimpoint, 2nd order -- distrib of flux within annulus from aimpoint).

I opt for case 1, using filter wheel closed ARF without vignetting/mirrors for
instrumental line model.


Observation bkg fit, notes and results
--------------------------------------

Error: local component (unabsorbed APEC) kT should be 0.1 keV, not 1 keV.  Big
difference!  That actually suffices to explain the low energy emission in my
background regions.
E.g., Kuntz & Snowden (2010) study Chandra 1Ms view of M101 and find
    kT_local ~ 0.10
    kT_distant ~ 0.24 (XMM), 0.27 (Chandra ACIS-S)
Note for Kuntz&Snowden, M101 is well above galactic plane so I think
`kT_distant` would be higher for our data.
Similar for Maggi+ (2015) study of LMC remnants; they have kT ~ 0.085 due to
Henley and Shelton 2008.

SWCX doesn't seem necessary, after changing unabsorbed APEC kT to 0.1 keV.
APEC explains the low-energy signal pretty well by itself.

I don't get the sense that PN/MOS soft proton power laws are well constrained,
despite them being the dominant component at high energy.  Too much going on
towards low-energy end of spectrum; lever arm for fitting is not great.

Two assumptions we could make:
1. line ratios, up to normalization, are same between bkg-ff and bkg (and
   src-ff,src)
2. ratio of line normalizations are same between (bkg-ff, src-ff) as for
   (bkg,src)
Taking both assumptions would completely constrain instrumental lines.
I'll just stick to 1 for now; no particular reason

### 0087940201 bkg fit

Some comments:
* removed constant terms in front of xrb. expect the normalizations to be same for all detectors
* mos1, mos2 power laws for SP contamination should be about the same

    ========================================================================
    Model instr:constant<1>(gaussian<2> + gaussian<3> + gaussian<4> + gaussian<5> + gaussian<6> + gaussian<7>) Source No.: 2   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
                               Data group: 1
       1    1   constant   factor              0.708683     +/-  3.44735E-02
       2    2   gaussian   LineE      keV      1.49000      frozen
       3    2   gaussian   Sigma      keV      0.0          frozen
       4    2   gaussian   norm                4.66700E-02  frozen
       5    3   gaussian   LineE      keV      1.75000      frozen
       6    3   gaussian   Sigma      keV      0.0          frozen
       7    3   gaussian   norm                8.89300E-03  frozen
      [... omitted norm=0 PN lines]
                               Data group: 2
      20    1   constant   factor              0.672653     +/-  3.21214E-02
      21    2   gaussian   LineE      keV      1.49000      = instr:p2
      22    2   gaussian   Sigma      keV      0.0          = instr:p3
      23    2   gaussian   norm                4.97500E-02  frozen
      24    3   gaussian   LineE      keV      1.75000      = instr:p5
      25    3   gaussian   Sigma      keV      0.0          = instr:p6
      26    3   gaussian   norm                9.34100E-03  frozen
      [... omitted norm=0 PN lines]
                               Data group: 3
      39    1   constant   factor              0.630177     +/-  1.91208E-02
      40    2   gaussian   LineE      keV      1.49000      = instr:p2
      41    2   gaussian   Sigma      keV      0.0          = instr:p3
      42    2   gaussian   norm                3.43500E-02  frozen
      [... omit norm=0 Si 1.75 keV line]
      46    4   gaussian   LineE      keV      7.49000      = instr:p8
      47    4   gaussian   Sigma      keV      0.0          = instr:p9
      48    4   gaussian   norm                1.51100E-02  frozen
      49    5   gaussian   LineE      keV      8.05000      = instr:p11
      50    5   gaussian   Sigma      keV      0.0          = instr:p12
      51    5   gaussian   norm                0.126000     frozen
      52    6   gaussian   LineE      keV      8.62000      = instr:p14
      53    6   gaussian   Sigma      keV      0.0          = instr:p15
      54    6   gaussian   norm                2.03100E-02  frozen
      55    7   gaussian   LineE      keV      8.90000      = instr:p17
      56    7   gaussian   Sigma      keV      0.0          = instr:p18
      57    7   gaussian   norm                1.65300E-02  frozen
    ________________________________________________________________________


    ========================================================================
    Model spm1:powerlaw<1> Source No.: 3   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
                               Data group: 1
       1    1   powerlaw   PhoIndex            0.425247     +/-  1.92588E-02
       2    1   powerlaw   norm                6.06012E-02  +/-  2.38054E-03
    ________________________________________________________________________


    ========================================================================
    Model spm2:powerlaw<1> Source No.: 4   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
                               Data group: 2
       1    1   powerlaw   PhoIndex            0.421315     +/-  1.73107E-02
       2    1   powerlaw   norm                6.44559E-02  +/-  2.29311E-03
    ________________________________________________________________________


    ========================================================================
    Model sppn:powerlaw<1> Source No.: 5   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
                               Data group: 3
       1    1   powerlaw   PhoIndex            0.379473     +/-  4.83896E-02
       2    1   powerlaw   norm                7.82846E-02  +/-  7.92473E-03
    ________________________________________________________________________


    ========================================================================
    Model xrb:apec<1> + TBabs<2>(powerlaw<3> + apec<4>) Source No.: 1   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
                               Data group: 1
       1    1   apec       kT         keV      0.233540     +/-  1.03482E-02
       2    1   apec       Abundanc            1.00000      frozen
       3    1   apec       Redshift            0.0          frozen
       4    1   apec       norm                2.40035E-04  +/-  1.95080E-05
       5    2   TBabs      nH         10^22    1.37624      +/-  0.116844
       6    3   powerlaw   PhoIndex            1.40000      frozen
       7    3   powerlaw   norm                1.28596E-04  +/-  2.75718E-05
       8    4   apec       kT         keV      0.394366     +/-  4.53429E-02
       9    4   apec       Abundanc            1.00000      frozen
      10    4   apec       Redshift            0.0          frozen
      11    4   apec       norm                4.36818E-03  +/-  1.50767E-03
      [... omit duplicate tied parameters 12-33 for data groups 2,3]
    ________________________________________________________________________


    Fit statistic : Chi-Squared =        1188.56 using 1070 PHA bins.

    Test statistic : Chi-Squared =        1188.56 using 1070 PHA bins.
     Reduced chi-squared =        1.12659 for   1055 degrees of freedom
     Null hypothesis probability =   2.496193e-03


### 0551000201 bkg fit

Fit result looks good, but the wildly differing soft proton (SP) power laws
between MOS1/2 are concerning.  Reassuring that XRB physical values are about
the same, although nH differs by ~30%...

(!) Do missing CCDs have an effect?  Which would cause soft proton spectrum to
appear softer for MOS2 vs. MOS1.  They should be same angle off-optical-axis.

    ========================================================================
    Model instr:constant<1>(gaussian<2> + gaussian<3>) Source No.: 2   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
                               Data group: 1
       1    1   constant   factor              1.42947      +/-  4.29158E-02
       2    2   gaussian   LineE      keV      1.49000      frozen
       3    2   gaussian   Sigma      keV      0.0          frozen
       4    2   gaussian   norm                6.04600E-02  frozen
       5    3   gaussian   LineE      keV      1.75000      frozen
       6    3   gaussian   Sigma      keV      0.0          frozen
       7    3   gaussian   norm                3.38600E-03  frozen
                               Data group: 2
       8    1   constant   factor              1.45193      +/-  3.99731E-02
       9    2   gaussian   LineE      keV      1.49000      = instr:p2
      10    2   gaussian   Sigma      keV      0.0          = instr:p3
      11    2   gaussian   norm                6.42700E-02  frozen
      12    3   gaussian   LineE      keV      1.75000      = instr:p5
      13    3   gaussian   Sigma      keV      0.0          = instr:p6
      14    3   gaussian   norm                5.21800E-03  frozen
    ________________________________________________________________________


    ========================================================================
    Model spm1:powerlaw<1> Source No.: 3   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
                               Data group: 1
       1    1   powerlaw   PhoIndex            0.533904     +/-  5.17374E-02
       2    1   powerlaw   norm                2.97647E-02  +/-  3.06942E-03
    ________________________________________________________________________


    ========================================================================
    Model spm2:powerlaw<1> Source No.: 4   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
                               Data group: 2
       1    1   powerlaw   PhoIndex            1.04537      +/-  0.100371
       2    1   powerlaw   norm                1.50520E-02  +/-  2.50700E-03
    ________________________________________________________________________


    ========================================================================
    Model xrb:apec<1> + TBabs<2>(powerlaw<3> + apec<4>) Source No.: 1   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
                               Data group: 1
       1    1   apec       kT         keV      0.226875     +/-  2.28387E-02
       2    1   apec       Abundanc            1.00000      frozen
       3    1   apec       Redshift            0.0          frozen
       4    1   apec       norm                2.30391E-04  +/-  4.00245E-05
       5    2   TBabs      nH         10^22    1.07922      +/-  0.146038
       6    3   powerlaw   PhoIndex            1.40000      frozen
       7    3   powerlaw   norm                4.60753E-04  +/-  3.22715E-05
       8    4   apec       kT         keV      0.355641     +/-  3.06881E-02
       9    4   apec       Abundanc            1.00000      frozen
      10    4   apec       Redshift            0.0          frozen
      11    4   apec       norm                4.55666E-03  +/-  1.63213E-03
      [... omit duplicate tied parameters 12-22 for data groups 2,3]
    ________________________________________________________________________


    Fit statistic : Chi-Squared =         520.77 using 495 PHA bins.

    Test statistic : Chi-Squared =         520.77 using 495 PHA bins.
     Reduced chi-squared =         1.0782 for    483 degrees of freedom
     Null hypothesis probability =   1.138531e-01


SNR fitting results
-------------------

General set-up for combined fit of all five exposures
* do NOT let constants float for XRB
* progressively thaw SNR tbabs/vnei parameters to get better fit
  - in order: Si, S, kT, nH, Tau

Some errors hit while fitting (in order of realization):
1. accidentally tied 0551000201 MOS data to 0087940201 (fixed)
2. forgot to correctly scale XRB normalizations based on BACKSCAL ratios.
    Because bkg data were scaled by exposure already when fitted,
    no need to do exposure adjustment.  Only need to adjust XRB, SP power law
    components. Instrumental lines taken from SRC region FWC.
      For 0087940201, no big deal; BACKSCAL ratio is ~0.97
      For 0551000201, BACKSCAL ratio is ~0.7.
    (fixed)
3. typo in ARF assignment for 0551000201 data (fixed)

The following fit results reflect all three corrections just noted.

General observation: residuals show a lot of systematic structure, especially
at low energy.  I think we're not correctly capturing all processes at play.

### Fit with ionization timescale tied to default 1e+11

(after having freed Si,S,kT,nH progressively)

    TBabs nH    2.43      +/-  3.9E-02  10^22
    vnei  kT    0.89      +/-  1.9E-02  keV
    vnei  Si    4.37      +/-  0.13
    vnei  S     3.75      +/-  0.15
    vnei  norm  1.03E-02  +/-  5.52E-04

    MOS1 instr con: 0.91
    MOS2 instr con: 0.82
    PN instr con: 0.57
    MOS1 (motch) instr con: 1.48
    MOS2 (motch) instr con: 1.63

    MOS1 SP: n=0.42, norm 7.2e-2
    MOS2 SP: n=0.50, norm 8.7e-2
    PN SP: n=0.55, norm 0.15
    MOS1 (motch) SP: n=0.40, norm 6.4e-2
    MOS2 (motch) SP: n=0.79, norm 3.5e-2  (!)

    Fit statistic : Chi-Squared =        2911.67 using 2240 PHA bins.
    Test statistic : Chi-Squared =        2911.67 using 2240 PHA bins.
     Reduced chi-squared =        1.31156 for   2220 degrees of freedom

### Same fit, now with Tau free

(nH, kT, Si, S, Tau, norm free)

    TBabs nH    2.10      +/-  3.9E-02  10^22
    vnei  kT    1.71      +/-  0.10     kev
    vnei  Si    4.39      +/-  0.12
    vnei  S     3.94      +/-  0.16
    vnei  Tau   2.35E+10  +/-  1.3E+09  s/cm^3
    vnei  norm  4.52E-03  +/-  3.0E-04

    MOS1 instr con: 1.02
    MOS2 instr con: 0.92
    PN instr con: 0.60
    MOS1 (motch) instr con: 1.62
    MOS2 (motch) instr con: 1.75

    MOS1 SP: n=0.41, norm 6.8e-2
    MOS2 SP: n=0.49, norm 8.2e-2
    PN SP: n=0.53, norm 0.14
    MOS1 (motch) SP: n=0.36, norm 5.7e-2
    MOS2 (motch) SP: n=0.83, norm 3.0e-2  (!)

    Fit statistic : Chi-Squared =        2790.84 using 2240 PHA bins.
    Test statistic : Chi-Squared =        2790.84 using 2240 PHA bins.
     Reduced chi-squared =        1.25770 for   2219 degrees of freedom

SNR fitting with (crude) straight background subtraction
--------------------------------------------------------

### Fitting progression

Start with nH,kT,Tau free, then thaw Si,S.
With all solar abundances, we get a poor fit, to no one's surprise.
Residuals show a line-shaped excess around Si He-alpha region.

    ========================================================================
    Model TBabs<1>*vnei<2> Source No.: 1   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
                               Data group: 1
       1    1   TBabs      nH         10^22    4.20507      +/-  2.74597E-02
       2    2   vnei       kT         keV      0.693725     +/-  8.45959E-03
       [... omit frozen abundances ...]
      16    2   vnei       Tau        s/cm^3   6.16578E+10  +/-  4.37994E+09
      17    2   vnei       Redshift            0.0          frozen
      18    2   vnei       norm                7.73004E-02  +/-  2.45807E-03
    ________________________________________________________________________


    Fit statistic : Chi-Squared =       12656.35 using 1877 PHA bins.
    Test statistic : Chi-Squared =       12656.35 using 1877 PHA bins.
     Reduced chi-squared =       6.757260 for   1873 degrees of freedom
     Null hypothesis probability =   0.000000e+00

Freeze nH, kT, Tau; free Si, fit.

    Yields Si = 1.75, chi-squared = 10674.72, reduced chi-squared 5.69
    Improvement, but still a lot of error in residuals.

Thaw nH,kT,Tau, with Si still free.

    Model Model Component  Parameter  Unit     Value
     par  comp
       1    1   TBabs      nH         10^22    2.69465      +/-  3.04639E-02
       2    2   vnei       kT         keV      1.51774      +/-  4.28172E-02
      10    2   vnei       Si                  2.64083      +/-  4.54133E-02
      16    2   vnei       Tau        s/cm^3   2.85722E+10  +/-  1.21985E+09
      18    2   vnei       norm                9.75483E-03  +/-  4.07743E-04

    Fit statistic : Chi-Squared =        9499.25 using 1877 PHA bins.
    Test statistic : Chi-Squared =        9499.25 using 1877 PHA bins.
     Reduced chi-squared =        5.07438 for   1872 degrees of freedom
     Null hypothesis probability =   0.000000e+00

Thaw all of nH,kT,Tau,Si,S.

    Model Model Component  Parameter  Unit     Value
     par  comp
       1    1   TBabs      nH         10^22    2.12828      +/-  2.61716E-02
       2    2   vnei       kT         keV      2.02251      +/-  7.39041E-02
      10    2   vnei       Si                  3.82517      +/-  6.42711E-02
      11    2   vnei       S                   4.88114      +/-  0.181313
      16    2   vnei       Tau        s/cm^3   1.54760E+10  +/-  4.70120E+08
      18    2   vnei       norm                4.87415E-03  +/-  2.01638E-04

    Fit statistic : Chi-Squared =        7391.95 using 1877 PHA bins.
    Test statistic : Chi-Squared =        7391.95 using 1877 PHA bins.
     Reduced chi-squared =        3.95080 for   1871 degrees of freedom
     Null hypothesis probability =   0.000000e+00

The chi-squared is quite high.  Increasing ignore range, to fit only
0.7-5.0keV, doesn't have much effect (reduced chi-squared still around 4).

Qualitatively, PNS003 data seems to be the worst of the lot.
Dropping data groups 3,4,5 and only fitting 0087940201 MOS1 and MOS2 actually
helps a ton.  Reduced chi-squared becomes 1.4.

Now to be clear, the PN fit doesn't look terrible -- I speculate that the poor fit occurs because the XSPEC errors don't account for increased error due to spectrum subtraction.

### Investigate fit discrepancy w.r.t. 2016 Jan 07 bkg-sub fits

Somehow, the fits aren't as good as my previous ad hoc test (see 2016 Jan 7
notes on ARF correction).  By eye it looks ok, but chi-squared is much worse.

On Friday Jan 8 (after my ad hoc fit result) I fixed a major bug in "specmeth"
where BACKSCAL keyword was not propagating correctly.
Subtracted spectra would have incorrect BACKSCAL; both bkg and src spectra
would have BACKSCAL 1.  Now that doesn't explain things for 0087940201 since
the bkg/src regions cover almost the same geometric area, and BACKSCAL scaling
wouldn't have changed much.  Same goes for EXPOSURE values (which should have
been correctly propagated regardless).

Maybe the change in fitting result occurs due to the change in PN error?!
I return to "specmeth" script and temporarily change the mathpha call for QPB
subtraction to 1. erroneously assume (c)ounts for PN spectra, and 2.
erroneously set BACKSCAL = 1.

With nH, kT, Tau free; Si,S = 1 fixed (includes 0551000201 exposures)

       1    1   TBabs      nH         10^22    4.26441      +/-  5.62672E-02
       2    2   vnei       kT         keV      0.680138     +/-  2.54352E-02
      16    2   vnei       Tau        s/cm^3   5.84882E+10  +/-  7.52978E+09
      18    2   vnei       norm                6.99632E-02  +/-  6.26161E-03

    Fit statistic : Chi-Squared =        7133.16 using 1881 PHA bins.
    Test statistic : Chi-Squared =        7133.16 using 1881 PHA bins.
     Reduced chi-squared =        3.80030 for   1877 degrees of freedom
     Null hypothesis probability =   0.000000e+00

OK, huge difference.  Now, thaw Si, S abundances and fit.

       1    1   TBabs      nH         10^22    2.43575      +/-  5.29364E-02
       2    2   vnei       kT         keV      1.20324      +/-  6.23764E-02
      10    2   vnei       Si                  4.46075      +/-  0.136747
      11    2   vnei       S                   5.84094      +/-  0.408087
      16    2   vnei       Tau        s/cm^3   1.95345E+10  +/-  1.15500E+09
      18    2   vnei       norm                7.21904E-03  +/-  6.40248E-04

    Fit statistic : Chi-Squared =        5086.12 using 1881 PHA bins.
    Test statistic : Chi-Squared =        5086.12 using 1881 PHA bins.
     Reduced chi-squared =        2.71260 for   1875 degrees of freedom
     Null hypothesis probability =  7.817741e-294

And, to try to replicate previous results, remove 0551000201 MOS exposures.
Result:

       1    1   TBabs      nH         10^22    2.20285      +/-  5.29141E-02
       2    2   vnei       kT         keV      1.36096      +/-  9.12594E-02
      10    2   vnei       Si                  4.24679      +/-  0.150958
      11    2   vnei       S                   4.71260      +/-  0.315012
      16    2   vnei       Tau        s/cm^3   2.24117E+10  +/-  1.66643E+09
      18    2   vnei       norm                6.06976E-03  +/-  5.90217E-04

    Fit statistic : Chi-Squared =        2680.20 using 1278 PHA bins.
    Test statistic : Chi-Squared =        2680.20 using 1278 PHA bins.
     Reduced chi-squared =        2.10708 for   1272 degrees of freedom
     Null hypothesis probability =  1.687869e-102

Happily, this was EXACTLY what I got last time, to individual parameter values.
Quick check with BACKSCAL error removes indicates that yes, error arises due
only to incorrect subtraction in PN data.

Two errors: BACKSCAL and PN ct rate not fixed; ARF correction in place
    Net count rate (cts/s) for Spectrum:1  2.408e-01 +/- 7.949e-03 (26.4 % total)
    Net count rate (cts/s) for Spectrum:2  2.180e-01 +/- 8.104e-03 (22.9 % total)
    Net count rate (cts/s) for Spectrum:3  8.262e-01 +/- 1.318e-02 (42.0 % total)

BACKSCAL error fixed, PN ct rate error not fixed; ARF correction in place
    Net count rate (cts/s) for Spectrum:1  2.522e-01 +/- 7.892e-03 (27.7 % total)
    Net count rate (cts/s) for Spectrum:2  2.555e-01 +/- 7.926e-03 (26.9 % total)
    Net count rate (cts/s) for Spectrum:3  8.512e-01 +/- 1.307e-02 (43.3 % total)

Both errors fixed.
    Net count rate (cts/s) for Spectrum:1  2.522e-01 +/- 7.892e-03 (27.7 % total)
    Net count rate (cts/s) for Spectrum:2  2.555e-01 +/- 7.926e-03 (26.9 % total)
    Net count rate (cts/s) for Spectrum:3  8.491e-01 +/- 7.824e-03 (43.3 % total)

BACKSCAL error causes a ~5-10% error in bkg subtraction; PN error causes a
smaller error in ct rates, but somehow significantly worsens the fit.

OK.  So now we understand the cause of the discrepancy.

### Investigate why bkg subtraction fits are so bad

Returning to correct background subtraction, the fit quality is terrible.
The data are not helping, looking at error bars in `20160112_sqpb_noise.png`.
What's going on?  I speculate that (1) the error bars could be incorrectly
computed, or (2) the binning is crap because we bin before background
subtraction.

QPB-subtracted spectrum `0087940201/odf/repro/pnS003_src_os_sqpb.pi` has rate
column but no error column, and the POISSERR keyword is set to true.
With properr=yes, default error method POISS-0 still sets POISSERR keyword to
True, so no error column is written in either MOS or PN data.  Recall that this
was forced because our counts are sometimes negative; any other method will
cause mathpha to spew errors/warnings.

Could grppha binning be messing up errors for count rate data?  From manual
check of one bin (summing counts in channels manually), grppha does bin count
rate data correctly, just scaling by EXPOSURE keyword.  So the grouping is OK
for PN if we are sticking to Poisson errors.

Let us trace the error propagation:

    mos1S001-src.pi, pnS003-src-os.pi, ...
        Counts and count rates, no edits.  Poisson errors are OK.

    mos1S001-src-qpb.pi, pnS003-src-qpb.pi, ...
        Count rate with relatively small statistical error

    mos1S001_src_sqpb.pi, pnS003_src_os_sqpb.pi
        Counts and count rates, with Poisson errors assumed.
        Given that QPB errors are small-ish, this seems acceptable, although we
        should recognize that purely Poisson errors are an underestimate.
        (and, we are totally ignoring systematics)

    XSPEC fit view of: mos1S001_src_sqpb_grp50.pi, back=mos1S001_bkg_sqpb.pi
        Sum background-subtracted-counts in each bin; compute purely Poisson
        error

Can we get XSPEC to use more reasonable errors?

From XSPEC manual for data command:
> A data file has the total observed counts for a number of channels and a
> factor for the size of any systematic error. Each channel is converted to a
> count rate per unit area (assumed cm–2). The default background file is used
> for background subtraction. An error term is calculated using Poisson
> statistics and any systematic error indicated in the file

But, I know from plotting QPB that XSPEC is able to use `STAT_ERR` column in
spectrum file.  I wish the XSPEC manual would describe the error determination
code.

From an old CIAO page:
> If the data are grouped then XSPEC calculates the `GRP_STAT_ERR = sqrt(SUM
> STAT_ERR**2)` over the group. This gives an error which is much larger than the
> correct one calculated from the counts in the group.

Therefore, yes: in order to apply our own error propagation, we would have to:
* perform background (XRB/lines) subtraction manually (must do this before binning)
* bin subtracted data
* add `STAT_ERR` column by hand, and set POISSERR=F

For now, I will:
* perform background (XRB/lines) subtraction manually
* bin subtracted data
* allow us to fit with POISSERR

This completely neglects error propagation, and may mess up weighting in
the fits.  But, fitting background-subtracted spectra is already an approximate
method.  Please note to self: chi-squared is large because our error estimates
are small, and our error estimates are flat-out wrong.  I record notes on
implementation in a new section of the notes (this block of fitting notes is
running long).


## Images to accompany notes

Plots of the various fit results are given in:
    20160112_bkg_fit_0087940201.png
    20160112_bkg_fit_0551000201.png
    20160112_snr_fit_allfree.png
        nH,kT,Tau free; Si,S free; SP power law gamma and norms free
        XRB fixed; instr fixed (except prefactor constants)
    20160112_snr_fit_rebin.png
    20160112_snr_fit_zoom_rebin.png
        as above, but zoomed in and with a fine binning
        (setplot rebin 15 100)
        rescale Y 1e-4 2.5
    20160112_sqpb_noise.png

The plot of `sqpb_noise` is of the background subtracted data -- the plot is
erroneous (PN data not subtracted correctly due to typo in an XSPEC command)
and filled with noise from the subtraction process (this is expected).

## Notes from Pat meeting, Tues Jan 12

* ARF/RMF weighting could be a 1st order effect (but we're still trying to
  figure out zero-th order anyways)
* In general, don't touch abundances until you've considered all other
  parameters (kT, nH, Tau)
* Omitting PNS003 is fine.  Not that much data loss, and QPB analysis
  assumptions would be tenuous...
* First-order ARF correction OK, obviously not worth sweating higher-energy
  ratio deviation
* FWC assumption of equivalent line ratios... that's the main question

* vnei ionization timescale (s/cm^3): assuming n=1, then yes, Tau ~ 1e11 is
  what is expected; indeed several times 10^11 or even larger is common.
  Tau ~ few x 10^10 is unusual.
  We might expect smaller Tau in spectra of recently shocked material (assuming
  spatially resolved), but for integrated spectra, no...



Wednesday 2016 January 13 -- tweak bkg-subtraction fits, SWCX cut, NEI reading
==============================================================================

## Corrected background subtraction

Comment: mathpha help page is internally inconsistent (in one place it states
ERRMETH='POISS-0' is default, in another it states 'POISS-1' to be default.
In practice (CfA install) mathpha is using 'POISS-0' with properr=Y.

Implemented subtraction in renamed script `spec_subtract` (formerly
`specmeth`).

Data, error bars, and fits look mostly like crap.  I'm really confused.
Thinking it's not worth spending a lot of time on this analysis.

Plotting together:
    mos1S001_src_sqpb.pi or mos1S001-src-grp50.pi
    mos1S001_bkg_sqpb.pi or mos1S001-bkg-grp50.pi
at least makes it clear that background-subtracted data look like crap, but
don't look wrong.

I think the reason that explicit background fit succeeds, is that by fitting
five backgrounds simultaneously we're improving the signal to noise ratio by
sqrt(5) or so.  Granted the SP contamination is still poorly constrained, but
it's something.


## Quick fit with soft proton power law values/normalizations fixed

First, try freezing power-law indices + norms and fitting solely with
1. absorbed vnei
2. instrumental line normalizations (ratios fixed)

       1    1   constant   factor              0.762071     +/-  4.68849E-02  
      20    1   constant   factor              0.710206     +/-  4.35130E-02  
      39    1   constant   factor              0.622259     +/-  2.39189E-02  
      58    1   constant   factor              1.32411      +/-  6.40511E-02  
      77    1   constant   factor              1.41944      +/-  5.83450E-02  

       1    1   TBabs      nH         10^22    3.45748      +/-  3.28116E-02  
       2    2   vnei       kT         keV      1.01224      +/-  2.53497E-02  
      10    2   vnei       Si                  1.00000      frozen
      11    2   vnei       S                   1.00000      frozen
      16    2   vnei       Tau        s/cm^3   4.25097E+10  +/-  3.74442E+09  
      18    2   vnei       norm                2.81065E-02  +/-  1.32207E-03

    Fit statistic : Chi-Squared =        6909.61 using 2240 PHA bins.
    Test statistic : Chi-Squared =        6909.61 using 2240 PHA bins.
     Reduced chi-squared =        3.09709 for   2231 degrees of freedom 
     Null hypothesis probability =   0.000000e+00


Next, thaw Si abundance.

       1    1   constant   factor              0.902636     +/-  4.61271E-02  
      20    1   constant   factor              0.843641     +/-  4.27518E-02  
      39    1   constant   factor              0.631403     +/-  2.38970E-02  
      58    1   constant   factor              1.53552      +/-  6.30878E-02  
      77    1   constant   factor              1.61105      +/-  5.75167E-02

       1    1   TBabs      nH         10^22    2.04067      +/-  2.40066E-02  
       2    2   vnei       kT         keV      3.77705      +/-  0.165704     
      10    2   vnei       Si                  3.37841      +/-  6.83132E-02  
      11    2   vnei       S                   1.00000      frozen
      16    2   vnei       Tau        s/cm^3   1.89320E+10  +/-  4.56341E+08  
      18    2   vnei       norm                3.95179E-03  +/-  1.12318E-04 

    Fit statistic : Chi-Squared =        4680.94 using 2240 PHA bins.
    Test statistic : Chi-Squared =        4680.94 using 2240 PHA bins.
     Reduced chi-squared =        2.09908 for   2230 degrees of freedom 
     Null hypothesis probability =  7.613902e-176

Next, thaw S abundance.

       1    1   constant   factor              0.999009     +/-  4.61798E-02  
      20    1   constant   factor              0.936468     +/-  4.27946E-02  
      39    1   constant   factor              0.646228     +/-  2.39052E-02  
      58    1   constant   factor              1.67338      +/-  6.32476E-02  
      77    1   constant   factor              1.73166      +/-  5.76348E-02

       1    1   TBabs      nH         10^22    1.76978      +/-  2.40078E-02  
       2    2   vnei       kT         keV      5.65797      +/-  0.418605     
      10    2   vnei       Si                  4.03651      +/-  8.46934E-02  
      11    2   vnei       S                   3.98772      +/-  0.153752     
      16    2   vnei       Tau        s/cm^3   1.61445E+10  +/-  3.07349E+08  
      18    2   vnei       norm                2.73357E-03  +/-  7.51694E-05

    Fit statistic : Chi-Squared =        3908.74 using 2240 PHA bins.
    Test statistic : Chi-Squared =        3908.74 using 2240 PHA bins.
     Reduced chi-squared =        1.75358 for   2229 degrees of freedom 
     Null hypothesis probability =   2.016358e-95

So, OK, clearly worse.  A lot of error coming from hard tail for 0551000201
MOS1 exposure only; seems to be a bit better for others.
Try freeing that normalization (`thaw spm1motch:2`).  Normalization
basically doubles from 2.976E-02 to ~6.4E-2.

       1    1   constant   factor              1.01946      +/-  4.62352E-02  
      20    1   constant   factor              0.955373     +/-  4.28486E-02  
      39    1   constant   factor              0.662830     +/-  2.38826E-02  
      58    1   constant   factor              1.53899      +/-  6.35252E-02  
      77    1   constant   factor              1.75845      +/-  5.77082E-02

       1    1   TBabs      nH         10^22    1.88757      +/-  2.88516E-02  
       2    2   vnei       kT         keV      3.30791      +/-  0.179701     
      10    2   vnei       Si                  4.19088      +/-  9.77357E-02  
      11    2   vnei       S                   3.90718      +/-  0.155719     
      16    2   vnei       Tau        s/cm^3   1.71551E+10  +/-  4.42182E+08  
      18    2   vnei       norm                3.16319E-03  +/-  1.34972E-04

    Model spm1motch:powerlaw<1>*constant<2> Source No.: 7   Active/On
       1    1   powerlaw   PhoIndex            0.534000     frozen
       2    1   powerlaw   norm                6.57093E-02  +/-  1.34021E-03  
       3    2   constant   factor              0.769000     frozen

    Fit statistic : Chi-Squared =        3218.15 using 2240 PHA bins.
    Test statistic : Chi-Squared =        3218.15 using 2240 PHA bins.
     Reduced chi-squared =        1.44441 for   2228 degrees of freedom 
     Null hypothesis probability =   2.061282e-39

OK, that's not terrible.  Same features mostly show up: low energy excess,
systematic-looking waviness to residuals.

I think the next steps will be
1. make that 3 band image (handling exposure maps correctly)
2. separate out spectra plots to make it actually viewable...
(maybe use sherpa...)


## Irrelevant realization

Does XMM SAS backscale account for missing CCDs?  If not, then my analysis of
0551000201 MOS1 data has incorrect BACKSCAL, which might explain the
normalization discrepancy in the fit w/ SP power law fixed...

Answer: yes, it does.  Recall that MOS2 CCD5 was omitted due to anomalous state
behavior, which does explain why the backscal ratios are similar.  Cheese masks
don't reflect my exclusion of CCD5.


## SWPC cut analysis

SWPC cut for 0087940201 test
    0087940201 plots:
        Start: 1.15354e8; stop: 1.15394e8  (span 40ks)
        Cut at time = 25000s + 1.1535e8 seconds
            = 115,350,000 + 25,000 ~ 115,375,000s
        est. proton density pre-cut ~8, post-cut ~4
        est. SWCX emission pre-cut ~3e12, post-cut ~1e12 and lower (to 1e11?)
    0551000201 plots:
        Start: 3.52724237e8, stop: 3.52778429e8 (span 50ks)
        est. SWCX emission ~1.5e12 during the quiet period
            jumps to ~2e12 in our flaring periods (already excised)
        est. proton density ~4 (arbitrary units) during quiet period

Quick reference for time filtering, other than selectlib:
http://heasarc.gsfc.nasa.gov/docs/xmm/abc/node8.html#SECTION00850000000000000000

Pre-cut:
    evselect:- selected 9600 rows from the input table.
    ** evselect: warning (ExpBadDssGlobal), A filtering expression has been specified which may not allow for calculation of a uniform exposure for all events.  Please ensure that all TIME related filters are applied uniformly.
    evselect:- evselect (evselect-3.62)  [xmmsas_20141104_1833-14.0.0] ended:    2016-01-14T03:01:30.000
    ** evselect: warning (SummaryOfWarnings), 
       warning ExpBadDssGlobal silently occurred 3 times
Post-cut:
    evselect:- selected 18531 rows from the input table.
    ** evselect: warning (ExpBadDssGlobal), A filtering expression has been specified which may not allow for calculation of a uniform exposure for all events.  Please ensure that all TIME related filters are applied uniformly.
    evselect:- evselect (evselect-3.62)  [xmmsas_20141104_1833-14.0.0] ended:    2016-01-14T03:02:20.000
    ** evselect: warning (SummaryOfWarnings), 
       warning ExpBadDssGlobal silently occurred 3 times

Total: 28131 events matches mos1S001-src.pi extraction, good.

The filtering expression warnings may affect calculated exposure times.  But,
that doesn't affect our assessment, I think...
In XSPEC the spectra qualitatively line up right, so I think it worked out.
Anything else would just show up as a constant shift.

Quick XSPEC plot, no background -- AND, with background + grouping --
I see no obvious sign of contamination.

Let's forge ahead with ignoring this contribution.
Anyways, should be covered by soft unabsorbed APEC.


## A few reading remarks on (v)(v)nei model

Running down list from XSPEC equil manual page, in reverse chronological order:

Borkowsky, Lyerly, Reynolds (2001) -- augment vnei by accounting for:
* spatial integration along line-of-sight through remnant (in this case I think
  completely integrated spectrum of remnant)
* discrepancy between electron / ion temperatures at shock
  (models evolution of this parameter)
Corresponds to sedov (& vsedov) in XSPEC.

Liedahl, Osterheld, Goldstein (1995) -- Fe L-shell calculation for 0.7-1.5 keV
emission

Borkowski, Sarazin, Blondin (1993) -- NEI emission calculation for Kepler SNR
First, find time-dependent (non-equilibrium) ion fractions:
* assume fully ionized H, He; compute state for C,N,O,Ne,Mg,Si,S,Ca,Fe,Ni
* neglect 3-body collisions, given low density of plasma
* assume collisional / de-excitation processes < radiative decay; i.e.,
  all excitation assumes interacting ions initially at ground state,
  all de-excitation assumed by emission (if not forbidden or whatever)
* neglect ambient radiation field; no stimulated radiation transitions,
  no alteration of gas dynamics/processes due to radiation
* optically thin; gas' own radiation passes straight through
Equation (5) describes time-dependent collisional ionization and recombination
(both radiative and dielectronic recombination.
 From http://www.nist.gov/pml/div684/grp01/research-324.cfm
 radiative recomb = ion captures electron + emits a photon, from energy decr.
 dielectronic recomb = ion captures electron + promote an electron to higher
   orbit, then that state eventually decays and radiates)
Collisional + recombination rates taken from Hamilton,Sarazin,Chevalier(1983)

With modeled ion fractions in hand from model, use another code
Hamilton+ (1983) and Wise&Sarazin (1993) to compute free-free, free-bound, and
line emission from all ions (H, He, C, N, ..., Fe, Ni).

Hamilton, Sarazin, Chevalier (1983, ApJS) -- didn't look closely, since I think
conceptually it's pretty clear.  A few bullets...
* with assumptions (as re-stated in Borkowski+ 1993),
    ionization/recombination rates ~ density
    emissivities ~ density^2
* Table 1 provides the default solar abundances (`log10[N(X)/N_H] + 12`)
* more description of the specific ionization / "de-ionization" processes,
  specific citations on collisional ionization, autoionization, recombination;
  temperature dependence is important.
This looks like a good, fundamental paper to read.


Friday 2016 January 15 -- split spectrum fit plots in matplotlib
================================================================

A few fitting questions to investigate:

* Fit background with MOS1/MOS2 soft proton power law indices tied?
* Fit background from 0087940201 and 0551000201 together?
* Use ESAS task "proton" to extrapolate src-region SP contamination, based
  on bkg-region fits?
* Freeze nH = 1.81e22 (fair bit higher than we're seeing in fits) for XRB?

Major: need to break fit plots apart.  Just going to translate tools to PyXSPEC
to get this done.

Background fits with MOS SP power law indices tied
--------------------------------------------------

0087940201 bkg fit: the MOS1/2 power laws were already quite close to begin
with (0.421 vs. 0.425).  The reduced chi-squared is marginally smaller,
actually, from 1055 to 1056 dof.  Basically, no difference.

    # Starting from only (nine) normalizations free
    XSPEC12>fit
    XSPEC12>thaw spm1:1 ; thaw spm2:1 ; thaw sppn:1
    XSPEC12>newpar spm2:1=spm1:1
    XSPEC12>fit
    XSPEC12>thaw xrb:1,5,8 
    XSPEC12>fit

    instr:
       1    1   constant   factor              0.709177     +/-  3.43667E-02  
      20    1   constant   factor              0.672088     +/-  3.20058E-02  
      39    1   constant   factor              0.630165     +/-  1.91210E-02  
    spm1:
       1    1   powerlaw   PhoIndex            0.422679     +/-  1.52330E-02  
       2    1   powerlaw   norm                6.03719E-02  +/-  2.15721E-03  
    spm2:
       1    1   powerlaw   PhoIndex            0.422679     = spm1:p1
       2    1   powerlaw   norm                6.45408E-02  +/-  2.21316E-03  
    sppn:
       1    1   powerlaw   PhoIndex            0.378153     +/-  4.83926E-02  
       2    1   powerlaw   norm                7.80593E-02  +/-  7.90120E-03  
    xrb:
       1    1   apec       kT         keV      0.233432     +/-  1.03283E-02  
       4    1   apec       norm                2.40479E-04  +/-  1.94625E-05  
       5    2   TBabs      nH         10^22    1.37450      +/-  0.116894     
       6    3   powerlaw   PhoIndex            1.40000      frozen
       7    3   powerlaw   norm                1.29226E-04  +/-  2.75281E-05  
       8    4   apec       kT         keV      0.394830     +/-  4.50515E-02  
      11    4   apec       norm                4.35085E-03  +/-  1.51239E-03  

    Fit statistic : Chi-Squared =        1188.60 using 1070 PHA bins.
    Test statistic : Chi-Squared =        1188.60 using 1070 PHA bins.
     Reduced chi-squared =        1.12556 for   1056 degrees of freedom 
     Null hypothesis probability =   2.660039e-03

0551000201 bkg fit:

    # Starting from only (seven) normalizations free;
    # initial fit chi-squared/dof = 604.64/488 = 1.2390
    XSPEC12>fit
    XSPEC12>thaw spm1:1 ; thaw spm2:1
    XSPEC12>newpar spm2:1=spm1:1
    XSPEC12>fit
    # SP index free: chi-squared/dof = 589.95/487 = 1.2114
    # residuals still quite poor, wave-like variation
    XSPEC12>thaw xrb:1,5,8 
    XSPEC12>fit

    instr:
       1    1   constant   factor              1.38973      +/-  4.28942E-02  
       8    1   constant   factor              1.40637      +/-  4.02865E-02  
    spm1:
       1    1   powerlaw   PhoIndex            0.224776     +/-  8.60053E-02  
       2    1   powerlaw   norm                1.57428E-02  +/-  2.66007E-03  
    spm2:
       1    1   powerlaw   PhoIndex            0.224776     = spm1:p1
       2    1   powerlaw   norm                2.26595E-03  +/-  9.75420E-04  
    xrb:
       1    1   apec       kT         keV      8.65018E-02  +/-  7.95029E-03  
       4    1   apec       norm                8.50525E-04  +/-  3.03417E-04  
       5    2   TBabs      nH         10^22    0.138951     +/-  4.27661E-02  
       6    3   powerlaw   PhoIndex            1.40000      frozen
       7    3   powerlaw   norm                5.10379E-04  +/-  2.14015E-05  
       8    4   apec       kT         keV      0.299661     +/-  2.18355E-02  
      11    4   apec       norm                3.24175E-04  +/-  1.10656E-04  

    Fit statistic : Chi-Squared =         547.00 using 495 PHA bins.
    Test statistic : Chi-Squared =         547.00 using 495 PHA bins.
     Reduced chi-squared =         1.1302 for    484 degrees of freedom 
     Null hypothesis probability =   2.473836e-02

    # Here's a better version, obtained after running:
    XSPEC12> newpar xrb:5 1 ; freeze xrb:5
    XSPEC12> fit
    XSPEC12> thaw xrb:5
    XSPEC12> fit
    # Not very "scientific", but the parameter values appear more credible
    # (reasonable nH) and much more comparable to values from 0087940201 fit

    instr:
       1    1   constant   factor              1.42406      +/-  4.28174E-02  
       8    1   constant   factor              1.45022      +/-  4.00298E-02  
    spm1:
       1    1   powerlaw   PhoIndex            0.383103     +/-  6.85431E-02  
       2    1   powerlaw   norm                2.13003E-02  +/-  2.88758E-03  
    spm2:
       1    1   powerlaw   PhoIndex            0.383103     = spm1:p1
       2    1   powerlaw   norm                4.26962E-03  +/-  1.43290E-03  
    xrb:
       1    1   apec       kT         keV      0.209976     +/-  1.16570E-02  
       4    1   apec       norm                3.52533E-04  +/-  2.97923E-05  
       5    2   TBabs      nH         10^22    1.03740      +/-  0.101135     
       6    3   powerlaw   PhoIndex            1.40000      frozen
       7    3   powerlaw   norm                5.19103E-04  +/-  2.98144E-05  
       8    4   apec       kT         keV      0.364388     +/-  3.07768E-02  
      11    4   apec       norm                4.38368E-03  +/-  1.32865E-03  

    Fit statistic : Chi-Squared =         542.39 using 495 PHA bins.
    Test statistic : Chi-Squared =         542.39 using 495 PHA bins.
     Reduced chi-squared =         1.1206 for    484 degrees of freedom 
     Null hypothesis probability =   3.381268e-02

Main verdict: not much effect that I can tell.

Combined bkg fit (consistent XRB, float SP/instr lines)
-------------------------------------------------------

Tried porting over to PyXSPEC for a bit.  Time sink is the set-up process, for
both XSPEC and PyXSPEC.  Mainly setting up parameters, hard-coding norm values,
etc...  Realized, this is not really a script-friendly task.  I'm performing
one fit [to rule them all], or a chain of such fits, and trying many variants
of said fit pipeline in a one-off fashion.  So it doesn't make sense to script
these, when there's not a lot to script "over".  So, stuck to XSPEC.

Also (re-)figured out how to export data:  iplot, then wdata.
It will save x, xerr, y, yerr, summed model, indiv model components
Wrote starter script to plot the fits and actually see what's going on.

New script `back_all.xcm`.

A little funky -- fits are less stable (unsurprisingly)
* PN power law index tends to float towards n=-0.25
* nH tends to float towards small values (0.1e22 - 0.5e22)
    but, sort of stable once it converges on the "nice" set of XRB parameters
    apec kT ~ 0.22 unabsorbed
    nH ~ 1.2
    apec kT ~ 0.37 absorbed
* coupling or de-coupling mos1/2 power laws doesn't seem to make an obviously
  big difference.

1:sppn:powerlaw[1]:PhoIndex:3>0.4, 0.01 0.1 0.2 1 1.4

Here's one fit with PN pegged to 0.3

    spm1:
       1    1   powerlaw   PhoIndex            0.386206     +/-  1.27444E-02  
       2    1   powerlaw   norm                5.35839E-02  +/-  1.41101E-03  
    spm1motch:
       1    1   powerlaw   PhoIndex            0.643859     +/-  2.39222E-02  
       2    1   powerlaw   norm                4.20071E-02  +/-  1.65950E-03  
    spm2:
       1    1   powerlaw   PhoIndex            0.386206     = spm1:p1
       2    1   powerlaw   norm                5.76602E-02  +/-  1.46190E-03  
    spm2motch:
       1    1   powerlaw   PhoIndex            0.643859     = spm1motch:p1
       2    1   powerlaw   norm                2.00493E-02  +/-  1.34130E-03  
    sppn:
       1    1   powerlaw   PhoIndex            0.300000     frozen
       2    1   powerlaw   norm                5.91043E-02  +/-  1.88141E-03  
    xrb:
       1    1   apec       kT         keV      0.229073     +/-  9.30238E-03  
       4    1   apec       norm                2.51608E-04  +/-  1.25539E-05  
       5    2   TBabs      nH         10^22    1.25395      +/-  8.88915E-02  
       6    3   powerlaw   PhoIndex            1.40000      frozen
       7    3   powerlaw   norm                2.48887E-04  +/-  1.62855E-05  
       8    4   apec       kT         keV      0.373489     +/-  2.65382E-02  
      11    4   apec       norm                4.55749E-03  +/-  1.08803E-03  

    Fit statistic : Chi-Squared =        1881.74 using 1565 PHA bins.
    Test statistic : Chi-Squared =        1881.74 using 1565 PHA bins.
     Reduced chi-squared =        1.21638 for   1547 degrees of freedom 
     Null hypothesis probability =   8.335663e-09

Pegged to 0.2, chi-squared drops to 

    spm1:
       1    1   powerlaw   PhoIndex            0.370655     +/-  1.30874E-02  
       2    1   powerlaw   norm                5.15866E-02  +/-  1.38651E-03  
    spm1motch:
       1    1   powerlaw   PhoIndex            0.625728     +/-  2.50292E-02  
       2    1   powerlaw   norm                4.00473E-02  +/-  1.65360E-03  
    spm2:
       1    1   powerlaw   PhoIndex            0.370655     = spm1:p1
       2    1   powerlaw   norm                5.55839E-02  +/-  1.44037E-03  
    spm2motch:
       1    1   powerlaw   PhoIndex            0.625728     = spm1motch:p1
       2    1   powerlaw   norm                1.83640E-02  +/-  1.30890E-03  
    sppn:
       1    1   powerlaw   PhoIndex            0.200000     frozen
       2    1   powerlaw   norm                4.89537E-02  +/-  1.55028E-03  
    xrb:
       1    1   apec       kT         keV      0.227647     +/-  8.73188E-03  
       4    1   apec       norm                2.70157E-04  +/-  1.24291E-05  
       5    2   TBabs      nH         10^22    1.24513      +/-  8.73373E-02  
       6    3   powerlaw   PhoIndex            1.40000      frozen
       7    3   powerlaw   norm                2.70931E-04  +/-  1.58232E-05  
       8    4   apec       kT         keV      0.375206     +/-  2.61329E-02  
      11    4   apec       norm                4.56488E-03  +/-  1.07852E-03  

    Fit statistic : Chi-Squared =        1867.14 using 1565 PHA bins.
    Test statistic : Chi-Squared =        1867.14 using 1565 PHA bins.
     Reduced chi-squared =        1.20694 for   1547 degrees of freedom 
     Null hypothesis probability =   3.113632e-08

Pegged to 0.4, chi-squared increases further.  Affects MOS power laws slightly.
(0.37 -> 0.4)

    spm1:
       1    1   powerlaw   PhoIndex            0.402701     +/-  1.24049E-02  
       2    1   powerlaw   norm                5.57489E-02  +/-  1.44037E-03  
    spm1motch:
       1    1   powerlaw   PhoIndex            0.662104     +/-  2.27601E-02  
       2    1   powerlaw   norm                4.40772E-02  +/-  1.66766E-03  
    spm2:
       1    1   powerlaw   PhoIndex            0.402701     = spm1:p1
       2    1   powerlaw   norm                5.99068E-02  +/-  1.48803E-03  
    spm2motch:
       1    1   powerlaw   PhoIndex            0.662104     = spm1motch:p1
       2    1   powerlaw   norm                2.19125E-02  +/-  1.37885E-03  
    sppn:
       1    1   powerlaw   PhoIndex            0.400000     frozen
       2    1   powerlaw   norm                7.07393E-02  +/-  2.27065E-03  


    Fit statistic : Chi-Squared =        1903.57 using 1565 PHA bins.
    Test statistic : Chi-Squared =        1903.57 using 1565 PHA bins.
     Reduced chi-squared =        1.23049 for   1547 degrees of freedom 
     Null hypothesis probability =   1.069616e-09


Wednesday,Thursday 2016 January 20-21 --
========================================

Tidy up spectrum dump/plot procedure from last Friday.
Results to review with Pat...

0. background subtracted fit looks terrible.  Could improve by correctly
   propagating errors (but, deferring).

   Initial fit (vnei fixed to defaults, norm free) : chi-squared = 177921
   Fit with nH,kT,Tau freed : chi-squared <= 95374
       (fit quite unstable, oscillated around a while before settling)
       (I interrupted fit in interest of time)

   Fit with all of nH,kT,Tau,Si,S free yielded:
        (again, fit oscillating slowly; allowed to finish)
        chi-squared = 50322
        
    I daresay, despite the low counts and incorrect error bars, the fit
    looks pretty good.

            TBabs  nH   10^22   2.36633      +/-  3.72574E-02  
            vnei   kT   keV     2.66443      +/-  3.71669E-02  
            vnei   Si           8.48006      +/-  0.117124     
            vnei   S            6.90476      +/-  9.28183E-02  
            vnei   Tau  s/cm^3  1.97230E+10  +/-  1.75384E+08

    Also, try a fit with binning to minimum 25 rather than 50.
    Just let nH, kT, Tau, Si, S all float immediately to save time.
    Chi-squared = 40752, but not useful/meaningful to compare against anything.

            TBabs  nH    10^22    2.10854      +/-  3.45018E-02  
            vnei   kT    keV      1.89506      +/-  2.76788E-02  
            vnei   Si             7.10899      +/-  0.107874     
            vnei   S              7.03597      +/-  0.125545     
            vnei   Tau   s/cm^3   2.09541E+10  +/-  3.23253E+08  
            vnei   norm           2.61578E-03  +/-  7.38639E-05

    Roughly the same idea... getting large kT, low Tau values.
    Qualitatively comparable to full bkg modeling fit, despite bad statistics.
    What's the deal?
    Should we check with a sedov fit?


1. Yes, stick to combined background fit using `back_all.xcm`.
   On basis of fit to 0087940201 bkg alone, it seems reasonable to fix PN power
   law index to somewhere in range 0.2 to 0.4; see results from last Friday.

   For simplicity (and better chi-squared -> better fidelity to background), I
   take power law index = 0.2 and roll with it.

2. Re-run SNR fit using
   - combined bkg fit result
   - freezing MOS1/MOS2 parameters together for both 0087940201, 0551000201

   Thaw snr:1,2,16 (nH, kT, Tau) and see where fit goes.
   Letting just these three parameters vary improves fit drastically.
   chisquared 17730 -> 5200
   BUT, it yields the following values:

        nH = 3.97082      +/-  4.18292E-02
        kT = 0.691246     +/-  1.40359E-02
        Tau =  7.88529E+10  +/-  9.16790E+09
        norm = 6.02865E-02  +/-  3.14678E-03

        Chi-Squared = 5234.69 using 2240 PHA bins
        Reduced chi-squared = 2.35478 for 2223 degrees of freedom

    There is a very clear residual signal around 1.85 keV for Si line.
    Now, fitting with nH,kT,Tau,Si free.

        nH = 2.40333      +/-  3.93432E-02
        kT = 1.61836      +/-  8.15888E-02 
        Si = 3.32760      +/-  8.22112E-02
        Tau =  3.02280E+10  +/-  2.22489E+09
        norm = 6.76236E-03  +/-  4.26485E-04
            *** 10x smaller normalization (!) ***

        Chi-Squared = 3526.81 using 2240 PHA bins.
        Reduced chi-squared = 1.58722 for 2222 degrees of freedom 

    Still exists clear residual signal around 2.45 keV for S line.
    Now fitting with nH,kT,Tau,Si,S free.

        nH = 2.06563      +/-  3.47055E-02
        kT = 1.82765      +/-  0.102800
        Si = 4.31783      +/-  0.115313
        S  = 3.91380      +/-  0.161020
        Tau =  2.25025E+10  +/-  1.17765E+09
        norm = 4.36376E-03  +/-  2.40878E-04

        Chi-Squared = 2797.45 using 2240 PHA bins.
        Reduced chi-squared = 1.25954 for 2221 degrees of freedom

    Finally, fit with nH=1.8, kT=1, Tau=1e11 fixed; Si/S free (maybe nH=1 would
    have been more appropriate, woops).  Fit does not look terrible, but wavy
    structure in residuals is more pronounced.

        nH = 1.80000      frozen
        kT = 1.00000      frozen
        Si = 7.03629      +/-  0.133485
        S  = 6.34056      +/-  0.165168
        Tau =  1.00000E+11  frozen
        norm = 4.75761E-03  +/-  6.96894E-05

        Chi-Squared = 3307.64 using 2240 PHA bins.
        Reduced chi-squared = 1.48725 for 2224 degrees of freedom

    Now, thaw Tau and see what happens. --> immediately starts decreasing
        Tau decreases slightly, S abundance increases slightly
        not sure what effect this had. chi-squared 3308->3279
    Refreeze Tau.  Reset Si/S to 1 (freeze) and fit only kT free.
        kT jumps to 1.85 keV, not very good fit (clear Si/S residuals)
    Then, thaw Si/S and re-fit.  Doesnt budge.
        kT settles back to 0.97, Si=7.12, S=6.6
        chi-squared 3308->3311

    Anyways return to general fit with nH, kT, Tau, Si, S free.
    At least the nH value seems credible (if rather high), I don't know how to
    understand the kT/Tau values, which seem to imply a far younger age than we
    expect for this remnant.

3. First look at an ESAS generated image for scientific analysis.

    # Following prescription for 0087940201 only
    # NOTE: this is working off of files from 0087940201 bkg region.
    # Output files:
    # mos1S001-back-im-sky-300-1250.fits
    # mos2S002-back-im-sky-300-1250.fits
    # pnS003-back-im-sky-300-1250.fits

    rot-im-det-sky prefix=1S001 elow=300 ehigh=1250 mode=1
    rot-im-det-sky prefix=2S002 elow=300 ehigh=1250 mode=1
    rot-im-det-sky prefix=S003 elow=300 ehigh=1250 mode=1

    # NOTE: SP parameters may be more robustly fit from source region
    # due to increased counts -- tied to, I think, placement of SNR along
    # optical axis and steep vignetting function for SP flares

    proton prefix=1S001 caldb="../../../caldb/" specname=mos1S001-bkg.pi \
        ccd1=1 ccd2=1 ccd3=1 ccd4=1 ccd5=1 ccd6=1 ccd7=1 \
        elow=300 ehigh=1250 pindex=0.37 pnorm="5.16e-2" spectrumcontrol=1 
    rot-im-det-sky prefix=1S001 elow=300 ehigh=1250 mode=2

    proton prefix=2S002 caldb="../../../caldb/" specname=mos2S002-bkg.pi ccd1=1 ccd2=1 ccd3=1 ccd4=1 ccd5=1 ccd6=1 ccd7=1 elow=300 ehigh=1250 pindex=0.37 pnorm="5.56e-2" spectrumcontrol=1
    rot-im-det-sky prefix=2S002 elow=300 ehigh=1250 mode=2

    proton prefix=S003 caldb="../../../caldb/" specname=pnS003-bkg-os.pi ccd1=1 ccd2=1 ccd3=1 ccd4=1 elow=300 ehigh=1250 pindex=0.2 pnorm="4.90e-2" spectrumcontrol=1
    rot-im-det-sky prefix=S003 elow=300 ehigh=1250 mode=2

    comb caldb="../../../caldb/" elowlist=300 ehighlist=1250 mask=1 withpartcontrol=1 withsoftcontrol=1 withswcxcontrol=0 prefixlist="1S001 2S002 S003" alpha=1.7


Another test just using evselect, for 0087940201 mos1S001 src region ONLY:

Three bands:
    0.3 to 1.25 keV, 1.25 to 2.65 keV, 2.65 to 11 keV

    evselect table=mos1S001-clean.fits:EVENTS withfilteredset=yes filtertype=expression expression='(PATTERN<=12)&&(FLAG == 0) &&((CCDNR == 1)||(CCDNR == 2)||(CCDNR == 3)||(CCDNR == 4)||(CCDNR == 5)||(CCDNR == 6)||(CCDNR == 7))&&region(mos1S001-bkg_region-det.fits)&&(PI in [300:1250])&&(((DETX,DETY) IN box(-2683.5,-15917,2780.5,1340,0))||((DETX,DETY) IN box(2743.5,-16051,2579.5,1340,0))||((DETX,DETY) IN circle(97,-172,17152)))&&((DETX,DETY) IN circle(-5846.5,-2782.0,8000))' imagebinning='imageSize' imagedatatype='Int32' imageset=mos1S001-src-im-det-300-1250-test.fits squarepixels=yes ignorelegallimits=yes withxranges=yes withyranges=yes xcolumn='DETX' ximagesize=780 ximagemax=19500 ximagemin=-19499 ycolumn='DETY' yimagesize=780 yimagemax=19500 yimagemin=-19499 updateexposure=yes filterexposure=yes

    evselect:- selected 4787 rows from the input table.

    evselect table=mos1S001-clean.fits:EVENTS withfilteredset=yes filtertype=expression expression='(PATTERN<=12)&&(FLAG == 0) &&((CCDNR == 1)||(CCDNR == 2)||(CCDNR == 3)||(CCDNR == 4)||(CCDNR == 5)||(CCDNR == 6)||(CCDNR == 7))&&region(mos1S001-bkg_region-det.fits)&&(PI in [1250:2650])&&(((DETX,DETY) IN box(-2683.5,-15917,2780.5,1340,0))||((DETX,DETY) IN box(2743.5,-16051,2579.5,1340,0))||((DETX,DETY) IN circle(97,-172,17152)))&&((DETX,DETY) IN circle(-5846.5,-2782.0,8000))' imagebinning='imageSize' imagedatatype='Int32' imageset=mos1S001-src-im-det-1250-2650-test.fits squarepixels=yes ignorelegallimits=yes withxranges=yes withyranges=yes xcolumn='DETX' ximagesize=780 ximagemax=19500 ximagemin=-19499 ycolumn='DETY' yimagesize=780 yimagemax=19500 yimagemin=-19499 updateexposure=yes filterexposure=yes

    evselect:- selected 10042 rows from the input table.

    evselect table=mos1S001-clean.fits:EVENTS withfilteredset=yes filtertype=expression expression='(PATTERN<=12)&&(FLAG == 0) &&((CCDNR == 1)||(CCDNR == 2)||(CCDNR == 3)||(CCDNR == 4)||(CCDNR == 5)||(CCDNR == 6)||(CCDNR == 7))&&region(mos1S001-bkg_region-det.fits)&&(PI in [2650:11000])&&(((DETX,DETY) IN box(-2683.5,-15917,2780.5,1340,0))||((DETX,DETY) IN box(2743.5,-16051,2579.5,1340,0))||((DETX,DETY) IN circle(97,-172,17152)))&&((DETX,DETY) IN circle(-5846.5,-2782.0,8000))' imagebinning='imageSize' imagedatatype='Int32' imageset=mos1S001-src-im-det-2650-11000-test.fits squarepixels=yes ignorelegallimits=yes withxranges=yes withyranges=yes xcolumn='DETX' ximagesize=780 ximagemax=19500 ximagemin=-19499 ycolumn='DETY' yimagesize=780 yimagemax=19500 yimagemin=-19499 updateexposure=yes filterexposure=yes

    evselect:- selected 10026 rows from the input table.

[note added Feb 8 2016: didn't go anywhere with these images.  ESAS process
only creates image for background region, not useful.  evselect image for MOS1
was ok but we need to be merging data to get anything useful]

## Meeting notes

Loads of helpful suggestions from Pat today, reprise meeting next Tues 2p.

background subtraction:
- the approach I took, pat hasn't really seen before
  generally group, then let xspec do background subtraction
- what the hell is wrong with PN
- consider not binning and using Cstatistic... make stat purists happy
- with my binning approach: try setting a larger group minimum, then do the bkg
  subtraction... ideally would like to have an adaptive binning or whatever, oh
  well.

Fits:
- no, don't put much stock in fits with x/y/z fixed if no physical insight
- better to do with bounds -- but, obviously, not so meaningful if you run up
  against the bound walls...
- do try (emphasized highly) fitting SNR + bkg regions together
  1. don't discard information on bkg
  2. when doing error commands, should consider uncertainties in background...
- soft excess around 0.5-1 keV
  * try freeing O, Ne?
  * SWCX? - explained to Pat, disfavored
  * see if it persists after fitting snr/bkg simultaneously.
- do run error commands, get a sense of how well constrained these numbers are.
  be advised that often it will stop and say, "found new best fit!"
  and prompt you to continue.  keep an eye out for this; save XSPEC logs...
- the "best fit" looks pretty good to Pat's eye, excepting funny bump
- sedov is worth a shot.
  obviously the vnei looks good already.
  note that sedov is quite slow; error command will be even slower...
- useful command: renorm, faster than fit...


Tuesday 2016 January 26 -- combined snr/bkg fit and XSPEC error runs
====================================================================

## Try accounting for 0.5-1keV bump with O,Ne free

Previous "standard" fit with nH,kT,Tau,Si,S free; PN power law fixed to 0.2.

    Fit statistic : Chi-Squared =        2812.40 using 2240 PHA bins.

    Test statistic : Chi-Squared =        2812.40 using 2240 PHA bins.
     Reduced chi-squared =        1.26571 for   2222 degrees of freedom 
     Null hypothesis probability =   1.365424e-16

against new fit with O, Ne free as well.

    O ~ 4, Ne ~ 0.6
    nH ~ 1.98, kT ~ 1.7, Tau ~ 2e10, Si ~ 4.4, S ~ 3.9

    Helps a little bit, but not noticeably...

    Fit statistic : Chi-Squared =        2702.86 using 2240 PHA bins.

    Test statistic : Chi-Squared =        2702.86 using 2240 PHA bins.
     Reduced chi-squared =        1.21750 for   2220 degrees of freedom 
     Null hypothesis probability =   5.646876e-12

## Joint fit of SNR and background

A new best fit from joint fit of snr and bkg.  Data groups are:
    1: 0087940201 MOS1 src
    2: 0087940201 MOS2 src
    3: 0087940201 PN src
    4: 0551000201 MOS1 src
    5: 0551000201 MOS2 src
    6: 0087940201 MOS1 bkg
    7: 0087940201 MOS2 bkg
    8: 0087940201 PN bkg
    9: 0551000201 MOS1 bkg
    10: 0551000201 MOS2 bkg

Started an XSPEC error run, with some fiddling, around 12:30...

    XSPEC12>error snr:10
     Parameter   Confidence Range (2.706)
        10      3.90491      4.32517    (-0.19848,0.221781)

Started a new run around 12:50.

    XSPEC12>error snr:1,2,11,16
     Parameter   Confidence Range (2.706)
    Apparent non-monotonicity in statistic space detected.
    Current bracket values 2.19373, 2.19397
    and delta stat 2.6866, 2.73392
    but latest trial 2.19386 gives 2.6837
    Suggest that you check this result using the steppar command.
         1      2.04851      2.19385    (-0.079417,0.0659235)
    Apparent non-monotonicity in statistic space detected.
    Current bracket values 1.59998, 1.57302
    and delta stat 2.5531, 3.41036
    but latest trial 1.59534 gives 2.46442
    Suggest that you check this result using the steppar command.
         2       1.5865        1.955    (-0.13324,0.23526)
        11      3.39296      3.95987    (-0.259479,0.307435)
    Apparent non-monotonicity in statistic space detected.
    Current bracket values 2.59075e+10, 2.59523e+10
    and delta stat 2.56306, 2.84881
    but latest trial 2.5933e+10 gives 2.85962
    Suggest that you check this result using the steppar command.
        16  2.11784e+10  2.59299e+10    (-2.7046e+09,2.04689e+09)

Check XRB parameter errors:

    XSPEC12>error xrb:2,6,9
     Parameter   Confidence Range (2.706)
    Apparent non-monotonicity in statistic space detected.
    Current bracket values 0.220108, 0.210198
    and delta stat 1.86328, 2.74213
    but latest trial 0.210584 gives 3.00948
    Suggest that you check this result using the steppar command.
    Apparent non-monotonicity in statistic space detected.
    Current bracket values 0.24061, 0.251438
    and delta stat 2.6385, 12.051
    but latest trial 0.240736 gives 2.44578
    Suggest that you check this result using the steppar command.
         2     0.215153     0.246024    (-0.0149965,0.0158742)
    Apparent non-monotonicity in statistic space detected.
    Current bracket values 1.06867, 0.914486
    and delta stat 0, 2.81712
    but latest trial 0.928353 gives 3.84069
    Suggest that you check this result using the steppar command.
         6     0.991579      1.19528    (-0.0770937,0.126602)
    Apparent non-monotonicity in statistic space detected.
    Current bracket values 0.407643, 0.440681
    and delta stat 1.86402, 3.06947
    but latest trial 0.428628 gives 4.43506
    Suggest that you check this result using the steppar command.
         9     0.347483     0.424162    (-0.0271213,0.0495577)

Combined fit result.  Note that:
* PN soft proton power law index is frozen to 0.2
* MOS1/2 soft proton power law indices are tied, within same obsid/region
  (00879... src, 00879... bkg, 0551... src, 0551... bkg)
* instrumental line normalizations are hardcoded from FWC fits,
  w/ constant prefactors free to vary
* XRB usual parameters free, but fixed for all regions
  place area-scaling factors in front of XRB values
  to account for (sampled area times ARF) differences
  between obsids (pointings) and regions.
  (see 2016 Feb 08 notes: this actually needs to be fixed)

    ========================================================================
    Model instr:constant<1>(gaussian<2> + gaussian<3> + gaussian<4> + gaussian<5> + gaussian<6> + gaussian<7>) Source No.: 2   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
                               Data group: 1
       1    1   constant   factor              0.937262     +/-  4.67237E-02  
       2    2   gaussian   LineE      keV      1.49000      frozen
       3    2   gaussian   Sigma      keV      0.0          frozen
       4    2   gaussian   norm                4.14600E-02  frozen
       5    3   gaussian   LineE      keV      1.75000      frozen
       6    3   gaussian   Sigma      keV      0.0          frozen
       7    3   gaussian   norm                1.28500E-02  frozen
    [PN lines omitted]
                               Data group: 2
      20    1   constant   factor              0.876559     +/-  4.32935E-02  
      21    2   gaussian   LineE      keV      1.49000      = instr:p2
      22    2   gaussian   Sigma      keV      0.0          = instr:p3
      23    2   gaussian   norm                4.53100E-02  frozen
      24    3   gaussian   LineE      keV      1.75000      = instr:p5
      25    3   gaussian   Sigma      keV      0.0          = instr:p6
      26    3   gaussian   norm                1.18200E-02  frozen
    [PN lines omitted]
                               Data group: 3
      39    1   constant   factor              0.601101     +/-  2.49396E-02  
      40    2   gaussian   LineE      keV      1.49000      = instr:p2
      41    2   gaussian   Sigma      keV      0.0          = instr:p3
      42    2   gaussian   norm                3.34800E-02  frozen
    [Si K line omitted]
      46    4   gaussian   LineE      keV      7.49000      = instr:p8
      47    4   gaussian   Sigma      keV      0.0          = instr:p9
      48    4   gaussian   norm                1.23600E-02  frozen
      49    5   gaussian   LineE      keV      8.05000      = instr:p11
      50    5   gaussian   Sigma      keV      0.0          = instr:p12
      51    5   gaussian   norm                8.82000E-02  frozen
      52    6   gaussian   LineE      keV      8.62000      = instr:p14
      53    6   gaussian   Sigma      keV      0.0          = instr:p15
      54    6   gaussian   norm                1.85000E-02  frozen
      55    7   gaussian   LineE      keV      8.90000      = instr:p17
      56    7   gaussian   Sigma      keV      0.0          = instr:p18
      57    7   gaussian   norm                1.09100E-02  frozen
                               Data group: 4
      58    1   constant   factor              1.67099      +/-  6.40617E-02  
      59    2   gaussian   LineE      keV      1.49000      = instr:p2
      60    2   gaussian   Sigma      keV      0.0          = instr:p3
      61    2   gaussian   norm                3.34000E-02  frozen
      62    3   gaussian   LineE      keV      1.75000      = instr:p5
      63    3   gaussian   Sigma      keV      0.0          = instr:p6
      64    3   gaussian   norm                2.00400E-02  frozen
    [PN lines omitted]
                               Data group: 5
      77    1   constant   factor              1.84268      +/-  5.81769E-02  
      78    2   gaussian   LineE      keV      1.49000      = instr:p2
      79    2   gaussian   Sigma      keV      0.0          = instr:p3
      80    2   gaussian   norm                3.86600E-02  frozen
      81    3   gaussian   LineE      keV      1.75000      = instr:p5
      82    3   gaussian   Sigma      keV      0.0          = instr:p6
      83    3   gaussian   norm                2.02100E-02  frozen
    [PN lines omitted]
                               Data group: 6
      96    1   constant   factor              0.684852     +/-  3.39676E-02  
      97    2   gaussian   LineE      keV      1.49000      = instr:p2
      98    2   gaussian   Sigma      keV      0.0          = instr:p3
      99    2   gaussian   norm                4.66700E-02  frozen
     100    3   gaussian   LineE      keV      1.75000      = instr:p5
     101    3   gaussian   Sigma      keV      0.0          = instr:p6
     102    3   gaussian   norm                8.89300E-03  frozen
    [PN lines omitted]
                               Data group: 7
     115    1   constant   factor              0.651508     +/-  3.16701E-02  
     116    2   gaussian   LineE      keV      1.49000      = instr:p2
     117    2   gaussian   Sigma      keV      0.0          = instr:p3
     118    2   gaussian   norm                4.97500E-02  frozen
     119    3   gaussian   LineE      keV      1.75000      = instr:p5
     120    3   gaussian   Sigma      keV      0.0          = instr:p6
     121    3   gaussian   norm                9.34100E-03  frozen
    [PN lines omitted]
                               Data group: 8
     134    1   constant   factor              0.639963     +/-  1.90249E-02  
     135    2   gaussian   LineE      keV      1.49000      = instr:p2
     136    2   gaussian   Sigma      keV      0.0          = instr:p3
     137    2   gaussian   norm                3.43500E-02  frozen
    [Si K line omitted]
     141    4   gaussian   LineE      keV      7.49000      = instr:p8
     142    4   gaussian   Sigma      keV      0.0          = instr:p9
     143    4   gaussian   norm                1.51100E-02  frozen
     144    5   gaussian   LineE      keV      8.05000      = instr:p11
     145    5   gaussian   Sigma      keV      0.0          = instr:p12
     146    5   gaussian   norm                0.126000     frozen
     147    6   gaussian   LineE      keV      8.62000      = instr:p14
     148    6   gaussian   Sigma      keV      0.0          = instr:p15
     149    6   gaussian   norm                2.03100E-02  frozen
     150    7   gaussian   LineE      keV      8.90000      = instr:p17
     151    7   gaussian   Sigma      keV      0.0          = instr:p18
     152    7   gaussian   norm                1.65300E-02  frozen
                               Data group: 9
     153    1   constant   factor              1.48159      +/-  4.23621E-02  
     154    2   gaussian   LineE      keV      1.49000      = instr:p2
     155    2   gaussian   Sigma      keV      0.0          = instr:p3
     156    2   gaussian   norm                6.04600E-02  frozen
     157    3   gaussian   LineE      keV      1.75000      = instr:p5
     158    3   gaussian   Sigma      keV      0.0          = instr:p6
     159    3   gaussian   norm                3.38600E-03  frozen
    [PN lines omitted]
                               Data group: 10
     172    1   constant   factor              1.51164      +/-  3.94339E-02  
     173    2   gaussian   LineE      keV      1.49000      = instr:p2
     174    2   gaussian   Sigma      keV      0.0          = instr:p3
     175    2   gaussian   norm                6.42700E-02  frozen
     176    3   gaussian   LineE      keV      1.75000      = instr:p5
     177    3   gaussian   Sigma      keV      0.0          = instr:p6
     178    3   gaussian   norm                5.21800E-03  frozen
    [PN lines omitted]
    ________________________________________________________________________


    ========================================================================
    Model snr:TBabs<1>*vnei<2> Source No.: 3   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
                               Data group: 1
       1    1   TBabs      nH         10^22    2.12793      +/-  4.30337E-02  
       2    2   vnei       kT         keV      1.71973      +/-  0.117876     
       3    2   vnei       H                   1.00000      frozen
       4    2   vnei       He                  1.00000      frozen
       5    2   vnei       C                   1.00000      frozen
       6    2   vnei       N                   1.00000      frozen
       7    2   vnei       O                   1.00000      frozen
       8    2   vnei       Ne                  1.00000      frozen
       9    2   vnei       Mg                  1.00000      frozen
      10    2   vnei       Si                  4.10339      +/-  0.118064     
      11    2   vnei       S                   3.65251      +/-  0.157932     
      12    2   vnei       Ar                  1.00000      frozen
      13    2   vnei       Ca                  1.00000      frozen
      14    2   vnei       Fe                  1.00000      frozen
      15    2   vnei       Ni                  1.00000      frozen
      16    2   vnei       Tau        s/cm^3   2.38845E+10  +/-  1.40433E+09  
      17    2   vnei       Redshift            0.0          frozen
      18    2   vnei       norm                4.86112E-03  +/-  3.39371E-04  
                               Data group: 2
    [snr model same for all data groups]
                               Data group: 3
    [snr model same for all data groups]
                               Data group: 4
    [snr model same for all data groups]
                               Data group: 5
    [snr model same for all data groups]
    ________________________________________________________________________


    ========================================================================
    Model sp:powerlaw<1>*constant<2> Source No.: 4   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
                               Data group: 1
       1    1   powerlaw   PhoIndex            0.381644     +/-  1.32677E-02  
       2    1   powerlaw   norm                5.75802E-02  +/-  1.60341E-03  
       3    2   constant   factor              0.983000     frozen
                               Data group: 2
       4    1   powerlaw   PhoIndex            0.381644     = sp:p1
       5    1   powerlaw   norm                6.25157E-02  +/-  1.74343E-03  
       6    2   constant   factor              0.945000     frozen
                               Data group: 3
       7    1   powerlaw   PhoIndex            0.200835     +/-  4.51651E-02  
       8    1   powerlaw   norm                6.29510E-02  +/-  5.62509E-03  
       9    2   constant   factor              0.978000     frozen
                               Data group: 4
      10    1   powerlaw   PhoIndex            0.397736     +/-  2.10714E-02  
      11    1   powerlaw   norm                6.41348E-02  +/-  2.64770E-03  
      12    2   constant   factor              0.769000     frozen
                               Data group: 5
      13    1   powerlaw   PhoIndex            0.397736     = sp:p10
      14    1   powerlaw   norm                2.00533E-02  +/-  1.48067E-03  
      15    2   constant   factor              0.779000     frozen
                               Data group: 6
      16    1   powerlaw   PhoIndex            0.340924     +/-  1.34719E-02  
      17    1   powerlaw   norm                4.82014E-02  +/-  1.32460E-03  
      18    2   constant   factor              1.00000      frozen
                               Data group: 7
      19    1   powerlaw   PhoIndex            0.340924     = sp:p16
      20    1   powerlaw   norm                5.20335E-02  +/-  1.38136E-03  
      21    2   constant   factor              1.00000      frozen
                               Data group: 8
      22    1   powerlaw   PhoIndex            0.200000     frozen
      23    1   powerlaw   norm                4.59799E-02  +/-  1.49250E-03  
      24    2   constant   factor              1.00000      frozen
                               Data group: 9
      25    1   powerlaw   PhoIndex            0.586935     +/-  2.67066E-02  
      26    1   powerlaw   norm                3.66085E-02  +/-  1.61620E-03  
      27    2   constant   factor              1.00000      frozen
                               Data group: 10
      28    1   powerlaw   PhoIndex            0.586935     = sp:p25
      29    1   powerlaw   norm                1.55066E-02  +/-  1.22479E-03  
      30    2   constant   factor              1.00000      frozen
    ________________________________________________________________________


    ========================================================================
    Model xrb:constant<1>(apec<2> + TBabs<3>(powerlaw<4> + apec<5>)) Source No.: 1   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
                               Data group: 1
       1    1   constant   factor              0.983000     frozen
       2    2   apec       kT         keV      0.230149     +/-  6.47079E-03  
       3    2   apec       Abundanc            1.00000      frozen
       4    2   apec       Redshift            0.0          frozen
       5    2   apec       norm                3.00393E-04  +/-  1.09362E-05  
       6    3   TBabs      nH         10^22    1.06867      +/-  7.10901E-02  
       7    4   powerlaw   PhoIndex            1.40000      frozen
       8    4   powerlaw   norm                3.04254E-04  +/-  1.37856E-05  
       9    5   apec       kT         keV      0.374602     +/-  2.00828E-02  
      10    5   apec       Abundanc            1.00000      frozen
      11    5   apec       Redshift            0.0          frozen
      12    5   apec       norm                3.29394E-03  +/-  6.13048E-04  
                               Data group: 2
      13    1   constant   factor              0.945000     frozen
    [xrb model, up to constant pre-factor,  same for all data groups]
                               Data group: 3
      25    1   constant   factor              0.978000     frozen
    [xrb model, up to constant pre-factor,  same for all data groups]
                               Data group: 4
      37    1   constant   factor              0.769000     frozen
    [xrb model, up to constant pre-factor,  same for all data groups]
                               Data group: 5
      49    1   constant   factor              0.779000     frozen
    [xrb model, up to constant pre-factor,  same for all data groups]
                               Data group: 6
      61    1   constant   factor              1.00000      frozen
    [xrb model, up to constant pre-factor,  same for all data groups]
                               Data group: 7
      73    1   constant   factor              1.00000      frozen
    [xrb model, up to constant pre-factor,  same for all data groups]
                               Data group: 8
      85    1   constant   factor              1.00000      frozen
    [xrb model, up to constant pre-factor,  same for all data groups]
                               Data group: 9
      97    1   constant   factor              1.00000      frozen
    [xrb model, up to constant pre-factor,  same for all data groups]
                               Data group: 10
     109    1   constant   factor              1.00000      frozen
    [xrb model, up to constant pre-factor,  same for all data groups]
    ________________________________________________________________________


    Fit statistic : Chi-Squared =        4608.36 using 3805 PHA bins.

    Test statistic : Chi-Squared =        4608.36 using 3805 PHA bins.
     Reduced chi-squared =        1.22302 for   3768 degrees of freedom 
     Null hypothesis probability =   7.182096e-20


Monday 2016 February 1 -- catch up, image creation
==================================================

This has been on the back-burner due to MP things.  Where did I leave off?
(text below partially fleshed out on Mon Feb. 08)

## Recap of recent fit results

Thurs Jan 20 -- reviewed fit results with Pat.
* bkg subtraction fits -- could improve procedure. Low priority.
  - fix error bars by manually adding new column to FITS file
  - change binning procedure, so XSPEC generates correct errors
  - try not binning and using C statistic
* fit snr/bkg together (done)
  - do document / show fits with Si/S frozen, then progressively thawing Si,S
    and S,Si (in that order) to demonstrate that both elements likely need to
    be enhanced in abundance (w.r.t. other elements)
* soft excess around 0.5-1 keV
  - try freeing O, Ne (done, eh)
  - see if persists after fitting snr/bkg together (small effect)
* sedov fit is worth an attempt, although slow
* use bounds if toying with fit parameter ranges
* run error commands to assess uncertainties

Tues Jan 26 -- again, quick touch of base on fit results.
* fit with O,Ne free made a small difference (chi-squared 2800 -> 2700)
  with O ~ 4, Ne ~ 0.6
* combined snr+bkg fit and error runs -- did not check results w/ steppar yet

Let's break and jump to image creation for a little bit.

Scribbled notes on image making:
XMM SAS style pipeline to do this, probably easiest way to mosaic both
0087940201 and 0551000201 (vs. ESAS procedure).

## Notes on XMM SAS imaging procedure

First, looking at Castro+ 2011 (G296.1-0.5 study), Daniel uses the tools:
evselect, merge, eexpmap, emosaic to create his image of G296.1-0.5 from three
distinct observations (nine instrument exposures).

emosaic does the simplest possible thing: merge images (from evselect) and
divide by merged exposure maps.
> The task will only handle images which are a tangent plane projection of the
> sky, for example those created from the X and Y columns of EPIC event lists
> using evselect.
NOTE: emosaic loop does handle reprojection of input images to output frame
(by default, output to frame of first input image) -- which is what merge does
as well.  Is merge even necessary?

Comment: process of creating image mosaic should be distinguished from
operation of EPIC in mosaic mode.  This mode improves efficiency of planned
mosaicking observations by not recomputing CCD offset maps for each pointing.

## Quick and dirty attempt to make images using SAS tools only

In integrated spectrum fits, background dominates < ~0.8 keV and > ~3 keV.

Therefore create:
1. broad band image from 0.8 to 3.3 keV
2. three band images:
   - 0.8 to 1.4 keV
   - 1.75 to 2.3 keV (Si He alpha/beta)
   - 2.3 to 3.3 keV (S He alpha/beta + muck)

The region 1.4-1.75 keV is omitted to avoid strong MOS instrumental lines
We won't get information on nonthermal continuum, unfortunately.
Maybe check the Chandra observation...

0087940201:
    Started: 2016-02-02T18:23:10.000 = 13:23:10
    Finished: 2016-02-02T18:37:42.000 = 13:37:42
        (each exposure map takes ~ 2 minutes)
        (weirdly, PN exposures took ~12 seconds -- ?!?! why so fast... or why is MOS so slow...)
0551000201:
    Started: 2016-02-02T18:45:10.000 = 13:45:10
    Finished: 2016-02-02T18:57:01.000 = 13:57:01
        (MOS command runs issue warning :** eexpmap: warning (NoExpoExt), Exposure extension not found )
                (is it possible I need to rerun chainfilter...)

Working with SAS tools: see the script `quick_image.sh`
I'm not sure how ESAS selects its {x,y}image{size,min,max} values.
Need to delve back into scripts.

Trial three-band image parameters:
    Bands: 0.8-1.4, 1.75-2.3, 2.3-3.3 keV 
    Net exposure time is ~(25.3 + 25.9 + 21.0 + 22.0 + 22.5) ks
    (obsids 0087940201 MOS1,MOS2,PN ; 0551000201 MOS1,MOS2)

    Bin factor 4 -> ~2.85 arcsec pixels + additional
    Gaussian smoothing, radius 10 (10 pixels?)
        (net result: image smoothed to ~ 28.5 arcsec, 2-3x PSF half-width)

    Scaling bounds:
        2e-6 to 5e-5 (red),
        1e-6 to 2.5e-5 (green),
        2e-6 to 2.5e-5 (blue)

    Aggressive colormap parameters to hide background signal

OK.  Image looks really nice, even though I haven't checked all parameter
settings.  For qualitative analysis it's probably OK.


Thursday 2016 February 4 -- spectra from smaller regions
========================================================

Select four new regions for spectral extraction, based on imaging analysis.

    src_north_clump.reg -- bright in all three bands
    src_SW_lobe.reg     -- kinda bright in all three bands...
    src_E_lobe.reg      -- less bright in red (0.8-1.4 keV)
    src_SE_dark.reg     -- X-ray dark, despite apparent radio limb

Ran usual commands to create regions in XMM detector coordinates for each
pointing.

    source sasinit 0551000201
    make_xmmregions 0551000201
    source sasinit 0087940201
    make_xmmregions 0087940201

Then set up spectrum run, starting ~1900.

    atran@statler:~/rsch/g309/xmm$ nohup /bin/tcsh -c 'source sasinit 0551000201; specbackgrp_0551000201 src_north_clump; specbackgrp_0551000201 src_SW_lobe; specbackgrp_0551000201 src_E_lobe; specbackgrp_0551000201 src_SE_dark;' >& 20160204_subsrc_0551000201.log &
    [1] 24615

    atran@cooper:~/rsch/g309/xmm$ nohup /bin/tcsh -c 'source sasinit 0087940201; specbackgrp_0087940201 src_north_clump; specbackgrp_0087940201 src_SW_lobe; specbackgrp_0087940201 src_E_lobe; specbackgrp_0087940201 src_SE_dark;' >& 20160204_subsrc_0087940201.log &
    [1] 15316

Finished around 2130 (0551000201) and 2320 (0087940201) -- this is quite slow.
But not unreasonable for extraction of four spectrum regions.


Friday 2016 February 5 -- clean up (taking advantage of nice snow day)
======================================================================

Add keywording to FWC spectrum extraction (in script for 0087940201, forgot to
update for 0551000201).  Manually add for FWC spectra from yesterday, creating:

    ${exp}-src_E_lobe-ff-key.pi
    ${exp}-src_SE_dark-ff-key.pi
    ${exp}-src_SW_lobe-ff-key.pi
    ${exp}-src_north_clump-ff-key.pi

where ${exp} runs over "mos1S001, mos2S002, pnS003".
Really need to consolidate scripts -- a lot of hassle to maintain separately.

Looking at spectrum of north clump (0087940201 MOS1) -- should not look much
different compared to integrated spectrum.  A few notes, from quick-and-dirty
fits (no background modeling, just tossing in powerlaw to account for SP
contamination)
* S/Si peaks stand out even more w.r.t. background in north clump spectrum
  preliminary fits suggest even higher Si/S abundances
* clump fit, although very rough, appears compatible with lower kT ~ 1 keV
  and higher ionization age Tau ~ 6e10.  But, fit to integrated src spectrum
  (kT ~ 3.4 keV, Tau ~ 1.9e10) with same procedure does NOT match the combined
  fitting results very well (kT ~ 1.7 keV, Tau ~ 2.4e10 from Jan 26).  I don't
  think we should believe these numbers too much; only robust indication is
  concentration of S and Si in this clump

Reduced chi-squared ~ 2.7 with just fits to `tbabs*vnei, powerlaw, gauss+gauss`
Ignoring cosmic X-ray background here, on assumption that its contribution is
small -- although, looking at previous combined fits, the XRB makes a
significant contribution around 0.3 to 1 keV

TODOs:
* remove some temporary files/spectra
* clean up XSPEC dump parsing script (split_xs_out.pl, xs_bkg_plotter.py)
* refactor spectrum fitting code -- either go back to PyXSPEC, write some
  templating code, or whatever is necessary...

End goal is to fit all sub-region spectra

Cleanup
-------
Move merged images, spectrum fit outputs (`*.dat` files) into folders
`results_img` and `results_spec`.

Refactored specbackgrp code into single, much more succinct bash script.
(caught/removed subtle, though unimportant, logging error in the process)

COMMENT: cflim parameter to mos-spectra is actually ignored.  Revolution number
for 0551000201 is 1692 < 2382, which is when the bad edge actually appeared on
MOS1 due to loss of MOS1 CCD3 (which is obviously still in our data).  Woops.

QUESTION: line 581 of mos-spectra, why is elow set to cflim?...
    rot-im-det-sky mode=4, mode=5 are NOT documented on ESAS cookbook
    Similarly passing mode=4,5 to rot-det-sky is not documented either.

    Anyways should ask...

Tested specbackgrp by commenting out commands (`*-spectra, *_back, grppha`) to
ensure everything resolves correctly.  Just a manual check, but should be
enough for our needs.

Awesome: test out by running entire script pipeline

    atran@statler:~/rsch/g309/xmm$ nohup /bin/tcsh -c './masterscript.tcsh 0087940201' >& 20160205_all_spec_rerun_0087940201.log &
    [1] 4336
    atran@cooper:~/rsch/g309/xmm$ nohup /bin/tcsh -c './masterscript.tcsh 0551000201' >& 20160205_all_spec_rerun_0551000201.log &
    [1] 24700

Started around 16:19p, finished 20:18p (0551000201) and 22:58 (0087940201).
Six region extractions in total requires ~7hrs.


Monday 2016 February 08 -- more cleanup, snr&bkg combined fit tweaks
====================================================================

## Adjustment and added caveat for SNR and bkg combined fit

Previously, BACKSCAL ratios accounted for geometric area being sampled in
different spectra; this was used to compare XRB across background and source
region fits.  This actually needs to be adjusted -- region sizes also vary a
comparable amount between exposures of same region too, due to different CCD
setups and slightly different pointings / alignments.

Is this correct?
- model is already folded through ARF, but ARF merely accounts for detector
  efficiency.
- if I fit XRB to a region in background, the norm result increases
  based on the area being sampled.
- therefore, XRB needs to have pre-factors for ALL data groups to account for
  differing extraction region sizes.

Modify script `bkg2src_norm` to handle this, and adjust fits accordingly...

Since the source region is slightly different between observations (missing
chips etc.), different exposures are sampling __slightly__ different parts of
the remnant!  This is hard to avoid/address for combined fits of SNR.
Ignore for now; source regions are more consistent in area than background,
being closer to optical axis.  This discrepancy is relatively small and only
occurs at edges of source region.

This could be important for small sub-regions within source.

## Bug catch in specbackgrp

Accidentally grouped non-OOT-subtracted spectra for PN exposure
(forgot to put `${os}` in grppha infile parameter)
Manually re-run correct command with short shell script:

    #!/bin/bash

    exp="pnS003"
    RSTEMS="src bkg src_north_clump src_SW_lobe src_E_lobe src_SE_dark"
    for RSTEM in $RSTEMS; do
      # Bin and set keywords for observation object spectra
      os="-os"
      grppha infile="${exp}-${RSTEM}${os}.pi" outfile="!${exp}-${RSTEM}${os}-grp50.pi" \
          comm="chkey BACKFILE ${exp}-${RSTEM}-qpb.pi & \
                chkey RESPFILE ${exp}-${RSTEM}.rmf & \
                chkey ANCRFILE ${exp}-${RSTEM}.arf & \
                group min 50 & exit" \
          chatter=10 \
        >& "grppha_${exp}-${RSTEM}${os}.log"
    done

OK.  Executed for 0087940201 PN exposures (6 spectrum files + 6 logs affected).

## Modifying pipeline to fit multiple region spectra

Need to integrate a few things that are currently being done by hand:
* FWC data fit to get instrumental line ratios (`ff_pn.xcm, ff_mos.xcm`)
  (scripted in pyxspec -- data interchange tbd)
* backscal value extraction (`bkg2src_norm`)
  (updated bash script behavior to output useful values)
* import the FWC instrument lines and backscal values.  for each region + bkg
  fit with 10 data groups, import 13 (bkg) + 13 (src) line norm values + 10
  backscal ratios = 36 constant terms
* after fit, script data dump (to .dat files) and plotting (`split_xs_out.pl`
  and `xs_replotter.py`)

Removed old `back_*.xcm` fitting scripts, superseded by `back_all.xcm` and
`snr_and_back.xcm`.

Must move to pyXspec for fitting, as previously started from 2016 Jan 15.
Although time-consuming, better than copy-pasting 36 x 5 = 180 constant terms
in individual XSPEC xcm files for different regions.

Possible, but cumbersome, to continue extracting and copying numbers by hand


Tuesday 2016 February 09 -- plots and tagup discussion, plots, 
====================================================================

## Plots

See images in `results_interm/`:

    20160202_quick_image_all_rgb.png
    20160202_quick_image_red_0.8-1.4kev.png
    20160202_quick_image_green_1.75-2.3kev.png
    20160202_quick_image_blue_2.3-3.3kev.png
    20160202_quick_image_all_rgb_withradio.png

    20160209_subsrc_and_src_spec.png
    20160209_subsrc_regs_and_mosaic.png
    20160209_xsreplot_snr.png
    20160209_xsreplot_snr_delch.png

The two images `20160209_subsrc_*.png` I printed out and annotated.
On the spectrum plot: cyan = integrated source, black = north clump,
red = SW lobe, green = E lobe, blue = SE dark.
(also, need to compare to background)

Spectra are not scaled to extraction area, so just represent counts.
Plots are as usual scaled to highlight faint features etc.

## Meeting discussion

Morphological features of interest:
* arcing ridge of emission in 0.8-1.4 keV image (appears to extend farther out than in 2.3-3.3 hard image)
* X-ray dark SE radio limb

SNRs to look at:
* MSH 11-61A = G290.1-0.8 (ASCA study by Pat; recent paper by Katie Auchettl)
* CTB109 (Castro+ 2011)

Suggestions for resolved spectroscopy:
* try fixing absorption nH values based on integrated fit.
  if fits w/ fixed nH don't work out, it might indicate variation in foreground
  x-ray absorption along different lines of sight.
* yes, do fix XRB values to those inferred from integrated fit.
  (of course, up to normalization scaling -- tack on a constant too to be sure)
  (still need to deal with FWC data)
* try extracting spectrum from annular regions, specifically to probe the arc
  of emission
  I think one of the G290.1-0.8 papers did this systematically
  (I don't know how we're doing on counts, if we have enough to do this..).

Additional misc. discussion on CXO target distribution on sky,
quantifying impact to thermal budgets; thermal modeling.


Friday 2016 February 19 -- Sunday 2016 February 21
==================================================

## Misc. comments on CTB 109 (G109.1-1.0) and MSH 11-61A (G290.1-0.8)
 
In elapsed time: some paper reading.
Other remnants with radio shells and center-filled X-ray emission

CTB 109 (G109.1-1.0)
* Discovered 1980 w/ Einstein
* contains magnetar = highly magnetized neutron stars
  1E 2259+586 (T = 6.98s)
* Castro+ 2011, Fermi-LAT and archived XMM-Newton analysis
  - Semi-circular shell in X-ray and radio apparent
  - GMC to west of remnant; X-ray/radio remnant is darker there.
  - XMM-Newton data: ~28-29ks of MOS exposure (remnant is quite bright, appears
  to have ~10 cts/s at 1 keV)
  Model: `tbabs*sedov` with parameters
    nH = 0.67e22
    kT_shock = 0.38 keV
    kT_electron = 0.18 keV
    n_e * t = 1.27e12
    F_abs = 6.7e-11 erg / (cm^2 s^1)    (average absorbed flux from 0.5-5 keV)
    F_unabs = 7.9e-10

MSH 11-61A (G290.1-0.8)
* Auchettl+ 2015 (HI, CO, archived Suzaku, Fermi-LAT data)
  - MM SNRs: thermal interior, ISM composition; limb bright radio profiles
    1. "cloudlets" unaffected by shock, slowly evaporate
       (mechanism to concentrate and heat ISM material behind shock)
    2. thermal conduction?? transfers heat/material to remnant center
  - MSH 11-61A: shell SNR with ear-like features, identified in radio
    angular size 19' x 11' (elongated)
  - recombining plasma claimed in Suzaku analysis...
  - estimates of ejecta masses based on measured abundances,
    and assuming all ejecta have been shocked
* Slane+ 2002 (ASCA GIS data)
  - Figure 1 - morphologically very similar!  limb ridge (very brightened)
    and ears.  ears not as dramatically bright as in G309.2-0.6.
  - filled center.  ASCA + MOST data look very similar in morphology,
  - They disfavor ejecta based on lack of abundance variation w.r.t. radius.
    I'm not sure how they can discern this with fuzzy data.
* Garcia+ 2012 (Chandra, XMM)
  - funky morphology -- ears are x-ray bright.

Both papers toss in a broadband modeling component.

My questions:
* why would ramming a giant molecular cloud cause x-ray emission to turn off?
* how do we understand SNR morphological classes?  look over reviews.
* why does the reverse shock occur as an "isolated" event?
  during adiabatic expansion (M_swept ~ M_ejecta)
  if the equations are self-similar then there is no "preferred" time
  where this discontinuity should occur.

## Reading on background emission

Quick query: how uniform is the X-ray background?
Answer: hard to say.  In brightness, certainly variable.  But, over what
lengthscales?  See start of notes in text.tex.

## Spectral fitting work

Where did I leave off?

* bkg2scal -- took a look at backscal ratio values (per my notes on Feb 08).
  By eye, estimated the bkscale values to be correct -- MOS2 CCD5 exclusion
  does not touch source, but affects bkg area.  OK.

    To remind myself: XSPEC fits model * rmf * arf to counts/sec data.
    UNLESS we explicitly include in model, we have no information about
    geometric sky area.  This makes sense, e.g., for point sources -- as long
    as the region encloses the entire PSF, we should NOT incorporate
    information about region size; this only matters for extended sources.

  I updated the prefixed constant terms in the XRB model for the combined snr
  and bkg fit.  This is a 10-20% effect, strongest effect for 0551000201 region
  fits.  So fit results will change; we will need to re-run error commands and
  re-assess chi-squared space behavior.

* sub-region fitting procedure (continuing to modify pipeline)
  - Bayesian fitting analysis?, to characterize uncertainty in parameters
    and parameter propagation (and, integrate out the nuisance parameters)
    Likely more robust than error command.
  - for now, freeze bkg parameters to those inferred from fit...
    extra floating SP powerlaw in subsrc-region-fit should pick up any
    discrepancy caused by varying SP powerlaw(s) in main fit.

## Revised combined snr+bkg fit

After making backscal value changes, the fit parameter space changes, and the
fit "path" also changes. Here I retrace the main steps:

1. initial fit (norms, SP indices free)

   SP indices go nuts
     0087940201 PNS003 src -> 0.6
     0087940201 PNS003 bkg -> -1.82
     0551000201 MOS1S001/MOS2S002 bkg -> ~0

     chisqr/dof = 17678/3775 = 4.683

2. thaw snr:1,2,16 ; fit

   Converges on MUCH saner values of SP index.
   0087940201 PNS003 bkg ~ 0 at this point
   All other SP indices floating between 0.3 to 0.45, seems reasonable.

   Fit for SNR model is funky (nH ~ 4, tau ~ 7e10, kT ~ 0.7), but that's OK.
   Si signal is evident in residuals; but in fact I cannot say S is present
   with any conviction.

    chisqr/dof = 6830.3/3772 = 1.811

3. thaw snr:10 ; fit

   Zooming in (iplot ; rescale X 2 3 ; rescale Y 0.01 2),
   there is definitely a Sulfur line present.  Continue.

    chisqr/dof = 5405/3771 = 1.433

4. thaw snr:11 ; fit

   Fit looks pretty good.  Vague bump around 0.5-1keV in residuals.
   But I have not thawed XRB parameters yet.
   SP index for PN S003 bkg is still at ~0.

    chisqr/dof = 4803/3770 = 1.274

5. thaw xrb:2,6,9; fit

   Fit looks to be running amok a bit.  XRB converged to weird values:
     unabs kT ~0.095
     abs kT ~0.29
     abs nH ~0.19
   SP power law indices strayed farther away:
     PNS003 bkg -> -0.31
     PNS003 src -> 0.025

   overall indices became harder.  Qualitatively this makes sense:
   decreased absorption means thermal plasmas contribute more to soft
   emission; for fixed contribution to high-energy tail, SP power law can be
   less steep.

    chisqr/dof = 4460/3767 = 1.184

6. newpar xrb:6 1 ; freeze xrb:6 ; fit ; thaw xrb:6 ; fit

    chisqr/dof = 4489.6/3768 = 1.19 after fit w/ frozen xrb nH

   Fit became seemingly rigid: "converged" to 4489.6/3767 = 1.191
   SP indices returned to larger (softer SP spectrum) values, which
   makes sense.
   SNR fit as follows:
    SNR nH ~ 2.25
    SNR kT ~ 1.39
    SNR Si ~ 4.24
    SNR S  ~ 3.81
    SNR Tau~ 2.8e10
    SNR norm 5.85e-3
   OK...  slightly different than fit results before (w/ wrong backscal values
   for XRB).  SNR fit values are not unreasonable; cannot be rejected out of
   hand.  But would be nice to understand variation in XRB fit parameters,
   especially with SP indices free to float.
   Make sure SNR fits don't jump like crazy.

7. steppar xrb:6 0.7 1.2

    XSPEC12>steppar xrb:6 0.7 1.2

         Chi-Squared    Delta           xrb:nH
                     Chi-Squared             6

              4498.9      9.3802    0         0.7
              4493.6      4.0743    1        0.75
              4489.5   -0.060003    2         0.8
              4486.8     -2.7976    3        0.85
              4485.7     -3.8049    4         0.9
              4486.7     -2.8965    5        0.95
              4489.6   0.0023685    6           1
              4494.5      4.9652    7        1.05
              4490.1     0.57781    8         1.1
              4491.9      2.3351    9        1.15
              4494.7      5.2008   10         1.2

    A new best fit was found during steppar.
    Parameters have been updated to the new best fit values.

8. steppar xrb:6 1.5 2.0

At this line-of-sight we expect galactic nH to be somewhat higher...
But the fit disfavors this (why?)

    XSPEC12>steppar xrb:6 1.5 2.0 

         Chi-Squared    Delta           xrb:nH
                     Chi-Squared             6

              4532.5      46.782    0         1.5
              4541.6      55.901    1        1.55
              4551.7      65.961    2         1.6
              4562.9      77.116    3        1.65
              4574.4      88.629    4         1.7
              4586.5      100.75    5        1.75
              4598.9      113.13    6         1.8
              4611.6      125.83    7        1.85
              4624.4      138.64    8         1.9
              4637.1      151.39    9        1.95
              4650.3      164.55   10           2

9. error xrb:2,6,9 ; error snr:1,2,10,11,16

Working off of best fit with nH = 0.9...

    XSPEC12>error xrb:2,6,9 ; error snr:1,2,10,11,16 ;
     Parameter   Confidence Range (2.706)
         2     0.196017     0.213212    (-0.00846654,0.00872889)
    Apparent non-monotonicity in statistic space detected.
    Current bracket values 0.9, 1.06377
    and delta stat 0, 3.94511
    but latest trial 1.01623 gives 5.1584
    Suggest that you check this result using the steppar command.
         6     0.815447     0.981884    (-0.0845527,0.081884)
    Apparent non-monotonicity in statistic space detected.
    Current bracket values 0.325315, 0.325314
    and delta stat 2.48915, 2.7233
    but latest trial 0.325314 gives 2.72336
    Suggest that you check this result using the steppar command.
    Apparent non-monotonicity in statistic space detected.
    Current bracket values 0.363392, 0.379575
    and delta stat 0.692145, 2.95434
    but latest trial 0.378223 gives 3.14001
    Suggest that you check this result using the steppar command.
         9     0.325314     0.371484    (-0.0253839,0.0207853)

     Parameter   Confidence Range (2.706)
    Apparent non-monotonicity in statistic space detected.
    Current bracket values 2.39412, 2.39741
    and delta stat 2.52063, 2.74404
    but latest trial 2.39686 gives 2.74571
    Suggest that you check this result using the steppar command.
         1      2.17868      2.39577    (-0.118616,0.0984694)
    Apparent non-monotonicity in statistic space detected.
    Current bracket values 1.1536, 1.14912
    and delta stat 2.45146, 3.13336
    but latest trial 1.1521 gives 2.42621
    Suggest that you check this result using the steppar command.
         2      1.15136      1.52398    (-0.123406,0.249218)
    ***Warning: Identical values of the parameter give different values of the statistic.
    Please check your result for the high end of the confidence range.
        10      4.00354      4.44167    (-0.214732,0.223393)
        11      3.51487      4.11332    (-0.292924,0.305522)
    Apparent non-monotonicity in statistic space detected.
    Current bracket values 2.58031e+10, 2.52502e+10
    and delta stat 2.061, 2.7316
    but latest trial 2.52757e+10 gives 3.22046
    Suggest that you check this result using the steppar command.
    Apparent non-monotonicity in statistic space detected.
    Current bracket values 3.61511e+10, 3.67984e+10
    and delta stat 2.6795, 3.18055
    but latest trial 3.61858e+10 gives 2.66074
    Suggest that you check this result using the steppar command.
        16  2.55267e+10  3.64747e+10    (-4.99535e+09,5.95274e+09)
    XSPEC12>

10. steppar log xrb:6 0.01 0.2

    XSPEC12>steppar log xrb:6 0.01 0.2

         Chi-Squared    Delta           xrb:nH
                     Chi-Squared             6

                4468     -17.784    0        0.01
                4460     -25.778    1    0.013493
              4454.3     -31.431    2    0.018206
              4448.3     -37.473    3    0.024565
              4442.5     -43.246    4    0.033145
              4438.3     -47.453    5    0.044721
              4436.3     -49.415    6    0.060342
                4438     -47.721    7    0.081418
              4443.7     -42.048    8     0.10986
              4453.1     -32.689    9     0.14823
              4464.7      -21.06   10         0.2

    A new best fit was found during steppar.
    Parameters have been updated to the new best fit values.

We find a local minimum at nH ~ 0.06.  chisqr 4436/3767 = 1.178 is the best fit
I've seen so far (compare chisqr/dof = 4460/3767 = 1.184 with nH=0.19).

Converges to best fit with absorbed kT ~ 0.77...
SNR parameters seem somewhat robust w.r.t. this.

As a preliminary quick-look, try fitting 0087940201 MOS1S001 "src_north_clump"
region.  Review what data inputs are needed, and how fit turns out based on
fixed background assumption.

Usual procedure:
1. set up all parameters
2. fit with norms and SP index free
3. fit with snr:1,2,16 free (nH, kT, Tau)
4. free snr:10,11 and refit, in succession (visually verifying line residuals)

Saved some files:

    20160222_stuff_for_northclump_fit.txt
    20160222_northclump_fit_0087940201_mos1S001_bkg-nH-0.9.png
    20160222_northclump_fit.log

where bkg-nH-0.9 indicates that I used x-ray background values fixed based on
best fit to total SNR and background that had nH ~ 0.9 (although not the global
best fit, it was the best fit I got with a "reasonable" value for nH for this
galactic line of sight).

"Standard" procedure fit:

    ==========================================================================================
     Variances and Principal Axes
               instr:1    snr:1    snr:2   snr:10   snr:11   snr:16   snr:18     sp:1     sp:2  
     2.2014E-08| -0.0004   0.0029  -0.0210  -0.0006  -0.0002  -0.0000  -0.9936   0.0009  -0.1106  
     1.4161E-07|  0.0000  -0.0001   0.0003   0.0003   0.0000  -0.0000   0.1106   0.0178  -0.9937  
     7.9203E-04| -0.0250   0.2867   0.9559  -0.0119   0.0484   0.0000  -0.0192  -0.0232  -0.0023  
     2.0126E-03|  0.0185  -0.1151   0.0585  -0.0345   0.0024   0.0000  -0.0026   0.9907   0.0175  
     1.3462E-02| -0.9484   0.2641  -0.1006   0.1309  -0.0050  -0.0000   0.0031   0.0589   0.0014  
     1.9459E-02|  0.3122   0.8583  -0.2372   0.2904  -0.1055  -0.0000   0.0070   0.1183   0.0028  
     9.5088E-01| -0.0440   0.1050   0.0019  -0.5582  -0.8219   0.0000   0.0008  -0.0046  -0.0002  
     1.6681E-01| -0.0121   0.2951  -0.1262  -0.7653   0.5577  -0.0000   0.0039   0.0140   0.0004  
     2.4653E+15| -0.0000   0.0000   0.0000  -0.0000  -0.0000  -1.0000  -0.0000  -0.0000  -0.0000  
    ------------------------------------------------------------------------------------------

    ============================================================================================================
      Covariance Matrix
            1           2           3           4           5           6           7           8           9   
       2.415e-02  -7.371e-03   7.244e-03   1.269e-02   8.681e-03  -6.483e+09  -1.853e-04  -2.604e-04  -8.376e-06
      -7.371e-03   4.252e-02  -1.382e-02  -8.181e-02  -4.414e-02   3.303e+09   4.699e-04   2.400e-03   5.870e-05
       7.244e-03  -1.382e-02   1.096e-02   2.809e-03  -3.368e-02  -5.671e+09  -2.599e-04  -1.203e-03  -3.550e-05
       1.269e-02  -8.181e-02   2.809e-03   4.140e-01   4.000e-01   9.612e+09  -6.578e-04   1.973e-03   6.664e-05
       8.681e-03  -4.414e-02  -3.368e-02   4.000e-01   7.637e-01   1.876e+10   1.401e-04   5.857e-03   1.910e-04
      -6.483e+09   3.303e+09  -5.671e+09   9.612e+09   1.876e+10   5.076e+21   1.152e+08   3.343e+08   1.108e+07
      -1.853e-04   4.699e-04  -2.599e-04  -6.578e-04   1.401e-04   1.152e+08   7.136e-06   2.690e-05   7.624e-07
      -2.604e-04   2.400e-03  -1.203e-03   1.973e-03   5.857e-03   3.343e+08   2.690e-05   2.369e-03   4.478e-05
      -8.376e-06   5.870e-05  -3.550e-05   6.664e-05   1.910e-04   1.108e+07   7.624e-07   4.478e-05   1.011e-06
    ------------------------------------------------------------------------------------------------------------

    ========================================================================
    Model instr:constant<1>(gaussian<2> + gaussian<3>) Source No.: 2   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
       1    1   constant   factor              0.930634     +/-  0.155396     
       2    2   gaussian   LineE      keV      1.49000      frozen
       3    2   gaussian   Sigma      keV      0.0          frozen
       4    2   gaussian   norm                8.60299E-03  frozen
       5    3   gaussian   LineE      keV      1.75000      frozen
       6    3   gaussian   Sigma      keV      0.0          frozen
       7    3   gaussian   norm                3.87235E-03  frozen
    ________________________________________________________________________


    ========================================================================
    Model snr:TBabs<1>*vnei<2> Source No.: 3   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
       1    1   TBabs      nH         10^22    3.04943      +/-  0.206202     
       2    2   vnei       kT         keV      0.684728     +/-  0.104673     
       3    2   vnei       H                   1.00000      frozen
       4    2   vnei       He                  1.00000      frozen
       5    2   vnei       C                   1.00000      frozen
       6    2   vnei       N                   1.00000      frozen
       7    2   vnei       O                   1.00000      frozen
       8    2   vnei       Ne                  1.00000      frozen
       9    2   vnei       Mg                  1.00000      frozen
      10    2   vnei       Si                  5.74772      +/-  0.643453     
      11    2   vnei       S                   5.87761      +/-  0.873918     
      12    2   vnei       Ar                  1.00000      frozen
      13    2   vnei       Ca                  1.00000      frozen
      14    2   vnei       Fe                  1.00000      frozen
      15    2   vnei       Ni                  1.00000      frozen
      16    2   vnei       Tau        s/cm^3   1.27150E+11  +/-  7.12445E+10  
      17    2   vnei       Redshift            0.0          frozen
      18    2   vnei       norm                7.06385E-03  +/-  2.67124E-03  
    ________________________________________________________________________


    ========================================================================
    Model sp:powerlaw<1>*constant<2> Source No.: 4   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
       1    1   powerlaw   PhoIndex            0.312233     +/-  4.86717E-02  
       2    1   powerlaw   norm                1.07603E-02  +/-  1.00525E-03  
       3    2   constant   factor              1.00000      frozen
    ________________________________________________________________________


    ========================================================================
    Model xrb:constant<1>(apec<2> + TBabs<3>(powerlaw<4> + apec<5>)) Source No.: 1   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
       1    1   constant   factor              0.215000     frozen
       2    2   apec       kT         keV      0.204483     frozen
       3    2   apec       Abundanc            1.00000      frozen
       4    2   apec       Redshift            0.0          frozen
       5    2   apec       norm                3.06343E-04  frozen
       6    3   TBabs      nH         10^22    0.900000     frozen
       7    4   powerlaw   PhoIndex            1.40000      frozen
       8    4   powerlaw   norm                3.68136E-04  frozen
       9    5   apec       kT         keV      0.350698     frozen
      10    5   apec       Abundanc            1.00000      frozen
      11    5   apec       Redshift            0.0          frozen
      12    5   apec       norm                2.83742E-03  frozen
    ________________________________________________________________________


    Fit statistic : Chi-Squared =         115.33 using 129 PHA bins.

    Test statistic : Chi-Squared =         115.33 using 129 PHA bins.
     Reduced chi-squared =        0.96108 for    120 degrees of freedom 
     Null hypothesis probability =   6.034602e-01



Highly speculative fit (instrumental line freed; Mg freed):

    ==========================================================================================
     Variances and Principal Axes
               instr:1  instr:2    snr:1    snr:2    snr:9   snr:10   snr:11   snr:16   snr:18     sp:1     sp:2  
     4.7011E-09| -0.0002   0.0001   0.0013  -0.0071  -0.0002  -0.0002  -0.0001   0.0000  -0.9990   0.0003  -0.0442  
     1.4276E-07|  0.0000   0.0003  -0.0001   0.0014   0.0000  -0.0001   0.0000   0.0000  -0.0442  -0.0179   0.9989  
     4.3505E-05| -0.0067  -0.9993  -0.0050   0.0361   0.0046  -0.0006  -0.0001   0.0000  -0.0004  -0.0008   0.0003  
     8.8169E-04|  0.0041   0.0327   0.2830   0.9550  -0.0736  -0.0036   0.0309   0.0000  -0.0063  -0.0168  -0.0019  
     1.9657E-03| -0.0210  -0.0018   0.1291  -0.0565  -0.0139   0.0209  -0.0004  -0.0000   0.0010  -0.9893  -0.0176  
     1.0977E-02|  0.7616   0.0054  -0.5370   0.1757   0.2817  -0.1033  -0.0155   0.0000  -0.0021  -0.1024  -0.0023  
     1.9696E-02| -0.6118   0.0160  -0.7435   0.2209   0.0237  -0.1110   0.0341   0.0000  -0.0024  -0.0993  -0.0023  
     6.8720E-02|  0.1999  -0.0043  -0.2360   0.0038  -0.9035   0.2755  -0.1082   0.0000  -0.0002  -0.0167  -0.0003  
     2.9092E-01| -0.0726   0.0038  -0.0426   0.0594   0.2762   0.6441  -0.7059   0.0000  -0.0006   0.0026   0.0000  
     6.0946E+00|  0.0041   0.0010  -0.0677   0.0115   0.1475   0.6970   0.6984  -0.0000  -0.0004   0.0028   0.0001  
     1.5463E+17|  0.0000   0.0000  -0.0000   0.0000   0.0000   0.0000   0.0000   1.0000  -0.0000   0.0000   0.0000  
    ------------------------------------------------------------------------------------------

    ====================================================================================================================================
      Covariance Matrix
            1           2           3           4           5           6           7           8           9          10          11   
       2.641e-02  -5.256e-04  -6.354e-03   8.902e-03  -1.830e-02   1.075e-02  -1.708e-02  -8.386e+09  -7.868e-05  -2.725e-04  -7.667e-06
      -5.256e-04   6.912e-05  -4.140e-04  -1.125e-04   1.638e-03   4.567e-03   4.851e-03   2.666e+08  -1.036e-06   4.039e-06   1.947e-07
      -6.354e-03  -4.140e-04   5.198e-02  -1.858e-02  -4.689e-02  -2.999e-01  -2.392e-01   6.853e+09   2.893e-04   1.240e-03   2.476e-05
       8.902e-03  -1.125e-04  -1.858e-02   1.855e-02   7.708e-03   6.276e-02  -2.623e-02  -1.113e+10  -1.755e-04  -8.804e-04  -2.716e-05
      -1.830e-02   1.638e-03  -4.689e-02   7.708e-03   2.160e-01   6.592e-01   6.115e-01   5.916e+09  -3.248e-04   3.755e-03   9.802e-05
       1.075e-02   4.567e-03  -2.999e-01   6.276e-02   6.592e-01   3.088e+00   2.818e+00  -2.561e+09  -1.781e-03   1.229e-02   3.513e-04
      -1.708e-02   4.851e-03  -2.392e-01  -2.623e-02   6.115e-01   2.818e+00   3.391e+00   4.812e+10  -1.013e-03   1.405e-02   4.309e-04
      -8.386e+09   2.666e+08   6.853e+09  -1.113e+10   5.916e+09  -2.561e+09   4.812e+10   8.488e+21   9.020e+07   4.457e+08   1.463e+07
      -7.868e-05  -1.036e-06   2.893e-04  -1.755e-04  -3.248e-04  -1.781e-03  -1.013e-03   9.020e+07   2.178e-06   2.933e-06   8.924e-08
      -2.725e-04   4.039e-06   1.240e-03  -8.804e-04   3.755e-03   1.229e-02   1.405e-02   4.457e+08   2.933e-06   2.326e-03   4.392e-05
      -7.667e-06   1.947e-07   2.476e-05  -2.716e-05   9.802e-05   3.513e-04   4.309e-04   1.463e+07   8.924e-08   4.392e-05   9.913e-07
    ------------------------------------------------------------------------------------------------------------------------------------

    ========================================================================
    Model instr:constant<1>(gaussian<2> + gaussian<3>) Source No.: 2   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
       1    1   constant   factor              0.855599     +/-  0.162502     
       2    2   gaussian   LineE      keV      1.51005      +/-  8.31361E-03  
       3    2   gaussian   Sigma      keV      0.0          frozen
       4    2   gaussian   norm                8.60299E-03  frozen
       5    3   gaussian   LineE      keV      1.75000      frozen
       6    3   gaussian   Sigma      keV      0.0          frozen
       7    3   gaussian   norm                3.87235E-03  frozen
    ________________________________________________________________________


    ========================================================================
    Model snr:TBabs<1>*vnei<2> Source No.: 3   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
       1    1   TBabs      nH         10^22    2.63116      +/-  0.227983     
       2    2   vnei       kT         keV      0.784386     +/-  0.136207     
       3    2   vnei       H                   1.00000      frozen
       4    2   vnei       He                  1.00000      frozen
       5    2   vnei       C                   1.00000      frozen
       6    2   vnei       N                   1.00000      frozen
       7    2   vnei       O                   1.00000      frozen
       8    2   vnei       Ne                  1.00000      frozen
       9    2   vnei       Mg                  1.94200      +/-  0.464721     
      10    2   vnei       Si                  8.85972      +/-  1.75721      
      11    2   vnei       S                   8.36059      +/-  1.84144      
      12    2   vnei       Ar                  1.00000      frozen
      13    2   vnei       Ca                  1.00000      frozen
      14    2   vnei       Fe                  1.00000      frozen
      15    2   vnei       Ni                  1.00000      frozen
      16    2   vnei       Tau        s/cm^3   1.66994E+11  +/-  9.21319E+10  
      17    2   vnei       Redshift            0.0          frozen
      18    2   vnei       norm                3.27565E-03  +/-  1.47575E-03  
    ________________________________________________________________________


    ========================================================================
    Model sp:powerlaw<1>*constant<2> Source No.: 4   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
       1    1   powerlaw   PhoIndex            0.317588     +/-  4.82322E-02  
       2    1   powerlaw   norm                1.08761E-02  +/-  9.95620E-04  
       3    2   constant   factor              1.00000      frozen
    ________________________________________________________________________


    ========================================================================
    Model xrb:constant<1>(apec<2> + TBabs<3>(powerlaw<4> + apec<5>)) Source No.: 1   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
       1    1   constant   factor              0.215000     frozen
       2    2   apec       kT         keV      0.204483     frozen
       3    2   apec       Abundanc            1.00000      frozen
       4    2   apec       Redshift            0.0          frozen
       5    2   apec       norm                3.06343E-04  frozen
       6    3   TBabs      nH         10^22    0.900000     frozen
       7    4   powerlaw   PhoIndex            1.40000      frozen
       8    4   powerlaw   norm                3.68136E-04  frozen
       9    5   apec       kT         keV      0.350698     frozen
      10    5   apec       Abundanc            1.00000      frozen
      11    5   apec       Redshift            0.0          frozen
      12    5   apec       norm                2.83742E-03  frozen
    ________________________________________________________________________


    Fit statistic : Chi-Squared =         104.82 using 129 PHA bins.

    Test statistic : Chi-Squared =         104.82 using 129 PHA bins.
     Reduced chi-squared =        0.88832 for    118 degrees of freedom 
     Null hypothesis probability =   8.018346e-01



Tuesday 2016 February 23 - sub-source fitting with all exposures
================================================================

* Modified `ff_fit.py` to start spewing out line normalizations
  (few more edits and it's almost done)
* Setup (read: mostly copy pasted) XSPEC commands to fit individual sub-regions
  (`snr_northclump.xcm` -- currently only set up for north clump region
   because instrumental line values, backscal ratios are copy-pasted by hand.)
  Must refactor this.  Almost tempted to just do a templating script instead
  of using PyXSPEC.  It is nice to have the interactive XSPEC environment.

  Weird blend of pipeline and interactive work.  I think the approach should be
  1. have a script handle the initial XSPEC setup.
  2. have some manual (interactive) commands take care of fitting
     and record notes on fitting process

Fit for north-clump with only Si/S free.  Usual assignments for data groups
(0087940201 mos1,mos2,pn;0551000201 mos1,mos2).
NOTE: PNS003 4.0-6.0 keV excised because of unmodeled instrumental lines in FWC
data.

    ========================================================================
    Model instr:constant<1>(gaussian<2> + gaussian<3> + gaussian<4> + gaussian<5> + gaussian<6> + gaussian<7>) Source No.: 2   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
                               Data group: 1
       1    1   constant   factor              0.945084     +/-  0.117919     
                               Data group: 2
      20    1   constant   factor              1.04559      +/-  0.121054     
                               Data group: 3
      39    1   constant   factor              0.603920     +/-  0.120828     
                               Data group: 4
      58    1   constant   factor              1.70397      +/-  0.151947     
                               Data group: 5
      77    1   constant   factor              1.73333      +/-  0.143367     
    ________________________________________________________________________


    ========================================================================
    Model snr:TBabs<1>*vnei<2> Source No.: 3   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
                               Data group: 1
       1    1   TBabs      nH         10^22    2.93431      +/-  8.17693E-02  
       2    2   vnei       kT         keV      0.800561     +/-  5.78135E-02  
       3    2   vnei       H                   1.00000      frozen
       4    2   vnei       He                  1.00000      frozen
       5    2   vnei       C                   1.00000      frozen
       6    2   vnei       N                   1.00000      frozen
       7    2   vnei       O                   1.00000      frozen
       8    2   vnei       Ne                  1.00000      frozen
       9    2   vnei       Mg                  1.00000      frozen
      10    2   vnei       Si                  4.78401      +/-  0.212749     
      11    2   vnei       S                   4.68643      +/-  0.269218     
      12    2   vnei       Ar                  1.00000      frozen
      13    2   vnei       Ca                  1.00000      frozen
      14    2   vnei       Fe                  1.00000      frozen
      15    2   vnei       Ni                  1.00000      frozen
      16    2   vnei       Tau        s/cm^3   7.32953E+10  +/-  1.40958E+10  
      17    2   vnei       Redshift            0.0          frozen
      18    2   vnei       norm                5.66898E-03  +/-  8.93280E-04  
    ________________________________________________________________________


    ========================================================================
    Model sp:powerlaw<1>*constant<2> Source No.: 4   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
                               Data group: 1
       1    1   powerlaw   PhoIndex            0.329019     +/-  3.22172E-02  
       2    1   powerlaw   norm                5.02867E-02  +/-  3.25140E-03  
       3    2   constant   factor              0.214617     frozen
                               Data group: 2
       4    1   powerlaw   PhoIndex            0.329019     = sp:p1
       5    1   powerlaw   norm                5.25933E-02  +/-  3.41547E-03  
       6    2   constant   factor              0.207497     frozen
                               Data group: 3
       7    1   powerlaw   PhoIndex            -0.192741    +/-  0.151261     
       8    1   powerlaw   norm                3.02888E-02  +/-  9.66795E-03  
       9    2   constant   factor              0.201593     frozen
                               Data group: 4
      10    1   powerlaw   PhoIndex            0.320899     +/-  4.42407E-02  
      11    1   powerlaw   norm                4.97075E-02  +/-  4.12063E-03  
      12    2   constant   factor              0.203098     frozen
                               Data group: 5
      13    1   powerlaw   PhoIndex            0.320899     = sp:p10
      14    1   powerlaw   norm                1.37258E-02  +/-  2.03895E-03  
      15    2   constant   factor              0.205135     frozen
    ________________________________________________________________________


    ========================================================================
    Model xrb:constant<1>(apec<2> + TBabs<3>(powerlaw<4> + apec<5>)) Source No.: 1   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
                               Data group: 1
       1    1   constant   factor              0.214617     frozen
       2    2   apec       kT         keV      0.204483     frozen
       3    2   apec       Abundanc            1.00000      frozen
       4    2   apec       Redshift            0.0          frozen
       5    2   apec       norm                3.06343E-04  frozen
       6    3   TBabs      nH         10^22    0.900000     frozen
       7    4   powerlaw   PhoIndex            1.40000      frozen
       8    4   powerlaw   norm                3.68136E-04  frozen
       9    5   apec       kT         keV      0.350698     frozen
      10    5   apec       Abundanc            1.00000      frozen
      11    5   apec       Redshift            0.0          frozen
      12    5   apec       norm                2.83742E-03  frozen
                               Data group: 2
      13    1   constant   factor              0.207497     frozen
                               Data group: 3
      25    1   constant   factor              0.201593     frozen
                               Data group: 4
      37    1   constant   factor              0.203098     frozen
                               Data group: 5
      49    1   constant   factor              0.205135     frozen
    ________________________________________________________________________


    Fit statistic : Chi-Squared =         847.38 using 686 PHA bins.

    Test statistic : Chi-Squared =         847.38 using 686 PHA bins.
     Reduced chi-squared =         1.2704 for    667 degrees of freedom 
     Null hypothesis probability =   2.432245e-06


Fit looks very acceptable.  Comparing to the integrated fit, this clump fit
gives us:

            clump fit       integrated fit
    nH      2.93            2.30
    kT      0.80            1.27
    Si      4.78            4.22
    S       4.69            3.81
    Tau     7.33e+10        3.05e+10
    norm    5.67e-3         6.51e-3

Interesting.  Why the trade-off between nH,kT,Tau?

Plot: clear Si/S He-beta lines (well, ok, S He-beta is more tenuous).
Magnesium emission, both He-alpha and He-beta, is clear.
  Forcing Mg abundance to 0.1 significantly worsens fit.
    chisqr/dof = 1136.25/667 = 1.704
  Therefore, we can extract a meaningful bound on Mg abundance wrt Si/S.

SP power law indices differ slightly from combined fit.
SP power law index for PNS003 has gone bonkers.

How do we interpret this?


Tuesday 2016 February 23 - discussion
=====================================

Meeting notes:
* constraining Mg abundance... maybe worthwhile, maybe not.
* Bayesian formalism - maybe. Certainly useful to learn, but likely not
  immediately useful for this project.
* Run fits with values for absorption fixed (and step different values).
* Think about interpretation - distance. HI measurements,
  discussed rotation curve and HI spectra.
  Obtained copy of `gal_rot` code; reviewed and cleaned up code slightly
  (including finding relevant source + rederiving equations)
  day after meeting (Weds Feb 24).

Main question: given expected remnant distance (~>5kpc) and angular size, we
don't expect the remnant spectrum to be ejecta-dominated.  So, why is this?


Tuesday-Wednesday 2016 March 1-2
================================

Cleaned up notes, commit recent changes.  Continue work on PyXSPEC port of
fitting code.

Finalized `ff_fit.py` (start refactoring PyXSPEC utilities, dump diagnostic
outputs).  Ran script for all current obsids/regions/exposures to generate slew
of outputs.


PN instrumental Ti/V/Cr line analysis
-------------------------------------
Two unmodeled lines, ~4.5 and 5.5 keV, are present in 0087940201 PNS003 FWC
spectra. Qualitatively, the lines appear strongest in `src` and
`src_north_clump` regions, weaker in `SE_dark` and `SW_lobe` subregions.

XMM user's guide section 3.3.7.2 plots suggest that the lines could be
attributed to 4.4-4.6 keV Ti K-alpha and ~5.5 (5.2-5.7) keV, Cr K-alpha.
There's a faint bump around 5.0 keV that can be attributed to Vanadium as well
(~4.85-5.05 keV).  Normally Ti/Cr lines are not bright, but our source regions
are right on the Ti/Cr bright spot (Fig. 36 of user's guide)

Here I try to add either 2 or 3 lines (Ti/Cr, or Ti/V/Cr) to FWC data fits
for the regions where the Ti/Cr lines are strongest: {0087940201,0551000201}
{`src`, `src_north_clump`}.  I first fit with frozen line energies (4.5, 5,
5.5), then thaw and refit.  As usual, all widths (sigma) are frozen to 0.
Temporary new commands in `ff_fit.py` are:

    # Ti,Cr lines
    instr.gaussian_2.LineE.frozen=False
    instr.gaussian_3.LineE.frozen=False
    xs.Xset.chatter=10
    xs.Fit.perform()
    xs.Plot("ldata resid delchi")

    # Vanadium line
    instr.gaussian_4.LineE.frozen=False
    xs.Fit.perform()
    xs.Plot("ldata resid delchi")

    # Throwaway output formatting commands not shown

Fit results are summarized in:
`results-interm/20160302_PN_ti-cr-v-line_fits.xlsx` and
`results-interm/20160302_PN_ti-cr-v-line_fits.csv`

And the summary statistics are as follows:
(for 8 fits; 4 with V line, 4 without; fits are to spectra for:

                    Ti LineE    V LineE     Cr LineE    Ti/Cr ratio
    AVG (no V)      4.5355                  5.436       0.8343
    STDEV (no V)    0.0071                  0.0055
    AVG (V)         4.5395      4.923       5.438       0.8347
    STDEV (V)       0.0079      0.017       0.0057

Ti/Cr line energies agree to within uncertainty.

Fits are not fully independent since `src_north_clump` is contained in `src`.
Net effect is to artificially decrease std-dev within group of either no V or
V fits, which would actually make it more difficult for Ti/Cr line energies to
agree.  Therefore this should not affect conclusion.

Outcome: model Ti and Cr lines with zero-width Gaussians at 4.54 and 5.44 keV.
No obvious need to model V line.  Actual observation data are FAR noisier, it's
doubtful that Ti/Cr lines will make much difference.  But, since they are
evident in FWC data, to assist FWC fit we should model these.
(e.g., could add constant shift to normalizations, which would otherwise
introduce systematics in our instrumental line modeling)

Comment: if we were to fit Vanadium line, it seems that we should also fit the
Zn/Au complex around 9.6 keV to be consistent.


Does freeing PN instr line energies (Al, Cu) matter?
----------------------------------------------------
I fit FWC data with Al xor Cu line energy free for PNS003 exposures of
0087940201/0551000201, using all six current regions (src, bkg, 4 subregions).
Did not consider MOS here.

If Al line energy floats:
* LineE range is 1.477-1.497 keV (average 1.488 keV)
* Largest % improvement in reduced chi-squared, -6.7%, occurs for the
  0087940201 src region (redchisqr 3976/2192=1.81 --> 3711/2191=1.69).
  0087940201 src_SW_lobe showed similar -6.2% decrease.

If Cu K-alpha line energy (~8.05 keV) floats:
* LineE range is 8.033-8.051 (average 8.044 keV)
* Largest % improvement in reduced chi-squared is 17% (!)
  for 0087940201 bkg.
  For that particular case, fit is pretty poor to start with
  (reduced chi-squared ~ 3)
  and the fit plot (data, residuals) suggests that the Cu K-alpha line width
  needs to be non-zero.
  Line norm changes for this region's FWC spectrum are ~few %, except for
  large shift in Cu K-beta normalization (17%).  Odd.

Comment: really should get acquainted with pandas for these one-off exploratory
analyses.

Outcome: don't try twiddling energies.  Exploratory analysis did not show clear
improvement for all regions/fits (which would suggest a good systematic to
model out).

Spreadsheet of analysis saved to:
* `g309/results-interm/20160302_PN_freelineE.xlsx`
* `g309/results-interm/20160302_PN_freelineE.zip`
(zip file contains HTML version)


Current FWC line modeling
-------------------------
Currently fitting the following fluorescent K-alpha lines:

MOS
* Al 1.49 keV
* Si 1.75 keV

PN
* Al 1.49 keV (strong)
* Ti 4.54 keV (faint, most evident in `src_north_clump`)
* Cr 5.44 keV (faint, most evident in `src_north_clump`)
* Ni 7.49 keV (medium-strong)
* Cu 8.05 keV (strong)
* Zn 8.62 keV (medium)
* Cu 8.90 keV, K-beta (medium)

In MOS, 3-4 additional lines we could be modeling:
* Cr ~ 5.5 keV
* Mn ~ 6 keV
* Fe ~ 6.5 keV
* Au ~ 9.7 keV (Ly-Alpha)

In PN, we could further be modeling
* Au ~ 9.7 keV (Ly-Alpha)

MOS Fe line in particular could explain bumps at high energy.  It may be worth
including the extra lines to help constrain high-energy counts, since we are
relying heavily on high energy noise to constrain soft proton power law
contamination.  Similar argument applies for PN Au line.

Later, maybe revisit this process.  Write code to be independent of exact
set-up of FWC line fits, so I can easily go back, edit FWC fitting process, and
verify that fit outputs are NOT affected.

At that time, by MANUAL inspection of FWC data, determine which line
energies/widths could be adjusted -- bearing in mind that uncertainties are
often ~1-10% already, and that this is a very small part of the fit process.


SNR and background fit, PyXSPEC port
------------------------------------
In works, fit seems to run acceptably.

"Best" fit so far of combined remnant and background, after running:

    xs.AllModels(8,'sp').powerlaw.PhoIndex = 0.2
    xs.AllModels(8,'sp').powerlaw.PhoIndex.frozen = True
    xs.Fit.perform()
    xs.Fit.steppar("xrb:6 0.1 1.0")
    xs.Fit.steppar("xrb:6 1.1 3.1")
    xs.Fit.steppar("xrb:6 0.8 1.3")
    xs.Fit.steppar("xrb:6 1.0 1.2")

Parameters:

    ========================================================================
    Model instr:constant<1>(gaussian<2> + gaussian<3> + gaussian<4> + gaussian<5> + gaussian<6> + gaussian<7> + gaussian<8>) Source No.: 2   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
                               Data group: 1-5
       1    1   constant   factor              0.951530     +/-  4.70074E-02
      23    1   constant   factor              0.879181     +/-  4.32999E-02
      45    1   constant   factor              0.602430     +/-  2.49881E-02
      67    1   constant   factor              1.67503      +/-  6.40679E-02
      89    1   constant   factor              1.81964      +/-  5.85563E-02
                               Data group: 6-10
     111    1   constant   factor              0.684556     +/-  3.40007E-02
     133    1   constant   factor              0.646738     +/-  3.16809E-02
     155    1   constant   factor              0.662818     +/-  1.98071E-02
     177    1   constant   factor              1.47118      +/-  4.24053E-02
     199    1   constant   factor              1.49487      +/-  3.97307E-02

    ========================================================================
    Model snr:TBabs<1>*vnei<2> Source No.: 3   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
                               Data group: 1
       1    1   TBabs      nH         10^22    2.18510      +/-  4.61000E-02  
       2    2   vnei       kT         keV      1.56191      +/-  0.102379     
      10    2   vnei       Si                  4.18992      +/-  0.124351     
      11    2   vnei       S                   3.73041      +/-  0.165336     
      16    2   vnei       Tau        s/cm^3   2.55486E+10  +/-  1.94064E+09  
      18    2   vnei       norm                5.26245E-03  +/-  3.97747E-04  

    ========================================================================
    Model sp:powerlaw<1>*constant<2> Source No.: 4   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
                               Data group: 1-5
       1    1   powerlaw   PhoIndex            0.387345     +/-  1.30585E-02  
       4    1   powerlaw   PhoIndex            0.387345     = sp:p1
       7    1   powerlaw   PhoIndex            0.340018     +/-  3.60713E-02  
      10    1   powerlaw   PhoIndex            0.334435     +/-  2.48019E-02  
      13    1   powerlaw   PhoIndex            0.334435     = sp:p10
                               Data group: 6-10
      16    1   powerlaw   PhoIndex            0.336369     +/-  1.36514E-02  
      19    1   powerlaw   PhoIndex            0.336369     = sp:p16
      22    1   powerlaw   PhoIndex            0.200000     frozen
      25    1   powerlaw   PhoIndex            0.499906     +/-  3.32571E-02  
      28    1   powerlaw   PhoIndex            0.499906     = sp:p25

    ========================================================================
    Model xrb:constant<1>(apec<2> + TBabs<3>(powerlaw<4> + apec<5>)) Source No.: 1   Active/On
    Model Model Component  Parameter  Unit     Value
     par  comp
                               Data group: 1
       1    1   constant   factor              1.00000      frozen
       2    2   apec       kT         keV      0.228217     +/-  6.47199E-03  
       3    2   apec       Abundanc            1.00000      frozen
       4    2   apec       Redshift            0.0          frozen
       5    2   apec       norm                2.89804E-04  +/-  1.06025E-05  
       6    3   TBabs      nH         10^22    1.06000      +/-  6.88249E-02  
       7    4   powerlaw   PhoIndex            1.40000      frozen
       8    4   powerlaw   norm                3.09916E-04  +/-  1.28723E-05  
       9    5   apec       kT         keV      0.367863     +/-  1.78543E-02  
      10    5   apec       Abundanc            1.00000      frozen
      11    5   apec       Redshift            0.0          frozen
      12    5   apec       norm                3.28805E-03  +/-  5.81986E-04  

    Fit statistic : Chi-Squared =        4526.94 using 3805 PHA bins.
    Test statistic : Chi-Squared =        4526.94 using 3805 PHA bins.
     Reduced chi-squared =        1.20142 for   3768 degrees of freedom 
     Null hypothesis probability =   9.865386e-17



Monday 2016 March 7 -- annulus region spectra
=============================================

Create five annulus regions:
* `ann_000_100.reg`
* `ann_100_200.reg`
* `ann_200_300.reg`
* `ann_300_400.reg`
* `ann_400_500.reg`
centered on the remnant (RA,dec = 13:46:35.381,-62:54:01.44), at the same point
as the larger src and bkg regions. Annuli are 100 arcsec wide, from 0 to 100
arcsec., 100 to 200 arcsec.. etc.  For comparison, current src region is 400"
radius (6.7'), bkg region is 510-700" radius (8.5-11.7').

Run spectrum extraction for 5 annuli (0-100", 100-200", ..., 400-500").
Ran into two errors (readily rectified):
1. needed to re-run cifbuild (new XMM SAS), so added sasrepro commands to
   masterscript.tcsh
2. mos-spectra-mod run failed for 0087940201 mos1S001 on `ann_000_100`
   for some reason.  Re-ran without change and it works, must have been a
   transient bug/error...
Result: ran the following scripts via `masterscript.tcsh`:
    sasinit
    sasrepro
    make_xmmregions
    specbackgrp
    ff_fit.py

Running scripts on morning of March 8:

    atran@cooper:~/rsch/g309/xmm$ nohup /bin/tcsh -c './masterscript.tcsh 0551000201' >& 20160308_annuli_0551000201.log &
    [1] 21082
    atran@statler:~/rsch/g309/xmm$ nohup /bin/tcsh -c './masterscript.tcsh 0087940201' >& 20160308_annuli_0087940201.log &
    [1] 809


Tuesday 2016 March 8 -- wrangling fit script into a usable tool
===============================================================

Set up arguments to specify fit parameters, regions, etc.

Now I can ask to fit a specific region, and the fit script will automatically:
- load the correct response/arf files
- compute the right BACKSCAL values for x-ray background normalization
- get FWC instrumental fits
- (optional) run a sensible starting sequence of fit commands
- drop user into an interactive environment

OK.  So I think the procedure is mostly set now.

Test usage -- how does the north clump spectrum fit depend on absorption?
Procedure:
1. `%run snr_and_back.py src_north_clump`
2. `snr.TBabs.nH.frozen = True`
3. `snr.TBabs.nH = 2.0 ; xs.Fit.perform() ; xs.Plot("ldata delch") ; print_fit()`

Best fit:

    Looks pretty acceptable.  Definite waviness around 1 keV.
    Some line-like excess in PN around 6-7 keV, not sure if iron or unmodeled
    instrumental line.  Don't really expect instrumental lines in PN at 6-7
    keV, but 7-8 keV is likely a stronger-than-expected Ni line.

    reduced chi-squared = 898.06/692 = 1.298

    snr model: TBabs*vnei
      nH (10^22)    2.917 +/- 0.080
      kT   (keV)    0.814 +/- 0.059
      Si            4.78  +/- 0.21
      S             4.62  +/- 0.26
      Tau (s/cm^3)  7.31e+10 +/- 1.40e+10
      norm          5.49e-03 +/- 8.58e-04

    soft proton power laws
      Data group 1, n     0.37 +/- 0.03
      Data group 2, n     0.37 +/- 0.00
      Data group 3, n     0.20 +/- 0.00
      Data group 4, n     0.37 +/- 0.04
      Data group 5, n     0.37 +/- 0.00

nH = 2:

    Not a good fit.  A lot of structure in residuals, especially around 1-2
    keV.  SP power laws hardened a bit (index 0.37 to 0.30 for all four MOS
    exposures), decreasing contribution in soft X-ray; this seems to be in
    response to decreased nH, which increases soft SNR emission.
    SNR norm also decreased (factor of 5 (!!)), with abundances jumping a lot
    to compensate.

    reduced chi-squared = 1069.54/693 = 1.543

    snr model: TBabs*vnei
      nH (10^22)    2.000 +/- 0.080
      kT   (keV)    1.721 +/- 0.105
      Si            7.51  +/- 0.25
      S             6.70  +/- 0.31
      Tau (s/cm^3)  2.83e+10 +/- 2.17e+09
      norm          1.16e-03 +/- 4.25e-05

    soft proton power laws
      Data group 1, n     0.31 +/- 0.03
      Data group 2, n     0.31 +/- 0.00
      Data group 3, n     0.20 +/- 0.00
      Data group 4, n     0.30 +/- 0.05
      Data group 5, n     0.30 +/- 0.00

nH = 1.5:

    Not a great fit.

    reduced chi-squared = 1369.12/693 = 1.976

    snr model: TBabs*vnei
      nH (10^22)    1.500 +/- 0.080
      kT   (keV)    4.345 +/- 0.549
      Si            10.52  +/- 0.41
      S             10.08  +/- 0.46
      Tau (s/cm^3)  1.87e+10 +/- 5.27e+08
      norm          4.74e-04 +/- 1.18e-05

    soft proton power laws
      Data group 1, n     0.30 +/- 0.04
      Data group 2, n     0.30 +/- 0.00
      Data group 3, n     0.20 +/- 0.00
      Data group 4, n     0.27 +/- 0.05
      Data group 5, n     0.27 +/- 0.00


nH = 1.0:

    Completely unphysical, fit looks terrible.  continuing trend, though,
    of raising kT and ramping up Si/S like crazy.

    reduced chi-squared = 1855.79/693 = 2.678

    snr model: TBabs*vnei
      nH (10^22)    1.000 +/- 0.080
      kT   (keV)    8.509 +/- 1.671
      Si            21.82  +/- 1.34
      S             21.93  +/- 1.29
      Tau (s/cm^3)  1.98e+10 +/- 3.99e+08
      norm          1.87e-04 +/- 7.82e-06


The driver on fits is relatively low soft emission, which XSPEC tries to
explain by ramping nH up to 3e22.  Forcing lower nH drives up soft emission,
which is countered by fits converging to higher kT and higher Si/S abundances
(which become unreasonably high for fits with nH <~ 1.5).

What if we freed O, Ne, Mg, Fe?

nH = 1.5; O,Ne,Mg,Fe free

    This is actually COMPARABLE to the very best fit.
    Indeed, the residuals don't look too bad.

    reduced chi-squared = 905.73/689 = 1.315

    snr model: TBabs*vnei
      nH (10^22)    1.500 +/- 0.080
      kT   (keV)    1.310 +/- 0.101
      Si            4.30  +/- 0.30
      S             5.53  +/- 0.38
      Tau (s/cm^3)  2.52e+10 +/- 2.41e+09
      norm          2.08e-03 +/- 2.72e-04

      O             1.66E-12  +/-  0.141
      Ne            0.125     +/-  0.067
      Mg            0.52      +/-  0.075
      Si            4.30      +/-  0.30
      S             5.53      +/-  0.38
      Fe            4.74E-02  +/-  0.056

nH = 2.0; O,Ne,Mg,Fe free

    reduced chi-squared = 889.91/689 = 1.292

    snr model: TBabs*vnei
      nH (10^22)    2.000 +/- 0.080
      kT   (keV)    1.061 +/- 0.081
      Si            4.00  +/- 0.32
      S             4.71  +/- 0.35
      Tau (s/cm^3)  3.44e+10 +/- 5.53e+09
      norm          3.31e-03 +/- 5.17e-04

      O             1.94E-05  +/-  0.35
      Ne            0.36      +/-  0.12
      Mg            0.59      +/-  0.090
      Fe            0.119     +/-  0.092

nH free (converges to nH = 2.6)

    Fit really does not look bad.  Obviously better than original fit,
    albeit not by a lot.  These fits with O/Ne/Mg/Fe free are relatively
    insensitive to actual value of nH, because fit has lots of knobs to
    twiddle.

    reduced chi-squared = 880.37/688 = 1.280

    snr model: TBabs*vnei
      nH (10^22)    2.605 +/- 0.179
      kT   (keV)    0.879 +/- 0.054
      Si            4.07  +/- 0.58
      S             4.33  +/- 0.64
      Tau (s/cm^3)  5.25e+10 +/- 7.60e+09
      norm          5.11e-03 +/- 8.52e-04

      O             0.27     +/-  1.23
      Ne            1.01     +/-  0.42
      Mg            0.77     +/-  0.16
      Fe            0.20     +/-  0.16

Basically: if nH is low, we can still get reasonable kT and Si/S abundances
by driving down O,Ne,Fe emission.


Wednesday 2016 March 9 -- manually run and inspect sub-source region fits
=========================================================================

Run a fit to SE dark region
Surprisingly, I'm able to get a good fit with a substantial SNR component.

## src\_SE\_dark region fit

Example with all solar abundances: norm seems quite high, for the small area.

    reduced chi-squared = 262.04/224 = 1.170
    snr model: TBabs*vnei
      nH (10^22)    3.112 +/- 0.215
      kT   (keV)    0.684 +/- 0.151
      Si            1.00  +/- 0.33
      S             1.00  +/- 0.00
      Tau (s/cm^3)  7.21e+10 +/- 5.59e+10
      norm          2.13e-03 +/- 1.01e-03

    soft proton power laws
      Data group 1, n  0.31 +/- 0.04,  norm  4.63e-02 +/- 3.64e-03
      Data group 2, n  0.31 +/- 0.00,  norm  4.47e-02 +/- 3.64e-03
      Data group 3, n  0.20 +/- 0.13,  norm  6.29e-02 +/- 3.97e-03
      Data group 4, n  0.20 +/- 0.07,  norm  4.26e-02 +/- 5.73e-03
      Data group 5, n  0.20 +/- 0.00,  norm  6.89e-03 +/- 2.02e-03

    instrumental lines
      Data group 1, instr const  0.57 +/- 0.11
      Data group 2, instr const  0.51 +/- 0.11
      Data group 3, instr const  0.64 +/- 0.05
      Data group 4, instr const  1.72 +/- 0.18
      Data group 5, instr const  1.62 +/- 0.16

Example with Si free:

    reduced chi-squared = 224.17/223 = 1.005
    snr model: TBabs*vnei
      nH (10^22)    2.537 +/- 0.224
      kT   (keV)    0.752 +/- 0.185
      Si            2.48  +/- 0.36
      S             1.00  +/- 0.00
      Tau (s/cm^3)  8.22e+10 +/- 7.89e+10
      norm          9.96e-04 +/- 5.06e-04

    soft proton power laws
      Data group 1, n     0.31 +/- 0.04
                    norm  4.67e-02 +/- 3.64e-03
      Data group 2, n     0.31 +/- 0.00
                    norm  4.51e-02 +/- 3.64e-03
      Data group 3, n     0.20 +/- 0.13
                    norm  6.37e-02 +/- 3.96e-03
      Data group 4, n     0.21 +/- 0.07
                    norm  4.38e-02 +/- 5.74e-03
      Data group 5, n     0.21 +/- 0.00
                    norm  7.48e-03 +/- 2.06e-03

    instrumental lines
      Data group 1, instr const  0.61 +/- 0.11
      Data group 2, instr const  0.56 +/- 0.11
      Data group 3, instr const  0.65 +/- 0.05
      Data group 4, instr const  1.78 +/- 0.18
      Data group 5, instr const  1.69 +/- 0.17

Example with NO SNR component (norm frozen to zero):
(started new fit with default parameters, set SNR norm to zero, then fit, to
avoid fit being stuck / influenced by previous fit with SNR model)

    reduced chi-squared = 800.69/228 = 3.512

    soft proton power laws
      Data group 1, n  0.45 +/- 0.03,  norm  6.38e-02 +/- 3.48e-03
      Data group 2, n  0.45 +/- 0.00,  norm  6.34e-02 +/- 3.55e-03
      Data group 3, n  0.20 +/- 0.00,  norm  8.01e-02 +/- 3.76e-03
      Data group 4, n  0.48 +/- 0.04,  norm  7.52e-02 +/- 5.10e-03
      Data group 5, n  0.48 +/- 0.00,  norm  2.12e-02 +/- 2.86e-03

    instrumental lines
      Data group 1, instr const  0.86 +/- 0.11
      Data group 2, instr const  0.88 +/- 0.11
      Data group 3, instr const  0.64 +/- 0.05
      Data group 4, instr const  2.43 +/- 0.17
      Data group 5, instr const  2.31 +/- 0.15

For sanity let's also try thawing the PN power law and see what comes out.

    reduced chi-squared = 774.44/227 = 3.412

    soft proton power laws
      Data group 1, n  0.45 +/- 0.03,  norm  6.38e-02 +/- 3.48e-03
      Data group 2, n  0.45 +/- 0.00,  norm  6.34e-02 +/- 3.55e-03
      Data group 3, n  0.52 +/- 0.05,  norm  1.29e-01 +/- 1.05e-02
      Data group 4, n  0.48 +/- 0.04,  norm  7.52e-02 +/- 5.10e-03
      Data group 5, n  0.48 +/- 0.00,  norm  2.12e-02 +/- 2.86e-03

    instrumental lines
      Data group 1, instr const  0.86 +/- 0.11
      Data group 2, instr const  0.88 +/- 0.11
      Data group 3, instr const  0.67 +/- 0.05
      Data group 4, instr const  2.43 +/- 0.17
      Data group 5, instr const  2.31 +/- 0.15

OK.  Looking at the region, this is really not surprising -- the region does
overlap with some limited extent of SNR emission.  Therefore, we may need
better regions for resolved analysis.

But, it is interesting that:
1. solar Si/S abundances give an acceptable fit (albeit better with Si free)
2. fitted abundance is lower
3. fitted ionization timescale is higher


## src\_E\_lobe region fit

First fit, solar abundances vnei; PN SP power law thawed

    reduced chi-squared = 301.25/208 = 1.448
    snr model: TBabs*vnei
      nH (10^22)    5.219 +/- 0.220
      kT   (keV)    0.544 +/- 0.043
      Si            1.00  +/- 0.00
      S             1.00  +/- 0.00
      Tau (s/cm^3)  8.60e+10 +/- 5.00e+10
      norm          1.33e-02 +/- 3.29e-03

    soft proton power laws
      Data group 1, n  0.23 +/- 0.05,  norm  4.26e-02 +/- 4.32e-03
      Data group 2, n  0.23 +/- 0.00,  norm  4.09e-02 +/- 4.17e-03
      Data group 3, n  -0.04 +/- 0.15,  norm  4.05e-02 +/- 1.17e-02
      Data group 4, n  0.35 +/- 0.08,  norm  4.86e-02 +/- 6.73e-03
      Data group 5, n  0.35 +/- 0.00,  norm  5.21e-03 +/- 2.58e-03

    instrumental lines
      Data group 1, instr const  0.74 +/- 0.15
      Data group 2, instr const  0.59 +/- 0.14
      Data group 3, instr const  0.44 +/- 0.16
      Data group 4, instr const  1.13 +/- 0.20
      Data group 5, instr const  1.52 +/- 0.19

Fit with Si free, PN SP power law thawed.

    reduced chi-squared = 213.72/207 = 1.032
    snr model: TBabs*vnei
      nH (10^22)    4.008 +/- 0.305
      kT   (keV)    0.801 +/- 0.156
      Si            2.61  +/- 0.31
      S             1.00  +/- 0.00
      Tau (s/cm^3)  6.95e+10 +/- 5.22e+10
      norm          2.46e-03 +/- 1.16e-03

    soft proton power laws
      Data group 1, n  0.24 +/- 0.05,  norm  4.34e-02 +/- 4.36e-03
      Data group 2, n  0.24 +/- 0.00,  norm  4.16e-02 +/- 4.21e-03
      Data group 3, n  -0.01 +/- 0.15,  norm  4.23e-02 +/- 1.21e-02
      Data group 4, n  0.35 +/- 0.08,  norm  4.86e-02 +/- 6.79e-03
      Data group 5, n  0.35 +/- 0.00,  norm  5.21e-03 +/- 2.62e-03

    instrumental lines
      Data group 1, instr const  0.82 +/- 0.15
      Data group 2, instr const  0.68 +/- 0.14
      Data group 3, instr const  0.51 +/- 0.17
      Data group 4, instr const  1.27 +/- 0.20
      Data group 5, instr const  1.66 +/- 0.19

These absorption values look way too high.
Redo this with PN SP power law frozen, for consistency.

First fit, solar abundances, PN power law frozen.

    reduced chi-squared = 304.34/209 = 1.456
    snr model: TBabs*vnei
      nH (10^22)    5.265 +/- 0.241
      kT   (keV)    0.543 +/- 0.076
      Si            1.00  +/- 0.00
      S             1.00  +/- 0.00
      Tau (s/cm^3)  7.62e+10 +/- 6.21e+10
      norm          1.36e-02 +/- 5.07e-03

    soft proton power laws
      Data group 1, n  0.24 +/- 0.05,  norm  4.34e-02 +/- 4.27e-03
      Data group 2, n  0.24 +/- 0.00,  norm  4.16e-02 +/- 4.12e-03
      Data group 3, n  0.20 +/- 0.00,  norm  6.13e-02 +/- 4.69e-03
      Data group 4, n  0.35 +/- 0.08,  norm  4.96e-02 +/- 6.64e-03
      Data group 5, n  0.35 +/- 0.00,  norm  5.53e-03 +/- 2.59e-03

    instrumental lines
      Data group 1, instr const  0.75 +/- 0.15
      Data group 2, instr const  0.61 +/- 0.14
      Data group 3, instr const  0.46 +/- 0.16
      Data group 4, instr const  1.16 +/- 0.20
      Data group 5, instr const  1.54 +/- 0.19

Second fit, Si free (clear line residual, so justified).

    reduced chi-squared = 216.24/208 = 1.040
    snr model: TBabs*vnei
      nH (10^22)    4.094 +/- 0.306
      kT   (keV)    0.760 +/- 0.127
      Si            2.64  +/- 0.33
      S             1.00  +/- 0.00
      Tau (s/cm^3)  8.00e+10 +/- 5.29e+10
      norm          2.72e-03 +/- 1.19e-03

    soft proton power laws
      Data group 1, n  0.25 +/- 0.05,  norm  4.44e-02 +/- 4.32e-03
      Data group 2, n  0.25 +/- 0.00,  norm  4.25e-02 +/- 4.17e-03
      Data group 3, n  0.20 +/- 0.00,  norm  6.12e-02 +/- 4.75e-03
      Data group 4, n  0.36 +/- 0.08,  norm  5.01e-02 +/- 6.71e-03
      Data group 5, n  0.36 +/- 0.00,  norm  5.72e-03 +/- 2.66e-03

    instrumental lines
      Data group 1, instr const  0.83 +/- 0.15
      Data group 2, instr const  0.69 +/- 0.14
      Data group 3, instr const  0.51 +/- 0.16
      Data group 4, instr const  1.28 +/- 0.20
      Data group 5, instr const  1.67 +/- 0.19

Very reasonable fit, but, again, nH is way too high.
What if I force nH = 2?  Perform that fit.

    reduced chi-squared = 291.89/209 = 1.397
    snr model: TBabs*vnei
      nH (10^22)    2.000 +/- 0.306
      kT   (keV)    4.285 +/- 1.171
      Si            6.19  +/- 0.59
      S             1.00  +/- 0.00
      Tau (s/cm^3)  2.11e+10 +/- 1.74e+09
      norm          1.72e-04 +/- 1.30e-05

    soft proton power laws
      Data group 1, n  0.22 +/- 0.06,  norm  4.03e-02 +/- 4.43e-03
      Data group 2, n  0.22 +/- 0.00,  norm  3.81e-02 +/- 4.26e-03
      Data group 3, n  0.20 +/- 0.00,  norm  5.48e-02 +/- 5.19e-03
      Data group 4, n  0.32 +/- 0.09,  norm  4.29e-02 +/- 6.90e-03
      Data group 5, n  0.32 +/- 0.00,  norm  2.41e-03 +/- 2.54e-03

    instrumental lines
      Data group 1, instr const  0.96 +/- 0.15
      Data group 2, instr const  0.83 +/- 0.14
      Data group 3, instr const  0.60 +/- 0.16
      Data group 4, instr const  1.52 +/- 0.19
      Data group 5, instr const  1.86 +/- 0.18

OK -- we start to see similar behavior as before.
kT ramps up, Si ramps up, norm ramps down (in this case Tau ramps down).

That suggests to me:
1. either x-ray absorption really is thick here, and there is a lot of local
   variability (not implausible!)
2. we're over-estimating the X-ray background
   (implies pretty-small scale variation, though)
3. something else is wrong??

General comment: X-ray background dominates at low energies, maybe a partial
driver for the high absorption values...


Weds-Sun 2016 March 9-13 - setup new regions, conversion
========================================================

Fiddling for this was done on Weds,Sat,Sun (Weds night, Thurs, Fri dominated by
MP work).

Create new region to sample bright rim (`src_ridge`)
create new region to truly sample dark part of remnant (`src_SE_ridge_dark`).
Regions match -- sample opposite radio ridges.

Modify `reg2xmmdets.pl` to deal with ellipses, boxes.
- tested with new/old regions. Ran to completion.
- old regions (circles, annuli) unchanged, checked by diff.
- new regions were not correct -- rotation was funky

Must compute the angle conversion from sky to detector coordinates.  I could
specify selections using X/Y coordinates, but ESAS recommends DETX/DETY (I am
too lazy to look into what exactly breaks if I use X/Y...) Added relevant
conversions to reg2xmmdets.pl, added a one-off script that makes XMM event
lists for checking that regions are created correctly.

Run specbackgrp on new regions.  Checked error logs, no issues.

    atran@statler:~/rsch/g309/xmm$ nohup /bin/tcsh -c './masterscript.tcsh 0087940201' >& 20160313_ridges_0087940201.log &
    [1] 20567
    atran@cooper:~/rsch/g309/xmm$ nohup /bin/tcsh -c './masterscript.tcsh 0551000201' >& 20160313_ridges_0551000201.log &
    [1] 12414


Monday 2016 March 14 - continue sub-source region fits
======================================================

## src\_ridge region fit

Fit with nH free, Si free -- the chi-squared is unusually high,
and the residuals look pretty poor.  I'm not convinced this is a good
description of the spectrum.  High ionization age.

    reduced chi-squared = 339.66/226 = 1.503
    snr model: TBabs*vnei
      nH (10^22)    2.939 +/- 0.108
      kT   (keV)    0.711 +/- 0.052
      Si            1.98  +/- 0.14
      S             1.00  +/- 0.00
      Tau (s/cm^3)  9.41e+10 +/- 3.79e+10
      norm          3.44e-03 +/- 6.45e-04

    soft proton power laws
      Data group 1, n  0.43 +/- 0.05,  norm  5.93e-02 +/- 5.39e-03
      Data group 2, n  0.43 +/- 0.00,  norm  6.77e-02 +/- 6.07e-03
      Data group 3, n  0.20 +/- 0.30,  norm  5.97e-02 +/- 5.43e-03
      Data group 4, n  0.51 +/- 0.07,  norm  7.15e-02 +/- 8.40e-03
      Data group 5, n  0.51 +/- 0.00,  norm  2.07e-02 +/- 4.61e-03

    instrumental lines
      Data group 1, instr const  0.92 +/- 0.22
      Data group 2, instr const  1.03 +/- 0.20
      Data group 3, instr const  0.55 +/- 0.08
      Data group 4, instr const  1.20 +/- 0.26
      Data group 5, instr const  1.57 +/- 0.23

The Si line in PN is, curiously, somewhat offset from the VNEI line -- actual
data look as though the line has lower-energy (from eyeballing, ~0.05keV
shift?).
IF this is a real effect, shift would be ~0.05/1.80 -> z ~ 0.03 ~ (9000km/s) / c
which is too high given the remnant age/size (unless it's closer than we think,
very unexpected).  More likely, it's just chance that we got more counts on the
low-energy side of the line than on the high side, or some kind of calibration
error, or whatever.

One more fit with Si/S both free.  Not obvious that we have abundant S in this
ridge, but the fit improves slightly w/ S -- smooths out residuals a bit.

    reduced chi-squared = 318.51/225 = 1.416
    snr model: TBabs*vnei
      nH (10^22)    2.884 +/- 0.104
      kT   (keV)    0.624 +/- 0.069
      Si            2.28  +/- 0.18
      S             2.06  +/- 0.30
      Tau (s/cm^3)  1.30e+11 +/- 7.24e+10
      norm          3.92e-03 +/- 9.80e-04

    soft proton power laws
      Data group 1, n  0.44 +/- 0.05,  norm  6.02e-02 +/- 5.35e-03
      Data group 2, n  0.44 +/- 0.00,  norm  6.87e-02 +/- 6.04e-03
      Data group 3, n  0.20 +/- 0.00,  norm  6.16e-02 +/- 5.33e-03
      Data group 4, n  0.51 +/- 0.07,  norm  7.21e-02 +/- 8.35e-03
      Data group 5, n  0.51 +/- 0.00,  norm  2.15e-02 +/- 4.58e-03

    instrumental lines
      Data group 1, instr const  0.97 +/- 0.22
      Data group 2, instr const  1.08 +/- 0.20
      Data group 3, instr const  0.55 +/- 0.08
      Data group 4, instr const  1.26 +/- 0.26
      Data group 5, instr const  1.62 +/- 0.23

## src\_SE\_ridge\_dark region fit

First, try fitting with NO SNR model.
PN power law set to 0.2 for consistency.  I'd say this is an acceptable fit, though
the residuals definitely show systematic structure.

    reduced chi-squared = 153.85/108 = 1.425
    snr model: TBabs*vnei
      norm          0.00e+00 +/- 5.89e-06

    soft proton power laws
      Data group 1, n  0.41 +/- 0.05,  norm  5.91e-02 +/- 5.14e-03
      Data group 2, n  0.41 +/- 0.00,  norm  5.76e-02 +/- 5.10e-03
      Data group 3, n  0.20 +/- 0.13,  norm  6.68e-02 +/- 4.74e-03
      Data group 4, n  0.26 +/- 0.09,  norm  5.00e-02 +/- 7.63e-03
      Data group 5, n  0.26 +/- 0.00,  norm  1.05e-02 +/- 2.93e-03

    instrumental lines
      Data group 1, instr const  0.72 +/- 0.12
      Data group 2, instr const  0.78 +/- 0.14
      Data group 3, instr const  0.69 +/- 0.07
      Data group 4, instr const  1.76 +/- 0.20
      Data group 5, instr const  1.82 +/- 0.19

I see two approaches.
1. What happens if we allow some SNR component?
2. What happens if we let x-ray background parameters float?

Allowing SNR component improves fit slightly, favors very high nH.

    reduced chi-squared = 121.46/104 = 1.168
    snr model: TBabs*vnei
      nH (10^22)    4.123 +/- 1.127
      kT   (keV)    0.528 +/- 0.833
      Si            1.00  +/- 0.00
      S             1.00  +/- 0.00
      Tau (s/cm^3)  5.01e+10 +/- 5.47e+11
      norm          1.24e-03 +/- 4.04e-03

    soft proton power laws
      Data group 1, n  0.34 +/- 0.06,  norm  5.10e-02 +/- 5.38e-03
      Data group 2, n  0.34 +/- 0.00,  norm  4.91e-02 +/- 5.33e-03
      Data group 3, n  0.20 +/- 0.13,  norm  6.10e-02 +/- 5.01e-03
      Data group 4, n  0.10 +/- 0.12,  norm  3.72e-02 +/- 8.19e-03
      Data group 5, n  0.10 +/- 0.00,  norm  6.18e-03 +/- 2.57e-03

    instrumental lines
      Data group 1, instr const  0.66 +/- 0.13
      Data group 2, instr const  0.68 +/- 0.14
      Data group 3, instr const  0.69 +/- 0.07
      Data group 4, instr const  1.48 +/- 0.21
      Data group 5, instr const  1.54 +/- 0.20

With Si free, fit runs away to really high Si values, which appears
almost degenerate wrt kT and Tau.  I don't show result here.

What happens if I let XRB normalizations float?
Didn't record exact fit results, but fit doesn't improve significantly.
Chi-squared is 147.38/105 = 1.404

So it can be argued that there is an SNR component here.  In the best fit,
SNR normalization is comparable to rest of remnant, just the statistics are
poor and the line emission is not pronounced.



## src\_SW\_lobe region fit

Finally, finish sub-source region fit that we didn't complete last time.
As usual, PN power law index forced to 0.2.

"Standard" fit with SNR Si/S free:

    reduced chi-squared = 592.32/438 = 1.352
    snr model: TBabs*vnei
      nH (10^22)    1.916 +/- 0.076
      kT   (keV)    2.403 +/- 0.376
      Si            3.90  +/- 0.22
      S             4.79  +/- 0.70
      Tau (s/cm^3)  1.35e+10 +/- 1.16e+09
      norm          6.72e-04 +/- 8.28e-05

    soft proton power laws
      Data group 1, n  0.41 +/- 0.03,  norm  5.72e-02 +/- 3.23e-03
      Data group 2, n  0.41 +/- 0.00,  norm  6.13e-02 +/- 3.49e-03
      Data group 3, n  0.20 +/- 0.00,  norm  7.08e-02 +/- 3.76e-03
      Data group 4, n  0.42 +/- 0.05,  norm  5.89e-02 +/- 5.19e-03
      Data group 5, n  0.42 +/- 0.00,  norm  1.17e-02 +/- 2.52e-03

    instrumental lines
      Data group 1, instr const  0.94 +/- 0.11
      Data group 2, instr const  0.87 +/- 0.10
      Data group 3, instr const  0.52 +/- 0.04
      Data group 4, instr const  1.74 +/- 0.15
      Data group 5, instr const  1.87 +/- 0.14


(!!) similar to `src_ridge fit`, the PN lines appears oddly offset.
Not clear that this is the case for MOS1/2 spectra.
Offset is apparent in both Si and S line.
Weird.
Fit otherwise looks good.  There is a fair bit of soft excess, looks like it
could easily be offset by letting XRB normalization float.

For reference, here are original "default" normalizations:

       2    2   apec       kT         keV      0.228000     frozen
       5    2   apec       norm                2.90000E-04  frozen
       6    3   TBabs      nH         10^22    1.06000      frozen
       7    4   powerlaw   PhoIndex            1.40000      frozen
       8    4   powerlaw   norm                3.10000E-04  frozen
       9    5   apec       kT         keV      0.368000     frozen
      12    5   apec       norm                3.29000E-03  frozen

Here are final normalizations.  It looks like a doubling of the harder apec
and the powerlaw contribution helps significantly.

   5    2   apec       norm                3.03355E-04  +/-  2.60276E-05  
   8    4   powerlaw   norm                5.72240E-04  +/-  6.69836E-05  
  12    5   apec       norm                6.35793E-03  +/-  4.65595E-04

Fit parameters w/XRB floating -- fit improves slightly but moves to an obscene
amount of S emission... which doesn't make sense.

    reduced chi-squared = 569.48/435 = 1.309
    snr model: TBabs*vnei
      nH (10^22)    3.077 +/- 0.295
      kT   (keV)    0.843 +/- 0.245
      Si            5.17  +/- 0.93
      S             15.65  +/- 7.98
      Tau (s/cm^3)  1.36e+10 +/- 2.85e+09
      norm          2.82e-03 +/- 1.60e-03

    soft proton power laws
      Data group 1, n  0.39 +/- 0.03,  norm  5.26e-02 +/- 3.66e-03
      Data group 2, n  0.39 +/- 0.00,  norm  5.62e-02 +/- 3.95e-03
      Data group 3, n  0.20 +/- 0.00,  norm  6.60e-02 +/- 4.11e-03
      Data group 4, n  0.36 +/- 0.06,  norm  5.12e-02 +/- 6.30e-03
      Data group 5, n  0.36 +/- 0.00,  norm  7.72e-03 +/- 2.63e-03

    instrumental lines
      Data group 1, instr const  0.88 +/- 0.11
      Data group 2, instr const  0.82 +/- 0.10
      Data group 3, instr const  0.51 +/- 0.04
      Data group 4, instr const  1.60 +/- 0.15
      Data group 5, instr const  1.72 +/- 0.14

## Why do we see line energy shifts?!

This would suggest weird calibration, incorrect RMF, or similar.
E.g., could the fact that we have not used a detector-mapped RMF explain the difference?

Looking at residuals for `src_SW_lobe`, it could be present in MOS1/2 spectra
as well -- shifted the opposite way.  But, hard to tell without disentangling
spectra (code not really well set-up for that yet).

I note that pn-spectra has not changed from `xmmsas_20141104_1833` to
`xmmsas_20160201_1833`.

As a sanity check, I re-run the fits for the integrated remnant (`src`)
and for the bright `src_north_clump`.
If the lines look good in PN, then it's a region dependent error/effect.
RESULT: lines look fine in `src_north_clump`.

So, something is up.


## vpshock model for integrated remnant

First, consider vpshock model fit to src region with Si,S free.

### vpshock with bkg fixed from snr/bkg vnei fit

WITHOUT Si,S free yet:

    reduced chi-squared = 5025.36/2222 = 2.262
    snr model: TBabs*vpshock
      nH (10^22)      3.960 +/- 0.042
      kT   (keV)      0.687 +/- 0.017
      Si              1.00               (frozen)
      S               1.00               (frozen)
      Tau_l (s/cm^3)  8.19e+10 +/- 1.2e+12   (huge uncertainty!)
      Tau_u (s/cm^3)  7.91e+10 +/- 1.3e+12   (huge uncertainty!)
      norm            6.06e-2 +/- 3.55e-3

    soft proton power laws
      Data group 1, n  0.41 +/- 0.01,  norm  6.05e-02 +/- 1.34e-03
      Data group 2, n  0.41 +/- 0.00,  norm  6.35e-02 +/- 1.41e-03
      Data group 3, n  0.44 +/- 0.03,  norm  1.07e-01 +/- 4.87e-03
      Data group 4, n  0.38 +/- 0.02,  norm  5.46e-02 +/- 1.94e-03
      Data group 5, n  0.38 +/- 0.00,  norm  1.40e-02 +/- 9.68e-04

    instrumental lines
      Data group 1, instr const  0.71 +/- 0.05
      Data group 2, instr const  0.66 +/- 0.05
      Data group 3, instr const  0.56 +/- 0.03
      Data group 4, instr const  1.31 +/- 0.07
      Data group 5, instr const  1.50 +/- 0.06

With Si/S free.  tau_l/tau_u badly constrained in fitting process

    reduced chi-squared = 2658.22/2220 = 1.197
    snr model: TBabs*vpshock
      nH (10^22)      2.197 +/- 0.040
      kT   (keV)      1.439 +/- 0.087
      Si              4.58 +/- 0.18
      S               4.47 +/- 0.27
      Tau_l (s/cm^3)  5.03e+10 +/- 3.9e+09
      Tau_u (s/cm^3)  1.00e+08 +/- 9.1e+09      (hit limit!)
      norm            5.99e-03 +/- 5.8e-04

    soft proton power laws
      Data group 1, n  0.39 +/- 0.01,  norm  5.78e-02 +/- 1.38e-03
      Data group 2, n  0.39 +/- 0.00,  norm  6.05e-02 +/- 1.45e-03
      Data group 3, n  0.34 +/- 0.03,  norm  8.73e-02 +/- 5.06e-03
      Data group 4, n  0.34 +/- 0.02,  norm  4.96e-02 +/- 2.04e-03
      Data group 5, n  0.34 +/- 0.00,  norm  1.20e-02 +/- 9.48e-04

    instrumental lines
      Data group 1, instr const  0.93 +/- 0.05
      Data group 2, instr const  0.86 +/- 0.04
      Data group 3, instr const  0.60 +/- 0.03
      Data group 4, instr const  1.64 +/- 0.07
      Data group 5, instr const  1.79 +/- 0.06

The fit looks pretty good, but with `Tau_u` at basically zero (I will make the
unproven assumption that `Tau_l` and `Tau_u` are symmetric -- but it looks like
the parameter bounds are quite different, so maybe not, and the fit should be
optimized by swapping the two values).

This is basically a vnei fit.  Parameters not quite the same as previous
integrated remnant vnei fit (of note, `Tau_l` is 2x larger), but kT and nH are
about consistent with what I saw before.


### vpshock with bkg free

Now, the above fit is __expected__ to force one of `Tau_l` or `Tau_u` towards
zero, simply because the fixed background "pigeonholes" the vpshock fit towards
the vnei model.  I.e., by fixing the background, the remaining part of the
signal is already optimized to look like a vnei model with Si/S free.

Therefore, to deduce anything useful we need to fit with background free.
Same applies to the attempted Sedov fit below.

First fit, as follows:
1. renorm and fit normalizations only
2. fit, simultaneously allow both ionization times, kT, nH, Si/S to float
3. fit, allow XRB temperatures/absorption to float

this particular fit looks excellent, I'm surprised that the parameters
are somewhat different w.r.t. simple VNEI fit...
check possible XRB values.

    reduced chi-squared = 4509.23/3768 = 1.197
    snr model: TBabs*vpshock
      nH (10^22)    2.048 +/- 0.044
      kT   (keV)    1.510 +/- 0.085
      Si            4.82  +/- 0.14
      S             4.85  +/- 0.22
      Tau_u (keV)    50961009423.873 +/- 3663433560.047  == 5.096e+10 +/- 3.66e+09
      Tau_l (keV)    0.000 +/- 9613613.450
      norm          5.47e-03 +/- 3.72e-04

    soft proton power laws
      Data group 1, n  0.34 +/- 0.01,  norm  5.22e-02 +/- 1.54e-03
      Data group 2, n  0.34 +/- 0.00,  norm  5.44e-02 +/- 1.61e-03
      Data group 3, n  0.20 +/- 0.00,  norm  6.53e-02 +/- 1.68e-03
      Data group 4, n  0.24 +/- 0.03,  norm  4.04e-02 +/- 2.41e-03
      Data group 5, n  0.24 +/- 0.00,  norm  8.45e-03 +/- 9.00e-04
      Data group 6, n  0.31 +/- 0.01,  norm  4.38e-02 +/- 1.29e-03
      Data group 7, n  0.31 +/- 0.00,  norm  4.58e-02 +/- 1.32e-03
      Data group 8, n  0.20 +/- 0.00,  norm  4.70e-02 +/- 1.45e-03
      Data group 9, n  0.43 +/- 0.04,  norm  2.29e-02 +/- 1.56e-03
      Data group 10, n  0.43 +/- 0.00,  norm  5.08e-03 +/- 8.23e-04

    instrumental lines
      Data group 1, instr const  0.88 +/- 0.05
      Data group 2, instr const  0.82 +/- 0.04
      Data group 3, instr const  0.59 +/- 0.02
      Data group 4, instr const  1.57 +/- 0.07
      Data group 5, instr const  1.71 +/- 0.06
      Data group 6, instr const  0.66 +/- 0.03
      Data group 7, instr const  0.62 +/- 0.03
      Data group 8, instr const  0.66 +/- 0.02
      Data group 9, instr const  1.45 +/- 0.04
      Data group 10, instr const  1.47 +/- 0.04

    X-ray background (!)

       1    1   constant   factor              1.00000      frozen
       2    2   apec       kT         keV      0.100734     +/-  5.18487E-03  
       3    2   apec       Abundanc            1.00000      frozen
       4    2   apec       Redshift            0.0          frozen
       5    2   apec       norm                6.29399E-04  +/-  1.02179E-04  
       6    3   TBabs      nH         10^22    0.256918     +/-  3.61750E-02  
       7    4   powerlaw   PhoIndex            1.40000      frozen
       8    4   powerlaw   norm                3.32290E-04  +/-  9.59905E-06  
       9    5   apec       kT         keV      0.294247     +/-  7.31701E-03  
      10    5   apec       Abundanc            1.00000      frozen
      11    5   apec       Redshift            0.0          frozen
      12    5   apec       norm                5.92547E-04  +/-  1.09444E-04 


## sedov model for integrated remnant

Next, consider sedov model fit to src region with Si,S free
and allow bkg fit.

### sedov with bkg fixed from snr/bkg vnei fit

FIRST RUN: start 19:48:53p EST, finish 22:23:00p EST (2hr 40min)
Allow fit to free nH, `kT_a`, `kT_b`, Tau, Si, S immediately.
Running in vnc session treble:1

Fit is running away (`kT_a` exploding)
XSPEC froze Si/S at very beginning of fit -- will have to revisit this.

    reduced chi-squared = 4390.09/2221 = 1.977
    snr model: TBabs*vsedov
      nH (10^22)    4.181 +/- 0.047
      kT_a (keV)    1.11 +/- 0.11
      kT_b (keV)    0.01 +/- 0.085          (fit hit limit value)
      Si            1.00                    (fit pegged to 1)
      S             1.00                    (fit pegged to 1)
      Tau (s/cm^3)  2.61e+11 +/- 2.70e+10
      norm          8.76e-2 +/- 6.48e-3

    soft proton power laws
      Data group 1, n  0.41 +/- 0.01,  norm  6.02e-02 +/- 1.33e-03
      Data group 2, n  0.41 +/- 0.00,  norm  6.31e-02 +/- 1.41e-03
      Data group 3, n  0.20 +/- 0.00,  norm  7.03e-02 +/- 1.56e-03
      Data group 4, n  0.38 +/- 0.02,  norm  5.39e-02 +/- 1.94e-03
      Data group 5, n  0.38 +/- 0.00,  norm  1.34e-02 +/- 9.60e-04

    instrumental lines
      Data group 1, instr const  0.79 +/- 0.05
      Data group 2, instr const  0.72 +/- 0.04
      Data group 3, instr const  0.55 +/- 0.03
      Data group 4, instr const  1.41 +/- 0.07
      Data group 5, instr const  1.60 +/- 0.06

Ouch.  Fit is ok, but there are clear residuals.  Certainly a clear Si line,
but not clear that S line is present (above solar).  Try again, nudging
parameters as follows:

    snr.TBabs.nH = 3
    snr.vsedov.Si = 2.5
    snr.vsedov.Tau = 1e11
    snr.vsedov.kT_a = 0.8
    snr.vsedov.S = 1.2

Now, repeat fit -- starting 00:48:14a EST (Tue Mar 15).
Finished 02:14:45a EST.

Wow, nothing worked.  Still see clear S residual.  Fit reconverged to almost
same parameters (within ~5-10%).  Let's try again with background free.

### sedov with bkg free

First, fit with "default" x-ray background parameters (norms free)
and let all vsedov parameters (Tau, Si, S, kT_a, kT_b, nH) vary freely.
See what happens.
Started around 11:08a EST
finished at 14:06p EST (3 hrs)

OK, still funky.  Si/S abundances refuse to budge from 1.
Fit doesn't look bad.  Thaw XRB parameters and let it fit again.

start at: 10:22:05a EST, 2016 Mar 16
finish: 10:52:06a EST, surprisingly

    reduced chi-squared = 6012.92/3768 = 1.596
    snr model: TBabs*vsedov
      nH (10^22)    4.341 +/- 0.054
      kT_a (keV)    1.088 +/- 0.126
      kT_b (keV)    0.010 +/- 0.087
      Si            1.00  +/- -1.00
      S             1.00  +/- -1.00
      Tau (s/cm^3)  2.55e+11 +/- 2.70e+10
      norm          9.91e-02 +/- 8.34e-03

    soft proton power laws
      Data group 1, n  0.39 +/- 0.01,  norm  5.78e-02 +/- 1.52e-03
      Data group 2, n  0.39 +/- 0.00,  norm  6.05e-02 +/- 1.60e-03
      Data group 3, n  0.20 +/- 0.00,  norm  7.06e-02 +/- 1.66e-03
      Data group 4, n  0.34 +/- 0.02,  norm  5.03e-02 +/- 2.35e-03
      Data group 5, n  0.34 +/- 0.00,  norm  1.24e-02 +/- 1.05e-03
      Data group 6, n  0.31 +/- 0.01,  norm  4.51e-02 +/- 1.30e-03
      Data group 7, n  0.31 +/- 0.00,  norm  4.71e-02 +/- 1.32e-03
      Data group 8, n  0.20 +/- 0.00,  norm  5.03e-02 +/- 1.49e-03
      Data group 9, n  0.44 +/- 0.04,  norm  2.45e-02 +/- 1.56e-03
      Data group 10, n  0.44 +/- 0.00,  norm  6.57e-03 +/- 8.69e-04

    instrumental lines
      Data group 1, instr const  0.81 +/- 0.05
      Data group 2, instr const  0.75 +/- 0.04
      Data group 3, instr const  0.56 +/- 0.03
      Data group 4, instr const  1.44 +/- 0.07
      Data group 5, instr const  1.62 +/- 0.06
      Data group 6, instr const  0.70 +/- 0.03
      Data group 7, instr const  0.66 +/- 0.03
      Data group 8, instr const  0.66 +/- 0.02
      Data group 9, instr const  1.48 +/- 0.04
      Data group 10, instr const  1.50 +/- 0.04

Si/S won't budge?!  Definite structure in residuals still present.


Tuesday-Tuesday 2016 March 15-22 - assemble, interpret sub-source region fits
=============================================================================

## Why do fits of Safi-Harb+ and Rakowski favor NH ~ 0.6e22?

Integrated source fit without background model (unlikely to do this)
yields:

        reduced chi-squared = 4478.93/2222 = 2.016
          nH (10^22)    1.554 +/- 0.019
          kT   (keV)    3.265 +/- 0.180
          Si            4.05  +/- 0.08
          S             4.25  +/- 0.15
          Tau (s/cm^3)  1.65e+10 +/- 4.58e+08
          norm          3.06e-03 +/- 9.70e-05

Integrated source fit with abundances above N free (i.e., thaw O, Ne, Mg, ...,
Ar, Ca, Fe, Ni) yields:

        reduced chi-squared = 2724.29/2215 = 1.230
        snr model: TBabs*vnei
          nH (10^22)    0.680 +/- 0.021
          kT   (keV)    2.602 +/- 0.129
          Si            2.04  +/- 0.05
          S             2.96  +/- 0.14
          Tau (s/cm^3)  1.56e+10 +/- 5.15e+08
          norm          4.57e-03 +/- 1.87e-04

          O             7.46164E-02  +/-  1.01773E-02
          Ne            5.62290E-02  +/-  1.29935E-02
          Mg            0.260458     +/-  1.47095E-02
          Ar            3.31201      +/-  0.494184
          Ca            14.4239      +/-  1.96441
          Fe            5.46430E-02  +/-  6.34211E-03
          Ni            0.556611     +/-  0.126530

Ramping down O/Ne/Mg/Fe lets us decrease nH.  Fit residuals do not look bad.
Abundances are wonky.  Ar/Ca lines are very ill-constrained, difficult to tease
out through high energy noise + not strong to begin with.

Run integrated source fit with background FREE, and O,Ne,Mg,Ca,Fe FREE

        reduced chi-squared = 4369.27/3762 = 1.161
        snr model: TBabs*vnei
          nH (10^22)    2.023 +/- 0.137
          kT   (keV)    1.008 +/- 0.089
          Si            3.72  +/- 0.38
          S             5.14  +/- 0.65
          Tau (s/cm^3)  2.61e+10 +/- 2.59e+09
          norm          8.90e-03 +/- 9.87e-04

          O             2.87211      +/-  1.31759
          Ne            1.02379      +/-  0.371537
          Mg            0.600475     +/-  8.85837E-02
          Ar            12.2653      +/-  2.98179
          Ca            77.1689      +/-  28.1898
          Fe            1.06280E-10  +/-  0.113155
          Ni            2.64724      +/-  0.933963

If I freeze Ar/Ca back to one, makes very little difference (fit parameters
shift slightly, reduced chi-squared increases slightly).  I do not reproduce
the numbers here.

## Sub-source fit scripting, first attempt

The tables of fit results in these notes are becoming a pain.
Makes it very difficult to organize my thoughts.

Present "standard" fit with:
* XRB parameters fixed from integrated-source fit
* integrated source fit, all free (nH, kT, Si, S, Tau)
* sub-source region fits (blobs + annuli), all free (nH, kT, Si, S, Tau)
* integrated source fit, nH tied to (1, 1.5, 2, 2.5)
* sub-source region fit, nH tied to (1, 1.5, 2, 2.5) -- parameters free depending on what was decided from earlier (Si/S)

and links to plots for each

List of assumptions to test.  How do the (KEY) fits above change if I:
* run vpshock/vsedov for integrated source or subregion (partially done)
* truncate the low/high energy ranges (cut MOS/PN off at 1keV, 7keV)
  (do separately to illustrate effects)
* change x-ray background fit parameters
* use x-ray background fit parameters from fitting XRB alone?

First: SRC 

    atran@statler:~/rsch/g309/xmm$ nohup /bin/tcsh -c './masterscript.tcsh 0087940201' >& 20160321_pre_ridge_specbackgrp.log &
    [1] 31353
    atran@cooper:~/rsch/g309/xmm$ nohup /bin/tcsh -c './masterscript.tcsh 0551000201' >& 20160321_pre_ridge_specbackgrp_0551000201.log &
    [1] 2571

Start using a shell script to save all the fits being run.

    nohup ./fitter.tcsh > & 20160321_fitter.log &

Started run around 3:10pm on Mon Mar 21.
Finished ~4:50pm.  So one set of fits requires ~1hr 40min (!).

## Innermost annulus [circle] fit is failing terribly

`ann_000_100` fit blew up, a few others went haywire.
Errors tied to weird high energy data in "blue" spectrum.
Solution: ignore >10 keV data in 05510002010 MOS1 alone.

Further note: must free PN power law in this region ALONE -- unclear why.
I speculate that, near aimpoint, SP contamination spectrum could be different
due to quite sharp vignetting function.

Saved a hand-coaxed fit to "ann_000_100_manual".  Fit is unusually poor -- a
lot of variation in soft/hard X-rays, strange.
(editorial note, 2016 April 5 -- probably deleted this...)

1. Tried thawing Fe alone, no dice (chi-squared barely budged, 1029.8->1028.5 ish)
   (but, settled towards Fe ~ 0.87... so OK, reassuring)
2. Try thawing O,Ne,Mg (refroze Fe=1 again)

   Thawing O,Ne,Mg made a big difference (chi-squared plummets to ~542, almost cut in half!)
   but, the SP power law parameters are pretty funky.
   Extremely low ionization age.
   Unusually low nH required by fit (larger nH would only drive up O
   abundance, and it's already atypically large?!)

   0551000201 MOS1/2 power laws have gone berserk.

   At such low Tau (~ 1e10 s /cm-cubed) could timescales of years be
   relevant?
   1 year = 3e7 seconds
   observations taken ~8 yrs apart = 2.5e8 seconds
   for densities n~10 (really high), ionization age would have changed by
   delta tau ~ 2.5e9 in the interim.
   For a fit value 1.7e10, that's a change 1.4 to 1.7e10.
   OK, probably not.

    Attempt to remedy weird power law with:
    xs.AllModels(4,"sp").powerlaw.PhoIndex = 0.2

Saved to `ann_000_100_ONeMg`.  Imperfect, but quite intriguing...

## Sub-source fit scripting, second/third attempt (troubleshooting)

Re-run fitter.tcsh with multiple nH values.

    atran@treble:/data/mpofls/atran/research/g309/xmm$ nohup ./fitter.tcsh > & 20160321_fitter_multinH.log &
    [1] 19126

Failed because I can't spell (Python choked on "Fase" typo).
The fits with nH fixed had gotten stuck anyways.
Make some modifications to perform fits more consistently.
Thaw Si/S for all fits except the darkest regions.

    atran@treble:/data/mpofls/atran/research/g309/xmm$ nohup ./fitter.tcsh >& 20160322_fitter_multinH_rerun.log &
    [1] 7668

    atran@treble:/data/mpofls/atran/research/g309/xmm$ nohup ./fitter.tcsh > & 20160322_fitter_multinH_rerun_pt2.log &
    [1] 12643

OK, looks ok... I have to clean this all up and git commit at this natural
checkpoint.  (editorial note April 5 2016: tidying up / commit took place much
later)

Fits are FAR from collisional equilibrium -- vpshock and vsedov disfavored.
Tau is very small.  So we should forget about recombining plasmas / adiabatic
cooling.  Material was heated very recently.

## Where else can we go?

Possibility: more systematic exploration of structure
* Scott Randall's approach to temperature mapping
  See Randall+ 2015 -> Randall+2008 [M86], which presents two maps:
  1. systematically fit temperature for a given pixel from a circular region
     with 1000 net counts (a massive averaging), up to a maximum radius.
  2. build a Voronoi-like tessellation of ~1000 counts/region to
     obtain non-overlapping estimates of temperature
  See also Li, Decourchelle et al. 2015 (SN 1006), which cites Randall 2008!
* Lopez+ (2015, 2013) approach to Tycho, W49B
  - Use grid of boxes overlaid on the remnant to perform spectra fits

Distance constraints
* See my notes regarding absorption and X-ray spectrum fits, and possibly
  constraining foreground column this way
* HI absorption -- Gaensler argues 5-14 kpc, likely 5-9kpc.
  I definitely believe >5kpc.
  Looking at his plots -- because the SNR-sampled spectra
  also show minimal absorption in the vLSR -20 to 0 km/s range,
  whereas the three background sources slope down smoothly,
  I could believe the source to be < 9 kpc.

(editorial note 2016 April 5: at least some SNRs have HI distance estimates
conflicting strongly with distances from other methods... so be cautious)

Based on: `https://upload.wikimedia.org/wikipedia/commons/a/a7/Milky_Way_Arms_ssc2008-10.svg`
(from `http://www.spitzer.caltech.edu/images/1923-ssc2008-10a-A-Roadmap-to-the-Milky-Way`)
our sight line crosses
* ~1-3 kpc, Carina-Sgr arm (likely location of foreground cluster NGC 5281 ??)
  => -20 to -40 km/s vLSR
* ~5-9 kpc, long sample of Scutum-Cen/Scutum-Crux arm
  => span -50 to 0 km/s vLSR roughly
* 14-15 kpc, hit Carina-Sgr arm again, far end of spiral.
  => +40 km/s vLSR spike

The key point is, like the annulus fits, to remove human bias in region
selection so that spatial variation in spectral fits __reveals__ information
about remnant, rather than being determined by our eyeball picks of
morphologically interesting regions.  These should be complementary tools.

Question: x-ray emission from foreground cluster?
almost certainly negligible (seems like only the biggest brightest clusters should be an issue)
but worth thinking about for a few hours at most?...

Question: how do we get meaningful results from these spectrum fits?

Extremely unclear to me that how/whether anything is meaningful.
Especially given uncertainty over:
- what elements should be thawed/frozen (may partially account for high
  absorption columns we're obtaining in fits)
- uncertainty about small scale (<~10 arcmin) variation in X-ray background,
  foreground absorption column
- uncertainty about absolute distance

Region selections are arbitrary.
Applying annuli is not necessarily better, given that we have clear evidence
that the emission is asymmetric (whether due to foreground column or intrinsic
to the remnant, doesn't matter).

It seems the solution, for now, is to run fits and probe all possible (and
feasible) options.  Then wait for X-ray surveyor to come out,
or ask for a whole bunch of Chandra time...

First, reviewing distance estimates by GGM98, RHS01, S+07 papers...
1. not sure I trust spectrum fits to SNR by RHS01 and S+07.
   S+ in particular gives few details.
2. nH values are WAY smaller.
   in my fits, dominated by x-ray background and sp power law.

COMMENT: is it possible that SNR morphology is affected by the presence of
absorbing interstellar clouds?
Yes, but cannot probe directly (unless we want to start looking for an X-ray
halo of HD 119682)

COMMENT: by nature, the fit to the `src_north_clump` will be better than other
sub-source regions because integrated spectrum fit, which was used to derive
background for all fits, ASSUMED that vnei was a good fit for the integrated
spectrum -- i.e., the brightest part of remnant.



Thursday 2016 March 24 - meeting
================================

List of things to go over:
1. odd shift in lines (esp. in PN?)  <- did not address this
2. absorbing column -- how to constrain?
   Discrepancy wrt old papers.
   Can we check out a point source in the field, fit it, and set an upper bound
   for the X-RAY "fit" column density?
   Make the assumption that this linearly scales wrt radio HI density...
3. discrepancy between X-ray spectrum fit / HI survey data (not unexpected)
4. Tables of fits

Mentioned:
* HI absorption discrepancy
* vpshock/vsedov fits not so helpful, odd vsedov bug
* x-rays from stellar clusters?  yes, definitely some very bright clusters
  but unclear that that's relevant here.

Few takeaways...
* tie nH in fits for all annuli.  Idea being that annuli should average out
  column variation (maybe excepting small regions) since you're integrating
  over azimuth at a large-ish radius
* the extragalactic background normalization is known, you should use it.



Friday-Tuesday 2016 April 05 - clean up, continue work
======================================================

Work placed on back-burner due to MP code work etc.
Take time to clean up and organize notes and thoughts.

## Misc tasks

Re-created "quick image" (exposure corrected mosaic) with PNS003 data from
0551000201, which increases counts ~10% in bright north blob of SNR.

## Extragalactic background normalization

Compare the fitted extragalactic power law norm to the expected norm from deep
and wide X-ray fields at high galactic latitude (see external notes).

The 0087940201 MOS1 "src" region is a circle of radius 400 arcseconds, yielding
region area = `5.03e5 arcsec^2`.  BACKSCAL for this spectrum is 191927484 (from
`mos1S001-src.pi`), which has units of detector pixels (0.05 x 0.05 arcsec).
This converts to region area = `4.80e5 arcsec^2`, about 10% smaller.  Use the
BACKSCAL value in calculations.

IF I use the Hickox and Markevitch value of 
`10.9 photons cm^-2 s^-1 sr^-1 keV^-1`, or
`9.2e-7 photons cm^2 s^-1 arcmin^-2 keV^-1` (at 1 keV), then expect fit norm
`1.2e-4 photons keV^-1 cm^-2 s^-1` for 0087940201 MOS1 src region.

In my fit, the current extragalactic power law norm is
`3.10e-4 photons keV^-1 cm^-2 s^-1` at 1 keV, for 0087940201 MOS1 src region,
based on the combined source/background fit.
The scaled normalization from our fit is for comparison
`2.3e-6 photons keV^-1 cm^-2 s^-1 arcmin^-2`.

Our fit value is 2-3x larger than expected!  This is a game changer.

## Fit with XRB normalization fixed causes some residual in soft X-ray emission

Initial attempt.  First run "usual" fit (in `xspec_fit_g309.py`), then
try stepping over nH (0.1 to 2.5, 25 steps).  Only marginally better,
chi-squared dropped by 10, parameter values largely the same.
I also tried stepping over absorbed kT, but fit just ran to the limit (0.8
keV), which is already hotter than expected for galactic halo background.

See the `20160405_*.png` plots of X-ray background.
Of note, I highlight that the background subtraction doesn't appear to change
the errors, where maybe the subtracted errors should be bigger than they are.

    reduced chi-squared = 4614.13/3770 = 1.224

    xrb:constant(apec + TBabs(powerlaw + apec))
      apec       kT         keV      0.259490     +/-  3.49084E-03  
      apec       norm                3.22541E-04  +/-  7.10725E-06  
      TBabs      nH         10^22    1.38236      +/-  4.08415E-02  
      powerlaw   PhoIndex            1.40000      frozen
      powerlaw   norm                1.20000E-04  frozen
      apec       kT         keV      0.753715     +/-  2.07931E-02  
      apec       norm                2.36253E-03  +/-  1.59583E-04

    snr model: TBabs*vnei
      nH (10^22)    2.108 +/- 0.041
      kT   (keV)    2.583 +/- 0.162
      Tau (s/cm^3)  1.75e+10 +/- 5.68e+08
      Si            3.66  +/- 0.09
      S             3.40  +/- 0.15
      norm          4.15e-03 +/- 2.40e-04

    soft proton power laws
      Data group 1, n  0.38 +/- 0.01,  norm  5.77e-02 +/- 1.46e-03
      Data group 2, n  0.38 +/- 0.00,  norm  6.03e-02 +/- 1.54e-03
      Data group 3, n  0.20 +/- 0.00,  norm  7.05e-02 +/- 1.73e-03
      Data group 4, n  0.32 +/- 0.02,  norm  4.86e-02 +/- 2.23e-03
      Data group 5, n  0.32 +/- 0.00,  norm  1.22e-02 +/- 1.02e-03
      Data group 6, n  0.35 +/- 0.01,  norm  5.09e-02 +/- 1.19e-03
      Data group 7, n  0.35 +/- 0.00,  norm  5.30e-02 +/- 1.20e-03
      Data group 8, n  0.20 +/- 0.00,  norm  5.78e-02 +/- 1.29e-03
      Data group 9, n  0.50 +/- 0.03,  norm  3.00e-02 +/- 1.39e-03
      Data group 10, n  0.50 +/- 0.00,  norm  1.07e-02 +/- 8.54e-04

    instrumental lines
      Data group 1, instr const  0.90 +/- 0.05
      Data group 2, instr const  0.83 +/- 0.04
      Data group 3, instr const  0.59 +/- 0.02
      Data group 4, instr const  1.61 +/- 0.06
      Data group 5, instr const  1.76 +/- 0.06
      Data group 6, instr const  0.65 +/- 0.03
      Data group 7, instr const  0.62 +/- 0.03
      Data group 8, instr const  0.64 +/- 0.02
      Data group 9, instr const  1.45 +/- 0.04
      Data group 10, instr const  1.47 +/- 0.04

One pitfall -- now that XRB power law is fixed, it's not obvious that we must
tie the PN power law.  Try freeing this.
Result -- very small difference.

    reduced chi-squared = 4606.86/3768 = 1.223

    xrb:constant(apec + TBabs(powerlaw + apec))
      apec       kT         keV      0.255595     +/-  3.98956E-03
      apec       norm                2.95927E-04  +/-  9.09787E-06
      TBabs      nH         10^22    1.36452      +/-  4.20174E-02
      powerlaw   PhoIndex            1.40000      frozen
      powerlaw   norm                1.20000E-04  frozen
      apec       kT         keV      0.647595     +/-  1.87526E-02
      apec       norm                2.67565E-03  +/-  1.89549E-04

    snr model: TBabs*vnei
      nH (10^22)    2.108 +/- 0.041
      kT   (keV)    2.497 +/- 0.159
      Tau (s/cm^3)  1.84e+10 +/- 6.73e+08
      Si            3.80  +/- 0.10
      S             3.40  +/- 0.15
      norm          4.09e-03 +/- 2.31e-04

    soft proton power laws
      Data group 1, n  0.40 +/- 0.01,  norm  6.04e-02 +/- 1.58e-03
      Data group 2, n  0.40 +/- 0.00,  norm  6.33e-02 +/- 1.67e-03
      Data group 3, n  0.38 +/- 0.03,  norm  9.88e-02 +/- 6.13e-03
      Data group 4, n  0.37 +/- 0.02,  norm  5.33e-02 +/- 2.42e-03
      Data group 5, n  0.37 +/- 0.00,  norm  1.43e-02 +/- 1.17e-03
      Data group 6, n  0.36 +/- 0.01,  norm  5.24e-02 +/- 1.25e-03
      Data group 7, n  0.36 +/- 0.00,  norm  5.46e-02 +/- 1.27e-03
      Data group 8, n  0.21 +/- 0.04,  norm  5.97e-02 +/- 3.90e-03
      Data group 9, n  0.53 +/- 0.03,  norm  3.17e-02 +/- 1.46e-03
      Data group 10, n  0.53 +/- 0.00,  norm  1.18e-02 +/- 9.20e-04

    instrumental lines
      Data group 1, instr const  0.92 +/- 0.05
      Data group 2, instr const  0.85 +/- 0.04
      Data group 3, instr const  0.60 +/- 0.02
      Data group 4, instr const  1.63 +/- 0.06
      Data group 5, instr const  1.79 +/- 0.06
      Data group 6, instr const  0.66 +/- 0.03
      Data group 7, instr const  0.63 +/- 0.03
      Data group 8, instr const  0.64 +/- 0.02
      Data group 9, instr const  1.45 +/- 0.04
      Data group 10, instr const  1.48 +/- 0.04

JUST for my reference, check how fixing extragalactic norm changed our combined
fit.

    unabsorbed kT 0.23 -> 0.26
    absorbed kT 0.37 -> 0.65 (as high as ~0.75... pending error run)
    unabsorbed apec norm ~ 2.9e-4 -> 2.96e-4 (about the same)
    absorbed apec norm 3.3e-3 -> 2.7e-3

    snr kT 1.56 -> 2.5
    snr tau 2.5e+10 -> 1.8e10
    snr Si, S lowered (4.2, 3.7 -> 3.8, 3.4) (more background contrib, different Tau/kT affected emission, ??)
    snr nH 2.19 -> 2.11

OK, so the changes aren't super dramatic.  The excess soft emission could be
explained by freeing the PN power law


Main observation is that kT, Tau remain quite consistent with a hot, recently
shocked plasma.  This continues to remain a robust result, even as we tweak our
background assumptions, etc.




RESEARCH:
* use proton to extrapolate power law indices based on energy-/space- dependent vignetting?
    (yes, do try this -- may reduce backgrounds in image. but your data are so noisy anyways that it may not have much effect).

In general: understanding of mixed morphology remnants
and discrepancy between x-ray and radio features,
with general eye towards other remnants and broader conclusions or predictions.
kepler similariy -- but in fact radio of kepler is brightest in the north (putative CSM interaction); ears are dominated by X-ray synchrotron emission.
I'm still curious as to whether there could be ties to a jet driven explosion.
when do jets appear in Ia models?



List of assumptions to test.  How do the (KEY) fits above change if I:
* run vpshock/vsedov for integrated source or subregion (partially done)
* truncate the low/high energy ranges (cut MOS/PN off at 1keV, 7keV)
  (do separately to illustrate effects)
* change x-ray background fit parameters
* use x-ray background fit parameters from fitting XRB alone?


Standing TODOs:
* Re-run everything from a clean slate to ensure your pipeline is good.
* Look over XMM ESAS scripts and see if I'm missing anything in procedures
  for image scripts.
* Image making -- remove corner events
* Images -- subtract soft proton contamination a la ESAS?  The sharp vignetting
  could contaminate soft emission near the aimpoint, which might look like SNR
  emission...  (partially helped by choice of energy bands for imaging,
  though, as at least it should not confuse sharp features).
* check the filtering threshold of de Luca and Molendi on the corner data.
  (see sec. 3.3 of de luca/molendi 2003) as a sanity check -- was our GTI
  filtering sufficient?

Standing questions:
* Why did exposure maps for PN generate so fast, relative to MOS maps???
* Why did exposure maps for 0551000201 MOS exposures issue warning
  about "NoExpoExt" (no exposure extension found)???

Standing ESAS questions:
* QUESTION: line 581 of mos-spectra, why is elow set to cflim?...
    rot-im-det-sky mode=4, mode=5 are NOT documented on ESAS cookbook
    Similarly passing mode=4,5 to rot-det-sky is not documented either.
* Why does ESAS cookbook recommend PN line at 7.11 keV?
  I haven't seen any evidence for this particular line
  If anything, we should be modeling another line at around 5.3 keV (Cr line?)

Standing low priority questions:
* Castro+2011, why use evselect,merge,eexpmap,emosaic?
  Seems like merge is not needed.
* for region conversion, are PN/MOS1/MOS2 all offset exactly 90 degrees?
  Seems like an OK assumption, <1 degree error will not affect results much.
  More than 1 degree error and I'd worry about shoddy build quality.

Reminders (caveats and loose threads):
* source region differs slightly between exposures; therefore combined fit is
  not completely "true" due to uneven sampling.
  Expect small effect for the integrated spectrum.
  May affect spectra small sub-regions of source (might require discarding 1-2
  exposures or adjusting sub-region selection)
* background region also differs slightly between exposures.
  XRB prefactors accounts for this, assuming uniform XRB.
  Free norms for instrumental lines and SP power laws accounts for the rest.
  Expect power law indices to differ slightly for MOS1/2, but they should not
  be far apart, so it simplifies fit to tie values together.


Standing TO-DOs
===============
vim -R xmmsas_20141104_1833/packages/esas/src/proton_mod.f90 

PENDING QUESTIONS
* PN - perform fit with and without detmapped RMF
  (why is it not detmapped in ESAS?)

REMINDER TO SELF:
* PNS003 filterwheel fit does NOT include OOT correction!
* (background subtraction fits) fitting binned spectra in XSPEC, with
  POISSERR = true, __underestimates__ the true error.
  The opposite approach of letting XSPEC adding all errors in quadrature will
  strongly overestimate the error.

ESAS: vet and submit bug fix for MOS1 CCD4 strip removal; inquire about
detector map for PN RMF...

1. check temporal variation of instrumental lines in (a) FWC data or (b) corner
   data from DB of public observations

2. check surrounding observations for 0551000201 to see how stable (or not) the
   PN QPB is in time.  If it looks stable we can use those obsids to extract PN
   corner spectra.  If not, skip.

   Adjacent obsids are (searching revolutions 1691-1694):
   * 0554600401 (SGR 1806-20) -- PN full frame, good
       (2009-03-03 15:34:01 to 2009-03-04 02:54:15) -- 41ks
   * 0551851301 (RX J0647.7+7015) -- PN ext full frame, good
       (2009-03-04 05:03:54 to 2009-03-05 02:15:19) -- 76ks
   * (before) 0552800201 (XTE J1810-197) -- PN large window
   * 0551000201 (2009-03-06 10:55:31 to 2009-03-07 02:50:01)
   * radzone
   * 0604940101 (CTA1) -- PN small window
   * 0553110201 (G341.2+0.9) -- PN full frame, good
       (2009-03-09 15:01:14 to 2009-03-09 21:02:35) -- 22ks
   * 0553850101 (PSR J1734-3333) -- large window, not useful
   * 0551120301 (Proxima Cen) -- large window (holy shit that's bright)
   * 0550410301 (Geminga) -- small window
   * 0551761001 (3C153) -- full frame, good
       (2009-03-10 20:13:55 to 2009-03-11 02:37:32) -- 23ks

   We have a baseline of about 4 observations within 1 week, centered on the
   observation of 0551000201.

* Explicitly note relative sizes of backgrounds for different instruments, and
  obsids.

Low-priority TO-DO (defer to later): remove pt sources within SNR region, and
merge pt source lists from each obsid.  Use ESAS region task to make
"stinky-cheese" masks with manually specified point sources.

Low-priority: in mos-spectra, rev>2382 also allows ((FLAG & 0x800) != 0)... I
don't know whether this is whats desired but OK.  Worried it would let events
with 0x800 + OTHER flags through.





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

See notes from October 12ish on this.  Well explained in Kuntz/Snowden.

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


