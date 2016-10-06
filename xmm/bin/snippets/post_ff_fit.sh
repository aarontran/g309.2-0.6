#!/bin/bash

# Copy files to web directory for quick inspection

obsids="0087940201 0551000201"
for obsid in $obsids; do

  echo $obsid

  cd ${XMM_PATH}/${obsid}/repro/
  ff_files=$(ls -1 *-ff-fit*)
  for f in $ff_files; do
    echo "cp ${f} /data/wdocs/atran/g309/${obsid}_$f"
    cp ${f} /data/wdocs/atran/g309/${obsid}_$f
  done
done

echo "/data/wdocs/atran/g309/regen_index.pl"
/data/wdocs/atran/g309/regen_index.pl
