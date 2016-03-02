#!/usr/bin/env python
"""
PyXSPEC port of combined SNR and background fit...

Run in top-level namespace to enable subsequent interactive work
(e.g. in ipython shell)
"""

#import argparse
#import json
#import matplotlib.pyplot as plt
#import numpy as np
import os

import xspec as xs

#parser = argparse.ArgumentParser(description="Make nice separated plots")
#parser.add_argument('--stem', default='snr', help="prefix stem for 5 dat files")
#parser.add_argument('--reg', default='snr', help="region (bkg or snr) to set plotting behavior")
#args = parser.parse_args()
#stem, reg = args.stem, args.reg
#stem = args.stem

# "Global" settings
xs.Xset.abund = "wilm"
xs.Fit.query = "yes"

xmmpath = os.environ['XMM_PATH']

# Define spectra to use (set keywords for iterating, file names, etc)
spec = {
        1: {'obsid': "0087940201", 'exp': "mos1S001", 'reg': "src"},
        2: {'obsid': "0087940201", 'exp': "mos2S002", 'reg': "src"},
        3: {'obsid': "0087940201", 'exp': "pnS003", 'reg': "src"},
        4: {'obsid': "0551000201", 'exp': "mos1S001", 'reg': "src"},
        5: {'obsid': "0551000201", 'exp': "mos2S002", 'reg': "src"},
        6: {'obsid': "0087940201", 'exp': "mos1S001", 'reg': "bkg"},
        7: {'obsid': "0087940201", 'exp': "mos2S002", 'reg': "bkg"},
        8: {'obsid': "0087940201", 'exp': "pnS003", 'reg': "bkg"},
        9: {'obsid': "0551000201", 'exp': "mos1S001", 'reg': "bkg"},
       10: {'obsid': "0551000201", 'exp': "mos2S002", 'reg': "bkg"}
    }

for i in spec.keys():
    spec[i]['instr'] = spec[i]['exp'].split('S')[0]  # mos1, mos2, pn


# Load spectra and supporting files (background,RMF,ARF) for each model
# ---------------------------------------------------------------------
# 0: x-ray background
# 1: instrumental lines
# 2: SNR plama model
# 3: soft proton background

for i in sorted(spec.keys()):
    obsid = spec[i]['obsid']
    exp = spec[i]['exp']
    reg = spec[i]['reg']
    instr = spec[i]['instr']

    repro_dir = xmmpath + "/{obs}/odf/repro".format(obs=obsid)

    # Load spectrum
    f_spec = repro_dir + "/{exp}-{reg}-grp50.pi".format(exp=exp, reg=reg)
    if exp[:2] == "pn":
        # Use OOT substracted spectrum for PN
        f_spec = repro_dir + "/{exp}-{reg}-os-grp50.pi".format(exp=exp, reg=reg)
    if os.getcwd() != repro_dir:
        # must chdir to resolve rmf/arf/background files listed in FITS header
        # (if files not found, XSPEC prompt blocks script execution)
        os.chdir(repro_dir)
    xs.AllData("{n}:{n} {path}".format(n=i, path=f_spec))

    asdf = xs.AllData(i)  # TODO temporary, pending better naming scheme.

    # Load QPB background
    f_qpb = repro_dir + "/{exp}-{reg}-qpb.pi".format(exp=exp, reg=reg)
    asdf.background = f_qpb

    # Load RMF/ARF files for each source model
    asdf.multiresponse[0]     = repro_dir + "/{exp}-{reg}.rmf".format(exp=exp, reg=reg)
    asdf.multiresponse[0].arf = repro_dir + "/{exp}-{reg}.arf".format(exp=exp, reg=reg)
    asdf.multiresponse[1]     = repro_dir + "/{exp}-{reg}.rmf".format(exp=exp, reg=reg)
    asdf.multiresponse[1].arf = repro_dir + "/{exp}-{reg}-ff.arf".format(exp=exp, reg=reg)

    if reg == "src":
        asdf.multiresponse[2]     = repro_dir + "/{exp}-{reg}.rmf".format(exp=exp, reg=reg)
        asdf.multiresponse[2].arf = repro_dir + "/{exp}-{reg}.arf".format(exp=exp, reg=reg)

    asdf.multiresponse[3]     = xmmpath + "/caldb/{}-diag.rsp".format(instr)
    asdf.multiresponse[3].arf = "none"
    # Note: pn-diag.rsp raises RMF TELESCOPE/INSTRUMENT keyword errors
    # this is OK; keywords are set to none in file header for whatever reason

    if instr == "mos1" or instr == "mos2":
        asdf.ignore("**-0.3, 11.0-**")
    elif instr == "pn":
        asdf.ignore("**-0.4, 11.0-**")


# Dump any outputs in xmmpath, not in random repro_dir
os.chdir(xmmpath)


# Model parameter set-up
# ======================

# Note: model variables are those of data group 1 only
# i.e., xrb only refers to model for XRB 1.
# But, XSPEC automatically creates copies of each model as declared...

# Sky X-ray background
# --------------------
xrb = xs.Model("constant * (apec + TBabs*(powerlaw + apec))", "xrb", 1)

xrb.constant.factor = 1
xrb.apec.kT = 0.1
xrb.TBabs.nH = 1
xrb.powerlaw.PhoIndex = 1.4
xrb.apec_5.kT = 0.25

xrb.constant.factor.frozen = True
xrb.apec.kT.frozen = True
xrb.TBabs.nH.frozen = True
xrb.powerlaw.PhoIndex.frozen = True
xrb.apec_5.kT.frozen = True

# TODO read in XRB backscal ratios

kkk

# XMM EPIC instrumental lines
# ---------------------------
instr = xs.Model("con*(gauss + gauss + gauss + gauss + gauss + gauss)", "instr", 2)

# Set and freeze line energies,widths
lines = [1.49, 1.75, 7.49, 8.05, 8.62, 8.90]
# cnames are: gaussian, gaussian_3, gaussian_4, ..., gaussian_7
for cname, en in zip(instr.componentNames[1:], lines):
    comp = eval('instr.'+cname)
    comp.LineE = en
    comp.Sigma = 0
    comp.LineE.frozen = True
    comp.Sigma.frozen = True

    # TODO how to iterate over different spectra,
    # and read in different line values?



#spec = [m1jph_bkg, m2jph_bkg, pnjph_bkg, m1cm_bkg, m2cm_bkg]
#
#for s in [m1jph_bkg, m2jph_bkg, m1cm_bkg, m2cm_bkg]:
#    s.ignore("**-0.3, 11.0-**")
#
#pnjph_bkg.ignore("**-0.4, 11.0-**")


# "Global" settings -- only apply when plotting
xs.Plot.device = "/xw"
xs.Plot.xAxis = "keV"
