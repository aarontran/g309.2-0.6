"""
Attempt to script FWC fits for multiple exposures and regions...
"""

#import argparse
import os

import xspec as xs

#parser = argparse.ArgumentParser(description="Make nice separated plots")
#parser.add_argument('--stem', default='snr', help="prefix stem for 5 dat files")
#parser.add_argument('--reg', default='snr', help="region (bkg or snr) to set plotting behavior")
#args = parser.parse_args()
#stem, reg = args.stem, args.reg
#stem = args.stem

obsid = "0087940201"
exp = "pnS003"
reg = "src_SE_dark"

instr_id = exp.split('S')[0]  # one of: mos1, mos2, pn

# "Global" settings
xs.Xset.abund = "wilm"

# Set up spectrum
# ---------------

xmmpath = os.environ['XMM_PATH']
specdir = "{xmmpath}/{obsid}/odf/repro".format(xmmpath=xmmpath, obsid=obsid)
fspec = "{exp}-{reg}-ff-key.pi".format(exp=exp, reg=reg)

# Must chdir so XSPEC can resolve rmf/arf/background files (otherwise, XSPEC
# prompt will block script execution...)
os.chdir(specdir)
spec = xs.Spectrum(fspec)

spec.multiresponse[1] = xmmpath + "/caldb/{instr}-diag.rsp".format(instr=instr_id)
spec.multiresponse[1].arf = "none"  # Not needed, just to be explicit


# Set up FWC models
# -----------------

if instr_id == "mos1" or instr_id == "mos2":  # MOS

    spec.ignore("**-0.5, 5.0-**")

    instr = xs.Model("gauss + gauss", "instr", 1)
    lines = [1.49, 1.75]

    conti = xs.Model("bknpower", "conti", 2)
    conti.bknpower.PhoIndx1 = 1.5
    conti.bknpower.BreakE = 1
    conti.bknpower.PhoIndx2 = 0.2

else:  # PN

    spec.ignore("**-1.0,12.0-**")

    instr = xs.Model("gauss + gauss + gauss + gauss + gauss", "instr", 1)
    lines = [1.49, 7.49, 8.05, 8.62, 8.90]

    conti = xs.Model("bknpower", "conti", 2)
    conti.bknpower.PhoIndx1 = 1.5
    conti.bknpower.BreakE = 5
    conti.bknpower.PhoIndx2 = 0.2

# Set and freeze instrumental line energies,widths
for cname, en in zip(instr.componentNames, lines):
    # cnames are gaussian, gaussian_2, ..., gaussian_6
    comp = eval('instr.'+cname)
    comp.LineE = en
    comp.Sigma = 0
    comp.LineE.frozen = True
    comp.Sigma.frozen = True

# Fit data and output fitted norms
# --------------------------------

# set query yes
# call fit
xs.Fit.renorm()
xs.Fit.perform()

# Plot to verify quality of fit

xs.Plot.device = "/xw"
xs.Plot.xAxis = "keV"
xs.Plot.xLog = True
xs.Plot.yLog = True

xs.Plot("ldata resid delchi")

# iplot to show stuff.
# xs.Plot.iPlot("ldata resid delchi")
# PLT> co ?
# PLT> co 2 on 2
# PLT> rescale y 1e-3 1
# PLT> pl
# PLT> exit

# spit out resulting line normalizations
# TBD, data interchange pending
# instr.gaussian.norm.values[0]
