#!/usr/local/bin/python
"""
Run fits -- tightly coupled to "g309_models.py".
Must be run in a sasinit-sourced environment

Outputs: user-choice.  nominally can produce plots, data dumps,
fit log dumps, LaTeX table dumps, etc.

Goal is to sit at interface of scripting + interactive work...

As an end user I want to:
1. run interactive PyXSPEC sessions, but call methods from this script
   to skip over boilerplate
   (load tbnew_gas, dump data quickly, etc.)
2. run script sessions -- call methods from this script, let fits run,
   dump outputs automatically (specified as method arguments or command line
   options)
3. record my interactive work.
   sometimes, save interactive work.

This would be well covered with the iPython notebook (or Jupyter),
but the way PyXSPEC works (lots of terminal logging and copious output) doesn't
play nice with jupyter.

The method I have settled on is to save interactive sessions to methods,
which essentially serve as a log of my analyses for re-running later.

One possible pitfall is that g309_models and g309_fits have a lot of hard-coded
pieces.
E.g., if I change g309_models to use 3 spectra instead of 5 for each region,
all the old methods will break horribly.

In a lot of cases we are forced to address spectra, models by hand (using XSPEC
numbering or whatever instead of semantic descriptors).

USAGE (drop the user into a nice interactive session with necessary modules)
    from g309_fits import *
"""

from __future__ import division

from subprocess import call
from datetime import datetime
import numpy as np
import os
import sys
import tempfile

import xspec as xs

import g309_models as g309
import xspec_utils as xs_utils
from nice_tables import LatexTable


############################################
# Stuff for printing and displaying output #
############################################

def print_model(m, f_out=None):
    """More succinct model output printer
    Ignores all frozen components
    prints model name, expression
    Prints parameters, with errors/units if available.
    """

    if f_out:
        fh = open(f_out, 'w')
        old_stdout = sys.stdout
        sys.stdout = fh

    print m.name, ":", m.expression

    for cname in m.componentNames:  # for comp in m.components
        comp = eval("m." + cname)

        for pname in comp.parameterNames:  # for par in comp.parameters
            par = eval("comp." + pname)

            if par.frozen:
                continue

            name = par.name
            val = par.values[0]

            if par.unit:
                name = name + " (" + par.unit + ")"

            if par.error[0] != 0:
                err_low = par.error[0] - par.values[0]
                err_high = par.error[1] - par.values[0]
                val = "{{{:g}}}^{{{:+.2g}}}_{{{:+.2g}}}".format(
                        val, err_high, err_low)

            print "{}: {:g} (sigma: {:g})".format(name, val, par.sigma)

            if par.error[2] != "FFFFFFFFF":
                print "  error status:", par.error[2]

    if f_out:
        fh.close()
        sys.stdout = old_stdout


# TODO this will block script execution if files already exist here.
# work around.... clobber in python or w/e
def wdata(fname):
    """Dump plot data for ALL spectra using iplot wdata command.
    Note that a plot command is invoked in the process.
    Output
        QDP file at fname
    """
    xs.Plot.addCommand("wdata " + fname)
    xs.Plot("ldata")
    xs.Plot.delCommand(len(xs.Plot.commands))


def pdf(fname, cmd="ldata delchi"):
    """Dump a plot w/ given cmd to fname

    WARNING: this will NOT WORK IN SCRIPTS IF THE PLOT DEVICE WAS SET TO /xw
        ALREADY (and something was displayed?...)!
        XSPEC will hang at a prompt "Type <RETURN> for next page:"
        Partial fix: use "/xs" instead...

    No plot settings are applied; tweak PyXSPEC parameters as you need first.

    Arguments
        f_stem: filename stem
        cmd:    XSPEC plot (sub)commands (default: ldata delchi)
    Output
        None.  File written to {fname}
        On occasion XSPEC dumps have not displayed properly
    """
    old_device = xs.Plot.device

    # Kludgy, but guarantees that no other application will overwrite the temp
    # file until method concludes
    fh_ps = tempfile.NamedTemporaryFile(delete=False)
    fh_ps.close()
    temp_ps = fh_ps.name

    xs.Plot.device = temp_ps + "/cps"
    xs.Plot(cmd)
    call(["ps2pdf", temp_ps, fname])
    call(["rm", temp_ps])

    xs.Plot.device = old_device


def clear():
    xs.AllData.clear()
    xs.AllModels.clear()


#############################################
# Specific fit setup and execution routines #
#############################################

def stopwatch(function, *args, **kwargs):
    """Time a function call, printing start/stop times to console after the
    function halts (after Exceptions as well)"""
    started = datetime.now()
    try:
        function(*args, **kwargs)
    finally:
        stopped = datetime.now()
        print "Started:", started
        print "Stopped:", stopped
        print "Elapsed:", stopped - started


def prep_xs(with_xs=False):
    """Apply standard XSPEC settings for G309"""
    xs.Xset.abund = "wilm"
    xs.AllModels.lmod("absmodel", dirPath=os.environ['XMM_PATH'] + "/../absmodel")
    xs.Fit.query = "yes"
    if with_xs:
        xs.Plot.device = "/xs"
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


def joint_src_bkg_fit(error=False, error_log=None):
    """Fit source + bkg regions, allowing XRB to float"""

    out = g309.load_data_and_models("src", "bkg", snr_model='vnei')
    set_energy_range(out['src'])
    set_energy_range(out['bkg'])
    xs.AllData.ignore("bad")

    xs.AllModels(4,'snr_src').constant.factor = 0.95  # TODO manual hack...  !!!!

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

    if error:

        # Now that the fit has converged, run the error command on parameters of
        # interest
        if error_log:
            xs.Xset.openLog(error_log)

        print "START OF FIRST ERROR RUN:", datetime.now()

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

        print "START OF SECOND ERROR RUN:", datetime.now()

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

        print "END OF ERROR RUNS:", datetime.now()

        if error_log:
            xs.Xset.closeLog()



def five_annulus_fit(error_log):
    """Fit five annuli simultaneously... extremely hard to see what's going on,
    so I don't make any fit adjustments.  That will have to be determined from
    individual region fits"""

    out = g309.load_data_and_models("ann_000_100", "ann_100_200", "ann_200_300",
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
    # 2016 May 24 - second run was ultimately not needed
    # this could change if the annulus fits or spectra are altered
    #xs.Xset.openLog(error_log + '_round2.log')
    #for reg in ['ann_000_100', 'ann_100_200', 'ann_200_300', 'ann_300_400', 'ann_400_500']:
    #    ring = out[reg][0].models['snr']
    #    xs.Fit.error("snr_{:s}:{:d}".format(reg, xs_utils.par_num(ring, ring.vnei.kT))
    #              + " snr_{:s}:{:d}".format(reg, xs_utils.par_num(ring, ring.vnei.Tau))
    #              + " snr_{:s}:{:d}".format(reg, xs_utils.par_num(ring, ring.vnei.Si))
    #              + " snr_{:s}:{:d}".format(reg, xs_utils.par_num(ring, ring.vnei.S))
    #              + " snr_{:s}:{:d}".format(reg, xs_utils.par_num(ring, ring.vnei.norm))
    #                 )
    #    print datetime.now()
    #xs.Fit.error("snr_ann_000_100:{:d}".format(xs_utils.par_num(rings[0], rings[0].tbnew_gas.nH)))
    #xs.Xset.closeLog()
    #print datetime.now()


def ann_400_500_fit():
    """Fit the 400-500" annulus"""

    out = g309.load_data_and_models("ann_400_500", snr_model='vnei')
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
    ###out = g309.load_data_and_models("ann_400_500", snr_model=None)
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

    prep_xs(with_xs=True)  # This is required before all fits actually...

    f_stem = "results_spec/20160610_src_bkg_rerun"

    stopwatch(joint_src_bkg_fit, error=True, error_log=f_stem+"_error.log")

    snr = xs.AllModels(1, 'snr_src')

    pdf(f_stem + ".pdf", cmd="ldata delchi")
    wdata(f_stem + ".qdp")
    xs_utils.dump_fit_log(f_stem + ".log")
    print_model(snr, f_out=f_stem+"_snr_model.txt")

    # Dump fit parameters to 1. copy-pastable table, 2. just rows alone
    latex_hdr = [['Region', ''],
                 [r'$n_\mathrm{H}$', r'($10^{22} \unit{cm^{-2}}$)'],
                 [r'$kT$', r'(keV)'],
                 [r'$\tau$', r'($10^{10} \unit{s\;cm^{-3}}$)'],
                 ['Si', '(-)'],
                 ['S', '(-)'],
                 [r'$\chi^2_{\mathrm{red}} (\mathrm{dof}$)', '']]
    latex_hdr = np.array(latex_hdr).T
    latex_cols = ['{:s}', 0, 0, 0, 0, 0, '{:s}'] # TODO incorporate errors
    ltab = LatexTable(latex_hdr, latex_cols, "G309.2-0.6 integrated fit", prec=4)

    ltr = ['Source',
           snr.tbnew_gas.nH.values[0],
           snr.vnei.kT.values[0],
           snr.vnei.Tau.values[0] / 1e10,
           snr.vnei.Si.values[0],
           snr.vnei.S.values[0],
           "{:0.3f} ({:d})".format(xs.Fit.statistic/xs.Fit.dof, xs.Fit.dof)]
    ltab.add_row(*ltr)

    with open(f_stem + ".tex", 'w') as f_tex:
        f_tex.write(str(ltab))
    with open(f_stem + "_row.tex", 'w') as f_tex:
        f_tex.write('\n'.join(ltab.get_rows()))



    # five_annulus_fit('2016mmdd_five_annulus_error.log')
    #rings = [xs.AllModels(1,  'snr_ann_000_100'),
    #         xs.AllModels(6,  'snr_ann_100_200'),
    #         xs.AllModels(11, 'snr_ann_200_300'),
    #         xs.AllModels(16, 'snr_ann_300_400'),
    #         xs.AllModels(21, 'snr_ann_400_500')]
    ##pdf(  "results_spec/2016mmdd_five_ann_fit.pdf", cmd="ldata delchi")  # USELESS MESS
    #wdata("results_spec/2016mmdd_five_ann_fit.qdp")
    #xs_utils.dump_fit_log("results_spec/2016mmdd_five_ann_fit.log")

    #for ring in rings:
    #    model_log = "results_spec/2016mmdd_five_ann_fit_" + ring.name + ".txt"
    #    print_model(ring, model_log)

    #latex_hdr = [['Annulus', ''],
    #             [r'$n_\mathrm{H}$', r'($10^{22} \unit{cm^{-2}}$)'],
    #             [r'$kT$', r'(keV)'],
    #             [r'$\tau$', r'($10^{10} \unit{s\;cm^{-3}}$)'],
    #             ['Si', '(-)'],
    #             ['S', '(-)'],
    #latex_hdr = np.array(latex_hdr).T

    #latex_cols = ['{:s}', 0, 0, 0, 0, 0] # TODO incorporate errors
    #ltab = LatexTable(latex_hdr, latex_cols, "G309.2-0.6 annuli fit", prec=2)

    ## IF error command results are available, can (conditionally) add here.
    #for ring in rings:
    #    ltr = [ring.name,
    #           snr.tbnew_gas.nH.values[0],
    #           snr.vnei.kT.values[0],
    #           snr.vnei.Tau.values[0] / 1e10,
    #           snr.vnei.Si.values[0],
    #           snr.vnei.S.values[0]]
    #    ltab.add_row(*ltr)




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
#            out = g309.load_data_and_models(reg, snr_model='vnei')
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
#            wdata(dump_str + ".qdp")
#            pdf(dump_str + ".pdf")
#            xs_utils.dump_fit_log(dump_str + ".log")
#            print_model(snr, dump_str + "_snr.txt")
#            #print_model(sp, dump_str + "_snr.txt")  #Or whatever - this won't work
#
#            clear()
#
#            indiv_finished = datetime.now()
#
#            times.append(["{}, nH {}".format(reg, nH), indiv_started, indiv_finished])
#            print "   start", indiv_started
#            print "  finish", indiv_finished

#    for indiv in times:
#        print indiv[0] + ":", indiv[2] - indiv[1]
#        print "   start", indiv[1]
#        print "  finish", indiv[2]

