#!/bin/bash

elow=$1  # ESAS formatting.  800, 1400 are OK, but 0800, 1.4e3 are NOT OK.
ehigh=$2
mask=$3

if [[ "$#" -ne 3 ]]; then
  echo "ERROR: three arguments (elow, ehigh, mask) required"
  exit 1
elif [[ $mask != "1" && $mask != "0" ]]; then
  echo "ERROR: mask argument (third arg) must be '1' or '0'"
  exit 1
fi

if [[ "$SAS_OBSID" == "0087940201" ]]; then
  exps=("mos1S001" "mos2S002" "pnS003")
elif [[ "$SAS_OBSID" == "0551000201" ]]; then
  exps=("mos1S001" "mos2S002")
else
  echo "ERROR: unsupported obsid $SAS_OBSID (pipeline not set up)"
  exit 1
fi

echo "Preparing $SAS_OBSID images for mosaicking"
echo "  with elow=$elow, ehigh=$ehigh, mask=$mask"

cd $SAS_REPRO

for ((j=0;j<${#exps[@]};++j)); do

  exp="${exps[$j]}"

  # ~~~~~~~~~~~~~~~~~~~~
  # WARNING: FILE LIST EDITS MUST BE PROPAGATED TO
  #   specbackprot_image
  # 1. I don't think "im-det" files are needed, but symlink to be sure
  # 2. ${exp}-back-im-det/sky-* files omitted because I want to use unmasked
  #    images (mask-0) in all cases; this is assured by specbackprot_image.
  # ~~~~~~~~~~~~~~~~~~~~
  BASENAMES="${exp}-obj-im-det-${elow}-${ehigh}
             ${exp}-obj-im-${elow}-${ehigh}
             ${exp}-exp-im-${elow}-${ehigh}
             ${exp}-mask-im-${elow}-${ehigh}
            "
  if [[ $exp =~ "pn" ]]; then
    BASENAMES="${BASENAMES}
               ${exp}-obj-im-det-${elow}-${ehigh}-oot
               ${exp}-obj-im-${elow}-${ehigh}-oot
               ${exp}-exp-im-det-${elow}-${ehigh}
               ${exp}-mask-im-det-${elow}-${ehigh}
              "
  fi

  for base in $BASENAMES; do
    #echo "mv ${base}.fits ${base}_mask-${mask}.fits"
    #mv "${base}.fits" "${base}_mask-${mask}.fits"
    ln -s -v -f "${base}_mask-${mask}.fits" "${base}.fits"
  done

done
