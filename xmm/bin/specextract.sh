#!/bin/bash

# Convert DS9 to XMM regions, extract spectra, fit FWC closed spectra
# run after sourcing sasinit for correct obsid

# WARNING: hardcoded exposure names for obsids 0087940201 and 0551000201,
# Assumes the presence of files mos1S001-ori.fits, mos2S002-ori.fits,
# pnS003-ori.fits from successful {mos,pn}-filter runs.

if [[ "$SAS_OBSID" == "0087940201" ]]; then
  exposures="mos1S001 mos2S002 pnS003"
elif [[ "$SAS_OBSID" == "0551000201" ]]; then
  exposures="mos1S001 mos2S002"
fi

#f_regions=$(ls -1 ${XMM_PATH}/regs/*.reg)
f_regions="/data/gas2/atran/g309/xmm/regs/bar.reg
/data/gas2/atran/g309/xmm/regs/lobe.reg
/data/gas2/atran/g309/xmm/regs/ridge.reg
"

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

  cd $SAS_REPRO

  for exp in $exposures; do
    echo "Running: ff_fit.py ${exp}-${reg}-ff.pi --exp=$exp"
    ff_fit.py "${exp}-${reg}-ff.pi" --exp=$exp
  done
  # Need to fit FWC data for mosmerge-* spectra as well
  echo "Running: ff_fit.py mosmerge-${reg}-ff.pi --exp=mosmerge"
  ff_fit.py "mosmerge-${reg}-ff.pi" --exp="mosmerge"

  echo ""
done

echo "Done!"
echo $start_script
echo "Finished specextract: $(date)"
