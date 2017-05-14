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


def single_fit(output, region='src', with_bkg=True, free_elements=None,
               error=False, error_rerun=False,
               tau_scan=False, tau_freeze=None, nH_freeze=None,
               snr_model='vnei', **kwargs):
    """Fit any region to an arbitrary remnant model, possibly fitting XRB with
    background region as well.

    Arguments
        output: file stem string
    Keyword arguments
        region: region spectrum to be fitted
        with_bkg: fit to X-ray background region (bkg) simultaneously
        snr_model: snr model expression (and parameter setup) to use
        free_elements: (default) is [Si,S]
            if [], use solar abundances
        error: perform single error run
        tau_scan: steppar over plausible Tau values to ensure convergence to "correct" best fit
        tau_freeze: freeze ionization timescale to provided value
        nH_freeze: freeze SNR absorption to provided value
        kwargs - passed to g309_models.load_data_and_models
            (suffix, mosmerge, marfrmf)
    """
    if free_elements is None:
        free_elements = ['Si', 'S']

    # Set up spectra and models in XSPEC
    if with_bkg:
        out = g309.load_data_and_models([region, 'bkg'], snr_model=snr_model, **kwargs)
        set_energy_range(out['bkg'])
    else:
        out = g309.load_data_and_models([region], snr_model=snr_model, **kwargs)

    set_energy_range(out[region])
    xs.AllData.ignore("bad")

    if snr_model == 'gauss':
        for extr in out[region]:
            extr.spec.ignore("**-5.0, 8.0-**")

    xrb = xs.AllModels(1, 'xrb')
    snr = xs.AllModels(1, 'snr_' + region)

    # Reset XRB to "typical" values, do NOT vary yet
    if with_bkg:
        xrb.setPars({xrb.apec.kT.index : "0.1, , 0, 0, 0.5, 1"},  # Unabsorped apec (local bubble)
                    {xrb.tbnew_gas.nH.index : "1, , 0.1, 0.5, 5, 10"},  # Extragalactic absorption
                    {xrb.tbnew_gas_5.nH.index : "1, , 0.1, 0.5, 5, 10"},  # Ridge absorption
                    {xrb.apec_6.kT.index : "0.5, , 0, 0, 2, 4"},  # Galactic ridge (+ minimal halo maybe)
                    {xrb.apec.norm.index : 1e-3},
                    {xrb.apec_6.norm.index : 1e-3} )
        xs_utils.freeze_model(xrb)
        # Try floating norms to help initial fit
        xrb.apec.norm.frozen = False
        xrb.apec_6.norm.frozen = False

        def thaw_bkg():
            for c in [xrb.apec.kT, xrb.tbnew_gas.nH, xrb.tbnew_gas_5.nH,
                      xrb.apec_6.kT]:
                c.frozen = False

    xs.Fit.renorm()

    # Let SNR model vary (NOTE: this assumes default to be vnei...)
    if snr_model.startswith('vnei'):

        xs_utils.freeze_model(snr)

        # Configure initial SNR parameters
        if nH_freeze:
            snr.tbnew_gas.nH = nH_freeze
        else:
            snr.tbnew_gas.nH.frozen=False

        snr.vnei.kT.frozen=False
        snr.vnei.norm.frozen=False

        if tau_freeze:
            snr.vnei.Tau = tau_freeze
        else:
            snr.vnei.Tau.frozen = False

        for elem in free_elements:
            comp = snr.vnei.__getattribute__(elem)
            comp.frozen = False

        if snr_model == 'vnei+nei':
            snr.nei.norm = 0
        elif snr_model == 'vnei+powerlaw':
            snr.powerlaw.PhoIndex = 2
            snr.powerlaw.norm = 0  # zero
        elif snr_model == 'vnei+srcutlog':
            # srcutlog, w/ one free parameter, behaves better than powerlaw
            snr.srcutlog.__getattribute__('break').frozen = False

        # Run initial fit
        if with_bkg:
            # Fit has enormous trouble converging
            if tau_freeze:
                thaw_bkg()
                xs.Fit.perform()
            else:
                snr.vnei.Tau = 2e10
                snr.vnei.Tau.frozen = True
                xs.Fit.perform()

                thaw_bkg()
                xs.Fit.perform()
                snr.vnei.Tau.frozen = False
                xs.Fit.perform()

        else:
            xs.Fit.perform()

        # Post-processing on initial fit

        if tau_scan:
            xs.Fit.steppar("log {:s}:{:d} 1e9 5e13 15".format(snr.name,
                                xs_utils.par_num(snr, snr.vnei.Tau)))

        if snr_model == 'vnei+nei':
            snr.nei.kT.frozen = False
            snr.nei.Tau.frozen = False
            snr.nei.norm.frozen = False
            xs.Fit.perform()
        elif snr_model == 'vnei+powerlaw':

            snr.powerlaw.PhoIndex = 2
            snr.powerlaw.norm = 0  # zero

            snr.powerlaw.norm.frozen = False
            xs.Fit.perform()

            snr.powerlaw.PhoIndex.frozen = False
            xs.Fit.perform()

            # Because powerlaw norm generally runs to zero, traverse moderately
            # strong power law cases
            xs.Fit.steppar("log {:s}:{:d} 1e-5 1e-2 30".format(snr.name,
                                xs_utils.par_num(snr, snr.powerlaw.norm)))

        elif snr_model == 'vnei+srcutlog':

            # Check reasonably high break values: 15 -- 17
            xs.Fit.steppar("{:s}:{:d} 15 17 20".format(snr.name,
                    xs_utils.par_num(snr, snr.srcutlog.__getattribute__('break'))
                    ))

    elif snr_model == 'vpshock':

        xs_utils.freeze_model(snr)

        snr.tbnew_gas.nH.frozen=False
        snr.vpshock.kT.frozen=False
        snr.vpshock.norm.frozen=False
        if tau_freeze:
            raise Exception("ERROR: vpshock not configured for fixed Tau")

        for elem in free_elements:
            comp = snr.vpshock.__getattribute__(elem)
            comp.frozen = False

        # vpshock fits are very ill behaved, must coerce into best fit
        snr.vpshock.Tau_l = 1e8
        snr.vpshock.Tau_u = 5e10
        xs.Fit.perform()

        if with_bkg:
            thaw_bkg()
            xs.Fit.perform()

        snr.vpshock.Tau_l.frozen = False
        snr.vpshock.Tau_u.frozen = False
        xs.Fit.perform()

        if tau_scan:
            # Since Tau_u is constrained to be greater than Tau_l (?) this
            # should ensure that both Tau_u and Tau_l traverse a range of
            # values.  But I haven't checked it yet...
            xs.Fit.steppar("log {:s}:{:d} 1e9 5e13 15".format(snr.name,
                                xs_utils.par_num(snr, snr.vpshock.Tau_u)))

    elif snr_model == 'gauss':

        # Not supported!  Not at all constrained . . .
        assert not with_bkg

        xs_utils.freeze_model(snr)

        # Coupling between code is too tight, abstractions keep leaking.
        # Because models must be addressed by NUMBER in XSPEC
        # commands to tweak model parameters necessarily break
        # abstraction interface between "load models" and "fit models"
        # Possible solutions: (1) give up and let interfaces merge
        # (monolithic "g309_models_fits"), or . . . (2) stop whining
        if 'mosmerge' not in kwargs or kwargs['mosmerge']:
            instr_1 = xs.AllModels(1, 'instr_1')
            #instr_2 = xs.AllModels(2, 'instr_2')  # Let PN instr lines fit
            instr_3 = xs.AllModels(3, 'instr_3')
            for instr in [instr_1, instr_3]:
                # Must update parameter lower limits
                instr.constant.factor.values = "0, , 0, 0, , "
                instr.constant.factor.frozen = True
        else:  # No MOS merging
            instr_1 = xs.AllModels(1, 'instr_1')
            instr_2 = xs.AllModels(2, 'instr_2')
            #instr_3 = xs.AllModels(3, 'instr_3')  # Let PN instr lines fit
            instr_4 = xs.AllModels(4, 'instr_4')
            instr_5 = xs.AllModels(5, 'instr_5')
            for instr in [instr_1, instr_2, instr_4, instr_5]:
                # Must update parameter lower limits
                instr.constant.factor.values = "0, , 0, 0, , "
                instr.constant.factor.frozen = True

        snr.tbnew_gas.nH = 0
        snr.tbnew_gas.nH.frozen = True

        # LineE: lower/upper bounds set from Yamaguchi+ 2014
        # Sigma: prevent line from over-widening to fit as "constant" addition
        # norm: no bounds
        snr.setPars({snr.gaussian.LineE.index : "6.55, , 6.2, 6.3, 6.8, 6.9",
                     snr.gaussian.Sigma.index : "0.1, , 0, 0, 0.2, 0.5"} )
        snr.gaussian.LineE.frozen=False
        snr.gaussian.Sigma.frozen=False
        snr.gaussian.norm.frozen=False

        xs.Fit.perform()

    else:
        raise Exception("Invalid SNR model - please add branch")


    # Compute standard 90% errors
    if error:

        xs.Xset.openLog(output + "_error.log")

        if with_bkg:
            xs.Fit.error(error_str_all_free(xrb))
        xs.Fit.error(error_str_all_free(snr))

        if error_rerun:
            if with_bkg:
                xs.Fit.error(error_str_all_free(xrb))
            xs.Fit.error(error_str_all_free(snr))
        xs.Xset.closeLog()

    # Dump standard outputs
    products(output)
    print_model(snr, output + "_{:s}.txt".format(snr.name))
    if with_bkg:
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
    # single_fit(output, error=False)
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
    stopwatch(single_fit, "results_spec/20161015_src_bkg_grp01_pgstat_mosmerge",
              error=True, error_rerun=True, mosmerge=True, suffix='grp01')
    # Time: 15.2 hrs on statler

    prep_xs(with_xs=True, statMethod='chi')
    stopwatch(single_fit, "results_spec/20161015_src_bkg_grp50_chi_mosmerge",
              error=True, error_rerun=True, mosmerge=True, suffix='grp50')
    # Time: 6.0 hrs on statler

    prep_xs(with_xs=True, statMethod='pgstat')
    stopwatch(single_fit, "results_spec/20161015_src_bkg_grp01_pgstat_nomerge",
              error=True, error_rerun=True, mosmerge=False, suffix='grp01')
    # Time: 18.75 hrs on statler

    prep_xs(with_xs=True, statMethod='pgstat')
    stopwatch(single_fit, "results_spec/20161015_src_bkg_grp50_chi_nomerge",
              error=True, error_rerun=True, mosmerge=False, suffix='grp50')
    # Time: (?) hrs on cooper (running now)

    # Reset stat method - to be safe
    prep_xs(with_xs=True, statMethod='pgstat')

    # Integrated source fits - varied abundances
    # ------------------------------------------
    # Note: snr_model='vnei', mosmerge=True, suffix='grp01' are current
    # (October 2016) defaults

    # Solar abundances just as a reference fit
    stopwatch(single_fit, "results_spec/20161028_src_bkg_solar", with_bkg=True,
              free_elements=[], tau_scan=True, sp_bknpower=False,
              error=True, error_rerun=True)

    # Conservative run: just get clear emission lines
    stopwatch(single_fit, "results_spec/20161015_src_bkg_mg",
              free_elements=['Mg', 'Si', 'S'],
              error=True, error_rerun=True)
    # Time: 10.0 hrs on cooper

    # Conservative run: just get clear emission lines + possible Ar, Ca bumps
    # around 3-4 keV
    prep_xs(with_xs=True, statMethod='pgstat')
    stopwatch(single_fit, "results_spec/20161015_src_bkg_mg-ar-ca",
              free_elements=['Mg', 'Si', 'S', 'Ar', 'Ca'],
              error=True, error_rerun=True)
    # Time: 37.4 hrs (~1.5 days) on cooper

    # Varied abundances (three knobs: {O & Ne}, {Fe}, {Ar & Ca})

    stopwatch(single_fit, "results_spec/20161028_src_bkg_mg-si-s-fe",
              with_bkg=True, free_elements=['Mg', 'Si', 'S', 'Fe'],
              tau_scan=True, sp_bknpower=False, error=True, error_rerun=True)

    stopwatch(single_fit, "results_spec/20161026_src_bkg_o-ne-mg-si-s-fe",
              with_bkg=True, free_elements=['O', 'Ne', 'Mg', 'Si', 'S', 'Fe'],
              tau_scan=False, sp_bknpower=False, error=True, error_rerun=True)
        # XRB xgal nH ran to 0.1, had to manually tweak and re-run errors

    stopwatch(single_fit, "results_spec/20161028_src_bkg_o-ne-mg-si-s-ar-ca-fe",
              with_bkg=True, free_elements=['O', 'Ne', 'Mg', 'Si', 'S', 'Ar', 'Ca', 'Fe'],
              tau_scan=False, sp_bknpower=False, error=True, error_rerun=True)
        # Fails horribly - do not do this.  Must do by hand or modify element freeing routine.

    # Integrated source fits - modify/add components
    # ----------------------------------------------

    stopwatch(single_fit, "results_spec/20161028_src_bkg_o-ne-mg-si-s-fe_nH-0.7_NOERR", with_bkg=True, free_elements=['O', 'Ne', 'Mg', 'Si', 'S', 'Fe'], tau_scan=False, nH_freeze=0.7, sp_bknpower=False, error=False, error_rerun=False)

    stopwatch(single_fit, "results_spec/20161031_src_bkg_o-ne-mg-si-s-fe_nH-0.867_NOERR", with_bkg=True, free_elements=['O', 'Ne', 'Mg', 'Si', 'S', 'Fe'], tau_scan=False, nH_freeze=0.867, sp_bknpower=False, error=False, error_rerun=False)

    # Fits with Tau = 1e11 fixed
    stopwatch(single_fit, "results_spec/20161028_src_bkg_mg-si-s_tau-5e13_NOERR", with_bkg=True, free_elements=['Mg', 'Si', 'S'], tau_scan=False, tau_freeze=5e13, sp_bknpower=False, error=False, error_rerun=False)
    # Time: ... on ...


    # Annulus fits, all varieties
    # ---------------------------

    stopwatch(annulus_fit, "results_spec/20161019_fiveann", error=True,
              error_rerun=True)
    # 2 days, 4.6 hrs on statler (3.2 hrs without errors)
    stopwatch(annulus_fit, "results_spec/20161019_fiveann_mg", error=True,
              error_rerun=True, free_all_elements=['Mg', 'Si', 'S'])
    # 2 days, 20.8 hrs on statler (4.3 hrs without errors)

    # Four annulus fits

    stopwatch(annulus_fit, "results_spec/20161019_fourann", error=True,
              error_rerun=True, four_ann=True)
    # ? days...
    stopwatch(annulus_fit, "results_spec/20161019_fourann_mg", error=True,
              error_rerun=True, free_all_elements=['Mg', 'Si', 'S'], four_ann=True)
    # ~3? hr without error
    # 1 day, 2.25 hrs on cooper (with error rerun)



    # Nonthermal component source model fits
    # --------------------------------------
    # out of date - to be redone

#    stopwatch(src_powerlaw, "results_spec/20160630_src_powerlaw_solar",
#              region='src', solar=True, error=True)
#
#    stopwatch(src_powerlaw, "results_spec/20160630_src_powerlaw_nonsolar",
#              region='src', solar=False, error=True)
#
#    stopwatch(src_srcutlog, "results_spec/20160630_src_srcutlog_solar",
#              region='src', solar=True, error=True)
#
#    stopwatch(src_srcutlog, "results_spec/20160630_src_srcutlog_nonsolar",
#              region='src', solar=False, error=True)
#
#    stopwatch(src_srcutlog, "results_spec/20160630_ann-400-500_srcutlog_nonsolar",
#              region='ann_400_500', solar=False, error=True)


    # XRB parameters from joint fit vs. bkg fit alone
    # are basically the same within error
    # -----------------------------------------------------------
    #stopwatch(bkg_only_fit, "results_spec/20160624_bkg_only_rerun",
    #          error=True)


    # Smaller region fits
    # -------------------

    # Each takes ~20-40 minutes (much faster w/ no background and fewer cts)

    # Standard vnei si/s fit for each case
    stopwatch(single_fit, "results_spec/20161220_lobe_si-s", region='lobe',
              tau_scan=True, error=True, error_rerun=False, free_elements=['Si', 'S'], mosmerge=True, suffix='grp01', with_bkg=False)
    stopwatch(single_fit, "results_spec/20161220_bar_si-s", region='bar',
              tau_scan=True, error=True, error_rerun=False, free_elements=['Si', 'S'], mosmerge=True, suffix='grp01', with_bkg=False)
    stopwatch(single_fit, "results_spec/20161220_ridge_si-s", region='ridge',
              tau_scan=True, error=True, error_rerun=False, free_elements=['Si', 'S'], mosmerge=True, suffix='grp01', with_bkg=False)

    # Variant fits for ridge specifically
    stopwatch(single_fit, "results_spec/20161220_ridge_vpshock_si-s",
              region='ridge', snr_model='vpshock',
              tau_scan=True, error=True, error_rerun=False, free_elements=['Si', 'S'], mosmerge=True, suffix='grp01', with_bkg=False)
    stopwatch(single_fit, "results_spec/20161220_ridge_solar", region='ridge',
              tau_scan=True, error=True, error_rerun=False, free_elements=[], mosmerge=True, suffix='grp01', with_bkg=False)
    stopwatch(single_fit, "results_spec/20161220_ridge_vpshock_solar",
              region='ridge', snr_model='vpshock',
              tau_scan=True, error=True, error_rerun=False, free_elements=[], mosmerge=True, suffix='grp01', with_bkg=False)

    # Set up new fits for more carefully chosen regions
    stopwatch(single_fit, "results_spec/20161222_core", region='core', tau_scan=True, error=True, error_rerun=False, free_elements=['Si', 'S'], mosmerge=True, suffix='grp01', with_bkg=False)
    stopwatch(single_fit, "results_spec/20161222_lobe_ne", region='lobe_ne', tau_scan=True, error=True, error_rerun=False, free_elements=['Si', 'S'], mosmerge=True, suffix='grp01', with_bkg=False)
    stopwatch(single_fit, "results_spec/20161222_lobe_sw", region='lobe_sw', tau_scan=True, error=True, error_rerun=False, free_elements=['Si', 'S'], mosmerge=True, suffix='grp01', with_bkg=False)
    stopwatch(single_fit, "results_spec/20161222_ridge_nw", region='ridge_nw', tau_scan=True, error=True, error_rerun=False, free_elements=['Si', 'S'], mosmerge=True, suffix='grp01', with_bkg=False)
    stopwatch(single_fit, "results_spec/20161222_ridge_se", region='ridge_se', tau_scan=True, error=True, error_rerun=False, free_elements=['Si', 'S'], mosmerge=True, suffix='grp01', with_bkg=False)
    stopwatch(single_fit, "results_spec/20161222_ridge_nw_solar", region='ridge_nw', tau_scan=True, error=True, error_rerun=False, free_elements=[], mosmerge=True, suffix='grp01', with_bkg=False)
    stopwatch(single_fit, "results_spec/20161222_ridge_se_solar", region='ridge_se', tau_scan=True, error=True, error_rerun=False, free_elements=[], mosmerge=True, suffix='grp01', with_bkg=False)

    # Sanity checks, though expect non-solar abundances to be required
    stopwatch(single_fit, "results_spec/20170109_lobe_ne_solar", region='lobe_ne', tau_scan=True, error=True, error_rerun=False, free_elements=[], mosmerge=True, suffix='grp01', with_bkg=False)
    stopwatch(single_fit, "results_spec/20170109_core_solar", region='core', tau_scan=True, error=True, error_rerun=False, free_elements=[], mosmerge=True, suffix='grp01', with_bkg=False)
    stopwatch(single_fit, "results_spec/20170109_lobe_sw_solar", region='lobe_sw', tau_scan=True, error=True, error_rerun=False, free_elements=[], mosmerge=True, suffix='grp01', with_bkg=False)

    # Special Fe-K line fit
    stopwatch(single_fit, "results_spec/20170328_src_gauss-fe-k", region='src',
            snr_model='gauss', tau_scan=False, error=True, error_rerun=False,
            mosmerge=True, suffix='grp01', with_bkg=False)
