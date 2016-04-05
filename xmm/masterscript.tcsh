#!/bin/tcsh

# This master script must be in (t)csh to run "source sasinit ..."
# which in turn must be in (t)csh to source CfA-HEA's csh environment scripts
# heainit->"headas-init.csh" and "/soft/XMM/xmmsas/setsas.csh"

# subsequent script invocations that assume a sasinit-sourced environment
# will work as expected

set obsid = $1
if ($obsid == "") then
  echo "Error: obsid required!"
  exit 1
endif

source sasinit $obsid
echo ""

if ($? != 0) then
  echo "Invalid obsid (could not sasinit)"
  exit 1
endif

cd $XMM_PATH
source sasrepro $obsid

make_xmmregions ${obsid}

set regions = "src_pre_ridge"
foreach reg ($regions)

  specbackgrp ${obsid} ${reg}
  echo ""

  echo "Fitting FWC spectrum lines for $reg mos1S001..."
  ff_fit.py --obsid=${obsid} --reg=${reg} --exp=mos1S001
  echo "Fitting FWC spectrum lines for $reg mos2S002..."
  ff_fit.py --obsid=${obsid} --reg=${reg} --exp=mos2S002
  echo "Fitting FWC spectrum lines for $reg pnS003..."
  ff_fit.py --obsid=${obsid} --reg=${reg} --exp=pnS003

  echo ""

end
