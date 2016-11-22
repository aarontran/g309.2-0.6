#!/bin/tcsh -f

# Merge point source lists from multiple XMM obsids/exposures created using SAS
# region in contour mode.
# Merged point source list is stored in celestial RA/dec.
# Then, create drop-in replacements for ESAS point source masks:
#     ${exp}-bkg_region-sky.fits 
#     ${exp}-bkg_region-det.fits 
# after saving ESAS originals to *-ori.fits.
#
# The end goal is to have a consistent set of source masks for all subsequent
# ESAS analysis.

# Must use tcsh because I source sasinit directly in this script

# Configuration

set OBSIDS = "0087940201 0551000201"
set EXPS = "mos1S001 mos2S002 pnS003"
set PNEXP = "pnS003"
set SAS_REPRO_MERGED = "${XMM_PATH}/repro_merged"

# Do work

cd $XMM_PATH

mkdir -p $SAS_REPRO_MERGED

foreach obsid ($OBSIDS)

  # Kludge to get SAS_REPRO... (copied from below)
  set sasinit_exe=`which sasinit`
  source $sasinit_exe $obsid

  cd $SAS_REPRO

  foreach exp ($EXPS)

    echo "Processing $obsid $exp ESAS cheese masks"
    echo "  Moving original cheese outputs to -ori.fits (unless already done)"

    # --no-clobber ensures that *-ori.fits
    # always represents original cheese output
    mv --verbose --no-clobber \
      "${exp}-bkg_region-det.fits" \
      "${exp}-bkg_region-det-ori.fits"
    mv --verbose --no-clobber \
      "${exp}-bkg_region-sky.fits" \
      "${exp}-bkg_region-sky-ori.fits"

    echo "  Validating coordinate transformation"

    # Validation step for coordinate transform.
    # FORCE user to inspect 1. RMS and min/max error, 2. quiver plot of errors
    ascregion_sky2radec.py --merge-dist 5 \
      "${exp}-bkg_region-sky-ori.fits" \
      --out "$SAS_REPRO_MERGED/${obsid}-${exp}-bkg_region-radec.fits"
    ascregion_radec2sky.py \
      "$SAS_REPRO_MERGED/${obsid}-${exp}-bkg_region-radec.fits" \
      --projection-reference "${exp}-bkg_region-sky-ori.fits" \
      --out "$SAS_REPRO_MERGED/${obsid}-${exp}-bkg_region-sky2radec2sky.fits"
    validate_sky2radec2sky.py \
      "${exp}-bkg_region-sky-ori.fits" \
      "$SAS_REPRO_MERGED/${obsid}-${exp}-bkg_region-sky2radec2sky.fits"
  end
end

# Validation step for coordinate transform

echo "Merging point sources..."

ascregion_sky2radec.py \
    "0087940201/repro/mos1S001-bkg_region-sky-ori.fits" \
    "0087940201/repro/mos2S002-bkg_region-sky-ori.fits" \
    "0087940201/repro/pnS003-bkg_region-sky-ori.fits" \
    "0551000201/repro/mos1S001-bkg_region-sky-ori.fits" \
    "0551000201/repro/mos2S002-bkg_region-sky-ori.fits" \
    "0551000201/repro/pnS003-bkg_region-sky-ori.fits" \
    --merge-dist 5 \
    --out "$SAS_REPRO_MERGED/all-bkg_region-radec.fits" \
  >& "$SAS_REPRO_MERGED/ascregion_sky2radec.log"


foreach obsid ($OBSIDS)

  # Kludge to set SAS_CCF, SAS_ODF for conv_reg invocation (╯°□°）╯︵ ┻━┻
  set sasinit_exe=`which sasinit`
  source $sasinit_exe $obsid

  cd $SAS_REPRO

  foreach exp ($EXPS)

    echo "Converting merged list into new masks for $obsid $exp"

    # touch to prevent weird primary header copy error that makes conv_reg
    # choke if output file doesn't already exist
    touch "${exp}-bkg_region-det.fits"
    conv_reg mode=1 inputfile="$SAS_REPRO_MERGED/all-bkg_region-radec.fits" \
      imagefile="${exp}-obj-im.fits" outputfile="${exp}-bkg_region-det.fits"
    rm -f detpos.txt

    ascregion_radec2sky.py "$SAS_REPRO_MERGED/all-bkg_region-radec.fits" \
      --projection-reference "${exp}-bkg_region-sky-ori.fits" \
      --out "${exp}-bkg_region-sky.fits"

    # Diagnostic image to verify successful point source exclusion
    # based on ESAS evselect calls in cheese, mos-spectra
    # (withxranges, withyranges are not officially documented but appear
    #  significant, based on perusing source code)
    if ($exp != $PNEXP) then
        set pattfilt = "(PATTERN<=12)"
    else
        set pattfilt = "(PATTERN<=4)"
    endif
    evselect table="${exp}-clean.fits:EVENTS" withfilteredset=yes \
      expression="${pattfilt}&&(FLAG == 0)&&(PI in [2500:12000])&&region(${exp}-bkg_region-det.fits)" \
      imageset="${exp}-merged-cheese-im_region-det.fits" \
      filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes \
      imagebinning='imageSize' squarepixels=yes ignorelegallimits=yes \
      xcolumn='X' ximagesize=900 ximagemax=48400 ximagemin=3401 \
      ycolumn='Y' yimagesize=900 yimagemax=48400 yimagemin=3401

    # Same call, but use sky version now.
    evselect table="${exp}-clean.fits:EVENTS" withfilteredset=yes \
      expression="${pattfilt}&&(FLAG == 0)&&(PI in [2500:12000])&&region(${exp}-bkg_region-sky.fits)" \
      imageset="${exp}-merged-cheese-im_region-sky.fits" \
      filtertype=expression keepfilteroutput=no updateexposure=yes filterexposure=yes \
      imagebinning='imageSize' squarepixels=yes ignorelegallimits=yes \
      xcolumn='X' ximagesize=900 ximagemax=48400 ximagemin=3401 \
      ycolumn='Y' yimagesize=900 yimagemax=48400 yimagemin=3401

  end
end

# Interactive usage: inspect diagnostic images against
#cd $XMM_PATH
#ds9 0087940201/repro/mos1S001-merged-cheese-im.fits \
#    0087940201/repro/mos1S001-cheese.fits \
#    0087940201/repro/mos2S002-cheese.fits \
#    0087940201/repro/pnS003-cheese.fits \
#    0551000201/repro/mos1S001-cheese.fits \
#    0551000201/repro/mos2S002-cheese.fits \
#    0551000201/repro/pnS003-cheese.fits
#
#ds9 0087940201/repro/mos1S001-merged-cheese-im.fits \
#    0087940201/repro/mos2S002-merged-cheese-im.fits \
#    0087940201/repro/pnS003-merged-cheese-im.fits \
#    0551000201/repro/mos1S001-merged-cheese-im.fits \
#    0551000201/repro/mos2S002-merged-cheese-im.fits \
#    0551000201/repro/pnS003-merged-cheese-im.fits

