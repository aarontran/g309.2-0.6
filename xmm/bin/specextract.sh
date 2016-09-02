#!/bin/bash

# Convert DS9 to XMM regions, extract spectra, fit FWC closed spectra
# run after sourcing sasinit for correct obsid
#
# In practice, comment in/out what you need (region creation, specbackgrp,
# ff_fit)...

# WARNING: hardcoded exposure names for obsids 0087940201 and 0551000201,
# Assumes the presence of files mos1S001-ori.fits, mos2S002-ori.fits,
# pnS003-ori.fits from successful {mos,pn}-filter runs.
exposures="mos1S001 mos2S002 pnS003"
f_regions=$(ls -1 ${XMM_PATH}/regs/*.reg)

start_script="Started specextract: $(date)"
echo $start_script

for f_reg in $f_regions; do

  # Region name: src, ann_000_100, ...
  reg="$(basename $f_reg | cut -d "." -f 1)"

  for exp in $exposures; do
    evli="${SAS_REPRO}/${exp}-ori.fits"
    det_reg="${XMM_PATH}/regs/${SAS_OBSID}/reg_${exp}_${reg}.txt"
    echo "Running: reg2xmmdets.pl $f_reg $evli > $det_reg"
    reg2xmmdets.pl $f_reg $evli > $det_reg
  done

  specbackgrp $reg
  sbg_status=$?
  if [[ $sbg_status != 0 ]]; then
    echo "NON-FATAL ERROR: specbackgrp failed with status $sbg_status"
  fi
  echo ""

#  # Must do this to resolve python dependencies
#  cd $XMM_PATH
#
#  for exp in $exps; do
#    echo "Fitting FWC spectrum lines for $reg $exp"
#    ff_fit.py --obsid=$SAS_OBSID --reg=$reg --exp=$exp
#  done
done

echo "Done!"
echo $start_script
echo "Finished specextract: $(date)"
