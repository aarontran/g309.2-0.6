"""
Background fit...
"""

#import json
#import matplotlib.pyplot as plt
#import numpy as np
import os

import xspec as xs

# "Global" settings
xs.Plot.device = "/xw"
xs.Plot.xAxis = "keV"
xs.Xset.abund = "wilm"

# Setup
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

m1jph = xs.AllData(1)
m2jph = xs.AllData(2)
pnjph = xs.AllData(3)
m1cm  = xs.AllData(4)
m2cm  = xs.AllData(5)

os.chdir(xmmpath)

m1jph.background = "0087940201/odf/repro/mos1S001-bkg-qpb.pi"
m2jph.background = "0087940201/odf/repro/mos2S002-bkg-qpb.pi"
pnjph.background = "0087940201/odf/repro/pnS003-bkg-qpb.pi"
m1cm.background = "0551000201/odf/repro/mos1S001-bkg-qpb.pi"
m2cm.background = "0551000201/odf/repro/mos2S002-bkg-qpb.pi"

# 0: x-ray background
# 1: instrumental lines
# 2: MOS1 soft proton background
# 3: MOS2 soft proton background
# 4: PN soft proton background
# 5: MOS1(motch) soft proton background
# 6: MOS2(motch) soft proton background

m1jph.multiresponse[0]     = "0087940201/odf/repro/mos1S001-bkg.rmf"
m1jph.multiresponse[0].arf = "0087940201/odf/repro/mos1S001-bkg.arf"
m1jph.multiresponse[1]     = "0087940201/odf/repro/mos1S001-bkg.rmf"
m1jph.multiresponse[1].arf = "0087940201/odf/repro/mos1S001-bkg-ff.arf"
m1jph.multiresponse[2]     = "caldb/mos1-diag.rsp"
m1jph.multiresponse[2].arf = "none"
print "loaded m1jph"

m2jph.multiresponse[0]     = "0087940201/odf/repro/mos2S002-bkg.rmf"
m2jph.multiresponse[0].arf = "0087940201/odf/repro/mos2S002-bkg.arf"
m2jph.multiresponse[1]     = "0087940201/odf/repro/mos2S002-bkg.rmf"
m2jph.multiresponse[1].arf = "0087940201/odf/repro/mos2S002-bkg-ff.arf"
m2jph.multiresponse[3]     = "caldb/mos2-diag.rsp"
m2jph.multiresponse[3].arf = "none"
print "loaded m2jph"

pnjph.multiresponse[0]     = "0087940201/odf/repro/pnS003-bkg.rmf"
pnjph.multiresponse[0].arf = "0087940201/odf/repro/pnS003-bkg.arf"
pnjph.multiresponse[1]     = "0087940201/odf/repro/pnS003-bkg.rmf"
pnjph.multiresponse[1].arf = "0087940201/odf/repro/pnS003-bkg-ff.arf"
pnjph.multiresponse[4]     = "caldb/pn-diag.rsp"
    # Note: pn-diag.rsp raises RMF TELESCOPE/INSTRUMENT keyword errors
    # this is OK; keywords are set to none in file header for whatever reason
pnjph.multiresponse[4].arf = "none"
print "loaded pnjph"

m1cm.multiresponse[0]     = "0551000201/odf/repro/mos1S001-bkg.rmf"
m1cm.multiresponse[0].arf = "0551000201/odf/repro/mos1S001-bkg.arf"
m1cm.multiresponse[1]     = "0551000201/odf/repro/mos1S001-bkg.rmf"
m1cm.multiresponse[1].arf = "0551000201/odf/repro/mos1S001-bkg-ff.arf"
m1cm.multiresponse[5]     = "caldb/mos1-diag.rsp"
m1cm.multiresponse[5].arf = "none"
print "loaded m1cm"

m2cm.multiresponse[0]     = "0551000201/odf/repro/mos2S002-bkg.rmf"
m2cm.multiresponse[0].arf = "0551000201/odf/repro/mos2S002-bkg.arf"
m2cm.multiresponse[1]     = "0551000201/odf/repro/mos2S002-bkg.rmf"
m2cm.multiresponse[1].arf = "0551000201/odf/repro/mos2S002-bkg-ff.arf"
m2cm.multiresponse[6]     = "caldb/mos2-diag.rsp"
m2cm.multiresponse[6].arf = "none"
print "loaded m2cm"

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



#spec = [m1jph, m2jph, pnjph, m1cm, m2cm]
#
#for s in [m1jph, m2jph, m1cm, m2cm]:
#    s.ignore("**-0.3, 11.0-**")
#
#pnjph.ignore("**-0.4, 11.0-**")
