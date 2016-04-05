#!/bin/bash

# Three narrow bands, one broad band
bands="0.8-1.4 1.75-2.3 2.3-3.3 0.8-3.3"
#bands="0.8-3.3"
for band in $bands; do

  imsets=""
  imsets="$imsets 0087940201/odf/repro/mos1S001-im-sky-${band}kev-test.fits"
  imsets="$imsets 0087940201/odf/repro/mos2S002-im-sky-${band}kev-test.fits"
  imsets="$imsets   0087940201/odf/repro/pnS003-im-sky-${band}kev-test.fits"
  imsets="$imsets 0551000201/odf/repro/mos1S001-im-sky-${band}kev-test.fits"
  imsets="$imsets 0551000201/odf/repro/mos2S002-im-sky-${band}kev-test.fits"
  imsets="$imsets  0551000201/odf/repro/pnS003-im-sky-${band}kev-test.fits"

  expsets=""
  expsets="$expsets 0087940201/odf/repro/mos1S001-exp-sky-${band}kev-test.fits"
  expsets="$expsets 0087940201/odf/repro/mos2S002-exp-sky-${band}kev-test.fits"
  expsets="$expsets   0087940201/odf/repro/pnS003-exp-sky-${band}kev-test.fits"
  expsets="$expsets 0551000201/odf/repro/mos1S001-exp-sky-${band}kev-test.fits"
  expsets="$expsets 0551000201/odf/repro/mos2S002-exp-sky-${band}kev-test.fits"
  expsets="$expsets   0551000201/odf/repro/pnS003-exp-sky-${band}kev-test.fits"

  emosaic imagesets="${imsets}" exposuresets="${expsets}" withexposure=Y \
    mosaicedset="merged-im-sky-${band}kev-test.fits"
done

