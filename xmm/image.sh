#!/bin/bash

# Must be run from ${XMM_PATH}/repro_merged/ or any directory that has an
# appropriate dir.dat file.

# Configuration
CALDB="${XMM_PATH}/caldb"
MASK_RADEC="all-bkg_region-radec.fits"
# Must have been created in specbackprot_image already
# Must be formatted in ESAS manner (no leading zeros, no 'E' notation)
PI_MINS=( "800" "1300" "1800" "2400" "1150" "1600" "1980" "2600")
PI_MAXS=("3300" "1400" "1900" "2500" "1250" "1650" "2050" "2700")

#BINNINGS="1 2 4 8 16"

# "Effective" smooth factors ~16, ~32
BINNING_COMBO=("4" "8" "16" "8" "16")
SMOOTH_COMBO=( "4" "2"  "1" "4"  "2")

# Merger commands

for ((i=0;i<${#PI_MINS[@]};++i)); do

  elow="${PI_MINS[$i]}"
  ehigh="${PI_MAXS[$i]}"

  echo "Processing ${elow}-${ehigh} eV images"

  # i = 1: count image,
  # i = 2: exposure,
  # i = 3: QPB counts,
  # i = 4: SP counts,
  # i = 5: SWCX counts (skipping)
  for ((j=1;j<=4;++j)); do
    # coord = 2: equatorial coordinates
    # crvaln1,2: center of coordinate projection (use 0087940201 values)
    # pixelsize=0.04166666667 arcmin/px = 2.5 arcsec/px
    # (matches output scaling from ESAS {mos,pn}-spectra sky images)
    #/soft/XMM/xmmsas_20141104_1833/bin/merge_comp_xmm \
    echo "  merge_comp_xmm component=${j} ..."
    merge_comp_xmm caldb=${CALDB} dirfile=dir.dat \
        coord=2 crvaln1=206.704208333333 crvaln2=-62.84125 \
        pixelsize=0.04166666667 component=${j} \
        elow=${elow} ehigh=${ehigh} maskcontrol=0 \
        xdim=1000 ydim=1000 clobber=1 \
      &> "merge_comp_xmm_${elow}-${ehigh}_component-${j}.log"
  done

  # Fill source holes in counts images, immediately after merge_comp_xmm
  # MUST be run immediately after merge_comp_xmm...
  echo "  hole_filler.py ..."
  mv "obj-im-${elow}-${ehigh}.fits" "obj-im-${elow}-${ehigh}-nofill.fits"
  hole_filler.py "obj-im-${elow}-${ehigh}-nofill.fits" \
      "exp-im-${elow}-${ehigh}.fits" \
      --out "obj-im-${elow}-${ehigh}-filled.fits" --clobber \
      --mask "$MASK_RADEC" --annulus-width 4 \
    &> "hole_filler_${elow}-${ehigh}.log"
  ln -s "obj-im-${elow}-${ehigh}-filled.fits" "obj-im-${elow}-${ehigh}.fits"

#  # Just vary parameters by hand for now since adaptively smoothed image is not
#  # being used for real analysis
#  echo "  adapt_merge ..."
#  adapt_merge elowlist="${elow} ${elow} ${elow} ${elow} ${elow}" \
#      ehighlist="${ehigh} ${ehigh} ${ehigh} ${ehigh} ${ehigh}" \
#      withpartcontrol=yes withsoftcontrol=yes withswcxcontrol=no \
#      withmaskcontrol=no \
#      binning=2 smoothingcounts=50 thresholdmasking=0.02 fill=0 clobber=yes \
#    &> "adapt_merge_${elow}-${ehigh}.log"

  # NOTE: ESAS task bin_image_merge does NOT subtract background correctly
  # for our low-count images.
  # (1) Use better approximation for Poisson error at low count rates
  # (2) Bin/smooth images before background subtraction, or else
  # background will be severely underestimated in our low-count images


  # Subtract background and correct for exposure
  # with varying bin/smooth combinations
  for ((j=0;j<${#BINNING_COMBO[@]};++j)); do

    BIN="${BINNING_COMBO[$j]}"
    SMOOTH="${SMOOTH_COMBO[$j]}"
    echo "  Bin $BIN, smooth $SMOOTH:"

    prefixes="obj exp prot back"
    for prefix in $prefixes; do
      echo "    Bin/smooth: $prefix"
      raw="${prefix}-im-${elow}-${ehigh}.fits"
      binned="${prefix}-im-${elow}-${ehigh}_bin${BIN}.fits"
      smoothed="${prefix}-im-${elow}-${ehigh}_bin${BIN}_gauss${SMOOTH}.fits"
      fimgbin "$raw" "$binned" ${BIN} clobber=yes
      fgauss "$binned" "$smoothed" ${SMOOTH} clobber=yes
    done

    # Compute errors from BINNED object image, because errors are
    # sqrt(sum_i n_i) rather than sum_i sqrt(n_i)
    echo "  Creating \"error\" counts image"
    # Gehrels' (1986) 1-sigma upper limit, eq. (7); same expression used by XSPEC
    ftpixcalc "sig-im-${elow}-${ehigh}_bin${BIN}.fits" "sqrt(a + 0.75) + 1" \
      a="obj-im-${elow}-${ehigh}_bin${BIN}.fits" clobber=yes
    # Smoothed error image is not really physical. need to think about this.
    fgauss "sig-im-${elow}-${ehigh}_bin${BIN}.fits" \
      "sig-im-${elow}-${ehigh}_bin${BIN}_gauss${SMOOTH}.fits" \
      ${SMOOTH} clobber=yes

    # Inputs
    obj="obj-im-${elow}-${ehigh}_bin${BIN}_gauss${SMOOTH}.fits"
    exp="exp-im-${elow}-${ehigh}_bin${BIN}_gauss${SMOOTH}.fits"
    sig="sig-im-${elow}-${ehigh}_bin${BIN}_gauss${SMOOTH}.fits"
    prot="prot-im-${elow}-${ehigh}_bin${BIN}_gauss${SMOOTH}.fits"
    back="back-im-${elow}-${ehigh}_bin${BIN}_gauss${SMOOTH}.fits"
    # Outputs
    out="corrected-${elow}-${ehigh}_bin${BIN}_gauss${SMOOTH}.fits"
    outsig="corrected-sig-${elow}-${ehigh}_bin${BIN}_gauss${SMOOTH}.fits"

    # Perform mathematical operations
    echo "    Exposure-corrected, background-subtracted ${elow}-${ehigh} image"
    farith "$obj" "$back" "temp_subtr_back.fits" "SUB" clobber=yes
    farith "temp_subtr_back.fits" "$prot" "temp_subtr_all.fits" "SUB" clobber=yes
    farith "temp_subtr_all.fits" "$exp" "$out" "DIV" null=yes clobber=yes
    rm temp_subtr_back.fits temp_subtr_all.fits

    echo "    Exposure-corrected ${elow}-${ehigh} error image"
    farith "$sig" "$exp" "$outsig" "DIV" null=yes clobber=yes

  done

done


for ((j=0;j<${#BINNING_COMBO[@]};++j)); do

  BIN="${BINNING_COMBO[$j]}"
  SMOOTH="${SMOOTH_COMBO[$j]}"
  echo "Equivalent width & line flux images: bin $BIN, smooth $SMOOTH"

  suffix="bin${BIN}_gauss${SMOOTH}"

  # Construct line flux images

  echo "  Mg line flux"
  eq_width.py "corrected-1300-1400_${suffix}.fits" "corrected-1150-1250_${suffix}.fits" "corrected-1600-1650_${suffix}.fits" \
    --bands "1150-1250,1300-1400,1600-1650" \
    --flux --out "mg_lineflux_${suffix}.fits" \
    --out-interp-cont "mg_interpcont_${suffix}.fits" --clobber

  echo "  Si line flux"
  eq_width.py "corrected-1800-1900_${suffix}.fits" "corrected-1600-1650_${suffix}.fits" "corrected-1980-2050_${suffix}.fits" \
    --bands "1600-1650,1800-1900,1980-2050" \
    --flux --out "si_lineflux_${suffix}.fits" \
    --out-interp-cont "si_interpcont_${suffix}.fits" --clobber

  echo "  S line flux"
  eq_width.py "corrected-2400-2500_${suffix}.fits" "corrected-1980-2050_${suffix}.fits" "corrected-2600-2700_${suffix}.fits" \
    --bands "1980-2050,2400-2500,2600-2700" \
    --flux --out "s_lineflux_${suffix}.fits" \
    --out-interp-cont "s_interpcont_${suffix}.fits" --clobber

  # Construct eq width images

  echo "  Mg eq.width"
  eq_width.py "corrected-1300-1400_${suffix}.fits" "corrected-1150-1250_${suffix}.fits" "corrected-1600-1650_${suffix}.fits" \
    --bands "1150-1250,1300-1400,1600-1650" \
    --out "mg_eqwidth_${suffix}.fits" --clobber

  echo "  Si eq.width"
  eq_width.py "corrected-1800-1900_${suffix}.fits" "corrected-1600-1650_${suffix}.fits" "corrected-1980-2050_${suffix}.fits" \
    --bands "1600-1650,1800-1900,1980-2050" \
    --out "si_eqwidth_${suffix}.fits" --clobber

  echo "  S eq.width"
  eq_width.py "corrected-2400-2500_${suffix}.fits" "corrected-1980-2050_${suffix}.fits" "corrected-2600-2700_${suffix}.fits" \
    --bands "1980-2050,2400-2500,2600-2700" \
    --out "s_eqwidth_${suffix}.fits" --clobber


  # Construct crude 1st-order approx error images for line flux and eq width
  # WARNING: I assume mean interpolation, which is NOT correct.
  # But our error estimates are very rough currently, anyways.
  # If presented, we should use the correct factors.
  # ----------------------------------------------------------

  # Expression to estimate absolute error for line flux
  lineflux_sigma_expr="sqrt(DL*DL + F*F * (0.5*(DA/A)*(DA/A) + 0.5*(DB/B)*(DB/B)))"

  echo "  Lineflux image errors..."

  ftpixcalc "mg_lineflux-sig_${suffix}.fits" "$lineflux_sigma_expr" \
    a="DL=corrected-sig-1300-1400_${suffix}.fits" \
    b="F=mg_interpcont_${suffix}.fits" \
    c="DA=corrected-sig-1150-1250_${suffix}.fits" \
    d="A=corrected-1150-1250_${suffix}.fits" \
    e="DB=corrected-sig-1600-1650_${suffix}.fits" \
    f="B=corrected-1600-1650_${suffix}.fits" \
    clobber=yes
  ftpixcalc "mg_lineflux-relsig_${suffix}.fits" \
    "a/b" \
    a="mg_lineflux-sig_${suffix}.fits" \
    b="mg_lineflux_${suffix}.fits" \
    clobber=yes

  ftpixcalc "si_lineflux-sig_${suffix}.fits" "$lineflux_sigma_expr" \
    a="DL=corrected-sig-1800-1900_${suffix}.fits" \
    b="F=si_interpcont_${suffix}.fits" \
    c="DA=corrected-sig-1600-1650_${suffix}.fits" \
    d="A=corrected-1600-1650_${suffix}.fits" \
    e="DB=corrected-sig-1980-2050_${suffix}.fits" \
    f="B=corrected-1980-2050_${suffix}.fits" \
    clobber=yes
  ftpixcalc "si_lineflux-relsig_${suffix}.fits" \
    "a/b" \
    a="si_lineflux-sig_${suffix}.fits" \
    b="si_lineflux_${suffix}.fits" \
    clobber=yes

  ftpixcalc "s_lineflux-sig_${suffix}.fits" "$lineflux_sigma_expr" \
    a="DL=corrected-sig-2400-2500_${suffix}.fits" \
    b="F=s_interpcont_${suffix}.fits" \
    c="DA=corrected-sig-1980-2050_${suffix}.fits" \
    d="A=corrected-1980-2050_${suffix}.fits" \
    e="DB=corrected-sig-2600-2700_${suffix}.fits" \
    f="B=corrected-2600-2700_${suffix}.fits" \
    clobber=yes
  ftpixcalc "s_lineflux-relsig_${suffix}.fits" \
    "a/b" \
    a="s_lineflux-sig_${suffix}.fits" \
    b="s_lineflux_${suffix}.fits" \
    clobber=yes

  # Now do equivalent width errors
  # ------------------------------

  # First piece of sigma expression
  eqwidth_sigma1_expr="sqrt((DL/L)*(DL/L) + 0.5*(DA/A)*(DA/A) + 0.5*(DB/B)*(DB/B))"

  echo "  Equivalent width image errors..."

  ftpixcalc "mg_sqrttmp.fits" "$eqwidth_sigma1_expr" \
    a="DL=corrected-sig-1300-1400_${suffix}.fits" \
    b="L=corrected-1300-1400_${suffix}.fits" \
    c="DA=corrected-sig-1150-1250_${suffix}.fits" \
    d="A=corrected-1150-1250_${suffix}.fits" \
    e="DB=corrected-sig-1600-1650_${suffix}.fits" \
    f="B=corrected-1600-1650_${suffix}.fits" \
    clobber=yes
  # ftpixcalc fails if I multiply something outside a sqrt...
  ftpixcalc "mg_eqwidth-sig_${suffix}.fits" \
    "(EW + 100) * SQRTTMP" \
    a="EW=mg_eqwidth_${suffix}.fits" \
    b="SQRTTMP=mg_sqrttmp.fits" \
    clobber=yes
  ftpixcalc "mg_eqwidth-relsig_${suffix}.fits" \
    "a/b" \
    a="mg_eqwidth-sig_${suffix}.fits" \
    b="mg_eqwidth_${suffix}.fits" \
    clobber=yes
  rm mg_sqrttmp.fits

  ftpixcalc "si_sqrttmp.fits" "$eqwidth_sigma1_expr" \
    a="DL=corrected-sig-1800-1900_${suffix}.fits" \
    b="L=corrected-1800-1900_${suffix}.fits" \
    c="DA=corrected-sig-1600-1650_${suffix}.fits" \
    d="A=corrected-1600-1650_${suffix}.fits" \
    e="DB=corrected-sig-1980-2050_${suffix}.fits" \
    f="B=corrected-1980-2050_${suffix}.fits" \
    clobber=yes
  ftpixcalc "si_eqwidth-sig_${suffix}.fits" \
    "(EW + 100) * SQRTTMP" \
    a="EW=si_eqwidth_${suffix}.fits" \
    b="SQRTTMP=si_sqrttmp.fits" \
    clobber=yes
  ftpixcalc "si_eqwidth-relsig_${suffix}.fits" \
    "a/b" \
    a="si_eqwidth-sig_${suffix}.fits" \
    b="si_eqwidth_${suffix}.fits" \
    clobber=yes
  rm si_sqrttmp.fits

  ftpixcalc "s_sqrttmp.fits" "$eqwidth_sigma1_expr" \
    a="DL=corrected-sig-2400-2500_${suffix}.fits" \
    b="L=corrected-2400-2500_${suffix}.fits" \
    c="DA=corrected-sig-1980-2050_${suffix}.fits" \
    d="A=corrected-1980-2050_${suffix}.fits" \
    e="DB=corrected-sig-2600-2700_${suffix}.fits" \
    f="B=corrected-2600-2700_${suffix}.fits" \
    clobber=yes
  ftpixcalc "s_eqwidth-sig_${suffix}.fits" \
    "(EW + 100) * SQRTTMP" \
    a="EW=s_eqwidth_${suffix}.fits" \
    b="SQRTTMP=s_sqrttmp.fits" \
    clobber=yes
  ftpixcalc "s_eqwidth-relsig_${suffix}.fits" \
    "a/b" \
    a="s_eqwidth-sig_${suffix}.fits" \
    b="s_eqwidth_${suffix}.fits" \
    clobber=yes
  rm s_sqrttmp.fits

done

