#!/usr/bin/env python
"""
PyXSPEC port of combined SNR and background fit...

Run in top-level namespace to enable subsequent interactive work
(e.g. in ipython shell)
"""

from __future__ import division

import argparse
from datetime import datetime
#import json
#import matplotlib.pyplot as plt
#import numpy as np
import os
import sys
from subprocess import call

from astropy.io import fits
import xspec as xs

from xspec_utils import load_fit_dict, dump_fit_log
from nice_tables import LatexTable

parser = argparse.ArgumentParser(description="Execute interactive G309 region fits in XSPEC")
parser.add_argument('reg', default='src',
    help="Region to fit to SNR/plasma model")
parser.add_argument('--snr_model', default='vnei',
    help="Choose SNR model")
parser.add_argument('--n_H', type=float, default=None,
    help="Fix SNR absorption nH in fits (units 10e22), else free to vary")
parser.add_argument('--no_fit', action='store_true',
    help="Don't start any fits; drop user straight into interactive mode")
parser.add_argument('--with_bkg', action='store_true',
    help=("Load bkg spectra for simultaneous fitting instead of using"
          " canned values from integrated SNR/bkg fit"))

args = parser.parse_args()
REG = args.reg
SNR_MODEL = args.snr_model
N_H = args.n_H
WITH_BKG = args.with_bkg
NO_FIT = args.no_fit

if SNR_MODEL not in ['vnei', 'vpshock', 'vsedov', 'xrb']:
    raise Exception("Invalid SNR model")

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
        m.vpshock.Tau_l = 1e9
        m.vpshock.Tau_u = 1e11
    elif SNR_MODEL == 'vsedov':
        m = xs.Model("TBabs * vsedov", 'snr', n)
        m.TBabs.nH = 1
        #m.vsedov.kT = 2
        #m.vsedov.kT_i = 1
    elif SNR_MODEL == 'xrb':
        m = None

    return m


def init_xrb_values(xrb):
    """Set starting XRB values"""
    if WITH_BKG or SNR_MODEL == 'xrb':
        # Generic starting values
        xrb.apec.kT = 0.1  # Unabsorped apec (local bubble)
        xrb.TBabs.nH = 1  # Galactic absorption
        xrb.apec_5.kT = 0.25  # Absorbed apec (galactic halo)
    else:
        # Best fit values from src/bkg combined fit, nH = 1.06
        # WARNING: this is out-of-date, after realization that powerlaw norm
        # is approx 2-3x larger than expected.
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

def prep_fit():
    """Set up fit (range ignores, PN power law setup, renorm)"""
    # PN SP power law not well-constrained at all
    xs.AllModels(3, 'sp').powerlaw.PhoIndex = 0.2
    xs.AllModels(3, 'sp').powerlaw.PhoIndex.frozen = True
    if WITH_BKG:
        xs.AllModels(8, 'sp').powerlaw.PhoIndex = 0.2
        xs.AllModels(8, 'sp').powerlaw.PhoIndex.frozen = True

    # TODO really weird bug -- try regenerating spectrum and see if it persists
    # and/or explore the actual data..
    if REG == 'ann_000_100':
        # Data are messed up in 10-11 keV range for just this spectrum?!
        xs.AllData(4).ignore("10.0-**")
        # SP PN contamination shows much softer power-law index
        xs.AllModels(3, 'sp').powerlaw.PhoIndex.frozen = False
        # Surprisingly, 0551000201 MOS SP power law is poorly constrained
        # (blows to negative).  This is extremely odd to me.  Something weird
        # is going on... (contamination from HD 119682?
        xs.AllModels(4, 'sp').powerlaw.PhoIndex = 0.2
        xs.AllModels(4, 'sp').powerlaw.PhoIndex.frozen = True

    if N_H:
        snr.TBabs.nH = N_H

    xs.Fit.renorm()



def execute_fit():
    """Fitting procedure to run after loading all models/spectra
    Basically, a giant configuration method
    """
    if SNR_MODEL != 'vsedov':
        xs.Fit.perform()
        xs.Plot("ldata delch")

    if SNR_MODEL == 'vnei':
        if N_H is None:
            snr.TBabs.nH.frozen=False
        snr.vnei.kT.frozen=False
        snr.vnei.Tau.frozen=False
        xs.Fit.perform()
        xs.Plot("ldata delch")

        if REG not in ['src_SE_ridge_dark']:
            snr.vnei.Si.frozen=False
            snr.vnei.S.frozen=False
            xs.Fit.perform()
            xs.Plot("ldata delch")

    if SNR_MODEL == 'vpshock':
        if N_H is None:
            snr.TBabs.nH.frozen=False
        snr.vpshock.kT.frozen=False
        snr.vpshock.Si.frozen=False
        snr.vpshock.S.frozen=False
        snr.vpshock.Tau_l.frozen=False
        snr.vpshock.Tau_u.frozen=False
        xs.Fit.perform()
        xs.Plot("ldata delch")

    if SNR_MODEL == 'vsedov':
        if N_H is None:
            snr.TBabs.nH.frozen=False
        snr.vsedov.kT_a.frozen=False  # Mean shock temperature
        snr.vsedov.kT_b.frozen=False  # e- temperature behind the shock
        snr.vsedov.Tau.frozen=False
        snr.vsedov.Si.frozen=False
        snr.vsedov.S.frozen=False
        xs.Fit.perform()

    # Vary XRB
    if WITH_BKG or SNR_MODEL == 'xrb':
        xrb.apec.kT.frozen = False
        xrb.TBabs.nH.frozen = False
        xrb.apec_5.kT.frozen = False
        xs.Fit.perform()
        # After this, likely need to run steppar on nH
        # and/or vary other XRB components to tweak fit


def print_fit(f_out=None):
    """More succinct output of fit parameters"""

    def f(par):
        """just to save typing..."""
        return par.values[0], par.sigma

    if f_out:
        fh = open(f_out, 'w')
        old_stdout = sys.stdout
        sys.stdout = fh

    print "reduced chi-squared = {:.2f}/{:d} = {:.3f}".format(xs.Fit.statistic,
                xs.Fit.dof, xs.Fit.statistic/xs.Fit.dof)

    if SNR_MODEL == 'xrb':
        print "No SNR model in use"
    else:
        print "snr model: {}".format(snr.expression)
        print "  nH (10^22)    {:.3f} +/- {:.3f}".format(*f(snr.TBabs.nH))
        plasma = None
        if SNR_MODEL == 'vnei':
            plasma = snr.vnei
            print "  kT   (keV)    {:.3f} +/- {:.3f}".format(*f(plasma.kT))
            print "  Tau (s/cm^3)  {:.2e} +/- {:.2e}".format(*f(plasma.Tau))
        if SNR_MODEL == 'vpshock':
            plasma = snr.vpshock
            print "  kT   (keV)    {:.3f} +/- {:.3f}".format(*f(plasma.kT))
            print "  Tau_u (keV)    {:.3f} +/- {:.3f}".format(*f(plasma.Tau_u))
            print "  Tau_l (keV)    {:.3f} +/- {:.3f}".format(*f(plasma.Tau_l))
        if SNR_MODEL == 'vsedov':
            plasma = snr.vsedov
            print "  kT_a (keV)    {:.3f} +/- {:.3f}".format(*f(plasma.kT_a))
            print "  kT_b (keV)    {:.3f} +/- {:.3f}".format(*f(plasma.kT_b))
            print "  Tau (s/cm^3)  {:.2e} +/- {:.2e}".format(*f(plasma.Tau))

        v_elements = ['H', 'He', 'C', 'N', 'O', 'Ne', 'Mg',
                    'Si', 'S', 'Ar', 'Ca', 'Fe', 'Ni']  # for XSPEC v* models
        for elem in v_elements:
            comp = eval("plasma."+elem)
            if comp.frozen:
                continue
            fmtstr = "  {:2s}            {:.2f}  +/- {:.2f}"
            print fmtstr.format(comp.name, *f(comp))

        print "  norm          {:.2e} +/- {:.2e}".format(*f(plasma.norm))
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

    if f_out:
        fh.close()  # Bad practice
        sys.stdout = old_stdout


def make_table():
    """Print SNR fit parameters to nice LaTeX table"""
    latex_hdr = ['Region',
                 r'$n_\mathrm{H}$ ($10^{22} \unit{cm^{-2}}$)',
                 r'$kT$ (keV)',
                 r'$\tau$ ($\unit{s\;cm^{-3}}$)',
                 'Si (-)', 'S (-)',
                 r'$\chi^2_{\mathrm{red}} (\mathrm{dof}$)']

    # TODO make row of units under column names
    # figure out title styling in nice_tables.py
    units = ['', r'($10^{22} \unit{cm^{-2}}$)',
             r'(keV)', r'($\unit{s\;cm^{-3}}$)',
             '(-)', '(-)', '']

    latex_cols = ['{:s}', '{:0.2f}', '{:0.2f}', '{:0.2e}',
                  '{:0.2f}', '{:0.2f}', '{:s}'] # TODO temporary, need to add errors

    # TODO prec is currently only relevant for fmt types 1,2
    # should be relevant for type 0 too.
    ltab = LatexTable(latex_hdr, latex_cols, "G309.2-0.6 region fits", prec=1)

    if SNR_MODEL == 'vnei':

        ltr = [REG,  # For obvious reasons, hand-edit this in the actual output
               snr.TBabs.nH.values[0],
               snr.vnei.kT.values[0],
               snr.vnei.Tau.values[0],
               snr.vnei.Si.values[0],
               snr.vnei.S.values[0],
               "{:0.3f} ({:d})".format(xs.Fit.statistic/xs.Fit.dof, xs.Fit.dof)]
        ltab.add_row(*ltr)

    return ltab


def dump_plots_data(f_stem):
    """Dump "standardized" fit reporting output.  User will get:
    * XSPEC pdf of plot
    * data points (data, model) dumped to QDP file
    * XSPEC fit log, the usual "show" output
    * more succinct fit log w/ most pertinent fit parameters
      (good for quick perusal)
    * LaTeX-formatted table row
    Assumes acceptable global XSPEC settings"""

    f_plot = f_stem

    # Dump XSPEC plot
    xs.Plot.device = f_plot + "/cps"
    xs.Plot("ldata delchi")
    call(["ps2pdf", f_plot, f_plot + ".pdf"])
    call(["rm", f_plot])

    # Dump data points
    xs.Plot.addCommand("wdata {}".format(f_stem + ".qdp"))
    xs.Plot.device = "/xw"
    xs.Plot("ldata")
    xs.Plot.delCommand(len(xs.Plot.commands))

    # Dump XSPEC fit log
    dump_fit_log(f_stem + ".log")

    # Dump nice LaTeX table -- full table, + just row(s)
    ltab = make_table()
    with open(f_stem + ".tex", 'w') as f_tex:
        f_tex.write(str(ltab))
    with open(f_stem + "_row.tex", 'w') as f_tex:
        f_tex.write('\n'.join(ltab.get_rows()))

    # Dump succinct summary of fit parameters
    print_fit(f_stem + ".txt")





# Miscellaneous setup (user configuration not needed)
# ---------------------------------------------------

# "Global" settings
xs.Xset.abund = "wilm"
xs.Fit.query = "yes"

xs.Plot.device = "/xw"
xs.Plot.xAxis = "keV"
xs.Plot.xLog = True
xs.Plot.yLog = True
xs.Plot.addCommand("rescale y 1e-5 3")  # TODO twiddle depending on SNR model

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
xrb.powerlaw.norm = 1.2e-4  # 0087940201 MOS1 norm,
# WARNING: DEPENDENT on current pt src exclusions, setup of norm.
# assumes BACKSCAL = 191927484.
# uses hickox/markevitch 2006 normalization of
# 10.9 photons cm^-2 s^-1 sr^-1 keV^-1

init_xrb_values(xrb)

xrb.constant.factor.frozen = True
xrb.powerlaw.PhoIndex.frozen = True
xrb.powerlaw.norm.frozen = True

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

prep_fit()

if not NO_FIT:
    execute_fit()

ltab = make_table()

print "Finished at:", datetime.now()


