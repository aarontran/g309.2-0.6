Notes on ESAS image creation and mosaicking
===========================================

ESAS tasks to create images:

    mos/pn-spectra
    mos/pn_back
    proton, sp_partial
    (optional: swcx)
    rot-im-det-sky
    comb, adapt
    merge_comp_xmm, adapt_merge

ESAS CALDB SP/flare image sizes are 780px x 780px, which helps explain why ESAS
outputs all output images in that specific size.

ESAS task `mos-spectra`
=======================

Key mos-spectra outputs = counts images + exposure maps in energy band
w/ correct ESAS image parameters

    {CHECK: which images are masked?}

    mos{prefix}-obj.pi - The observation data spectrum from the selected region.
    mos{prefix}.arf - The ARF file for the mosprefix-obj.pi spectrum.
    mos{prefix}.rmf - The RMF file for the mosprefix-obj.pi spectrum.

    mos{prefix}-obj-im.fits - image (sky coords), FOV, "full energy band" (0.3-8 keV)
    mos{prefix}-exp-im.fits - exposure map, FOV, "full energy band"
    mos{prefix}-mask-im.fits - derived mask for above

    mos{prefix}-obj-im-{elow}-{ehigh}.fits - image (sky coords), region, energy band
    mos{prefix}-exp-im-{elow}-{ehigh}.fits - exposure map, region, energy band
    mos{prefix}-mask-im-{elow}-{ehigh}.fits - derived mask for above

    mos{prefix}-obj-im-sp-det.fits - image (det coords), region, "ALL energies" (for proton_scale)
    mos{prefix}-obj-im-det-{elow}-{ehigh}.fits - image (det coords), region, energy band

Key mos_back outputs:

    mos{prefix}-back-im-det-{elow}-{ehigh}.fits - model QPB image (det coords), region, energy band


ESAS tasks `proton` and `sp_partial`
====================================

Key proton INPUTS:

    {mos1,mos2,pn}-flare.fits.gz                        <- SP map
    {spectrum}.pi                                       <- used to get: exposure time
    mos{prefix}-obj-im-det-{elow}-{ehigh}.fits          <- used to get: revolution, file header (template)

Key proton OUTPUTS:

    mos{prefix}-prot-im-det-{elow}-{ehigh}.fits         -> re-scaled SP map in specific energy band

Key sp_partial INPUTS:

    spectrum + image for each of {region, full FOV}     -> manually scale up normalization for proton

For reference: proton (SP) band boundaries are:
300.0, 750.0, 1250.0, 2000.0, 4000.0, 8000.0, 12000.0 (eV).
which yields six energy bands of uneven size.

Question: what is the difference between:

    -flare.fits.gz ?
        = 780 x 780 image, broken down by 6x energy bands & 3x filters
        plus mysterious "SPEXTHIN", "SPEXMEDI", "SPEXTHIC" images
        (I might surmise it means exposure, but why is it lower towards center
         and higher towards edges?...)
    -sp-tot.fits.gz ?
        = 780 x 780 image, showing weak vignetting,
          with pixel size 2.5" square.
          Curious exclusion area right around the boresight.

what are their units?  Doesn't matter because we are always normalizing these
maps, so units cancel.

    proton prefix=1S003 caldb=/CALDB/ specname=mos1S003-obj-grp.pi \
      ccd1=1 ccd2=1 ccd3=1 ccd4=1 ccd5=0 ccd6=1 ccd7=1 \
      elow=400 ehigh=1250 \
      pindex=0.75 pnorm=0.099 spectrumcontrol=1 

    rot-im-det-sky prefix=1S003 elow=400 ehigh=1250 mode=2 

Note: version 5 (2012) does NOT work for broken power law.

Dive into code:

    elim = 300.0, 750.0, 1250.0, 2000.0, 4000.0, 8000.0, 12000.0 (units: eV)
    -> six bands for soft proton image.
    (require elow < 12000 eV)

    elim_low = min{ elim > elow }
    elim_high = min{ elim > ehigh }

    (for elow=300, ehigh=1250,
     we get bands: 300-750, 750-1250)

     ibb = band#s
     fb = scale factors for each band identified in ibb

     IF il < 2:
        il = 2

    do ib=il,ih                     # loop over ib=il,il+1, ..., ih
        ibb(ib - il + 1) = ib-1     # starts at ib-il+1 = 1, ib-1 = il-1
        if ib == il:
            fb(ib-il+1) = max[1, (elim(ib) - elow) / (elim(ib) - elim(ib-1)) ]
        elseif ib == ih:
            fb(ib-il+1) = max[1, (ehigh - elim(ib)) / (elim(ib) - elim(ib-1)) ]
        else:
            fb(ib-il+1) = 1
        endif
    enddo

    # = linear scaling factor.
    # e.g., if I asked for elow=525, ehigh=1250
    # I would get scaling factor 0.5 for band #1
    # (instead of 300-750 eV, only need SP emission for 525-750 eV)
    # Interesting.  why not some logarithmic scaling based on power law
    # index?

    #db_fi = xmmdir + sp_file
        = ../../caldb/mos1-flare.fits.gz
        = ../../caldb/mos2-flare.fits.gz
        = ../../caldb/pn-flare.fits.gz

    creates LUN = fortran logical unit
        open SP flare image into LUN.

    For EACH SP band
        For EACH XMM filter:
            print band#, iext (band# + 2 + {0,7,14})

            Call CFITSIO subroutines to navigate SP flare file.
                FTMAHD: move to (HDU#3)
                FTGHPR: read HDU header
                FTGKYS: get keyword EXTNAME
                    hdu #1 = FITS header
                    hdu #2 = ?
                    hdu #3 = band#1, thin filter
                    hdu #4 = band#2, thin filter
                    ...
                    hdu #10 = band#1, medium filter
                    hdu #11 = band#2, medium filter
                    ...
                    hdu #17 = band#1, thick filter
                    hdu #18 = band#2, thick filter
                    ...
                FTG2DE: read 2-d image of real values

                spmap = spmap + fb(j) * image  # multiply by scale factor, then add to image

    FTCLOS: close the file

    Mask out chips

    rn = sum(spmap, naxis = all)

    FTGIOU, FTOPEN:: open new LUN and load spectrum (mos1S001-src.pi)
    FTGKYE: read EXPOSURE keyword
        exposen = exposure

    eh = ehigh/1000     (0.3 keV)
    el = elow/1000      (1.25 keV)

    if ispec=spectrumcontrol == 1:
        rind = 1 - pindex   # raised index
        prot = pnorm * (eh**rind - el**rind) / rind

    GET TEMPLATE IMAGE FROM
        mos1S001-obj-im-det-{elow}-{ehigh}.fits
        (this is why the {MOS,PN}-SPECTRA call matters...)

    Read out: useful information from header, REVOLUT keyword,
    check for missing MOS1 CCD6,

    prot = exposen * prot       # SP counts [photons/cm^2] in observation

    scale = prot / rn           # scale = {# obs SP counts} / {# spmap counts}

        {# spmap counts = ALL counts in ALL filters, for ALL energy bands of interest}


What does ESAS sp_partial do?

    Input: fullimage, fullspec regionimage, regionspec,
           rnorm (fitted SP normalization for the small region)

    Compute:
      backfull, cfull = spscale(fullimage, fullspec)
      backsel, csel = spscale(regionimage, regionspec)

        spscale:
            db_fi = ../../caldb/mos1-sp-tot.fits.gz
            db_fi = ../../caldb/pn-sp-tot.fits.gz

            load SP image (sp-tot.fits.gz) -> sp
            load maskfile = image -> mask
            load spectrum -> lunspec

            back = BACKSCAL / 1440000.0

            c = sum( sp counts | mask > 0) / (number of mask pixels > 0)

            return back, c

    # Scale up based on BACKSCAL ratio and SP-total ratio
    rrnorm = rnorm * (backfull / backsel) * (cfull / csel)

    return rrnorm


INTERVENING STEP, BEFORE MERGING IMAGES
=======================================

Here, add correctly scaled instrumental line counts to QPB image.
    COMMENT: discrepancy in instr. line fitting could be linked to the ARF/RMF
    files that I'm using... e.g., if FWC line fits are NOT accounting for
    detector QE because I don't use any ARF.

DO check instrumental line counts image against actual spectrum flux.

PNS003 filterwheel fit does NOT include OOT correction!
This may need to be factored into image creation...



ESAS task `comb`
================

Implicitly required inputs for comb:

    mos{prefix}-cheese.fits             # mask (sky, 900x900) (neither contains merged pt source list)
        OR mos{prefix}-mask-im-{elow}-{ehigh}.fits      # exposure-map-based mask

    mos{prefix}-obj-im-{elow}-{ehigh}.fits          # cts image (sky, 900x900)
    pn{prefix}-obj-im-{elow}-{ehigh}-oot.fits       # OOT cts image for PN - must have correct SUBMODE !
    mos{prefix}-back-im-sky-{elow}-{ehigh}.fits     # QPB image (REGION - must create new for full FOV...)
    mos{prefix}-prot-im-sky-{elow}-{ehigh}.fits     # SP image (full FOV)
    mos{prefix}-exp-im-{elow}-{ehigh}.fits          # exposure image (filter scaled)
        + assumed ALPHA for thick/medium filter scaling

    --> comb-obj-im-{ebmin}-{ebmax}.fits
    --> comb-prot-im-sky-{ebmin}-{ebmax}.fits
    --> comb-back-im-sky-{ebmin}-{ebmax}.fits
    --> comb-exp-im-{ebmin}-{ebmax}.fits

    All are co-added 900x900 sky images, multiplied by mask.
        Notably, counts image (obj-im) subtracts OOT events for PN

What does ESAS comb do?  Separately merge count, exposure, QPB, SP, SWCX.

    xmmdir=caldb
    clobber=clobber
    ipart=withpartcontrol       # booleans...
    iprot=withsoftcontrol
    iswcx=withswcxcontrol
    iel=elowlist                # list of lower bounds on energy bands
    ieh=ehighlist               # list of upper bounds on energy bands
        nbands=len(elowlist)
    alpha=alpha                 # re-mapping filter responses
    imask=mask
    prefix=prefixlist
        ndata=len(prefix)

    ebmin = min(elowlist)       # eV
    ebmax = max(ehighlist)      # eV

    islow = (ebmin + 25) / 50           -> used for "hard_scale"
    ishigh = (ebmax + 25) / 50          -> used for "hard_scale"

    if imask = 1:
        im_name = mos{prefix}-cheese.fits
        mask(:,:,n) = retfit(im_name, ...)      # ESAS routine: get FITS file
    elif imask == 0:
        for n in range(len(prefixlist)):
            mask(:,:,n) = np.ones(900,900)
    elif imask == 2:
        im_name = mos{prefix}-mask-im-{elow}-{ehigh}.fits
        mask(:,:,n) = ret
        # do something similar
    elif imask == 3:
        # make_mask_merge - not relevant here

    # -------------------------------------------------------------------------
    # Count images (with OOT event correction)

    for band in bands:
        for n in range(len(prefixlist)):

            im_name = mos{prefix}-obj-im-{elow}-{ehigh}.fits
            im_nameo = pn{prefix}-obj-im-{elow}-{ehigh}-oot.fits         # OOT image for PN
            image = retfit(im_name)

            outim = image * mask(n)
            ncounts(band) += sum(outim)     # sum masked image counts
            totcou += sum(outim)            # sum of masked image counts

            # APPLY OOT CORRECTION
            IF PN:      
                image = retfit(OOT image)
                mode = {SUBMODE keyword from OOT image header}
                if mode == PrimeFullWindow:
                    ootsca = 0.063
                elif mode == PrimeFullWindowExtended
                    ootsca = 0.023
                elif mode == PrimeFullWindowExtended5
                    ootsca = 0.013

                outim -= ootsca * {oot_image}*mask
                ncounts(band) -= ootsca * {oot_image}*mask
                totcou -= ootsca * {oot_image}*mask

    ftopen(luna, im_name)   # open template image [last cts image] to lun{a}

    imo_name = comb-obj-im-{ebmin}-{ebmax}.fits

    ftcphd(luna, lunb)      # Copy header
    ftpdef(lunb, ...)       # Define image extension
    ftmkyj('BITPIX', ...)   # define keyword
    ftp2de(lunb, outim, ...)    # write image

    # -------------------------------------------------------------------------
    # QPB images

    for band in bands:
        for n in range(len(prefixlist)):
            im_name = mos{prefix}-back-im-sky-{elow}-{ehigh}.fits
            ... same spiel
            outim += image*mask
            nback += image*mask
    imo_name = comb-back-im-sky-{ebmin}-{ebmax}.fits


    # -------------------------------------------------------------------------
    # Soft proton images

    for band in bands:
        for n in range(len(prefixlist)):
            im_name = mos{prefix}-prot-im-sky-{elow}-{ehigh}.fits
            ... same spiel
            outim += image*mask
            nback += image*mask
    imo_name = comb-prot-im-sky-{ebmin}-{ebmax}.fits

    # -------------------------------------------------------------------------
    # SWCX images

    same spiel
    for band in bands:
        for n in range(len(prefixlist)):
            ...
            outim += image*mask
            nback += image*mask
    ...

    # -------------------------------------------------------------------------
    # Exposure images (WARNING: different handling!)

    for band in bands:
        for n in range(len(prefixlist)):
            im_name = mos{prefix}-exp-im-{elow}-{ehigh}.fits

            filter = {FILTER keyword from exposure image}
            fscal = hard_scale(alpha, idet, filt,
                               islow=(ebmin+25)/50,
                               ishigh=(ebmax+25)/50)
            # uses ESAS "scal-factors-s/m/h" to map filter responses...
            # normalize to MOS2 medium filter.

            IF nbands > 1
                outim += (ncounts - nback) * fscal * image * mask
            ELSE
                outim += fscal * image * mask

    IF nbands > 1:
        outim = outim / (sum_{band} [ncounts(band) - nback(band)])
        # Funny normalizing (weighting by cts/band), doesn't affect us.

    imo_name = comb-exp-im-{ebmin}-{ebmax}.fits


ESAS task `adapt`
=================

How does adapt work?

    # Some baseline arrays - used fr smoothing and radial plot?...
    XH = -0.1 + 1/15, -0.1 + 2/15, ..., -0.1+1000/15
    YH = 0, 0, ..., 0 [1000x]

    ioff = mod(900, ibin) / 2
    xdim = 900/ibin
    ydim = 900/ibin
    output = (xdim, ydim) shape
    size = (xdim, ydim) shape

    COUNTS = RETFIT("comb-obj-im-{elow}-{ehigh}.fits")
    SCA = -1.0 / ( CDELT(1) * CDELT(2) )            # scale = -1 / (pixel_x_size * pixel_y_size)
        # I.e., scale from counts/pixel to counts/deg^2.

    EXPOSE = RETFIT("comb-exp-im-{elow}-{ehigh}.fits", ...)
    BACK = RETFIT("comb-back-im-sky-{elow}-{ehigh}.fits", ...)
    PROT = RETFIT("comb-prot-im-sky-{elow}-{ehigh}.fits", ...)
    SWCX = RETFIT("comb-swcx-im-sky-{elow}-{ehigh}.fits", ...)

    BACK = BACK + PROT + SWCX  (straightforward addition)
        No need to deal with PROT, SWCX after this.

    RNC = sum(COUNTS)       # Counts...
    RNB = sum(BACK)
    RBP = sum(PROT)
    RNS = sum(SWCX)
    REX = sum(EXPOSE)

    EX = max(EXPOSE)
    XCEN, YCEN = coords_of_max(EXPOSE)

    if MASKFILE:
        MASK = RETFIT(MASKFILE, ...)
    else:
        MASK = EXPOSE

    TLIM = sum(MASK)
    J = count(non_zero(MASK))   # number of non-zero pixels in mask
    TLIM = TEMSC * TLIM / J     # threshold for masking: TEMSC = fraction of
                                # avg mask value at which to cut pixels

    CTS, BCK, EXPO, N = length 50 arrays
    # ... write radial-filt-{elow}-{ehigh}.qdp

    i2 = 900/ibin       # same as xdim = ydim ...

    # bin,

        # bin BACK, COUNTS, EXPOSE

    # smooth

        # adaptively gaussian smooth BACK, COUNTS, EXPOSE

        OUTPUT = SCA * (CLAST - BLAST)/ELAST

    adapt-{elow}-{ehigh}.fits
    size-{elow}-{ehigh}.fits

OK, task ADAPT is pretty straightforward.

BUT, multiple adaptively smoothed images should not be co-added -- this ruins
part of the point of adaptive smoothing.

And, for equivalent width images, I think each image needs to be smoothed
identically to allow correct continuum subtraction.

Output units: counts/sec/deg^2

ESAS task `merge_comp_xmm`
==========================

What is the principle undertaken for mosaicking multiple observations, now?
This supersedes comb/adapt (!).

    setup:

        xmm/merge
        xmm/0087940201/odf
        xmm/0087940201/repro
        xmm/0551000201/odf
        xmm/0551000201/repro

    Write to xmm/merge/dir.dat:

        ../0087940201/repro/mos1S001
        ../0087940201/repro/mos2S002
        ../0087940201/repro/pnS003
        ../0551000201/repro/mos1S001
        ../0551000201/repro/mos2S002

    merge_comp_xmm caldb=/CALDB dirfile=dir.dat
    coord=2 crvaln1=210.85 crvaln2=54.35
    pixelsize=0.03 component={1,2,3,4}              <- counts, exp, QPB, SP
    elow=400 ehigh=750 maskcontrol=0
    xdim=1100 ydim=1100

inputs are:

    {dirstr}-obj-im-{elow}-{ehigh}.fits
    {dirstr}-obj-im-{elow}-{ehigh}-oot.fits
    {dirstr}-exp-im-{elow}-{ehigh}.fits
    {dirstr}-back-im-sky-{elow}-{ehigh}.fits
    {dirstr}-prot-im-sky-{elow}-{ehigh}.fits
    {dirstr}-swcx-im-sky-{elow}-{ehigh}.fits

    {dirstr}-cheese{/-s/-h}.fits
    {dirstr}-mask-im-{elow}-{ehigh}.fits
    {dirstr}-msl-cheese{/-s/-h}.fits

merge_comp_xmm outputs to:

    obj-im-{elow}-{ehigh}.fits
    exp-im-{elow}-{ehigh}.fits
    back-im-{elow}-{ehigh}.fits
    prot-im-{elow}-{ehigh}.fits
    swcx-im-{elow}-{ehigh}.fits

Exposure map merge accounts for filter scaling (hard,med,soft power law like before)

Basically does the obvious: reproject and merge.  No binning/smoothing.

