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
from nice_tables import LatexTable

parser = argparse.ArgumentParser(description="Execute interactive G309 region fits in XSPEC")
parser.add_argument('reg', default='src',
    help="Region to fit to SNR/plasma model")
parser.add_argument('--snr_model', default='vnei',
    help="Choose SNR model")
parser.add_argument('--no_fit', action='store_true',
    help="Don't start any fits; drop user straight into interactive mode")
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
    elif SNR_MODEL == 'vpshock':
        m = xs.Model("TBabs * vpshock", 'snr', n)
        m.TBabs.nH = 1
        m.vpshock.kT = 1
        #m.vpshock.tau_low = 1e10
        #m.vpshock.tau_high = 1e11
    elif SNR_MODEL == 'vsedov':
        m = xs.Model("TBabs * vsedov", 'snr', n)
        m.TBabs.nH = 1
        #m.vsedov.kT = 2
        #m.vsedov.kT_i = 1

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

        xrb.apec.norm = 2.90e-4
        xrb.powerlaw.norm = 3.10e-4
        xrb.apec_5.norm = 3.29e-3

        xrb.apec.norm.frozen = True
        xrb.powerlaw.norm.frozen = True
        xrb.apec_5.norm.frozen = True

    xrb.apec.kT.frozen = True
    xrb.TBabs.nH.frozen = True
    xrb.apec_5.kT.frozen = True


def execute_fit():
    """Fitting procedure to run after loading all models/spectra
    Basically, a giant configuration method
    """

    if REG == 'src' and SNR_MODEL == 'vnei':

        # Force background SP power law to index 0.2
        if WITH_BKG: # Note: hardcoded model number
            xs.AllModels(8, 'sp').powerlaw.PhoIndex = 0.2
            xs.AllModels(8, 'sp').powerlaw.PhoIndex.frozen = True

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

    ## Basic VNEI fits for first four subsample regions

    if REG == 'src_north_clump' and SNR_MODEL == 'vnei':

        # PN SP power law not well-constrained at all
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

        # Release PN SP power law (don't do this, just goes to wonky values)
        #xs.AllModels(3, 'sp').powerlaw.PhoIndex.frozen = False
        #xs.Fit.perform()

    if REG == 'src_SE_dark' and SNR_MODEL == 'vnei':

        # PN SP power law not well-constrained at all
        xs.AllModels(3, 'sp').powerlaw.PhoIndex = 0.2
        xs.AllModels(3, 'sp').powerlaw.PhoIndex.frozen = True
        xs.Fit.renorm()
        xs.Fit.perform()

        # Vary SNR
        snr.TBabs.nH.frozen=False
        snr.vnei.kT.frozen=False
        snr.vnei.Tau.frozen=False
        xs.Fit.perform()

        # Let Si float (solar abund S still gives acceptable fit)
        snr.vnei.Si.frozen=False
        xs.Fit.perform()

    if REG == 'src_E_lobe' and SNR_MODEL == 'vnei':

        # PN SP power law tends towards index 0
        xs.AllModels(3, 'sp').powerlaw.PhoIndex = 0.2
        xs.AllModels(3, 'sp').powerlaw.PhoIndex.frozen = True
        xs.Fit.renorm()
        xs.Fit.perform()

        xs.Plot("ldata delch")

        # Vary SNR
        snr.TBabs.nH.frozen=False
        snr.vnei.kT.frozen=False
        snr.vnei.Tau.frozen=False
        xs.Fit.perform()

    if REG == 'src_SW_lobe' and SNR_MODEL == 'vnei':

        # PN SP power law tends towards index 0
        xs.AllModels(3, 'sp').powerlaw.PhoIndex = 0.2
        xs.AllModels(3, 'sp').powerlaw.PhoIndex.frozen = True
        xs.Fit.renorm()
        xs.Fit.perform()

        xs.Plot("ldata delch")

        # Vary SNR
        snr.TBabs.nH.frozen=False
        snr.vnei.kT.frozen=False
        snr.vnei.Tau.frozen=False
        xs.Fit.perform()

    if REG == 'src_ridge' and SNR_MODEL == 'vnei':

        # PN SP power law tends towards index 0
        xs.AllModels(3, 'sp').powerlaw.PhoIndex = 0.2
        xs.AllModels(3, 'sp').powerlaw.PhoIndex.frozen = True
        xs.Fit.renorm()
        xs.Fit.perform()

        xs.Plot("ldata delch")

        # Vary SNR, incl. Si/S simultaneously
        snr.TBabs.nH.frozen=False
        snr.vnei.kT.frozen=False
        snr.vnei.Tau.frozen=False
        snr.vnei.Si.frozen=False
        snr.vnei.S.frozen=False
        xs.Fit.perform()

    if REG == 'src_SE_ridge_dark' and SNR_MODEL == 'vnei':

        # PN SP power law tends towards index 0
        xs.AllModels(3, 'sp').powerlaw.PhoIndex = 0.2
        xs.AllModels(3, 'sp').powerlaw.PhoIndex.frozen = True
        xs.Fit.renorm()
        xs.Fit.perform()

        xs.Plot("ldata delch")

        # Vary SNR, incl. Si/S simultaneously
        #snr.TBabs.nH.frozen=False
        #snr.vnei.kT.frozen=False
        #snr.vnei.Tau.frozen=False
        #snr.vnei.Si.frozen=False
        #snr.vnei.S.frozen=False
        #xs.Fit.perform()



def print_fit():
    """More succinct output of fit parameters"""

    def f(par):
        """just to save typing..."""
        return par.values[0], par.sigma

    print "reduced chi-squared = {:.2f}/{:d} = {:.3f}".format(xs.Fit.statistic,
                xs.Fit.dof, xs.Fit.statistic/xs.Fit.dof)

    print "snr model: {}".format(snr.expression)
    if SNR_MODEL == 'vnei':
        print "  nH (10^22)    {:.3f} +/- {:.3f}".format(*f(snr.TBabs.nH))
        print "  kT   (keV)    {:.3f} +/- {:.3f}".format(*f(snr.vnei.kT))
        print "  Si            {:.2f}  +/- {:.2f}".format(*f(snr.vnei.Si))
        print "  S             {:.2f}  +/- {:.2f}".format(*f(snr.vnei.S))
        print "  Tau (s/cm^3)  {:.2e} +/- {:.2e}".format(*f(snr.vnei.Tau))
        print "  norm          {:.2e} +/- {:.2e}".format(*f(snr.vnei.norm))
    print ""

    print "soft proton power laws"
    for i in sorted(spec.keys()):
        m = xs.AllModels(i, 'sp')
        pstr = "  Data group {}, n  {:.2f} +/- {:.2f}".format(i, *f(m.powerlaw.PhoIndex))
        pstr = pstr + ",  norm  {:.2e} +/- {:.2e}".format(*f(m.powerlaw.norm))
        print pstr
    print ""

    print "instrumental lines"
    for i in sorted(spec.keys()):
        m = xs.AllModels(i, 'instr')
        print "  Data group {}, instr const  {:.2f} +/- {:.2f}".format(i, *f(m.constant.factor))
    print ""


def print_fit_latex():
    """Print SNR fit parameters to nice LaTeX table"""

    # TODO have option to make row of units
    # underneath column names
    # figure out title style -- using caption vs. two rules may
    # make more sense. depends on context.
    # no need to get too specific, anyways
    latex_hdr = ['Region',
                 r'$n_\mathrm{H}$ ($10^{22} \unit{cm^{-2}}$)',
                 r'$kT$ (keV)',
                 r'$\tau$ ($\unit{s\;cm^{-3}}$)',
                 'Si (-)', 'S (-)',
                 r'$\chi^2_{\mathrm{red}} (\mathrm{dof}$)']

    """
    units = ['',
             r'($10^{22} \unit{cm^{-2}}$)',
             r'(keV)',
             r'($\unit{s\;cm^{-3}}$)',
             '(-)', '(-)',
             '']
     """

    latex_cols = ['{:s}', '{:0.2f}', '{:0.2f}', '{:0.2e}',
                  '{:0.2f}', '{:0.2f}', '{:s}'] # TODO temporary, need to add errors

    # TODO prec is currently only relevant for fmt types 1,2
    # should be relevant for type 0 too.
    ltab = LatexTable(latex_hdr, latex_cols, "G309.2-0.6 region fits", prec=1)

    ltr = [REG,  # For obvious reasons, hand-edit this in the actual output
           snr.TBabs.nH.values[0],
           snr.vnei.kT.values[0],
           snr.vnei.Tau.values[0],
           snr.vnei.Si.values[0],
           snr.vnei.S.values[0],
           "{:0.3f} ({:d})".format(xs.Fit.statistic/xs.Fit.dof, xs.Fit.dof)]
    ltab.add_row(*ltr)

    print(ltab)



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
xrb.powerlaw.PhoIndex.frozen = True

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

        # Found a mos1 spectrum.
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
                raise Exception("Got extra mos2 spectrum! Data group {}".format(j))
            # Found match, and sp_mos2 not already defined
            sp_mos2 = xs.AllModels(j, 'sp')

        if not sp_mos2:
            raise Exception("Got mos1 without mos2; Data group {}".format(j))

        # Form link, getting parameter index in convoluted way
        par_idx = sp_mos1.startParIndex - 1 + sp_mos1.powerlaw.PhoIndex.index
        sp_mos2.powerlaw.PhoIndex.link = "sp:{:d}".format(par_idx)


# Start fit process
# =================

if not NO_FIT:
    execute_fit()



