#!/usr/local/bin/python
"""
Run fits programatically
Basically a massive configuration file
Exploiting the fact that xspec objects are global (AllData, AllModels, etc...)

Tightly coupled to methods in g309_models

Must be run in a sasinit-sourced environment
"""

from __future__ import division

from datetime import datetime
from subprocess import call
import os
import sys

import xspec as xs

import g309_models as g309
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
            1. tbnew_gas * vnei
            2. tbnew_gas * vpshock
            3. tbnew_gas * vsedov
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
    print "  nH (10^22)    {:.3f} +/- {:.3f}".format(*f(snr.tbnew_gas.nH))
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
           snr.tbnew_gas.nH.values[0],
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


def joint_src_bkg_fit(error_log):
    """Fit source + bkg regions, allowing XRB to float"""

    out = g309.load_data("src", "bkg", snr_model='vnei')
    set_energy_range(out['src'])
    set_energy_range(out['bkg'])
    xs.AllData.ignore("bad")

    xs.AllModels(4,'snr_src').constant.factor = 0.95  # TODO manual hack...

    # Reset XRB parameters to "typical" values, but do NOT allow to vary
    xrb = xs.AllModels(1, 'xrb')
    xrb.setPars({xrb.apec.kT.index : "0.1, , 0, 0, 0.5, 1"},  # Unabsorped apec (local bubble)
                {xrb.tbnew_gas.nH.index : "1, , 0.01, 0.1, 5, 10"},  # Galactic absorption
                {xrb.apec_5.kT.index : "0.5, , 0, 0, 2, 4"},  # Absorbed apec (galactic halo)
                {xrb.apec.norm.index : 1e-3},
                {xrb.apec_5.norm.index : 1e-3} )
    xrb.apec.kT.frozen = True
    xrb.tbnew_gas.nH.frozen = True
    xrb.apec_5.kT.frozen = True
    xrb.apec.norm.frozen = True
    xrb.apec_5.norm.frozen = True

    xs.Fit.renorm()

    # Let SNR model vary
    snr = xs.AllModels(1,'snr_src')
    snr.tbnew_gas.nH.frozen=False
    snr.vnei.kT.frozen=False
    snr.vnei.Tau.frozen=False
    #xs.Fit.perform()
    snr.vnei.Si.frozen=False
    snr.vnei.S.frozen=False
    xs.Fit.perform()

    # XRB is not as well constrained as SNR, and fits w/ XRB free
    # (and SNR at default vnei values) tend to run away
    xrb.apec.kT.frozen = False
    xrb.tbnew_gas.nH.frozen = False
    xrb.apec_5.kT.frozen = False
    xrb.apec.norm.frozen = False
    xrb.apec_5.norm.frozen = False
    xs.Fit.perform()

    # Now that the fit has converged, run the error command on parameters of
    # interest
    print datetime.now()
    xs.Xset.openLog(error_log)
    xs.Fit.error("snr_src:{:d}".format(xs_utils.par_num(snr, snr.tbnew_gas.nH))
              + " snr_src:{:d}".format(xs_utils.par_num(snr, snr.vnei.kT))
              + " snr_src:{:d}".format(xs_utils.par_num(snr, snr.vnei.Tau))
              + " snr_src:{:d}".format(xs_utils.par_num(snr, snr.vnei.Si))
              + " snr_src:{:d}".format(xs_utils.par_num(snr, snr.vnei.S))
              + " snr_src:{:d}".format(xs_utils.par_num(snr, snr.vnei.norm))
                 )

    xs.Fit.error("xrb:{:d}".format(xs_utils.par_num(xrb, xrb.apec.kT))
              + " xrb:{:d}".format(xs_utils.par_num(xrb, xrb.tbnew_gas.nH))
              + " xrb:{:d}".format(xs_utils.par_num(xrb, xrb.apec_5.kT)))
    print datetime.now()

    # Repeat because a new best fit gets found in the process
    xs.Fit.error("snr_src:{:d}".format(xs_utils.par_num(snr, snr.tbnew_gas.nH))
              + " snr_src:{:d}".format(xs_utils.par_num(snr, snr.vnei.kT))
              + " snr_src:{:d}".format(xs_utils.par_num(snr, snr.vnei.Tau))
              + " snr_src:{:d}".format(xs_utils.par_num(snr, snr.vnei.Si))
              + " snr_src:{:d}".format(xs_utils.par_num(snr, snr.vnei.S))
              + " snr_src:{:d}".format(xs_utils.par_num(snr, snr.vnei.norm))
                 )

    xs.Fit.error("xrb:{:d}".format(xs_utils.par_num(xrb, xrb.apec.kT))
              + " xrb:{:d}".format(xs_utils.par_num(xrb, xrb.tbnew_gas.nH))
              + " xrb:{:d}".format(xs_utils.par_num(xrb, xrb.apec_5.kT)))
    xs.Xset.closeLog()
    print datetime.now()


def five_annulus_fit(error_log):
    """Fit five annuli simultaneously... extremely hard to see what's going on,
    so I don't make any fit adjustments.  That will have to be determined from
    individual region fits"""

    out = g309.load_data("ann_000_100", "ann_100_200", "ann_200_300",
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
    # Each region has 5 spectra (5 exposures)
    # [0] gets 1st of 5 ExtractedSpectra objects
    # .models['...'] call obtains corresponding 1st of 5 XSPEC models
    rings = [out['ann_000_100'][0].models['snr'],
             out['ann_100_200'][0].models['snr'],
             out['ann_200_300'][0].models['snr'],
             out['ann_300_400'][0].models['snr'],
             out['ann_400_500'][0].models['snr']]
    for ring in rings[1:]:  # Exclude center
        ring.tbnew_gas.nH.link = xs_utils.link_name(rings[0], rings[0].tbnew_gas.nH)

    xs.Fit.renorm()
    xs.Fit.perform()

    for ring in rings:
        ring.tbnew_gas.nH.frozen = False
        ring.vnei.kT.frozen = False
        ring.vnei.Tau.frozen = False

    xs.Fit.perform()

    for ring in rings:
        ring.vnei.Si.frozen = False
        ring.vnei.S.frozen = False

    xs.Fit.perform()

    # RUN ERROR CMDS
    print datetime.now()
    xs.Xset.openLog(error_log)
    for reg in ['ann_000_100', 'ann_100_200', 'ann_200_300', 'ann_300_400', 'ann_400_500']:
        ring = out[reg][0].models['snr']
        xs.Fit.error("snr_{:s}:{:d}".format(reg, xs_utils.par_num(ring, ring.vnei.kT))
                  + " snr_{:s}:{:d}".format(reg, xs_utils.par_num(ring, ring.vnei.Tau))
                  + " snr_{:s}:{:d}".format(reg, xs_utils.par_num(ring, ring.vnei.Si))
                  + " snr_{:s}:{:d}".format(reg, xs_utils.par_num(ring, ring.vnei.S))
#                  + " snr_{:s}:{:d}".format(reg, xs_utils.par_num(ring, ring.vnei.norm))
                     )
        print datetime.now()
    xs.Fit.error("snr_ann_000_100:{:d}".format(xs_utils.par_num(rings[0], rings[0].tbnew_gas.nH)))
    xs.Xset.closeLog()
    print datetime.now()

    # RUN ERROR CMDS AGAIN, presuming that we'll find better fits
    print datetime.now()
    xs.Xset.openLog(error_log + '_round2.log')
    for reg in ['ann_000_100', 'ann_100_200', 'ann_200_300', 'ann_300_400', 'ann_400_500']:
        ring = out[reg][0].models['snr']
        xs.Fit.error("snr_{:s}:{:d}".format(reg, xs_utils.par_num(ring, ring.vnei.kT))
                  + " snr_{:s}:{:d}".format(reg, xs_utils.par_num(ring, ring.vnei.Tau))
                  + " snr_{:s}:{:d}".format(reg, xs_utils.par_num(ring, ring.vnei.Si))
                  + " snr_{:s}:{:d}".format(reg, xs_utils.par_num(ring, ring.vnei.S))
                  + " snr_{:s}:{:d}".format(reg, xs_utils.par_num(ring, ring.vnei.norm))
                     )
        print datetime.now()
    xs.Fit.error("snr_ann_000_100:{:d}".format(xs_utils.par_num(rings[0], rings[0].tbnew_gas.nH)))
    xs.Xset.closeLog()
    print datetime.now()

def ann_400_500_fit():
    """Fit the 400-500" annulus"""

    out = g309.load_data("ann_400_500", snr_model='vnei')
    set_energy_range(out['ann_400_500'])
    xs.AllData.ignore("bad")

    xs.Fit.renorm()
    xs.Fit.perform()
    # chi-squared = 1160.25/826 = 1.40466

    snr.tbnew_gas.nH.frozen=False
    snr.vnei.kT.frozen=False
    snr.vnei.Tau.frozen=False
    xs.Fit.perform()
    #nH         10^22    3.71168      +/-  0.444826
    #kT         keV      4.21543      +/-  1.89369
    #Tau        s/cm^3   1.31465E+10  +/-  3.57926E+09
    #norm                1.30286E-03  +/-  4.13489E-04
    # chi-squared = 970.40/823 = 1.1791

    # Annulus 400-500" is dominated by background emission
    # If I set SNR norm to 0 from best fit, the excess is quite subtle --
    # although you can see Si/S lines if you quint.

    snr.vnei.Si.frozen=False
    snr.vnei.S.frozen=False
    xs.Fit.perform()
    # Fit runs away to kT = 10 keV, unreasonable.
    # Freeze to 1, fit, thaw, fit.
    # chi-squared = 961.04/821 = 1.1706

    # Freeze SNR nH, kT to nH=2, kT=1, fit, thaw, fit
    # No dice.  Numbers just keep running up.

    # Final attempt:
    # freeze SNR nH, kT to values from integrated spectrum fit.
    # Si = 4.44, S = 4.05, Tau = 3.4e+10
    # chi-squared = 999.40/823 = 1.2143

    # Freezing SNR nH just lets kT run away.
    # Now try freezing Si,S to 1. -- same as previous fit, but just
    # force lower nH.

    # kT keeps running away.

    # Finally compare to a fit with NO SNR component, XRB component free
    # The SNR component definitely helps.
    ###out = g309.load_data("ann_400_500", snr_model=None)
    ###set_energy_range(out['ann_400_500'])
    ###xs.AllData.ignore("bad")
    #### Reset XRB parameters to "typical" values, but do NOT allow to vary
    ###xrb = xs.AllModels(1, 'xrb')
    ###xrb.setPars({xrb.apec.kT.index : "0.1, , 0, 0, 0.5, 1"},  # Unabsorped apec (local bubble)
    ###            {xrb.tbnew_gas.nH.index : "1, , 0.01, 0.1, 5, 10"},  # Galactic absorption
    ###            {xrb.apec_5.kT.index : "0.5, , 0, 0, 2, 4"},  # Absorbed apec (galactic halo)
    ###            {xrb.apec.norm.index : 1e-3},
    ###            {xrb.apec_5.norm.index : 1e-3} )
    ###xrb.apec.kT.frozen = True
    ###xrb.tbnew_gas.nH.frozen = True
    ###xrb.apec_5.kT.frozen = True
    ###xrb.apec.norm.frozen = True
    ###xrb.apec_5.norm.frozen = True

    ###xs.Fit.renorm()
    ###xs.Fit.perform()

    ###xrb.apec.kT.frozen = False
    ###xrb.tbnew_gas.nH.frozen = False
    ###xrb.apec_5.kT.frozen = False
    ###xrb.apec.norm.frozen = False
    ###xrb.apec_5.norm.frozen = False
    ###xs.Fit.perform()
    # Result:
    # Test statistic : Chi-Squared =        1047.48 using 840 PHA bins.
    #  Reduced chi-squared =        1.27430 for    822 degrees of freedom
    #  Null hypothesis probability =   1.394979e-07
    # Yes, adding a SNR model helps somewhat.


###########################
# Actually run stuff here #
###########################

if __name__ == '__main__':

    prep_xs(with_xw=True)

    # Clock in
    # --------
    started = datetime.now()

    # Option 1:
    #joint_src_bkg_fit('20160523_error_rerun.log')  # Now includes error runs
    #dump_plots_data('results_spec/20160421_src_and_bkg', xs.AllModels(1,'snr_src'), 'src')

#    out = g309.load_data("ann_200_300", snr_model='vnei')
#    set_energy_range(out['ann_200_300'])
#    xs.AllData.ignore("bad")
#
#    xs.Fit.renorm()
#    xs.Fit.perform()
#
#    snr = xs.AllModels(1, 'snr_ann_200_300')
#    snr.tbnew_gas.nH.frozen=False
#    snr.vnei.kT.frozen=False
#    snr.vnei.Tau.frozen=False
#    xs.Fit.perform()
#
#    snr.vnei.Si.frozen=False
#    xs.Fit.perform()
#    #reduced chi-squared = 1000.32/799 = 1.252
#    #snr model: constant*tbnew_gas*vnei
#    #  nH (10^22)    2.714 +/- 0.139
#    #  kT   (keV)    1.411 +/- 0.194
#    #  Tau (s/cm^3)  3.53e+10 +/- 6.79e+09
#    #  Si            2.51  +/- 0.20
#    #  norm          4.42e-03 +/- 8.32e-04
#    #soft proton power laws
#    #  Data group 1, n  0.35 +/- 0.02,  norm  5.29e-02 +/- 2.00e-03
#    #  Data group 2, n  0.35 +/- 0.00,  norm  5.63e-02 +/- 2.08e-03
#    #  Data group 3, n  0.09 +/- 0.06,  norm  5.04e-02 +/- 6.26e-03
#    #  Data group 4, n  0.35 +/- 0.03,  norm  4.89e-02 +/- 2.89e-03
#    #  Data group 5, n  0.35 +/- 0.00,  norm  1.37e-02 +/- 1.48e-03
#
#    snr.vnei.S.frozen=False
#    xs.Fit.perform()
#    #reduced chi-squared = 958.13/798 = 1.201
#    #snr model: constant*tbnew_gas*vnei
#    #  nH (10^22)    2.372 +/- 0.134
#    #  kT   (keV)    1.721 +/- 0.307
#    #  Tau (s/cm^3)  2.34e+10 +/- 3.87e+09
#    #  Si            3.08  +/- 0.25
#    #  S             2.56  +/- 0.34
#    #  norm          2.80e-03 +/- 5.62e-04
#    #soft proton power laws
#    #  Data group 1, n  0.35 +/- 0.02,  norm  5.25e-02 +/- 2.02e-03
#    #  Data group 2, n  0.35 +/- 0.00,  norm  5.59e-02 +/- 2.10e-03
#    #  Data group 3, n  0.09 +/- 0.06,  norm  5.12e-02 +/- 6.36e-03
#    #  Data group 4, n  0.34 +/- 0.03,  norm  4.83e-02 +/- 2.92e-03
#    #  Data group 5, n  0.34 +/- 0.00,  norm  1.35e-02 +/- 1.48e-03
#
#    # Do note that the PN power law is almost FLAT, which may be unphysical.
#
#    print_fit(snr)
#    xs.Fit.error("snr_ann_200_300:4")  # By construction, PyXSPEC will require
    # us to reference parameters using indices

    # For a single parameter, takes ~3 minutes.

    five_annulus_fit('20160524_five_annulus_error.log')
    dump_plots_data('results_spec/20160524_fiveannfit_with_error_ann_000_100', xs.AllModels( 1, 'snr_ann_000_100'), 'ann_000_100')
    dump_plots_data('results_spec/20160524_fiveannfit_with_error_ann_100_200', xs.AllModels( 6, 'snr_ann_100_200'), 'ann_100_200')
    dump_plots_data('results_spec/20160524_fiveannfit_with_error_ann_200_300', xs.AllModels(11, 'snr_ann_200_300'), 'ann_200_300')
    dump_plots_data('results_spec/20160524_fiveannfit_with_error_ann_300_400', xs.AllModels(16, 'snr_ann_300_400'), 'ann_300_400')
    dump_plots_data('results_spec/20160524_fiveannfit_with_error_ann_400_500', xs.AllModels(21, 'snr_ann_400_500'), 'ann_400_500')


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
#            out = g309.load_data(reg, snr_model='vnei')
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
#                snr.tbnew_gas.nH = nH
#                snr.tbnew_gas.nH.frozen=True
#            else:
#                snr.tbnew_gas.nH.frozen=False
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

