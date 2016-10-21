#!/usr/local/bin/python
"""
Run fits.  Loaded in an interactive session, allows one to load data, fit,
compute parameter errors, etc.  Must be run in a sasinit-sourced environment

Code is tightly coupled to "g309_models.py", and changes to pipeline will
require edits to both scripts.

USAGE (drop the user into a nice interactive session with necessary modules):

    from g309_fits import *
    prep_xs(with_xs=True, statmethod='pgstat')
    ...
"""

from __future__ import division

from subprocess import call
from datetime import datetime
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
    """Dump plot data for ALL spectra using iplot wdata command, with
    all additive components groups.
    Note that a plot command is invoked in the process.
    Output
        QDP file at fname
    """
    old_add = xs.Plot.add
    xs.Plot.add = True  # Dump additive components within each model
    xs.Plot.addCommand("wdata " + fname)

    xs.Plot("ldata")

    xs.Plot.delCommand(len(xs.Plot.commands))
    xs.Plot.add = old_add


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
    """Reset XSPEC session (unload all data and models)"""
    xs.AllData.clear()
    xs.AllModels.clear()


def stopwatch(function, *args, **kwargs):
    """Time a function call, printing start/stop times to console after the
    function halts (after Exceptions as well)"""
    started = datetime.now()
    try:
        ret = function(*args, **kwargs)
    finally:
        stopped = datetime.now()
        # use str(...) instead of .func_name to work with
        # class initializers
        print str(function), "timing"
        print "  Started:", started
        print "  Stopped:", stopped
        print "  Elapsed:", stopped - started
    return ret


########################
# Customized fit setup #
########################

def prep_xs(with_xs=False, statMethod='pgstat'):
    """Apply standard XSPEC settings for G309"""

    xs.Xset.abund = "wilm"
    xs.Xset.xsect = "vern"
    xs.AllModels.lmod("absmodel", dirPath=os.environ['XMM_PATH'] + "/../absmodel")
    xs.AllModels.lmod("srcutlog", dirPath=os.environ['XMM_PATH'] + "/../srcutlog")

    xs.Fit.query = "yes"
    #xs.Fit.method = "leven delay"
    xs.Xset.parallel.leven = 4  # could set using nproc command
    xs.Xset.parallel.error = 4

    if statMethod not in ['pgstat', 'chi']:
        raise Exception("Invalid statmethod requested")
    xs.Fit.statMethod = statMethod

    if with_xs:
        xs.Plot.device = "/xs"
    xs.Plot.xAxis = "keV"
    xs.Plot.xLog = True
    xs.Plot.yLog = True
    xs.Plot.addCommand("rescale y 1e-5 3")  # may need to twiddle
    if statMethod == 'pgstat':
        xs.Plot.setRebin(minSig=5, maxBins=50)


def set_energy_range(all_extrs):
    """Set up fit (range ignores, PN power law setup, renorm)
    These are specific ALWAYS-ON tweaks or fixes, typically determined after
    running some fits...
    """
    for extr in all_extrs:
        if extr.instr in ["mos1", "mos2", "mosmerge"]:
            extr.spec.ignore("**-0.3, 11.0-**")
        elif extr.instr == "pn":
            extr.spec.ignore("**-0.4, 11.0-**")
        else:
            raise Exception("Invalid instrument: got {}".format(extr.instr))

def error_str(model, comp, par_names):
    """Construct an error string"""
    pars = [comp.__getattribute__(par_name) for par_name in par_names]
    par_nums = ["{:d}".format(xs_utils.par_num(model, par)) for par in pars]
    err_str = model.name + ":" + ",".join(par_nums)
    return err_str

def augment_error_str(err_str, model, comp, par_names):
    """Append more stuff to an error string
    WARNING: model must be the same as for the original error string.

    This provides a crude mechanism to construct error strings for different
    components in a given model
    """
    assert model.name == err_str.split(':')[0]
    for p_name in par_names:
        par = comp.__getattribute__(p_name)
        # Does NOT modify string in calling scope
        err_str = err_str + ",{:d}".format(xs_utils.par_num(model, par))
    return err_str

def error_str_all_free(model):
    """Construct error string for all free and unlinked parameters in an
    XSPEC model
    """
    # Alternative: we could just write 1--len(model.nParameters)
    # but this tends to generate warnings

    err_str = model.name + ":"

    for par in xs_utils.get_all_pars(model):
        if not par.frozen and par.link == '':
            err_str += ",{:d}".format(xs_utils.par_num(model, par))
    err_str = err_str.replace(":,", ":")

    return err_str

############################
# Customized fit execution #
############################

def src_powerlaw_xrbfree(output, error=False):
    """Fit integrated source w/ vnei+powerlaw, XRB free"""

    out = g309.load_data_and_models(['src', 'bkg'], snr_model='vnei+powerlaw')
    set_energy_range(out['src'])
    set_energy_range(out['bkg'])
    xs.AllData.ignore('bad')

    # Reset XRB to "typical" values, do NOT vary yet
    xrb = xs.AllModels(1, 'xrb')
    xrb.setPars({xrb.apec.kT.index : "0.1, , 0, 0, 0.5, 1"},  # Unabsorped apec (local bubble)
                {xrb.tbnew_gas.nH.index : "1, , 0.01, 0.1, 5, 10"},  # Galactic absorption
                {xrb.apec_6.kT.index : "0.5, , 0, 0, 2, 4"},  # Absorbed apec (galactic halo)
                {xrb.apec.norm.index : 1e-3},
                {xrb.apec_6.norm.index : 1e-3} )
    xrb.apec.kT.frozen = True
    xrb.tbnew_gas.nH.frozen = True
    xrb.apec_6.kT.frozen = True
    xrb.apec.norm.frozen = True
    xrb.apec_6.norm.frozen = True

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
    xrb.apec_6.kT.frozen = False
    xrb.apec.norm.frozen = False
    xrb.apec_6.norm.frozen = False
    xs.Fit.perform()
    xs.Plot("ld delch")

    if error:
        xs.Fit.error("snr_src:21,22,2,4,12,13,18,20")

        xs.Fit.error("xrb:{:d},{:d},{:d}".format(
            xs_utils.par_num(xrb, xrb.apec.kT),
            xs_utils.par_num(xrb, xrb.tbnew_gas.nH),
            xs_utils.par_num(xrb, xrb.apec_6.kT)))

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

    out = g309.load_data_and_models([region], snr_model='vnei+srcutlog')
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

    out = g309.load_data_and_models([region], snr_model='vnei')
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

    out = g309.load_data_and_models([region], snr_model='vnei+powerlaw')
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



def joint_src_bkg_fit(output, free_elements=None, error=False,
                      error_rerun=False, backscal_ratio_hack=None,
                      tau_scan=True, tau_freeze=None, **kwargs):
    """
    Fit source + bkg regions, allowing XRB to float
    backscal_ratio_hack = arbitrary adjustment to 0551000201 MOS1S001
        source region backscal ratio.
        This was the smallest geometric w.r.t. 0087940201 MOS1 (ratio 0.88).
        Because the missing area (missing chip #6) sampled little of the
        remnant, I thought that this ratio might underestimate the sampled
        remnant flux, so I arbitrary changed the BACKSCAL ratio to 0.95 in some
        fits.
        Retain this parameter as a way to explore fit systematics.

    Arguments
        output: file stem string
        snr_model: snr model expression (and parameter setup) to use
        free_elements: (default) is [Si,S]
            if [], use solar abundances
        error: perform single error run
        backscal_ratio_hack: see above
        tau_scan: steppar over plausible Tau values to ensure convergence to "correct" best fit
        tau_freeze: freeze ionization timescale to provided value
        kwargs - passed to g309_models.load_data_and_models
            (suffix, mosmerge, marfrmf)
    """
    if free_elements is None:
        free_elements = ['Si', 'S']

    out = g309.load_data_and_models(["src", "bkg"], **kwargs)
    set_energy_range(out['src'])
    set_energy_range(out['bkg'])
    xs.AllData.ignore("bad")

    if backscal_ratio_hack:
        xs.AllModels(4,'snr_src').constant.factor = backscal_ratio_hack

    xrb = xs.AllModels(1, 'xrb')
    snr = xs.AllModels(1, 'snr_src')

    # Reset XRB to "typical" values, do NOT vary yet
    xrb.setPars({xrb.apec.kT.index : "0.1, , 0, 0, 0.5, 1"},  # Unabsorped apec (local bubble)
                {xrb.tbnew_gas.nH.index : "1, , 0.1, 0.5, 5, 10"},  # Extragalactic absorption
                {xrb.tbnew_gas_5.nH.index : "1, , 0.1, 0.5, 5, 10"},  # Ridge absorption
                {xrb.apec_6.kT.index : "0.5, , 0, 0, 2, 4"},  # Galactic ridge (+ minimal halo maybe)
                {xrb.apec.norm.index : 1e-3},
                {xrb.apec_6.norm.index : 1e-3} )
    xrb.apec.kT.frozen = True
    xrb.tbnew_gas.nH.frozen = True
    xrb.tbnew_gas_5.nH.frozen = True
    xrb.apec_6.kT.frozen = True
    xrb.apec.norm.frozen = True
    xrb.apec_6.norm.frozen = True

    xs.Fit.renorm()

    # Let SNR model vary
    if 'snr_model' not in kwargs or kwargs['snr_model'] == 'vnei':

        snr.tbnew_gas.nH.frozen=False
        snr.vnei.kT.frozen=False
        if tau_freeze:
            snr.vnei.Tau.frozen = tau_freeze
            snr.vnei.Tau.frozen = True
        else:
            snr.vnei.Tau.frozen = False

        for elem in free_elements:
            comp = snr.vnei.__getattribute__(elem)
            comp.frozen = False

    elif kwargs['snr_model'] == 'vpshock':

        snr.tbnew_gas.nH.frozen=False
        snr.vpshock.kT.frozen=False
        snr.vpshock.Tau_l.frozen=False
        if tau_freeze:
            snr.vpshock.Tau_u.frozen = tau_freeze
            snr.vpshock.Tau_u.frozen = True
        else:
            snr.vpshock.Tau_u.frozen = False

        for elem in free_elements:
            comp = snr.vpshock.__getattribute__(elem)
            comp.frozen = False

    elif kwargs['snr_model'] == 'vnei+nei':

        snr.tbnew_gas.nH.frozen=False
        snr.vnei.kT.frozen=False
        if tau_freeze:
            snr.vnei.Tau.frozen = tau_freeze
            snr.vnei.Tau.frozen = True
        else:
            snr.vnei.Tau.frozen = False

        snr.nei.kT.frozen=False
        snr.nei.Tau.frozen=False
        xs.Fit.perform()

        # Reserve element variation to second step fit
        for elem in free_elements:
            comp = snr.vnei.__getattribute__(elem)
            comp.frozen = False

    xs.Fit.perform()

    # XRB is not as well constrained as SNR, and fits w/ XRB free
    # (and SNR at default vnei values) tend to run away
    xrb.apec.kT.frozen = False
    xrb.tbnew_gas.nH.frozen = False  # tbnew_gas * powerlaw
    xrb.tbnew_gas_5.nH.frozen = False  # tbnew_gas_5 * apec_6
    xrb.apec_6.kT.frozen = False
    xrb.apec.norm.frozen = False
    xrb.apec_6.norm.frozen = False
    xs.Fit.perform()

    # SNR Tau is not well constrained in general fits.
    # Either converges to ~2-3e10, or runs to 5e13
    # Grid over (roughly): [1e9, 2e9, 5e9, 1e10, 2e10, 5e10, ... 1e13]
    if tau_scan:
        if 'snr_model' not in kwargs or kwargs['snr_model'] in ['vnei', 'vnei+nei']:
            xs.Fit.steppar("log snr_src:{:d} 1e9 1e13 13".format(
                                xs_utils.par_num(snr, snr.vnei.Tau)))
        elif kwargs['snr_model'] == 'vpshock':
            # Since Tau_u is constrained to be greater than Tau_l
            # this ensures that both Tau_u and Tau_l traverse a range of values
            xs.Fit.steppar("log snr_src:{:d} 1e9 1e13 13".format(
                                xs_utils.par_num(snr, snr.vpshock.Tau_u)))
        else:
            raise Exception("Invalid SNR MODEL not configured for tau scan")

    if error:

        xs.Xset.openLog(output + "_error.log")
        print "Error run start:", datetime.now()

        # Perform XRB error run first because a new best fit is [typically]
        # found in this step
        # Note: error commands cannot be combined; XSPEC only looks at
        # parameter numbers after the first "<model name>: ...",
        # so error command reruns must be done manually
        xs.Fit.error(error_str_all_free(xrb))
        xs.Fit.error(error_str_all_free(snr))

        if error_rerun:
            print "Second error run:", datetime.now()
            xs.Fit.error(error_str_all_free(xrb))
            xs.Fit.error(error_str_all_free(snr))

        print "Error run stop:", datetime.now()
        xs.Xset.closeLog()

    products(output)
    print_model(snr, output + "_snr_src.txt")
    print_model(xrb, output + "_xrb.txt")



def annulus_fit(output, error=False, error_rerun=False,
                free_center_elements=None, free_all_elements=None,
                four_ann=False, **kwargs):
    """
    Fit radial annuli simultaneously

    Arguments:
        output = output products file stem
        error = run error commands?
        error_rerun = run error commands 2nd time?
        four_ann = fit only 4 instead of 5 annuli?
        free_all_elements = (case-sensitive) elements to free in all annuli.
            Element names much match XSPEC parameter names.
            Default: Si, S free
        free_center_elements = (case-sensitive) additional elements to free in
            central circle (0-100 arcsec)
            Element names much match XSPEC parameter names.
        kwargs - passed to g309_models.load_data_and_models
            (suffix, mosmerge, marfrmf)
    Output: n/a
        loads of stuff dumped to output*
        XSPEC session left in fitted state
    """

    if free_center_elements is None:
        free_center_elements = []
    if free_all_elements is None:
        free_all_elements = ['Si', 'S']

    regs = ["ann_000_100", "ann_100_200", "ann_200_300", "ann_300_400", "ann_400_500"]
    if four_ann:
        regs = ["ann_000_100", "ann_100_200", "ann_200_300", "ann_300_400"]

    out = g309.load_data_and_models(regs, snr_model='vnei', **kwargs)
    for reg in regs:
        set_energy_range(out[reg])
    xs.AllData.ignore("bad")

    # Link nH across annuli
    # Each region has n spectra (n exposures)
    # [0] gets 1st of n ExtractedSpectra objects
    # .models['...'] gets corresponding 1st of n XSPEC models
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
        for elem in free_all_elements:
            comp = ring.vnei.__getattribute__(elem)
            comp.frozen = False

    for elem in free_center_elements:
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
            print "Running", reg, "errors:", datetime.now()
            xs.Fit.error(error_str_all_free(ring))
            print reg, "errors complete:", datetime.now()  # Will not appear in error log

        if error_rerun:
            print "Second error run:", datetime.now()
            for reg, ring in zip(regs, rings):
                print "Running", reg, "errors:", datetime.now()
                xs.Fit.error(error_str_all_free(ring))
                print reg, "errors complete:", datetime.now()  # Will not appear in error log

        xs.Xset.closeLog()
        print "Error runs complete:", datetime.now()

    # Output products
    products(output)

    for ring in rings:
        model_log = output + "_{}.txt".format(ring.name)
        print_model(ring, model_log)



def bkg_only_fit(output, steppar=False, error=False):
    """
    Fit bkg region alone to XRB model
    """
    out = g309.load_data_and_models(["bkg"], snr_model=None)
    set_energy_range(out['bkg'])
    xs.AllData.ignore("bad")

    # Reset XRB to "typical" values
    # As usual, fit is pretty sensitive to initial values
    # (initial kT values that are too small drive fit to a bad local minimum)
    xrb = xs.AllModels(1, 'xrb')
    xrb.setPars({xrb.apec.kT.index : "0.2, , 0, 0, 0.5, 1"},  # Unabsorped apec (local bubble)
                {xrb.tbnew_gas.nH.index : "1.5, , 0.01, 0.1, 5, 10"},  # Galactic absorption
                {xrb.apec_6.kT.index : "0.7, , 0, 0, 2, 4"},  # Absorbed apec (galactic halo)
                {xrb.apec.norm.index : 1e-3},
                {xrb.apec_6.norm.index : 1e-3} )
    xrb.apec.kT.frozen = False
    xrb.tbnew_gas.nH.frozen = False
    xrb.apec_6.kT.frozen = False
    xrb.apec.norm.frozen = False
    xrb.apec_6.norm.frozen = False

    xs.Fit.perform()
    if xs.Plot.device == "/xs":
        xs.Plot("ldata delchi")

    if steppar:
        xs.Fit.steppar("xrb:{:d} 0.1 0.5 20".format(xs_utils.par_num(xrb, xrb.apec.kT)))
        xs.Fit.steppar("xrb:{:d} 0.4 0.8 20".format(xs_utils.par_num(xrb, xrb.apec_6.kT)))
        if xs.Plot.device == "/xs":
            xs.Plot("ldata delchi")

    if error:

        xs.Xset.openLog(output + "_error.log")

        print "Error run started:", datetime.now()
        xs.Fit.error("xrb:{:d}".format(xs_utils.par_num(xrb, xrb.apec.kT))
                  + " xrb:{:d}".format(xs_utils.par_num(xrb, xrb.apec.norm))
                  + " xrb:{:d}".format(xs_utils.par_num(xrb, xrb.tbnew_gas.nH))
                  + " xrb:{:d}".format(xs_utils.par_num(xrb, xrb.apec_6.kT))
                  + " xrb:{:d}".format(xs_utils.par_num(xrb, xrb.apec_6.norm)))

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

    # N.B. if you actually run this code, insert clear() between all calls.
    # but best not to run these fits sequentially...

    # Integrated source fits - standard setup
    # ---------------------------------------
    prep_xs(with_xs=True, statMethod='pgstat')
    stopwatch(joint_src_bkg_fit, "results_spec/20161015_src_bkg_grp01_pgstat_mosmerge",
              error=True, error_rerun=True, mosmerge=True, suffix='grp01')
    # Time: 15.2 hrs on statler

    prep_xs(with_xs=True, statMethod='chi')
    stopwatch(joint_src_bkg_fit, "results_spec/20161015_src_bkg_grp50_chi_mosmerge",
              error=True, error_rerun=True, mosmerge=True, suffix='grp50')
    # Time: 6.0 hrs on statler

    prep_xs(with_xs=True, statMethod='pgstat')
    stopwatch(joint_src_bkg_fit, "results_spec/20161015_src_bkg_grp01_pgstat_nomerge",
              error=True, error_rerun=True, mosmerge=False, suffix='grp01')
    # Time: 18.75 hrs on statler

    prep_xs(with_xs=True, statMethod='pgstat')
    stopwatch(joint_src_bkg_fit, "results_spec/20161015_src_bkg_grp50_chi_nomerge",
              error=True, error_rerun=True, mosmerge=False, suffix='grp50')
    # Time: (?) hrs on cooper (running now)

    # Reset stat method - to be safe
    prep_xs(with_xs=True, statMethod='pgstat')

    # Integrated source fits - varied abundances
    # ------------------------------------------
    # Note: snr_model='vnei', mosmerge=True, suffix='grp01' are current
    # (October 2016) defaults

    # Conservative run: just get clear emission lines
    stopwatch(joint_src_bkg_fit, "results_spec/20161015_src_bkg_mg",
              free_elements=['Mg', 'Si', 'S'],
              error=True, error_rerun=True)
    # Time: 10.0 hrs on cooper
    # Time without error: ? hours

    # Conservative run: just get clear emission lines + possible Ar, Ca bumps
    # around 3-4 keV
    prep_xs(with_xs=True, statMethod='pgstat')
    stopwatch(joint_src_bkg_fit, "results_spec/20161015_src_bkg_mg-ar-ca",
              free_elements=['Mg', 'Si', 'S', 'Ar', 'Ca'],
              error=True, error_rerun=True)
    # Time: 37.4 hrs (~1.5 days) on cooper

    ##### OLD, NOT YET UPDATED RUNS #####

    stopwatch(joint_src_bkg_fit, "results_spec/20160726_src_bkg_o-ne-mg-fe",
              free_elements=['O', 'Ne', 'Mg', 'Si', 'S', 'Fe'], error=True,
              error_rerun=True)
    # Time: 4.5 hrs on statler (one error run only)
    # Time: 7.5 hrs on statler (with error rerun)

    stopwatch(joint_src_bkg_fit, "results_spec/20160726_src_bkg_o-ne-mg-ar-ca-fe-ni",
            free_elements=['O', 'Ne', 'Mg', 'Si', 'S', 'Ar', 'Ca', 'Fe', 'Ni'],
            error=True, error_rerun=True)
    # Time: 9.5 hrs on statler

    stopwatch(joint_src_bkg_fit, "results_spec/20160803_src_bkg_o-ne-mg-ar-ca-fe",
            free_elements=['O', 'Ne', 'Mg', 'Si', 'S', 'Ar', 'Ca', 'Fe'],
            error=True, error_rerun=True)
    # Time: ... on statler

    stopwatch(joint_src_bkg_fit, "results_spec/20160728_src_bkg_o-mg", free_elements=['O', 'Mg', 'Si', 'S'], error=True, error_rerun=True)
    # Time: 2.8 hrs on statler
    stopwatch(joint_src_bkg_fit, "results_spec/20160726_src_bkg_ne-mg", free_elements=['Ne', 'Mg', 'Si', 'S'], error=True, error_rerun=True)
    # Time: 2.9 hrs on statler
    stopwatch(joint_src_bkg_fit, "results_spec/20160728_src_bkg_mg-fe", free_elements=['Mg', 'Si', 'S', 'Fe'], error=True, error_rerun=True)
    # Time: 4.1 hrs on statler
    stopwatch(joint_src_bkg_fit, "results_spec/20160728_src_bkg_o-ne-mg", free_elements=['O', 'Ne', 'Mg', 'Si', 'S'], error=True, error_rerun=True)
    # Time: 4.1 hrs on cooper

    # Duplicate Rakowski+ fit
    stopwatch(joint_src_bkg_fit, "results_spec/20160729_src_bkg_ne-mg-ar-ca-fe", free_elements=['Ne', 'Mg', 'Si', 'S', 'Ar', 'Ca', 'Fe'], error=True, error_rerun=True)
    # Time: 2.6 hrs on cooper (only 1 error run; rerun not needed. interrupted)


    stopwatch(joint_src_bkg_fit, "results_spec/20160726_src_bkg_with-ism-nei", snr_model='vnei+nei', error=True, error_rerun=True)
    # Time: 6.1 hrs on treble
    stopwatch(joint_src_bkg_fit, "results_spec/20160802_src_bkg_o-ne-mg-fe_with-ism-nei", snr_model='vnei+nei', free_elements=['O', 'Ne', 'Mg', 'S', 'Si', 'Fe'], error=True, error_rerun=True)
    # Time: ... on treble
    stopwatch(joint_src_bkg_fit, "results_spec/20160726_src_bkg_vpshock", snr_model='vpshock', error=True, error_rerun=True)
    # Time: 5.9 hrs on treble

    # Fits with Tau = 1e11 fixed
    stopwatch(joint_src_bkg_fit, "results_spec/20160802_src_bkg_tau-1e11", tau_freeze=1e11, error=True, error_rerun=True)
    # Time: 2.9 hrs on statler
    stopwatch(joint_src_bkg_fit, "results_spec/20160802_src_bkg_o-ne-mg-fe_tau-1e11", free_elements=['O', 'Ne', 'Mg', 'Si', 'S', 'Fe'], tau_freeze=1e11, error=True, error_rerun=True)
    # Time: ... on statler




    # Annulus fits, all varieties
    # ---------------------------

    # FIVE ANNULUS FITS

    stopwatch(annulus_fit, "results_spec/20161019_fiveann", error=True, error_rerun=True)
#    # Rerun error command for center only
#    ring = xs.AllModels(1,'snr_ann_000_100')
#    xs.Xset.openLog("results_spec/20160701_fiveann" + "_error_rerun_manual.log")
#    stopwatch(xs.Fit.error, "snr_ann_000_100:{:d},{:d},{:d},{:d}".format(
#                                    xs_utils.par_num(ring, ring.vnei.kT),
#                                    xs_utils.par_num(ring, ring.vnei.Tau),
#                                    xs_utils.par_num(ring, ring.vnei.Si),
#                                    xs_utils.par_num(ring, ring.vnei.S)))
#    xs.Xset.closeLog()
#    print_model(ring, "results_spec/20160701_fiveann_snr_ann_000_100.txt")
    # Time: 2 days, 17 hrs on treble
    #   + extra 5 hours for center error rerun
    # (would roughly double to 4 days with full error_rerun)

    stopwatch(annulus_fit, "results_spec/2016xxxx_fiveann_center-mg-free",
              error=True, error_rerun=True, free_center_elements=['Mg'])
    # WARNING - needs to be regenerated.

    stopwatch(annulus_fit, "results_spec/20160701_fiveann_center-mg-fe-free", free_center_elements=["Mg", "Fe"], error=True, error_rerun=True)
    # Time: 6 days, 10 hrs (!) on treble

    # FOUR ANNULUS FITS

    stopwatch(annulus_fit, "results_spec/20160725_fourann", four_ann=True, error=True, error_rerun=True)
    # Time: 1 day, 19.5 hrs on treble (with error rerun)
    # Time: 2 days, 7 hrs on cooper (with error rerun, incl norm errors)

    stopwatch(annulus_fit, "results_spec/20160725_fourann_all-mg-free", four_ann=True, free_all_elements=["Mg", "Si", "S"], error=True, error_rerun=True)
    # Time: 2 days, 17 hrs on cooper (with error rerun & norm errors)
    stopwatch(annulus_fit, "results_spec/20160802_fourann_o-ne-mg-fe-free", four_ann=True, free_all_elements=['O', 'Ne', 'Mg', 'Si', 'S', 'Fe'], error=True, error_rerun=True)
    # Time: ... on statler
    stopwatch(annulus_fit, "results_spec/20160803_fourann_o-ne-mg-ar-ca-fe-free", four_ann=True, free_all_elements=['O', 'Ne', 'Mg', 'Si', 'S', 'Ar', 'Ca', 'Fe'], error=True, error_rerun=True)
    # Time: ... on statler

    stopwatch(annulus_fit, "results_spec/20160725_fourann_center-mg-free", four_ann=True, free_center_elements=["Mg"], error=True, error_rerun=True)
    # Time: 2 days, 14 hrs on treble (37 minutes without error run)
    # Time: ... on statler (running now)
    stopwatch(annulus_fit, "results_spec/20160708_fourann_center-mg-ne-free", four_ann=True, free_center_elements=["Mg", "Ne"], error=True, error_rerun=True)
    # Time: 2 days, 11 hrs on statler
    stopwatch(annulus_fit, "results_spec/20160708_fourann_center-mg-o-free", four_ann=True, free_center_elements=["Mg", "O"], error=True, error_rerun=True)
    # Time: 1 day, 17.5 hrs on statler
    stopwatch(annulus_fit, "results_spec/20160708_fourann_center-mg-o-ne-free", four_ann=True, free_center_elements=["Mg", "O", "Ne"], error=True, error_rerun=True)
    # Time: 3 days, 2 hrs on cooper
    stopwatch(annulus_fit, "results_spec/20160708_fourann_center-mg-fe-free", four_ann=True, free_center_elements=["Mg", "Fe"], error=True, error_rerun=True)
    # Time: 1 day, 23.75 hrs on cooper
    stopwatch(annulus_fit, "results_spec/20160712_fourann_center-mg-o-fe-free", four_ann=True, free_center_elements=["Mg", "O", "Fe"], error=True, error_rerun=True)
    # Time: 2 days, 18.5 hrs on cooper
    # Time without error runs: 34 minutes on treble



    # Nonthermal component source model fits
    # --------------------------------------
    # (n.b. some are out of date / run with old XRB parameters)

    stopwatch(src_powerlaw, "results_spec/20160630_src_powerlaw_solar",
              region='src', solar=True, error=True)

    stopwatch(src_powerlaw, "results_spec/20160630_src_powerlaw_nonsolar",
              region='src', solar=False, error=True)

    stopwatch(src_srcutlog, "results_spec/20160630_src_srcutlog_solar",
              region='src', solar=True, error=True)

    stopwatch(src_srcutlog, "results_spec/20160630_src_srcutlog_nonsolar",
              region='src', solar=False, error=True)

    stopwatch(src_srcutlog, "results_spec/20160630_ann-400-500_srcutlog_nonsolar",
              region='ann_400_500', solar=False, error=True)


    # XRB parameters from joint fit vs. bkg fit alone
    # are basically the same within error
    # -----------------------------------------------------------
    #stopwatch(bkg_only_fit, "results_spec/20160624_bkg_only_rerun",
    #          error=True)

    # Changing BACKSCAL ratio for 0551000201 MOS1 source region
    # has no practical effect on fits.
    # ---------------------------------------------------------
    #stopwatch(joint_src_bkg_fit, "results_spec/20160624_src_bkg_hack_eq_one_rerun",
    #          backscal_ratio_hack=1, error=True)


    # Sub region fits with varying nH values
    # --------------------------------------
    #regs = ["src_north_clump", "src_E_lobe", "src_SW_lobe", "src_SE_dark",
    #        "src_ridge", "src_SE_ridge_dark", "src_pre_ridge"]
    #nH_vals = [None, 1.5, 2.0, 2.5, 3.0]
    # ... TBD ...
