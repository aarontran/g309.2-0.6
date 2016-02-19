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

xs.Xset.abund = "wilm"

# Set up spectra
# --------------

xmmpath = os.environ['XMM_PATH'] + "/"

# Must chdir so XSPEC can resolve rmf/arf/background files
# (if cannot resolve, XSPEC prompt will block script execution...)
os.chdir(xmmpath + "0087940201/odf/repro")
xs.AllData("1:1 " + xmmpath + "0087940201/odf/repro/mos1S001-bkg-grp50.pi")
xs.AllData("2:2 " + xmmpath + "0087940201/odf/repro/mos2S002-bkg-grp50.pi")
xs.AllData("3:3 " + xmmpath + "0087940201/odf/repro/pnS003-bkg-os-grp50.pi")
os.chdir(xmmpath + "0551000201/odf/repro")
xs.AllData("4:4 " + xmmpath + "0551000201/odf/repro/mos1S001-bkg-grp50.pi")
xs.AllData("5:5 " + xmmpath + "0551000201/odf/repro/mos2S002-bkg-grp50.pi")

reg = "src"  # TODO temporary

os.chdir(xmmpath + "0087940201/odf/repro")
xs.AllData("6:6 " + xmmpath + "0087940201/odf/repro/mos1S001-{}-grp50.pi".format(reg))
xs.AllData("7:7 " + xmmpath + "0087940201/odf/repro/mos2S002-{}-grp50.pi".format(reg))
xs.AllData("8:8 " + xmmpath + "0087940201/odf/repro/pnS003-{}-os-grp50.pi".format(reg))
os.chdir(xmmpath + "0551000201/odf/repro")
xs.AllData("9:9 " + xmmpath + "0551000201/odf/repro/mos1S001-{}-grp50.pi".format(Reg))
xs.AllData("10:10 " + xmmpath + "0551000201/odf/repro/mos2S002-{}-grp50.pi".format(reg))

os.chdir(xmmpath)  # Reset back to "main" directory to set rmfs/arfs/etc

m1jph_bkg = xs.AllData(6)
m2jph_bkg = xs.AllData(7)
pnjph_bkg = xs.AllData(8)
m1cm_bkg  = xs.AllData(9)
m2cm_bkg  = xs.AllData(10)

m1jph_bkg.background = "0087940201/odf/repro/mos1S001-bkg-qpb.pi"
m2jph_bkg.background = "0087940201/odf/repro/mos2S002-bkg-qpb.pi"
pnjph_bkg.background = "0087940201/odf/repro/pnS003-bkg-qpb.pi"
m1cm_bkg.background = "0551000201/odf/repro/mos1S001-bkg-qpb.pi"
m2cm_bkg.background = "0551000201/odf/repro/mos2S002-bkg-qpb.pi"

# 0: x-ray background
# 1: instrumental lines
# 2: SNR plama model
# 3: soft proton background

m1jph_bkg.multiresponse[0]     = "0087940201/odf/repro/mos1S001-bkg.rmf"
m1jph_bkg.multiresponse[0].arf = "0087940201/odf/repro/mos1S001-bkg.arf"
m1jph_bkg.multiresponse[1]     = "0087940201/odf/repro/mos1S001-bkg.rmf"
m1jph_bkg.multiresponse[1].arf = "0087940201/odf/repro/mos1S001-bkg-ff.arf"
m1jph_bkg.multiresponse[3]     = "caldb/mos1-diag.rsp"
m1jph_bkg.multiresponse[3].arf = "none"
print "loaded m1jph_bkg"

m2jph_bkg.multiresponse[0]     = "0087940201/odf/repro/mos2S002-bkg.rmf"
m2jph_bkg.multiresponse[0].arf = "0087940201/odf/repro/mos2S002-bkg.arf"
m2jph_bkg.multiresponse[1]     = "0087940201/odf/repro/mos2S002-bkg.rmf"
m2jph_bkg.multiresponse[1].arf = "0087940201/odf/repro/mos2S002-bkg-ff.arf"
m2jph_bkg.multiresponse[3]     = "caldb/mos2-diag.rsp"
m2jph_bkg.multiresponse[3].arf = "none"
print "loaded m2jph_bkg"

pnjph_bkg.multiresponse[0]     = "0087940201/odf/repro/pnS003-bkg.rmf"
pnjph_bkg.multiresponse[0].arf = "0087940201/odf/repro/pnS003-bkg.arf"
pnjph_bkg.multiresponse[1]     = "0087940201/odf/repro/pnS003-bkg.rmf"
pnjph_bkg.multiresponse[1].arf = "0087940201/odf/repro/pnS003-bkg-ff.arf"
pnjph_bkg.multiresponse[3]     = "caldb/pn-diag.rsp"
pnjph_bkg.multiresponse[3].arf = "none"
print "loaded pnjph_bkg"
# Note: pn-diag.rsp raises RMF TELESCOPE/INSTRUMENT keyword errors
# this is OK; keywords are set to none in file header for whatever reason

m1cm_bkg.multiresponse[0]     = "0551000201/odf/repro/mos1S001-bkg.rmf"
m1cm_bkg.multiresponse[0].arf = "0551000201/odf/repro/mos1S001-bkg.arf"
m1cm_bkg.multiresponse[1]     = "0551000201/odf/repro/mos1S001-bkg.rmf"
m1cm_bkg.multiresponse[1].arf = "0551000201/odf/repro/mos1S001-bkg-ff.arf"
m1cm_bkg.multiresponse[5]     = "caldb/mos1-diag.rsp"
m1cm_bkg.multiresponse[5].arf = "none"
print "loaded m1cm_bkg"

m2cm_bkg.multiresponse[0]     = "0551000201/odf/repro/mos2S002-bkg.rmf"
m2cm_bkg.multiresponse[0].arf = "0551000201/odf/repro/mos2S002-bkg.arf"
m2cm_bkg.multiresponse[1]     = "0551000201/odf/repro/mos2S002-bkg.rmf"
m2cm_bkg.multiresponse[1].arf = "0551000201/odf/repro/mos2S002-bkg-ff.arf"
m2cm_bkg.multiresponse[3]     = "caldb/mos2-diag.rsp"
m2cm_bkg.multiresponse[3].arf = "none"
print "loaded m2cm_bkg"

# Note: model variables are those of data group 1 only
# But, XSPEC automatically creates copies of each model as declared

# Sky X-ray background
# --------------------
xrb = xs.Model("apec + TBabs * (powerlaw + apec)", "xrb", 1)

xrb.apec.kT = 0.1
xrb.TBabs.nH = 1
xrb.powerlaw.PhoIndex = 1.4
xrb.apec_4.kT = 0.25

xrb.apec.kT.frozen = True
xrb.TBabs.nH.frozen = True
xrb.powerlaw.PhoIndex.frozen = True
xrb.apec_4.kT.frozen = True

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



#spec = [m1jph_bkg, m2jph_bkg, pnjph_bkg, m1cm_bkg, m2cm_bkg]
#
#for s in [m1jph_bkg, m2jph_bkg, m1cm_bkg, m2cm_bkg]:
#    s.ignore("**-0.3, 11.0-**")
#
#pnjph_bkg.ignore("**-0.4, 11.0-**")


# "Global" settings -- only apply when plotting
xs.Plot.device = "/xw"
xs.Plot.xAxis = "keV"
