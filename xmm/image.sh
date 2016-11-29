#!/bin/bash

# Configuration
CALDB="${XMM_PATH}/caldb"
# Must have been created in specbackprot_image already
PI_MINS=( "800" "1300" "1800" "2400" "1150" "1600" "1980" "2600")
PI_MAXS=("3300" "1400" "1900" "2500" "1250" "1650" "2050" "2700")

BINNINGS="1 2 4 8 16"

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
        xdim=1100 ydim=1100 clobber=1 \
      &> "merge_comp_xmm_${elow}-${ehigh}_component-${j}.log"
  done

  # Just vary parameters by hand for now since adaptively smoothed image is not
  # being used for real analysis
  echo "  adapt_merge ..."
  adapt_merge elowlist="${elow} ${elow} ${elow} ${elow} ${elow}" \
      ehighlist="${ehigh} ${ehigh} ${ehigh} ${ehigh} ${ehigh}" \
      withpartcontrol=yes withsoftcontrol=yes withswcxcontrol=no \
      withmaskcontrol=no \
      binning=2 smoothingcounts=50 thresholdmasking=0.02 fill=0 clobber=yes \
    &> "adapt_merge_${elow}-${ehigh}.log"

  for binning in $BINNINGS; do

    # WARNING: task requires pixel size 2.5" x 2.5" (hardcoded in ESAS)
    echo "  bin_image_merge binning=${binning} ..."
    bin_image_merge elowlist="${elow} ${elow} ${elow} ${elow} ${elow}" \
        ehighlist="${ehigh} ${ehigh} ${ehigh} ${ehigh} ${ehigh}" \
        withpartcontrol=yes withsoftcontrol=yes withswcxcontrol=no \
        withmaskcontrol=no \
        binning=${binning} thresholdmasking=0.02 clobber=yes \
      &> "bin_image_merge_${elow}-${ehigh}_binning-${binning}.log"

    mv -v "bin-${elow}-${ehigh}.fits" "bin-${elow}-${ehigh}_binning-${binning}.fits"
    mv -v "sig-${elow}-${ehigh}.fits" "sig-${elow}-${ehigh}_binning-${binning}.fits"
  done

done


