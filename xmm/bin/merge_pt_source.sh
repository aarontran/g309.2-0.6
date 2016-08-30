#!/bin/tcsh -f

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
  foreach exp ($EXPS)
    mv --verbose --no-clobber \
      "${obsid}/repro/${exp}-bkg_region-det.fits" \
      "${obsid}/repro/${exp}-bkg_region-det-ori.fits"
  end
end

ascregion_sky2radec.py --out "$SAS_REPRO_MERGED/all-bkg_region-radec.fits" \
    --merge-dist 5 \
    0087940201/repro/mos1S001-bkg_region-sky.fits \
    0087940201/repro/mos2S002-bkg_region-sky.fits \
    0087940201/repro/pnS003-bkg_region-sky.fits \
    0551000201/repro/mos1S001-bkg_region-sky.fits \
    0551000201/repro/mos2S002-bkg_region-sky.fits \
    0551000201/repro/pnS003-bkg_region-sky.fits \
  >& "$SAS_REPRO_MERGED/ascregion_sky2radec.log"

foreach obsid ($OBSIDS)

  # Kludge to set SAS_CCF, SAS_ODF for conv_reg invocation (╯°□°）╯︵ ┻━┻
  set sasinit_exe=`which sasinit`
  source $sasinit_exe $obsid

  cd $SAS_REPRO

  foreach exp ($EXPS)

    # touch to prevent weird primary header copy error
    touch "${exp}-bkg_region-det.fits"
    conv_reg mode=1 inputfile="$SAS_REPRO_MERGED/all-bkg_region-radec.fits" \
      imagefile="${exp}-obj-im.fits" outputfile="${exp}-bkg_region-det.fits"
    rm -f detpos.txt

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
      imageset="${exp}-merged-cheese-im.fits" \
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

