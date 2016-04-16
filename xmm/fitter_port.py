#!/usr/local/bin/python
"""
Run fits programatically
Basically a massive configuration file
Exploiting the fact that xspec objects are global (AllData, AllModels, etc...)

Must be run in a sasinit-sourced environment
"""

from datetime import datetime

import xspec as xs

import xspec_fit_g309 as myxs
import xspec_utils
from nice_tables import LatexTable


xs.Xset.abund = "wilm"
xs.Fit.query = "yes"
xs.Plot.device = "/xw"
xs.Plot.xAxis = "keV"
xs.Plot.xLog = True
xs.Plot.yLog = True
xs.Plot.addCommand("rescale y 1e-5 3")  # twiddle depending on SNR model

# COMMENT -- regions should only have underscores in their names
regs = ["src_north_clump", "src_E_lobe", "src_SW_lobe", "src_SE_dark",
        "src_ridge", "src_SE_ridge_dark", "src_pre_ridge",
        "ann_000_100", "ann_100_200", "ann_200_300", "ann_300_400", "ann_400_500"]

nH_vals = [1.5, 2.0, 2.5, 3.0]

# Fits with nH free
# -----------------

"""
for reg in regs:

    myxs.load_data([reg], snr_model='vnei', fit_xrb=False)  # Sanity check
    myxs.prep_fit()

    xs.Fit.perform()

    snr = xs.AllModels(1, 'snr')
    snr.vnei.kT.frozen=False
    snr.vnei.Tau.frozen=False
    snr.TBabs.nH.frozen=False
    xs.Fit.perform()

    if REG not in ['src_SE_ridge_dark']:
        snr.vnei.Si.frozen=False
        snr.vnei.S.frozen=False
        xs.Fit.perform()

    print "Finished at:", datetime.now()
"""

started = datetime.now()
out = myxs.load_data("src", snr_model='vnei')
prep_fit(out['src'])

print "Started at:", started
print "Finished at:", datetime.now()

# result:
# XRBs all frozen, set to "default" parameters
# SP power laws all free, except MOS1/MOS2 tied for same regions+obsids
# INSTR lines all indep and frozen, except for constants (all indep)
# SNR model -- all frozen EXCEPT For 0087940201 MOS
#   which is used to control everything
#   also excepting backscal value (should be 5-10% correction at max)


# Currently (Thurs april 14) takes ~6 minutes to load
# Fit five annuli with nH tied together
#out = myxs.load_data(["ann_000_100", "ann_100_200", "ann_200_300", "ann_300_400", "ann_400_500"],
#               snr_model='vnei', fit_xrb=False)  # Sanity check

# TODO really weird bug -- try regenerating spectrum and see if it persists
# and/or explore the actual data..
#for extr in out['ann_000_100']:
#    # 10-11 keV range messed up
#    xs.AllData(extr.spec.index).ignore("10.0-**")
#    # SP PN contamination shows much softer power-law index than usual
#    # TODO disabled pending further tests and exploration
#    #if extr.instr == 'pn':
#    #    extr.spec.models['sp'].powerlaw.PhoIndex.frozen = False
#    ## Surprisingly, 0551000201 MOS SP power law is poorly constrained, extremely odd (HD 119682 contamination?)
#    #if extr.obsid == '0551000201' and extr.instr == 'mos1':
#    #    extr.spec.models['sp'].powerlaw.PhoIndex = 0.2
#    #    extr.spec.models['sp'].powerlaw.PhoIndex.frozen = True
#
## procedure to link nH across annuli
## Directly addressing with XSPEC datagroup #s
##center = xs.AllModels( 1, 'snr_ann_000_100')
##rings = [xs.AllModels( 6, 'snr_ann_100_200'),
##         xs.AllModels(11, 'snr_ann_200_300'),
##         xs.AllModels(16, 'snr_ann_300_400'),
##         xs.AllModels(21, 'snr_ann_400_500')]
#center = out['ann_000_100'][0].models['snr_ann_000_100']
#rings = [out['ann_100_200'][0].models['snr_ann_100_200'],
#         out['ann_200_300'][0].models['snr_ann_200_300'],
#         out['ann_300_400'][0].models['snr_ann_300_400'],
#         out['ann_400_500'][0].models['snr_ann_400_500']]
#for ring in rings:
#    ring.TBabs.nH.link = link_name(center, center.TBabs.nH)

#dump['ann_400_500'][0].models['snr_ann_400_500'].TBabs

# Here I needed:
#  model names
#  datagroup numbers for "1st" datagroups for this source



# Fits for a range of nH values
# -----------------------------

"""
for nH_val in nH_vals:

    for reg in regs:

        myxs.load_data([reg], snr_model='vnei', fit_xrb=False)  # Sanity check
        myxs.prep_fit()

        snr = xs.AllModels(1, 'snr')
        snr.TBabs.nH = nH_val
        snr.TBabs.nH.frozen=True

        xs.Fit.perform()

        snr.vnei.kT.frozen=False
        snr.vnei.Tau.frozen=False
        xs.Fit.perform()

        if REG not in ['src_SE_ridge_dark']:
            snr.vnei.Si.frozen=False
            snr.vnei.S.frozen=False
            xs.Fit.perform()

        print "Finished at:", datetime.now()
"""

# This obviously depends on the details of how the data are loaded
# But, fine-grained tweaking will require specific addressing anyways...
# that depends on the
# 1. ordering of regions you input,
# 2. number of obsids/exposures you're working with
#
# One solution is to build another layer of abstraction --
# convert from obsid / exposure / region ---> xspec model number
#
# Goal would be to reduce coupling between setup and fitting code
# but that may be unavoidable -- we have to interface with global
# XSPEC objects everywhere!

#dump_plots_data('results_spec/${reg}');"
#dump_plots_data('results_spec/${reg}_nH-${nH}');"

# ##################################################
# STUFF FOR FIT SETUP.... region specific hacks, etc
# ##################################################

def free_xrb(model):
    """This is obviously just a convenience method - strongly coupled to myxs.load_cxrb"""
    model.apec.kT = 0.1  # Unabsorped apec (local bubble)
    model.TBabs.nH = 1  # Galactic absorption
    model.apec_5.kT = 0.25  # Absorbed apec (galactic halo)
    model.apec.kT.frozen = False
    model.TBabs.nH.frozen = False
    model.apec_5.kT.frozen = False


def prep_fit(all_extrs):
    """Set up fit (range ignores, PN power law setup, renorm)
    These are specific ALWAYS-ON tweaks or fixes, typically determined after
    running some fits...
    """
    for extr in all_extrs:
        if extr.instr == "mos1" or extr.instr == "mos2":
            extr.spec.ignore("**-0.3, 11.0-**")
        if extr.instr == "pn":
            extr.spec.ignore("**-0.4, 11.0-**")
        # PN SP power law not well-constrained at all
        # TODO may not need to fix, now that extragalactic xrb is pinned
        #if extr.instr == 'pn':
        #    extr.spec.models['sp'].powerlaw.PhoIndex = 0.2
        #    extr.spec.models['sp'].powerlaw.PhoIndex.frozen = True
    xs.AllData.ignore("bad")
    xs.Fit.renorm()


def initial_fit(N_H=None):
    """This can be just tossed into main fitting setup"""

    if snr_model != 'vsedov':
        xs.Fit.perform()
        xs.Plot("ldata delch")

    if snr_model == 'vnei':
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

    if snr_model == 'vpshock':
        if N_H is None:
            snr.TBabs.nH.frozen=False
        snr.vpshock.kT.frozen=False
        snr.vpshock.Si.frozen=False
        snr.vpshock.S.frozen=False
        snr.vpshock.Tau_l.frozen=False
        snr.vpshock.Tau_u.frozen=False
        xs.Fit.perform()
        xs.Plot("ldata delch")

    if snr_model == 'vsedov':
        if N_H is None:
            snr.TBabs.nH.frozen=False
        snr.vsedov.kT_a.frozen=False  # Mean shock temperature
        snr.vsedov.kT_b.frozen=False  # e- temperature behind the shock
        snr.vsedov.Tau.frozen=False
        snr.vsedov.Si.frozen=False
        snr.vsedov.S.frozen=False
        xs.Fit.perform()

    # Vary XRB
    if WITH_BKG or snr_model == 'xrb':
        xrb.apec.kT.frozen = False
        xrb.TBabs.nH.frozen = False
        xrb.apec_5.kT.frozen = False
        xs.Fit.perform()
        # After this, likely need to run steppar on nH
        # and/or vary other XRB components to tweak fit

#################################################
# Stuff for printing and displaying output
#################################################


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

    if snr_model == 'xrb':
        print "No SNR model in use"
    else:
        print "snr model: {}".format(snr.expression)
        print "  nH (10^22)    {:.3f} +/- {:.3f}".format(*f(snr.TBabs.nH))
        plasma = None
        if snr_model == 'vnei':
            plasma = snr.vnei
            print "  kT   (keV)    {:.3f} +/- {:.3f}".format(*f(plasma.kT))
            print "  Tau (s/cm^3)  {:.2e} +/- {:.2e}".format(*f(plasma.Tau))
        if snr_model == 'vpshock':
            plasma = snr.vpshock
            print "  kT   (keV)    {:.3f} +/- {:.3f}".format(*f(plasma.kT))
            print "  Tau_u (keV)    {:.3f} +/- {:.3f}".format(*f(plasma.Tau_u))
            print "  Tau_l (keV)    {:.3f} +/- {:.3f}".format(*f(plasma.Tau_l))
        if snr_model == 'vsedov':
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
    for i in sorted(cfgspec.keys()):
        m = xs.AllModels(i, 'sp')
        pstr = "  Data group {}, n  {:.2f} +/- {:.2f}".format(i, *f(m.powerlaw.PhoIndex))
        pstr = pstr + ",  norm  {:.2e} +/- {:.2e}".format(*f(m.powerlaw.norm))
        print pstr
    print ""

    print "instrumental lines"
    for i in sorted(cfgspec.keys()):
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
    xs_utils.dump_fit_log(f_stem + ".log")

    # Dump nice LaTeX table -- full table, + just row(s)
    ltab = make_table()
    with open(f_stem + ".tex", 'w') as f_tex:
        f_tex.write(str(ltab))
    with open(f_stem + "_row.tex", 'w') as f_tex:
        f_tex.write('\n'.join(ltab.get_rows()))

    # Dump succinct summary of fit parameters
    print_fit(f_stem + ".txt")
