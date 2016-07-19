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


############################################
# Stuff for printing and displaying output #
############################################

def products(output):
    """Standardized output products for any XSPEC fit"""
    pdf(output + ".pdf", cmd="ldata delchi")
    wdata(output + ".qdp")
    xs_utils.dump_fit_log(output + ".log")
    xs_utils.dump_dict(xs_utils.fit_dict(), output + ".json")


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
        comp = m.__getattribute__(cname)

        for pname in comp.parameterNames:  # for par in comp.parameters
            par = comp.__getattribute__(pname)

            if par.frozen:
                continue

            name = par.name
            val = "{:g}".format(par.values[0])

            if par.unit:
                name = name + " (" + par.unit + ")"

            if par.error[0] != 0:
                err_low = par.error[0] - par.values[0]
                err_high = par.error[1] - par.values[0]
                val = "{{{:s}}}^{{{:+.2g}}}_{{{:+.2g}}}".format(
                        val, err_high, err_low)

            # recall both name, val are already-formatted strings
            print "{}: {} (sigma: {:g})".format(name, val, par.sigma)

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


def stopwatch(function, *args, **kwargs):
    """Time a function call, printing start/stop times to console after the
    function halts (after Exceptions as well)"""
    started = datetime.now()
    try:
        function(*args, **kwargs)
    finally:
        stopped = datetime.now()
        print function.func_name, "timing"
        print "  Started:", started
        print "  Stopped:", stopped
        print "  Elapsed:", stopped - started


########################
# Customized fit setup #
########################

def prep_xs(with_xs=False):
    """Apply standard XSPEC settings for G309"""
    xs.Xset.abund = "wilm"
    xs.AllModels.lmod("absmodel", dirPath=os.environ['XMM_PATH'] + "/../absmodel")
    xs.AllModels.lmod("srcutlog", dirPath=os.environ['XMM_PATH'] + "/../srcutlog")
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


############################
# Customized fit execution #
############################

def src_powerlaw_xrbfree(output, error=False):
    """Fit integrated source w/ vnei+powerlaw, XRB free"""

    out = g309.load_data_and_models('src', 'bkg', snr_model='vnei+powerlaw')
    set_energy_range(out['src'])
    set_energy_range(out['bkg'])
    xs.AllData.ignore('bad')

    # Reset XRB to "typical" values, do NOT vary yet
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

    # Ordering: (1) free vnei, (2) free power law, (3) free XRB
    # then let error runs investigate non-monotonicity...
    snr = xs.AllModels(1,'snr_src')

    snr.tbnew_gas.nH.frozen=False
    snr.vnei.kT.frozen=False
    snr.vnei.Tau.frozen=False
    snr.vnei.Si.frozen=False
    snr.vnei.S.frozen=False
    snr.powerlaw.PhoIndex=2
    snr.powerlaw.PhoIndex.frozen=True
    snr.powerlaw.norm=0
    snr.powerlaw.norm.frozen=True
    xs.Fit.perform()
    xs.Plot("ld delch")

    snr.powerlaw.norm.frozen=False
    xs.Fit.perform()
    snr.powerlaw.PhoIndex.frozen=False
    xs.Fit.perform()
    xs.Plot("ld delch")

    xrb.apec.kT.frozen = False
    xrb.tbnew_gas.nH.frozen = False
    xrb.apec_5.kT.frozen = False
    xrb.apec.norm.frozen = False
    xrb.apec_5.norm.frozen = False
    xs.Fit.perform()
    xs.Plot("ld delch")

    if error:
        xs.Fit.error("snr_src:21,22,2,4,12,13,18,20")

        xs.Fit.error("xrb:{:d},{:d},{:d}".format(
            xs_utils.par_num(xrb, xrb.apec.kT),
            xs_utils.par_num(xrb, xrb.tbnew_gas.nH),
            xs_utils.par_num(xrb, xrb.apec_5.kT)))

    products(output)


def src_srcutlog(output, region='src', solar=False, error=False):
    """
    Fit a region to vnei+srcutlog, XRB fixed
    Arguments
        output: file stem string
        region: region ID
        solar: fit to solar abundances, or let Si,S run free
        error: perform error runs
    """

    out = g309.load_data_and_models(region, snr_model='vnei+srcutlog')
    set_energy_range(out[region])
    xs.AllData.ignore('bad')

    xs.Fit.renorm()

    # Let XSPEC fit vnei and srcutlog simultaneously,
    # a little better behaved than w/ powerlaw
    snr = xs.AllModels(1,'snr_'+region)
    snr.tbnew_gas.nH.frozen = False
    snr.vnei.kT.frozen = False
    snr.vnei.Tau.frozen = False
    if solar:
        snr.vnei.Si.frozen = True
        snr.vnei.S.frozen = True
    else:
        snr.vnei.Si.frozen = False
        snr.vnei.S.frozen = False

    # Set 10^10 Hz break, basically zero contribution at X-ray energies
    #break_p = snr.srcutlog.__getattribute__('break')
    #break_p._setValues(10)  # HACKY WORKAROUND...
    #break_p.frozen = True

    xs.Fit.perform()
    xs.Plot("ld delch")

    # In case srcutlog break ran to zero, make sure we do traverse
    # reasonably high break values: 15 -- 17 in 10+1 steps.
    xs.Fit.steppar("snr_{}:22 15 17 10".format(region))

    if error:
        xs.Xset.openLog(output + "_error.log")
        print "Error run start:", datetime.now()

        # 22 = srcutlog break
        # 2 = nH, 4 = kT, 12/13 = Si/S, 18 = Tau, 20 = vnei norm
        xs.Fit.error("snr_{}:22,2,4,12,13,18,20".format(region))
        # note: if Si/S frozen, XSPEC will print a benign warning

        xs.Xset.closeLog()
        print "Error run stop:", datetime.now()

    # Diagnostic plots and numbers
    products(output)
    print_model(snr, output + "_snr_" + region + ".txt")

    # Zero out the vnei component to isolate srcutlog contribution
    norm_vnei = snr.vnei.norm.values[0]
    snr.vnei.norm = 0
    wdata(output + "_srcutlog-only.qdp")
    snr.vnei.norm = norm_vnei  # Reset

    # Zero out the srcutlog component to isolate vnei contribution
    break_p = snr.srcutlog.__getattribute__('break')  # hacky workaround
    break_srcutlog = break_p.values[0]
    break_p._setValues(1e-7)  # log(freq), so break=10 is already negligible
    wdata(output + "_vnei-only.qdp")
    break_p._setValues(break_srcutlog)  # Reset



def single_fit(output, region='src', free_elements=None, error=False):
    """
    Fit a region to vnei, XRB fixed
    Arguments
        output: file stem string
        region: region ID
        free_elements: (default) is [Si,S]
            if [], use solar abundances
        error: perform single error run
    """
    if free_elements is None:
        free_elements = ['Si', 'S']

    out = g309.load_data_and_models(region, snr_model='vnei')
    set_energy_range(out[region])
    xs.AllData.ignore('bad')

    xs.Fit.renorm()

    snr = xs.AllModels(1,'snr_'+region)
    snr.tbnew_gas.nH.frozen = False
    snr.vnei.kT.frozen = False
    snr.vnei.Tau.frozen = False
    for elem in free_elements:
        comp = snr.vnei.__getattribute__(elem)
        comp.frozen=False

    xs.Fit.perform()
    xs.Plot("ld delch")

    # TODO - may need to provide rerun functionality
    if error:
        xs.Xset.openLog(output + "_error.log")

        err_str = "snr_{:s}:{:d},{:d},{:d},{:d}".format(reg,
                        xs_utils.par_num(snr, snr.tbnew_gas.nH),
                        xs_utils.par_num(snr, snr.vnei.kT),
                        xs_utils.par_num(snr, snr.vnei.Tau),
                        xs_utils.par_num(snr, snr.vnei.norm)
                        )
        for elem in free_elements:
            comp = snr.vnei.__getattribute__(elem)
            err_str = err_str + ",{:d}".format(xs_utils.par_num(snr, comp))

        print "Error run start:", datetime.now()
        xs.Fit.error(err_str)
        xs.Xset.closeLog()
        print "Error run stop:", datetime.now()

    products(output)
    print_model(snr, output + "_snr_" + region + ".txt")


def src_powerlaw(output, region='src', solar=False, error=False):
    """
    Fit a region to vnei+powerlaw, XRB fixed
    Arguments
        output: file stem string
        region: region ID
        solar: fit to solar abundances, or let Si,S run free
        error: perform error runs
    """

    out = g309.load_data_and_models(region, snr_model='vnei+powerlaw')
    set_energy_range(out[region])
    xs.AllData.ignore('bad')

    xs.Fit.renorm()

    # Let SNR model attain nominal best fit without power law first
    # (fit does not converge well otherwise)
    snr = xs.AllModels(1,'snr_'+region)
    snr.tbnew_gas.nH.frozen = False
    snr.vnei.kT.frozen = False
    snr.vnei.Tau.frozen = False
    if solar:
        snr.vnei.Si.frozen = True
        snr.vnei.S.frozen = True
    else:
        snr.vnei.Si.frozen = False
        snr.vnei.S.frozen = False

    snr.powerlaw.PhoIndex=2
    snr.powerlaw.PhoIndex.frozen=True
    snr.powerlaw.norm=0
    snr.powerlaw.norm.frozen=True

    xs.Fit.perform()
    xs.Plot("ld delch")

    # Now introduce power law
    snr.powerlaw.norm.frozen=False
    xs.Fit.perform()
    snr.powerlaw.PhoIndex.frozen=False
    xs.Fit.perform()
    xs.Plot("ld delch")

    # Because powerlaw generally runs to zero, make sure we do traverse
    # moderately strong power law cases
    xs.Fit.steppar("snr_{}:22 1e-5 1e-3 10".format(region))

    if error:
        xs.Xset.openLog(output + "_error.log")
        print "Error run start:", datetime.now()

        # 21 = PhoIndex, 22 = norm
        # 2 = nH, 4 = kT, 12/13 = Si/S, 18 = Tau, 20 = vnei norm
        xs.Fit.error("snr_{}:21,22,2,4,12,13,18,20".format(region))
        # note: if Si/S frozen, XSPEC will print a benign warning

        xs.Xset.closeLog()
        print "Error run stop:", datetime.now()

    # Diagnostic plots and numbers
    products(output)
    print_model(snr, output + "_snr_" + region + ".txt")

    # Zero out the vnei component to isolate powerlaw contribution
    norm_vnei = snr.vnei.norm.values[0]
    snr.vnei.norm = 0
    wdata(output + "_powerlaw-only.qdp")
    snr.vnei.norm = norm_vnei  # Reset

    # Zero out the powerlaw component to isolate vnei contribution
    norm_powerlaw = snr.powerlaw.norm.values[0]
    snr.powerlaw.norm = 0
    wdata(output + "_vnei-only.qdp")
    snr.powerlaw.norm = norm_powerlaw  # Reset



def joint_src_bkg_fit(output, free_elements=None, error=False,
                      backscal_ratio_hack=None):
    """
    Fit source + bkg regions, allowing XRB to float
    backscal_ratio_hack = arbitrary adjustment to 0551000201 MOS1S001
        source region backscal ratio.
        This was the smallest geometric w.r.t. 0087940201 MOS1 (ratio 0.88).
        But, because the missing area (missing chip #6) sampled little of the
        remnant, I thought that this ratio might be an underestimate of the
        true sampled remnant flux, and therefore introduced an arbitrary ratio
        adjustment to 0.95 in some fits.
        Build in this parameter as a way to explore fit scaling tension.

    Arguments
        output: file stem string
        free_elements: (default) is [Si,S]
            if [], use solar abundances
        error: perform single error run
        backscal_ratio_hack: see above
    """
    if free_elements is None:
        free_elements = ['Si', 'S']

    out = g309.load_data_and_models("src", "bkg", snr_model='vnei')
    set_energy_range(out['src'])
    set_energy_range(out['bkg'])
    xs.AllData.ignore("bad")

    if backscal_ratio_hack:
        xs.AllModels(4,'snr_src').constant.factor = backscal_ratio_hack

    # Reset XRB to "typical" values, do NOT vary yet
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
    for elem in free_elements:
        comp = snr.vnei.__getattribute__(elem)
        comp.frozen=False
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

        xs.Xset.openLog(output + "_error.log")
        print "Error run start:", datetime.now()

        # Perform XRB error run first because a new best fit is [typically]
        # found in this step
        xrb_err_str = "xrb:{:d},{:d},{:d}".format(
                            xs_utils.par_num(xrb, xrb.apec.kT),
                            xs_utils.par_num(xrb, xrb.tbnew_gas.nH),
                            xs_utils.par_num(xrb, xrb.apec_5.kT)
                        )
        xs.Fit.error(xrb_err_str)

        # Note: error commands cannot be combined; XSPEC only looks at
        # parameter numbers after the first "<model name>: ...", so error
        # command reruns must be done manually
        snr_err_str = "snr_src:{:d},{:d},{:d},{:d}".format(
                            xs_utils.par_num(snr, snr.tbnew_gas.nH),
                            xs_utils.par_num(snr, snr.vnei.kT),
                            xs_utils.par_num(snr, snr.vnei.Tau),
                            xs_utils.par_num(snr, snr.vnei.norm)
                        )
        for elem in free_elements:
            comp = snr.vnei.__getattribute__(elem)
            snr_err_str = snr_err_str + ",{:d}".format(xs_utils.par_num(snr, comp))
        xs.Fit.error(snr_err_str)

        print "Error run stop:", datetime.now()
        xs.Xset.closeLog()

    products(output)
    print_model(snr, output + "_snr_src.txt")
    print_model(xrb, output + "_xrb.txt")



def annulus_fit(output, error=False, error_rerun=False,
                free_center_elements=None, four_ann=False):
    """
    Fit five annuli simultaneously...

    Arguments:
        output = output products file stem
        error = run error commands?
        error_rerun = run error commands 2nd time?
        four_ann = fit only 4 instead of 5 annuli?
        free_center_elements = (case-sensitive) elements to free in central
            circle (0-100 arcsec).
            Element names much match XSPEC parameter names.
            Si, S already free by default.
    Output: n/a
        loads of stuff dumped to output*
        XSPEC session left in fitted state
    """

    if free_center_elements is None:
        free_center_elements = []

    regs = ["ann_000_100", "ann_100_200", "ann_200_300", "ann_300_400", "ann_400_500"]
    if four_ann:
        regs = ["ann_000_100", "ann_100_200", "ann_200_300", "ann_300_400"]

    out = g309.load_data_and_models(*regs, snr_model='vnei')
    for reg in regs:
        set_energy_range(out[reg])

    xs.AllData.ignore("bad")

    # TODO really weird bug -- regenerate spectrum and see if it persists
    for extr in out['ann_000_100']:
        extr.spec.ignore("10.0-**")  # 10-11 keV range messed up

    # Link nH across annuli
    # Each region has 5 spectra (5 exposures)
    # [0] gets 1st of 5 ExtractedSpectra objects
    # .models['...'] gets corresponding 1st of 5 XSPEC models
    rings = [out[reg][0].models['snr'] for reg in regs]
    for ring in rings[1:]:  # Exclude center
        ring.tbnew_gas.nH.link = xs_utils.link_name(rings[0], rings[0].tbnew_gas.nH)

    # Start fit process

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

    for elem in free_center_elements:
        # rings[0] to get center region only
        comp = rings[0].vnei.__getattribute__(elem)
        comp.frozen = False

    xs.Fit.perform()

    if xs.Plot.device == "/xs":
        xs.Plot("ldata delchi")

    # Error runs

    if error:

        xs.Xset.openLog(output + "_error.log")

        print "First error run:", datetime.now()
        for reg, ring in zip(regs, rings):
            xs.Fit.error("snr_{:s}:{:d},{:d},{:d},{:d}".format(reg,
                            xs_utils.par_num(ring, ring.vnei.kT),
                            xs_utils.par_num(ring, ring.vnei.Tau),
                            xs_utils.par_num(ring, ring.vnei.Si),
                            xs_utils.par_num(ring, ring.vnei.S))
                         )
            print reg, "errors complete:", datetime.now()  # Will not appear in error log

        center_str = "snr_ann_000_100:{:d}".format(xs_utils.par_num(rings[0], rings[0].tbnew_gas.nH))
        for elem in free_center_elements:
            comp = rings[0].vnei.__getattribute__(elem)
            center_str = center_str + ",{:d}".format(xs_utils.par_num(rings[0], comp))
        print "Running center errors:", center_str
        xs.Fit.error(center_str)

        if error_rerun:
            print "Second error run:", datetime.now()
            for reg, ring in zip(regs, rings):
                xs.Fit.error("snr_{:s}:{:d},{:d},{:d},{:d}".format(reg,
                                xs_utils.par_num(ring, ring.vnei.kT),
                                xs_utils.par_num(ring, ring.vnei.Tau),
                                xs_utils.par_num(ring, ring.vnei.Si),
                                xs_utils.par_num(ring, ring.vnei.S))
                             )
                print reg, "errors complete:", datetime.now()  # Will not appear in error log
            xs.Fit.error(center_str)  # Take advantage of previous work

        xs.Xset.closeLog()
        print "Error runs complete:", datetime.now()

    # Output products
    products(output)

    for ring in rings:
        model_log = output + "_{}.txt".format(ring.name)
        print_model(ring, model_log)
        # Save best fit model parameters to JSON -- includes errors & errorstr
        # (redundant -- all in giant fit dict, but easier to work with)
        xs_utils.dump_dict(xs_utils.model_dict(ring),
                           output + "_{}.json".format(ring.name))



def bkg_only_fit(output, error=False):
    """
    Fit bkg region alone to XRB model
    """
    out = g309.load_data_and_models("bkg", snr_model=None)
    set_energy_range(out['bkg'])
    xs.AllData.ignore("bad")

    # Reset XRB to "typical" values
    # As usual, fit is pretty sensitive to initial values
    # (initial kT values that are too small drive fit to a bad local minimum)
    xrb = xs.AllModels(1, 'xrb')
    xrb.setPars({xrb.apec.kT.index : "0.2, , 0, 0, 0.5, 1"},  # Unabsorped apec (local bubble)
                {xrb.tbnew_gas.nH.index : "1.5, , 0.01, 0.1, 5, 10"},  # Galactic absorption
                {xrb.apec_5.kT.index : "0.7, , 0, 0, 2, 4"},  # Absorbed apec (galactic halo)
                {xrb.apec.norm.index : 1e-3},
                {xrb.apec_5.norm.index : 1e-3} )
    xrb.apec.kT.frozen = False
    xrb.tbnew_gas.nH.frozen = False
    xrb.apec_5.kT.frozen = False
    xrb.apec.norm.frozen = False
    xrb.apec_5.norm.frozen = False

    xs.Fit.perform()
    if xs.Plot.device == "/xs":
        xs.Plot("ldata delchi")

    xs.Fit.steppar("xrb:{:d} 0.1 0.5 20".format(xs_utils.par_num(xrb, xrb.apec.kT)))
    xs.Fit.steppar("xrb:{:d} 0.4 0.8 20".format(xs_utils.par_num(xrb, xrb.apec_5.kT)))

    if xs.Plot.device == "/xs":
        xs.Plot("ldata delchi")

    if error:

        xs.Xset.openLog(output + "_error.log")

        print "Error run started:", datetime.now()
        xs.Fit.error("xrb:{:d}".format(xs_utils.par_num(xrb, xrb.apec.kT))
                  + " xrb:{:d}".format(xs_utils.par_num(xrb, xrb.apec.norm))
                  + " xrb:{:d}".format(xs_utils.par_num(xrb, xrb.tbnew_gas.nH))
                  + " xrb:{:d}".format(xs_utils.par_num(xrb, xrb.apec_5.kT))
                  + " xrb:{:d}".format(xs_utils.par_num(xrb, xrb.apec_5.norm)))

        print "Error run complete:", datetime.now()

        xs.Xset.closeLog()

    # Dump useful things here...
    products(output)
    print_model(xrb, output + "_xrb.txt")


###########################
# Actually run stuff here #
###########################

if __name__ == '__main__':

    # Options so far:
    # five_annulus_fit(output, error=False, error_rerun=False)
    # joint_src_bkg_fit(output, error=False)
    # src_powerlaw(output, region='src', error=False)
    # src_powerlaw_xrbfree(error=False, error=False)
    # src_srcutlog(...)
    # bkg_only_fit(...)
    # ...

    prep_xs(with_xs=True)  # Required before all fits

    # Integrated source fits
    # ----------------------

    stopwatch(joint_src_bkg_fit, "results_spec/20160630_src_bkg_nohack_rerun",
              error=True)
    clear()
    # Time: ~1-2 hrs

    stopwatch(joint_src_bkg_fit, "results_spec/20160712_src_bkg_mg",
              free_elements=["Mg", "Si", "S"], error=True)
    # Time: 1.5 hrs on statler
    # Time without error: ~2 minutes (4 minutes on treble)


    # Annulus fits, all varieties
    # ---------------------------

    # FIVE ANNULUS FITS

    stopwatch(annulus_fit, "results_spec/20160701_fiveann", error=True, error_rerun=False)
    # Rerun error command for center only
    ring = xs.AllModels(1,'snr_ann_000_100')
    xs.Xset.openLog("results_spec/20160701_fiveann" + "_error_rerun_manual.log")
    stopwatch(xs.Fit.error, "snr_ann_000_100:{:d},{:d},{:d},{:d}".format(
                                    xs_utils.par_num(ring, ring.vnei.kT),
                                    xs_utils.par_num(ring, ring.vnei.Tau),
                                    xs_utils.par_num(ring, ring.vnei.Si),
                                    xs_utils.par_num(ring, ring.vnei.S)))
    xs.Xset.closeLog()
    print_model(ring, "results_spec/20160701_fiveann_snr_ann_000_100.txt")
    clear()
    # Time: 2 days, 17 hrs on treble
    #   + extra 5 hours for error_rerun redo
    # (would roughly double to 4 days with error_rerun)

    stopwatch(five_annulus_fit, "results_spec/2016xxxx_fiveann_center-mg-free",
              error=True, error_rerun=True, free_center_mg=True)
    clear()
    # WARNING - needs to be regenerated.

    stopwatch(annulus_fit, "results_spec/20160701_fiveann_center-mg-fe-free", free_center_elements=["Mg", "Fe"], error=True, error_rerun=True)
    clear()
    # Time: 6 days, 10 hrs (!) on treble

    # FOUR ANNULUS FITS

    stopwatch(annulus_fit, "results_spec/20160706_fourann_stock", four_ann=True, error=True, error_rerun=True)
    clear()
    # Time: 1 day, 19.5 hrs on treble

    stopwatch(annulus_fit, "results_spec/20160708_fourann_center-mg-free", four_ann=True, free_center_elements=["Mg"], error=True, error_rerun=True)
    clear()
    # Time: 2 days, 14 hrs on treble (37 minutes without error run)

    stopwatch(annulus_fit, "results_spec/20160708_fourann_center-mg-ne-free", four_ann=True, free_center_elements=["Mg", "Ne"], error=True, error_rerun=True)
    clear()
    # Time: 2 days, 11 hrs on statler

    stopwatch(annulus_fit, "results_spec/20160708_fourann_center-mg-o-free", four_ann=True, free_center_elements=["Mg", "O"], error=True, error_rerun=True)
    clear()
    # Time: 1 day, 17.5 hrs on statler

    stopwatch(annulus_fit, "results_spec/20160708_fourann_center-mg-o-ne-free", four_ann=True, free_center_elements=["Mg", "O", "Ne"], error=True, error_rerun=True)
    clear()
    # Time: 3 days, 2 hrs on cooper

    stopwatch(annulus_fit, "results_spec/20160708_fourann_center-mg-fe-free", four_ann=True, free_center_elements=["Mg", "Fe"], error=True, error_rerun=True)
    clear()
    # Time: 1 day, 23.75 hrs on cooper

    stopwatch(annulus_fit, "results_spec/20160712_fourann_center-mg-o-fe-free", four_ann=True, free_center_elements=["Mg", "O", "Fe"], error=True, error_rerun=True)
    clear()
    # Time: 2 days, 18.5 hrs on cooper
    # Time without error runs: 34 minutes on treble


    # Nonthermal component source model fits
    # --------------------------------------
    # (n.b. some are out of date / run with old XRB parameters)

    stopwatch(src_powerlaw, "results_spec/20160630_src_powerlaw_solar",
              region='src', solar=True, error=True)
    clear()
    stopwatch(src_powerlaw, "results_spec/20160630_src_powerlaw_nonsolar",
              region='src', solar=False, error=True)
    clear()

    stopwatch(src_srcutlog, "results_spec/20160630_src_srcutlog_solar",
              region='src', solar=True, error=True)
    clear()
    stopwatch(src_srcutlog, "results_spec/20160630_src_srcutlog_nonsolar",
              region='src', solar=False, error=True)
    clear()
    stopwatch(src_srcutlog, "results_spec/20160630_ann-400-500_srcutlog_nonsolar",
              region='ann_400_500', solar=False, error=True)
    clear()


    # XRB parameters from joint fit vs. bkg fit alone
    # are basically the same within error
    # -----------------------------------------------------------
    #stopwatch(bkg_only_fit, "results_spec/20160624_bkg_only_rerun",
    #          error=True)
    #clear()

    # Changing BACKSCAL ratio for 0551000201 MOS1 source region
    # has no practical effect on fits.
    # ---------------------------------------------------------
    #stopwatch(joint_src_bkg_fit, "results_spec/20160624_src_bkg_hack_eq_one_rerun",
    #          backscal_ratio_hack=1, error=True)
    #clear()






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

