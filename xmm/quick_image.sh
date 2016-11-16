#!/bin/bash

# TODO: interesting error messages for 0551000201
# and PN exposure maps are computed much faster than MOS maps

OBSID=$1

if [[ "$#" -ne 1 ]]; then
    echo "ERROR: one argument (obsid) required"
    exit 1
fi
if [[ "$OBSID" != "$SAS_OBSID" ]]; then
  echo "ERROR: obsid $OBSID does not match SASINIT value ($SAS_OBSID)"
  exit 1
fi

cd "${XMM_PATH}/${OBSID}/repro"

exposures="mos1S001 mos2S002 pnS003"

# Three bands, one broad band, three narrow line bands (Mg, Si, S)
bands=("0.8-3.3" "0.8-1.4" "1.75-2.3" "2.3-3.3" "1.3-1.4" "1.8-1.9" "2.4-2.5")
pi_mins=( "800"   "800" "1750" "2300" "1300" "1800" "2400")
pi_maxs=("3300" "1400"  "2300" "3300" "1400" "1900" "2500")

# Broadband 0.8-3.3 keV exposure map will not be great !...

for exp in $exposures; do

  for ((i=0;i<${#bands[@]};++i)); do

    band="${bands[$i]}"
    pi_min="${pi_mins[$i]}"
    pi_max="${pi_maxs[$i]}"

    evselect table="${exp}-clean.fits:EVENTS" withfilteredset=yes \
      filtertype=expression expression="(PATTERN<=12)&&(FLAG == 0) && (PI in [${pi_min}:${pi_max}])" \
      withimageset=yes imageset="${exp}-im-sky-${band}kev-test.fits" \
      squarepixels=yes ignorelegallimits=yes \
      xcolumn='X' ycolumn='Y' ximagebinsize=8 yimagebinsize=8 \
      updateexposure=yes filterexposure=yes

    # Broadband exp map
    eexpmap eventset="${exp}-clean.fits:EVENTS" attitudeset=atthk.fits \
      imageset="${exp}-im-sky-${band}kev-test.fits" \
      expimageset="${exp}-exp-sky-${band}kev-test.fits" \
      pimin="${pi_min}" pimax="${pi_max}"

  done

done
