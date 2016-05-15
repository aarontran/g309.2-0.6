#!/usr/local/bin/python
"""
Run fits programatically
Basically a massive configuration file
Exploiting the fact that xspec objects are global (AllData, AllModels, etc...)

Must be run in a sasinit-sourced environment
"""

from __future__ import division

from datetime import datetime
from subprocess import call
import os
import sys

import xspec as xs

import xspec_fit_g309 as myxs
import xspec_utils as xs_utils
from nice_tables import LatexTable


############################################
# Stuff for printing and displaying output #
############################################

def print_fit(snr, f_out=None):
    """More succinct output of fit parameters
    TODO not really in use, mostly used
    to throw fit parameters into notes

    Input: snr = XSPEC model object for a source of form
            1. TBabs * vnei
            2. TBabs * vpshock
            3. TBabs * vsedov
    Input (optional): f_out
        file to print output to.  If None, print to stdout
    Output: n/a.  As advertised, this prints stuff.
    """

    def f(par):
        """just to save typing..."""
        return par.values[0], par.sigma

    if f_out:
        fh = open(f_out, 'w')
        old_stdout = sys.stdout
        sys.stdout = fh

    print "reduced chi-squared = {:.2f}/{:d} = {:.3f}".format(xs.Fit.statistic,
                xs.Fit.dof, xs.Fit.statistic/xs.Fit.dof)

    print "snr model: {}".format(snr.expression)
    print "  nH (10^22)    {:.3f} +/- {:.3f}".format(*f(snr.TBabs.nH))
    if 'vnei' in snr.componentNames:
        plasma = snr.vnei
        print "  kT   (keV)    {:.3f} +/- {:.3f}".format(*f(plasma.kT))
        print "  Tau (s/cm^3)  {:.2e} +/- {:.2e}".format(*f(plasma.Tau))
    elif 'vpshock' in snr.componentNames:
        plasma = snr.vpshock
        print "  kT    (keV)   {:.3f} +/- {:.3f}".format(*f(plasma.kT))
        print "  Tau_u (keV)   {:.2e} +/- {:.2e}".format(*f(plasma.Tau_u))
        print "  Tau_l (keV)   {:.2e} +/- {:.2e}".format(*f(plasma.Tau_l))
    elif 'vsedov' in snr.componentNames:
        plasma = snr.vsedov
        print "  kT_a (keV)    {:.3f} +/- {:.3f}".format(*f(plasma.kT_a))
        print "  kT_b (keV)    {:.3f} +/- {:.3f}".format(*f(plasma.kT_b))
        print "  Tau (s/cm^3)  {:.2e} +/- {:.2e}".format(*f(plasma.Tau))

    v_elements = ['H', 'He', 'C', 'N', 'O', 'Ne', 'Mg',
                  'Si', 'S', 'Ar', 'Ca', 'Fe', 'Ni']
    for elem in v_elements:
        comp = eval("plasma."+elem)
        if comp.frozen:
            continue
        fmtstr = "  {:2s}            {:.2f}  +/- {:.2f}"
        print fmtstr.format(comp.name, *f(comp))

    print "  norm          {:.2e} +/- {:.2e}".format(*f(plasma.norm))
    print ""

    # Cumbersome way to get these models but oh well

    print "soft proton power laws"
    for i in range(xs.AllData.nSpectra):
        m = xs.AllModels(i+1, 'sp')
        pstr = "  Data group {}, n  {:.2f} +/- {:.2f}".format(i+1, *f(m.powerlaw.PhoIndex))
        pstr = pstr + ",  norm  {:.2e} +/- {:.2e}".format(*f(m.powerlaw.norm))
        print pstr
    print ""

    print "instrumental lines"
    for i in range(xs.AllData.nSpectra):
        m = xs.AllModels(i+1, "instr_{:d}".format(i+1))
        print "  Data group {}, instr const  {:.2f} +/- {:.2f}".format(i+1, *f(m.constant.factor))
    print ""

    if f_out:
        fh.close()
        sys.stdout = old_stdout


def make_table(snr, region_name):
    """Print SNR fit parameters to nice LaTeX table"""

    if 'vnei' not in snr.componentNames:
        raise Exception('why are you printing this out')

    latex_hdr = ['Region',
                 r'$n_\mathrm{H}$ ($10^{22} \unit{cm^{-2}}$)',
                 r'$kT$ (keV)',
                 r'$\tau$ ($10^{10} \unit{s\;cm^{-3}}$)',
                 'Si (-)', 'S (-)',
                 r'$\chi^2_{\mathrm{red}} (\mathrm{dof}$)']

    # TODO make row of units under column names
    # figure out title styling in nice_tables.py
    units = ['', r'($10^{22} \unit{cm^{-2}}$)',
             r'(keV)', r'($\unit{s\;cm^{-3}}$)',
             '(-)', '(-)', '']

    latex_cols = ['{:s}', '{:0.2f}', '{:0.2f}', '{:0.2e}',
                  '{:0.2f}', '{:0.2f}', '{:s}'] # TODO temporary, need errors

    # TODO prec is currently only relevant for fmt types 1,2
    # should be relevant for type 0 too.
    ltab = LatexTable(latex_hdr, latex_cols, "G309.2-0.6 region fits", prec=1)

    ltr = [region_name,  # For obvious reasons, hand-edit this in the actual output
           snr.TBabs.nH.values[0],
           snr.vnei.kT.values[0],
           snr.vnei.Tau.values[0] / 1e10,
           snr.vnei.Si.values[0],
           snr.vnei.S.values[0],
           "{:0.3f} ({:d})".format(xs.Fit.statistic/xs.Fit.dof, xs.Fit.dof)]
    ltab.add_row(*ltr)

    return ltab



def dump_plots_data(f_stem, snr, region_name):
    """Dump "standardized" fit reporting output.  User will get:
    * XSPEC pdf of plot
    * data points (data, model) dumped to QDP file
    * XSPEC fit log, the usual "show" output
    * more succinct fit log w/ most pertinent fit parameters
      (good for quick perusal)
    * LaTeX-formatted table row
    Assumes acceptable global XSPEC settings"""

    # TODO the args odn't make sense

    f_plot = f_stem

    # Dump XSPEC plot
    xs.Plot.device = f_plot + "/cps"
    xs.Plot("ldata delchi")
    call(["ps2pdf", f_plot, f_plot + ".pdf"])
    call(["rm", f_plot])

    # Dump data points -- this can be done far more elegantly with PyXSPEC
    # interface... but OK for now.
    xs.Plot.addCommand("wdata {}".format(f_stem + ".qdp"))
    #xs.Plot.device = "/xw"  # Not necessary
    xs.Plot("ldata")
    xs.Plot.delCommand(len(xs.Plot.commands))

    # Dump XSPEC fit log
    xs_utils.dump_fit_log(f_stem + ".log")

    # Dump nice LaTeX table -- full table, + just row(s)
    ltab = make_table(snr, region_name)
    with open(f_stem + ".tex", 'w') as f_tex:
        f_tex.write(str(ltab))
    with open(f_stem + "_row.tex", 'w') as f_tex:
        f_tex.write('\n'.join(ltab.get_rows()))

    # Dump succinct summary of fit parameters
    print_fit(snr, f_stem + ".txt")


#############################################
# Specific fit setup and execution routines #
#############################################

def set_energy_range(all_extrs):
    """Set up fit (range ignores, PN power law setup, renorm)
    These are specific ALWAYS-ON tweaks or fixes, typically determined after
    running some fits...
    """
    for extr in all_extrs:
        if extr.instr == "mos1" or extr.instr == "mos2":
            extr.spec.ignore("**-0.3, 11.0-**")
        if extr.instr == "pn":
            extr.spec.ignore("**-0.4, 11.0-**")
        #if extr.instr == 'pn':  # May not need to fix by default
        #    extr.spec.models['sp'].powerlaw.PhoIndex = 0.2
        #    extr.spec.models['sp'].powerlaw.PhoIndex.frozen = True


def joint_src_bkg_fit():
    """Fit source + bkg regions, allowing XRB to float"""

    out = myxs.load_data("src", "bkg", snr_model='vnei')
    set_energy_range(out['src'])
    set_energy_range(out['bkg'])
    xs.AllData.ignore("bad")

    xs.AllModels(4,'snr_src').constant.factor = 0.95  # TODO manual hack...

    # Set XRB parameters to "typical" values, but do NOT allow to vary
    xrb = xs.AllModels(1, 'xrb')
    xrb.setPars({xrb.apec.kT.index : "0.1, , 0, 0, 0.5, 1"},  # Unabsorped apec (local bubble)
                {xrb.TBabs.nH.index : "1, , 0.01, 0.1, 5, 10"},  # Galactic absorption
                {xrb.apec_5.kT.index : "0.5, , 0, 0, 2, 4"},  # Absorbed apec (galactic halo)
                {xrb.apec.norm.index : 1e-3},
                {xrb.apec_5.norm.index : 1e-3} )
    xrb.apec.kT.frozen = True
    xrb.TBabs.nH.frozen = True
    xrb.apec_5.kT.frozen = True
    xrb.apec.norm.frozen = True
    xrb.apec_5.norm.frozen = True

    xs.Fit.renorm()

    # Let SNR model vary
    snr = xs.AllModels(1,'snr_src')
    snr.TBabs.nH.frozen=False
    snr.vnei.kT.frozen=False
    snr.vnei.Tau.frozen=False
    #xs.Fit.perform()
    snr.vnei.Si.frozen=False
    snr.vnei.S.frozen=False
    xs.Fit.perform()

    # XRB is not as well constrained as SNR, and fits w/ XRB free
    # (and SNR at default vnei values) tend to run away
    xrb.apec.kT.frozen = False
    xrb.TBabs.nH.frozen = False
    xrb.apec_5.kT.frozen = False
    xrb.apec.norm.frozen = False
    xrb.apec_5.norm.frozen = False
    xs.Fit.perform()


def five_annulus_fit():
    """Fit five annuli simultaneously... extremely hard to see what's going on,
    so I don't make any fit adjustments.  That will have to be determined from
    individual region fits"""

    out = myxs.load_data("ann_000_100", "ann_100_200", "ann_200_300",
                         "ann_300_400", "ann_400_500", snr_model='vnei')

    set_energy_range(out['ann_000_100'])
    set_energy_range(out['ann_100_200'])
    set_energy_range(out['ann_200_300'])
    set_energy_range(out['ann_300_400'])
    set_energy_range(out['ann_400_500'])
    xs.AllData.ignore("bad")

    # TODO really weird bug -- regenerate spectrum and see if it persists
    for extr in out['ann_000_100']:
        extr.spec.ignore("10.0-**")  # 10-11 keV range messed up

    # Link nH across annuli
    rings = [out['ann_000_100'][0].models['snr_ann_000_100'],
             out['ann_100_200'][0].models['snr_ann_100_200'],
             out['ann_200_300'][0].models['snr_ann_200_300'],
             out['ann_300_400'][0].models['snr_ann_300_400'],
             out['ann_400_500'][0].models['snr_ann_400_500']]
    for ring in rings[1:]:  # Exclude center
        ring.TBabs.nH.link = xs_utils.link_name(rings[0], rings[0].TBabs.nH)

    xs.Fit.renorm()
    xs.Fit.perform()

    for ring in rings:
        ring.TBabs.nH.frozen = False
        ring.vnei.kT.frozen = False
        ring.vnei.Tau.frozen = False

    xs.Fit.perform()

    for ring in rings:
        ring.vnei.Si.frozen = False
        ring.vnei.S.frozen = False

    xs.Fit.perform()

def prep_xs(with_xw=False):
    """Apply standard XSPEC settings for G309"""
    xs.Xset.abund = "wilm"
    xs.AllModels.lmod("absmodel", dirPath=os.environ['XMM_PATH'] + "/../absmodel")
    xs.Fit.query = "yes"
    if with_xw:
        xs.Plot.device = "/xw"  # Must disable if you are using dump_plots_data
    xs.Plot.xAxis = "keV"
    xs.Plot.xLog = True
    xs.Plot.yLog = True
    xs.Plot.addCommand("rescale y 1e-5 3")  # may need to twiddle

###########################
# Actually run stuff here #
###########################

if __name__ == '__main__':

    prep_xs(with_xw=False)

    # Clock in
    # --------
    started = datetime.now()

    #joint_src_bkg_fit()
    out = myxs.load_data("src", "bkg", snr_model='vnei')
    #dump_plots_data('results_spec/20160421_src_and_bkg', xs.AllModels(1,'snr_src'), 'src')

    # five_annulus_fit()
    # dump_plots_data('fiveannfit_ann_000_100', xs.AllModels( 1, 'snr_ann_000_100'), 'ann_000_100')
    # dump_plots_data('fiveannfit_ann_100_200', xs.AllModels( 6, 'snr_ann_100_200'), 'ann_100_200')
    # dump_plots_data('fiveannfit_ann_200_300', xs.AllModels(11, 'snr_ann_200_300'), 'ann_200_300')
    # dump_plots_data('fiveannfit_ann_300_400', xs.AllModels(16, 'snr_ann_300_400'), 'ann_300_400')
    # dump_plots_data('fiveannfit_ann_400_500', xs.AllModels(21, 'snr_ann_400_500'), 'ann_400_500')


    # Sub region fits with varying nH values
    # --------------------------------------
#    regs = ["src_north_clump", "src_E_lobe", "src_SW_lobe", "src_SE_dark",
#            "src_ridge", "src_SE_ridge_dark", "src_pre_ridge",
#            "ann_000_100", "ann_100_200", "ann_200_300", "ann_300_400", "ann_400_500"]
#    nH_vals = [None, 1.5, 2.0, 2.5, 3.0]
#
#    times = []
#
#    for nH in nH_vals:
#        for reg in regs:
#
#            indiv_started = datetime.now()
#
#            out = myxs.load_data(reg, snr_model='vnei')
#            set_energy_range(out[reg])
#            if reg == 'ann_000_100':
#                for extr in out[reg]:
#                    extr.spec.ignore("10.0-**")  # 10-11 keV range messed up
#            xs.AllData.ignore("bad")
#
#            # Initial fit to help get reasonable soft proton values
#            xs.Fit.renorm()
#            xs.Fit.perform()
#
#            # Thaw kT, Tau, nH (if desired)
#            snr = out[reg][0].models['snr_'+reg]
#            snr.vnei.kT.frozen=False
#            snr.vnei.Tau.frozen=False
#            if nH is not None:
#                snr.TBabs.nH = nH
#                snr.TBabs.nH.frozen=True
#            else:
#                snr.TBabs.nH.frozen=False
#            xs.Fit.perform()
#
#            # Thaw Si, S
#            snr.vnei.Si.frozen=False
#            snr.vnei.S.frozen=False
#            xs.Fit.perform()
#
#            # WARNING: this will fail if files already exist at dump_str.
#            # Reason being, xspec /cps or /xw qdp dump stalls and waits for
#            # user input -- obviously undesirable.  TODO fix or work around
#            # WARNING 2: you CANNOT swap between /cps and /xw
#            # or else XSPEC will prompt you for input, blocking your script.
#            if nH is not None:
#                dump_str = 'results_spec/20160420_{}_nH_{}'.format(reg,nH)
#            else:
#                dump_str = 'results_spec/20160420_{}_nH_free'.format(reg)
#            dump_plots_data(dump_str, snr, reg)
#
#            xs.AllData.clear()
#            xs.AllModels.clear()
#
#            indiv_finished = datetime.now()
#
#            times.append(["{}, nH {}".format(reg, nH), indiv_started, indiv_finished])
#            print "   start", indiv_started
#            print "  finish", indiv_finished

    # Clock out
    # ---------
    print "Started at:", started
    print "Finished at:", datetime.now()

    print ""
#    for indiv in times:
#        print indiv[0] + ":", indiv[2] - indiv[1]
#        print "   start", indiv[1]
#        print "  finish", indiv[2]

