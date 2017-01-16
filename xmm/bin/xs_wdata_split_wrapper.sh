#!/bin/bash

NAMES="
20161222_ridge_se
20161222_ridge_nw
20161222_lobe_sw
20161222_lobe_ne
20161222_core
20161222_ridge_se_solar
20161222_ridge_nw_solar
20170109_lobe_sw_solar
20170109_lobe_ne_solar
20170109_core_solar
"

for name in $NAMES; do
  echo "xs_wdata_split.pl -i \"${name}.qdp\" -o \"${name}_spec\" -v"
  xs_wdata_split.pl -i "${name}.qdp" -o "${name}_spec" -v
done
