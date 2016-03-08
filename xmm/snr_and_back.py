#!/usr/bin/env python
"""
PyXSPEC port of combined SNR and background fit...

Run in top-level namespace to enable subsequent interactive work
(e.g. in ipython shell)
"""

from __future__ import division

import argparse
#import json
#import matplotlib.pyplot as plt
#import numpy as np
import os

from astropy.io import fits
import xspec as xs

from xspec_utils import load_fit_dict

parser = argparse.ArgumentParser(description="Execute interactive G309 region fits in XSPEC")
parser.add_argument('reg', default='src',
    help="Region to fit to SNR/plasma model")
parser.add_argument('--snr_model', default='vnei',
    help="Choose SNR model")
parser.add_argument('--no_fit', action='store_true',
    help="Don't run fit steps; drop user straight into interactive mode")
parser.add_argument('--with_bkg', action='store_true',
    help=("Load bkg spectra for simultaneous fitting instead of using"
          " canned values from integrated SNR/bkg fit"))

args = parser.parse_args()
REG = args.reg
SNR_MODEL = args.snr_model
WITH_BKG = args.with_bkg
NO_FIT = args.no_fit

# Configure fit process (spectra, models)
# ---------------------------------------

# In order to put all configuration code together, I had to
# make a lot of assumptions on what goes on in the main body of code.
# This sort of script doesn't refactor well, generally.

spec = {
        1: {'obsid': "0087940201", 'exp': "mos1S001", 'reg': REG},
        2: {'obsid': "0087940201", 'exp': "mos2S002", 'reg': REG},
        3: {'obsid': "0087940201", 'exp': "pnS003",   'reg': REG},
        4: {'obsid': "0551000201", 'exp': "mos1S001", 'reg': REG},
        5: {'obsid': "0551000201", 'exp': "mos2S002", 'reg': REG}
    }

if (WITH_BKG):
    spec[ 6] = {'obsid': "0087940201", 'exp': "mos1S001", 'reg': "bkg"}
    spec[ 7] = {'obsid': "0087940201", 'exp': "mos2S002", 'reg': "bkg"}
    spec[ 8] = {'obsid': "0087940201", 'exp': "pnS003",   'reg': "bkg"}
    spec[ 9] = {'obsid': "0551000201", 'exp': "mos1S001", 'reg': "bkg"}
    spec[10] = {'obsid': "0551000201", 'exp': "mos2S002", 'reg': "bkg"}


def init_snr_model(n):
    """Initialize SNR model
    Input: n, model/source number for XSPEC
    Output: XSPEC model object"""

    if SNR_MODEL == 'vnei':

        m = xs.Model("TBabs * vnei", 'snr', n)

        m.TBabs.nH = 1
        m.vnei.kT = 1
        m.vnei.Tau = 1e11

        m.TBabs.nH.frozen = True
        m.vnei.kT.frozen = True
        m.vnei.Tau.frozen = True

    return m

def init_xrb_values(xrb):
    """Set starting XRB values"""
    if WITH_BKG:
        # Generic starting values
        xrb.apec.kT = 0.1  # Unabsorped apec (local bubble)
        xrb.TBabs.nH = 1  # Galactic absorption
        xrb.apec_5.kT = 0.25  # Absorbed apec (galactic halo)
    else:
        # Best fit values from src/bkg combined fit, nH = 1.06
        xrb.apec.kT = 0.228
        xrb.TBabs.nH = 1.06
        xrb.apec_5.kT = 0.368


def execute_fit():
    """Fitting procedure to run after loading all models/spectra
    Basically, a giant configuration method
    """

    if REG == 'src' and SNR_MODEL == 'vnei':

        xs.Fit.renorm()
        xs.Fit.perform()

        # Vary SNR
        snr.TBabs.nH.frozen=False
        snr.vnei.kT.frozen=False
        snr.vnei.Tau.frozen=False
        snr.vnei.S.frozen=False
        snr.vnei.Si.frozen=False
        xs.Fit.perform()

        # Vary XRB
        if WITH_BKG:
            xrb.apec.kT.frozen = False
            xrb.TBabs.nH.frozen = False
            #xrb.powerlaw.PhoIndex.frozen = True
            xrb.apec_5.kT.frozen = False
            xs.Fit.perform()

            # Run steppar on nH -- for which we do expect a "reasonable" value
            # Find local chi-squared minima at nH ~ 0.91, 1.06
            # xs.Fit.steppar("xrb:6 0.1 1.0")
            # xs.Fit.steppar("xrb:6 1.1 3.1")
            # xs.Fit.steppar("xrb:6 0.8 1.3")
            # xs.Fit.steppar("xrb:6 1.0 1.2")

            # Result (skip ahead)
            xrb.TBabs.nH = 1.06
            xs.Fit.perform()

    if REG == 'src_north_clump' and SNR_MODEL == 'vnei':

        # PN SP power law not well-constrained at first
        xs.AllModels(3, 'sp').powerlaw.PhoIndex = 0.2
        xs.AllModels(3, 'sp').powerlaw.PhoIndex.frozen = True
        xs.Fit.renorm()
        xs.Fit.perform()

        # Vary SNR
        snr.TBabs.nH.frozen=False
        snr.vnei.kT.frozen=False
        snr.vnei.Tau.frozen=False
        snr.vnei.S.frozen=False
        snr.vnei.Si.frozen=False
        xs.Fit.perform()  # This fit takes a little while to converge

        # Release PN SP power law
        xs.AllModels(3, 'sp').powerlaw.PhoIndex.frozen = False
        xs.Fit.perform()





# Miscellaneous setup (user configuration not needed)
# ---------------------------------------------------

# "Global" settings
xs.Xset.abund = "wilm"
xs.Fit.query = "yes"

xs.Plot.device = "/xw"
xs.Plot.xAxis = "keV"
xs.Plot.xLog = True
xs.Plot.yLog = True
xs.Plot.addCommand("rescale y 1e-5 3")

xmmpath = os.environ['XMM_PATH']

for i in spec.keys():
    spec[i]['instr'] = spec[i]['exp'].split('S')[0]  # mos1, mos2, pn


# Load spectra and supporting files (background,RMF,ARF) for each model
# ---------------------------------------------------------------------
# 0: x-ray background
# 1: instrumental lines
# 2: SNR plasma model
# 3: soft proton background
# (maps to 1,2,3,4 in PyXSPEC methods)

# Fiducial backscal value for area ratio constants
f = fits.open('0087940201/odf/repro/mos1S001-src-grp50.pi', memmap=True)
fiducial_backscal = f[1].header['backscal']
f.close()

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

    # RMF/ARF for SNR value, not applicable to bkg region
    if reg != "bkg":
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

    # Save some information to our data structure
    spec[i]['f_spec'] = f_spec
    spec[i]['repro_dir'] = repro_dir

    f = fits.open(f_spec, memmap=True)
    spec[i]['backscal_ratio'] = f[1].header['backscal'] / fiducial_backscal
    f.close()


# Dump any outputs in xmmpath, not in random repro_dir
os.chdir(xmmpath)


# Model parameter set-up
# ======================

# Sky X-ray background
# --------------------
xrb = xs.Model("constant * (apec + TBabs*(powerlaw + apec))", "xrb", 1)
# xrb points only to model for datagroup 1, but XSPEC automatically clones
# model for each datagroup w/ corresponding source response/arf

xrb.constant.factor = 1
xrb.powerlaw.PhoIndex = 1.4  # Extragalactic background (unresolved AGN)

init_xrb_values(xrb)

xrb.constant.factor.frozen = True
xrb.apec.kT.frozen = True
xrb.TBabs.nH.frozen = True
xrb.powerlaw.PhoIndex.frozen = True
xrb.apec_5.kT.frozen = True

# Scale BACKSCAL values to fiducial value (0087940201 MOS1S001 src BACKSCAL)
# to get XRB normalizations right across regions AND exposures
for i in sorted(spec.keys()):
    xrb_curr = xs.AllModels(i, 'xrb')
    xrb_curr.constant.factor = spec[i]['backscal_ratio']
    xrb_curr.constant.factor.frozen = True

# Note: this effect could also affect source fits (snr model).
# But, due to spatial structure of SNR + smaller variation between src regions
# between exposures (vs. sky expected to be ~constant everywhere), we neglect
# this discrepancy.  Effect would mostly affect 0087940201 PNS003 (large column
# exclusions) and 0551000201 MOS1S001 (missing CCD #6).  0551000201 MOS2S002
# has excluded CCD #5 due to anomalous state behavior, but exclusion only
# affects the background region; src region is unscathed.


# XMM EPIC instrumental lines
# ---------------------------
instr = xs.Model("con*(gauss + gauss + gauss + gauss + gauss + gauss + gauss)", "instr", 2)

# Expecting at most 7 lines to be modeled in FWC spectrum
# Currently set by PN lines: Al, Ti, Cr, Ni, Cu, Zn, Cu(K-beta)

# Fix instr line energies/widths/norms, but allow overall norm to vary
# (i.e., all line ratios fixed to FWC line ratios)
for i in sorted(spec.keys()):

    instr_curr = xs.AllModels(i, 'instr')

    instr_curr.constant.factor = 1
    instr_curr.constant.factor.frozen = False

    fwc_fit = load_fit_dict("{rdir}/{exp}-{reg}-ff-key-fit.json".format(
                                rdir=spec[i]['repro_dir'],
                                exp=spec[i]['exp'],
                                reg=spec[i]['reg']))

    # Assign gaussians until we run out of FWC gaussians
    # then zero out the rest
    fwc_idx = 0
    def comp2lineE(comp):
        return comp['LineE']['value']
    fwc_comps = sorted(fwc_fit['comps'].values(), key=comp2lineE)

    for cname in instr_curr.componentNames[1:]:

        comp = eval('instr_curr.'+cname)

        if fwc_idx < len(fwc_comps):
            fwc_comp = fwc_comps[fwc_idx]
            comp.LineE = fwc_comp['LineE']['value']
            comp.Sigma = fwc_comp['Sigma']['value']
            comp.norm = fwc_comp['norm']['value']
            fwc_idx += 1
        else:
            comp.LineE = 0
            comp.Sigma = 0
            comp.norm = 0

        comp.LineE.frozen = True
        comp.Sigma.frozen = True
        comp.norm.frozen = True

    # if we have more FWC gaussians than model gaussians the model here needs
    # to be updated, or there's a bug in the FWC fit process
    if fwc_idx != len(fwc_comps):
        raise Exception("Got unexpected FWC lines for data group {}".format(i))



# SUPERNOVA REMNANT
# -----------------
snr = init_snr_model(n=3)


# Soft proton contamination
# -------------------------
sp = xs.Model("powerlaw * constant", "sp", 4)

for i in sorted(spec.keys()):
    sp_curr = xs.AllModels(i, 'sp')

    # Hold power law index for initial renorm
    sp_curr.powerlaw.PhoIndex = 0.4
    sp_curr.powerlaw.PhoIndex.frozen = False
    # Let norms vary independently
    sp_curr.powerlaw.norm = 1e-2
    sp_curr.powerlaw.norm.frozen = False
    # Apply backscal ratio scalings to make comparing norms easier
    sp_curr.constant.factor = spec[i]['backscal_ratio']
    sp_curr.constant.factor.frozen = True

# Tie MOS1/MOS2 indices together
# Brute-force approach to hacking this up...

for i in sorted(spec.keys()):

    if spec[i]['instr'] == 'mos1':

        sp_mos1 = xs.AllModels(i, 'sp')
        sp_mos2 = None

        # Find matching MOS2 observation
        for j in sorted(spec.keys()):
            if spec[j]['instr'] != 'mos2':
                continue
            if spec[j]['obsid'] != spec[i]['obsid']:
                continue
            if spec[j]['reg'] != spec[i]['reg']:
                continue
            if sp_mos2:
                raise Exception("Extra mos2 spectrum! Data group {}".format(j))
            # Found match, and sp_mos2 not already defined
            sp_mos2 = xs.AllModels(j, 'sp')

        # Continue gracefully if no match found
        if not sp_mos2:
            continue

        # Form link, getting parameter index in convoluted way
        par_idx = sp_mos1.startParIndex - 1 + sp_mos1.powerlaw.PhoIndex.index
        sp_mos2.powerlaw.PhoIndex.link = "sp:{:d}".format(par_idx)

# Force background SP power law to index 0.2
if WITH_BKG: # Note: hardcoded model number
    xs.AllModels(8, 'sp').powerlaw.PhoIndex = 0.2
    xs.AllModels(8, 'sp').powerlaw.PhoIndex.frozen = True


# Start fit process
# =================

if not NO_FIT:
    execute_fit()

