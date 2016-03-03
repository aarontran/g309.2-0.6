#!/usr/local/bin/python

# For portability, use /usr/bin/env python for shebang
# /usr/bin/env python points to a really old version on my computer
# and I'm too lazy to fix right now

"""
Fit instrumental lines in XMM EPIC FWC data for an individual exposure and
region, handling either PN or MOS
"""

import argparse
import json
import os
from subprocess import call

import xspec as xs

from xspec_utils import dump_fit_log, dump_fit_dict

# Set up paths, XSPEC params
# --------------------------

parser = argparse.ArgumentParser(description="Fit FWC instrumental lines for region")
parser.add_argument('--obsid', default='0087940201', help="XMM obsid")
parser.add_argument('--exp', default='mos1S001', help="Exposure ID (mos1S001, pnS003, or similar)")
parser.add_argument('--reg', default='src', help="Region identifier")
args = parser.parse_args()

obsid = args.obsid
exp = args.exp
reg = args.reg

instr_id = exp.split('S')[0]  # one of: mos1, mos2, pn

# "Global" settings
xs.Xset.chatter = 0
xs.Xset.abund = "wilm"
xs.Fit.query = "yes"

# inputs
xmm_path = os.environ['XMM_PATH']
spec_dir = xmm_path + "/{obsid}/odf/repro".format(obsid=obsid)
f_spec = "{exp}-{reg}-ff-key.pi".format(exp=exp, reg=reg)

# outputs
f_plot = "{exp}-{reg}-ff-key-fit".format(exp=exp, reg=reg)
f_log = "{exp}-{reg}-ff-key-fit.log".format(exp=exp, reg=reg)
f_fit = "{exp}-{reg}-ff-key-fit.json".format(exp=exp, reg=reg)


# Set up FWC models
# -----------------

os.chdir(spec_dir)  # chdir for xspec to resolve rmf/arf/bkg files
spec = xs.Spectrum(f_spec)
spec.multiresponse[1] = xmm_path + "/caldb/{instr}-diag.rsp".format(instr=instr_id)
spec.multiresponse[1].arf = "none"  # Not needed, just to be explicit

if instr_id == "mos1" or instr_id == "mos2":  # MOS
    spec.ignore("**-0.5, 5.0-**")
    instr = xs.Model("gauss + gauss", "instr", 1)
    lines = [1.49, 1.75]
else:  # PN
    spec.ignore("**-1.0,12.0-**")
    instr = xs.Model("gauss + gauss + gauss + gauss + gauss", "instr", 1)
    lines = [1.49, 7.49, 8.05, 8.62, 8.90]

conti = xs.Model("bknpower", "conti", 2)
conti.bknpower.PhoIndx1 = 1.5
conti.bknpower.BreakE = 2
conti.bknpower.PhoIndx2 = 0.2

# Set and freeze instrumental line energies,widths
for cname, en in zip(instr.componentNames, lines):
    # cnames are gaussian, gaussian_2, ..., gaussian_6
    comp = eval('instr.'+cname)
    comp.LineE = en
    comp.Sigma = 0
    comp.LineE.frozen = True
    comp.Sigma.frozen = True

# Fit and dump fit information/plot
# ---------------------------------

xs.Fit.renorm()
xs.Fit.perform()

xs.Plot.xAxis = "keV"
xs.Plot.xLog = True
xs.Plot.yLog = True
xs.Plot.addCommand("co 2 on 2")
xs.Plot.addCommand("rescale y 1e-3 1")
xs.Plot.device = f_plot + "/cps"
xs.Plot("ldata resid delchi")

call(["ps2pdf", f_plot, f_plot + ".pdf"])
call(["rm", f_plot])

dump_fit_dict(f_fit, instr)
dump_fit_log(f_log)



