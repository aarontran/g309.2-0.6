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
if ($? != 0) then
    echo "Invalid obsid (could not sasinit)"
    exit 1
endif

make_xmmregions ${obsid}

echo ""

specbackgrp ${obsid} src
specbackgrp ${obsid} bkg
specbackgrp ${obsid} src_north_clump
specbackgrp ${obsid} src_SW_lobe
specbackgrp ${obsid} src_E_lobe
specbackgrp ${obsid} src_SE_dark
