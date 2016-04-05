#!/bin/bash

# MUST RUN FROM REPRO DIRECTORY

# TODO: interesting error messages for 0551000201
# and PN exposure maps are computed much faster than MOS maps

#exposures="mos1S001 mos2S002 pnS003"
#exposures="mos1S001 mos2S002"
exposures="pnS003"

for exp in $exposures; do

  # Broadband 0.8-3.3 keV -- exposure map will not be great !...
  evselect table="${exp}-clean.fits:EVENTS" withfilteredset=yes \
    filtertype=expression expression='(PATTERN<=12)&&(FLAG == 0) && (PI in [800:3300])' \
    withimageset=yes imageset="${exp}-im-sky-0.8-3.3kev-test.fits" \
    squarepixels=yes ignorelegallimits=yes \
    xcolumn='X' ycolumn='Y' ximagebinsize=8 yimagebinsize=8 \
    updateexposure=yes filterexposure=yes

  # Create image in three bands
  evselect table="${exp}-clean.fits:EVENTS" withfilteredset=yes \
    filtertype=expression expression='(PATTERN<=12)&&(FLAG == 0) && (PI in [800:1400])' \
    withimageset=yes imageset="${exp}-im-sky-0.8-1.4kev-test.fits" \
    squarepixels=yes ignorelegallimits=yes \
    xcolumn='X' ycolumn='Y' ximagebinsize=8 yimagebinsize=8 \
    updateexposure=yes filterexposure=yes
  evselect table="${exp}-clean.fits:EVENTS" withfilteredset=yes \
    filtertype=expression expression='(PATTERN<=12)&&(FLAG == 0) && (PI in [1750:2300])' \
    withimageset=yes imageset="${exp}-im-sky-1.75-2.3kev-test.fits" \
    squarepixels=yes ignorelegallimits=yes \
    xcolumn='X' ycolumn='Y' ximagebinsize=8 yimagebinsize=8 \
    updateexposure=yes filterexposure=yes
  evselect table="${exp}-clean.fits:EVENTS" withfilteredset=yes \
    filtertype=expression expression='(PATTERN<=12)&&(FLAG == 0) && (PI in [2300:3300])' \
    withimageset=yes imageset="${exp}-im-sky-2.3-3.3kev-test.fits" \
    squarepixels=yes ignorelegallimits=yes \
    xcolumn='X' ycolumn='Y' ximagebinsize=8 yimagebinsize=8 \
    updateexposure=yes filterexposure=yes

  # Broadband exp map
  eexpmap eventset="${exp}-clean.fits:EVENTS" attitudeset=atthk.fits \
    imageset="${exp}-im-sky-0.8-3.3kev-test.fits" \
    expimageset="${exp}-exp-sky-0.8-3.3kev-test.fits" \
    pimin=800 pimax=3300

  # Band exp map
  eexpmap eventset="${exp}-clean.fits:EVENTS" attitudeset=atthk.fits \
    imageset="${exp}-im-sky-0.8-1.4kev-test.fits" \
    expimageset="${exp}-exp-sky-0.8-1.4kev-test.fits" \
    pimin=800 pimax=1400
  eexpmap eventset="${exp}-clean.fits:EVENTS" attitudeset=atthk.fits \
    imageset="${exp}-im-sky-1.75-2.3kev-test.fits" \
    expimageset="${exp}-exp-sky-1.75-2.3kev-test.fits" \
    pimin=1750 pimax=2300
  eexpmap eventset="${exp}-clean.fits:EVENTS" attitudeset=atthk.fits \
    imageset="${exp}-im-sky-2.3-3.3kev-test.fits" \
    expimageset="${exp}-exp-sky-2.3-3.3kev-test.fits" \
    pimin=2300 pimax=3300

done
