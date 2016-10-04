#!/usr/local/bin/python

# For portability, use /usr/bin/env python for shebang
# /usr/bin/env python points to a really old version on my computer
# and I'm too lazy to fix right now

"""
Fit instrumental lines in XMM EPIC FWC data for an individual exposure and
region, handling either PN or MOS.

Dumps output in same directory as spectrum file
"""

import argparse
import json
import os
from subprocess import call

import xspec as xs

from xspec_utils import dump_fit_log, fit_dict, dump_dict

# Config, file IO setup
# ---------------------

parser = argparse.ArgumentParser(description="Fit FWC instrumental lines for region")
parser.add_argument('pha', default='mos1S001-src-ff.pi',
                    help="PHA file (spectrum) to be fit")
parser.add_argument('--exp', default='mos1S001',
                    help="Exposure ID (mos1S001, pnS003, or similar)")
parser.add_argument('--free-en', action='store_true',
                    help="Allow line energies to float within 0.05 keV")
args = parser.parse_args()

pha = args.pha
exp = args.exp

pha_dir, pha_fname = os.path.split(pha)
root = (os.path.splitext(pha_fname))[0]
instr_id = exp.split('S')[0]  # one of: mos1, mos2, pn; mosmerge (special case)

# "Global" settings
xs.Xset.chatter = 0
xs.Xset.abund = "wilm"  # irrelevant
xs.Fit.query = "yes"
xs.Fit.statMethod = "cstat"

# outputs
f_plot = root + "-fit"
f_log = root + "-fit.log"
f_fit = root + "-fit.json"

# Set up FWC models
# -----------------

if pha_dir:
    # for xspec to resolve rmf/arf/bkg files (else script execution blocks)
    os.chdir(pha_dir)
spec = xs.Spectrum(pha)

# Use a flat response for broken power law background
if instr_id in ["mosmerge"]:
    spec.multiresponse[1] = os.environ['XMM_PATH'] + "/caldb/mos1-diag.rsp"
else:
    spec.multiresponse[1] = (os.environ['XMM_PATH']
                            + "/caldb/{}-diag.rsp".format(instr_id))
spec.multiresponse[1].arf = "none"  # Not needed, just to be explicit

if instr_id in ["mos1", "mos2", "mosmerge"]:  # MOS
    spec.ignore("**-0.5, 5.0-**")
    instr = xs.Model("gauss + gauss", "instr", 1)
    lines = [1.49, 1.75]
elif instr_id == "pn":  # PN
    spec.ignore("**-1.0,12.0-**")
    instr = xs.Model("gauss + gauss + gauss + gauss + gauss + gauss + gauss", "instr", 1)
    lines = [1.49, 4.54, 5.44, 7.49, 8.05, 8.62, 8.90]
else:
    raise Exception("Invalid exposure ID")

conti = xs.Model("bknpower", "conti", 2)
conti.bknpower.PhoIndx1 = 1.5
conti.bknpower.BreakE = 2
conti.bknpower.PhoIndx2 = 0.2

# Set and freeze instrumental line energies,widths
for cname, en in zip(instr.componentNames, lines):
    # cnames are gaussian, gaussian_2, ..., gaussian_6
    comp = instr.__getattribute__(cname)
    comp.LineE = en
    comp.Sigma = 0
    comp.LineE.frozen = True
    comp.Sigma.frozen = True

# Fit and dump fit information/plot
# ---------------------------------

xs.Fit.renorm()
xs.Fit.perform()

if args.free_en:
    for cname, en in zip(instr.componentNames, lines):
        comp = instr.__getattribute__(cname)
        comp.LineE.frozen = False
        comp.Sigma.frozen = False
    xs.Fit.perform()


xs.Plot.xAxis = "keV"
xs.Plot.xLog = True
xs.Plot.yLog = True
xs.Plot.addCommand("co 2 on 2")
xs.Plot.addCommand("rescale y 1e-4 1")

xs.Plot.device = f_plot + "/cps"
xs.Plot("ldata resid delchi")
call(["ps2pdf", f_plot, f_plot + ".pdf"])
call(["rm", f_plot])

# Save current XSPEC state
dump_dict(fit_dict(), f_fit)
dump_fit_log(f_log)

