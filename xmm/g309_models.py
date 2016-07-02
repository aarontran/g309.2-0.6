#!/usr/local/bin/python
"""
PyXSPEC port of combined SNR and background fit...

Run in top-level namespace to enable subsequent interactive work

Using /usr/local/bin/python for HEAD network use
"""

from __future__ import division

#import argparse
from math import pi
import os

import xspec as xs
import xspec_utils as xs_utils
from ExtractedSpectrum import ExtractedSpectrum


def load_data_and_models(*regs, **kwargs):
    """
    Load G309.2-0.6 data and initialize responses and models.

    After successful load (~1-10 minutes), global XSPEC session has
    5*len(regs) spectra loaded (for the five XMM exposures we're using)
    and ready to be simultaneously fit to a model with sources:
        cosmic x-ray background
        source model (set by snr_model kwarg)
        soft proton power laws
        instrumental lines fixed from FWC data fits
    The returned hash is used to manipulate individual spectra or models

    Input: region stems for extracted XMM ESAS spectra; duplicates disallowed

    Keyword arguments:
      snr_model = vnei, vpshock None

    Output: hash keying each region to 5 ExtractedSpectrum objects,
        one per XMM exposure in use
    """
    if len(set(regs)) != len(regs):
        raise Exception("Duplicate regions not allowed")

    # ExtractedSpectrum objects allow script to easily resolve pipeline outputs
    # order of regs sets the order of XSPEC datagroup assignment
    extrs_from = {}
    all_extrs = []  # Keep regs ordering for XSPEC datagroup assignment
    for reg in regs:
        extrs = [ ExtractedSpectrum("0087940201", "mos1S001", reg),
                  ExtractedSpectrum("0087940201", "mos2S002", reg),
                  ExtractedSpectrum("0087940201", "pnS003",   reg),
                  ExtractedSpectrum("0551000201", "mos1S001", reg),
                  ExtractedSpectrum("0551000201", "mos2S002", reg) ]
        extrs_from[reg] = extrs
        all_extrs.extend(extrs)

    # Spectrum and response assignment
    # --------------------------------
    for i, extr in enumerate(all_extrs, start=1):
        spec = xs_utils.load_spec(i, extr.pha(), background=extr.qpb(),
                                  default_dir=extr.repro_dir())
        extr.spec = spec

    # Load models
    # -----------
    # 1: x-ray background
    # 2: instrumental lines
    # 3, ... (3+n_reg-1): SNR plasma model
    # (3+n_reg), ..., (3+n_reg+n_spec): soft proton background

    # NOTE: loader methods below require that ExtractedSpectrum objects have
    # xs.Spectrum objects attached in .spec attribute

    # Attach xs.Model objects to ExtractedSpectrum for convenience
    # no need to address by: xs.AllModels(extr.spec.index, model_name)
    for extr in all_extrs:
        extr.models = {}

    load_cxrb(1, 'xrb', all_extrs)

    load_soft_proton(2, 'sp', all_extrs)
    for extr in all_extrs:
        extr.models['sp'] = xs.AllModels(extr.spec.index, 'sp')
        extr.models['xrb'] = xs.AllModels(extr.spec.index, 'xrb')

    # SNR model -- distinct source model for each region
    # if "bkg" in regs, source numbering will be discontinuous
    for n_reg, reg in enumerate(regs):
        if reg == "bkg" or kwargs['snr_model'] is None:
            continue
        model_n = 3 + n_reg
        load_remnant_model(model_n, "snr_" + reg, extrs_from[reg], case=kwargs['snr_model'])
        for extr in extrs_from[reg]:
            extr.models['snr'] = xs.AllModels(extr.spec.index, "snr_" + reg)

    # One instrumental line model per spectrum
    for n_extr, extr in enumerate(all_extrs):
        model_n = 3 + len(regs) + n_extr
        load_instr(model_n, "instr_{:d}".format(n_extr+1), extr)
        extr.models['instr'] = xs.AllModels(extr.spec.index, "instr_{:d}".format(n_extr+1))

    return extrs_from



def load_instr(model_n, model_name, extr):
    """Create instrumental line model for ExtractedSpectrum extr
    Fix line energies and norms based on FWC fit data, but allow overall norm
    to vary (i.e., all line ratios pinned to FWC line ratios).
    Use ARFs appropriate for FWC data (no telescope vignetting).

    Currently expect 2 lines (MOS) and 7 lines (PN) modeled in FWC spectrum
    MOS lines: Al, Si
    PN lines: Al, Ti, Cr, Ni, Cu, Zn, Cu(K-beta)

    WARNING -- operates on a single ExtractedSpectrum, rather than a list,
    which breaks convention with other model loaders.
    Reason being, each spectrum has a DIFFERENT instr. line model.

    ExtractedSpectrum object additionally _must_ have an attached
    xs.Spectrum object, referenced via .spec attribute.

    (alternative approach: create a single model w/ both MOS and PN lines,
    and freeze or zero out values accordingly.
    This makes xs.AllModels.show() output much harder to read (many zeroed,
    meaningless parameters, but model #s easier to track)

    Arguments
        model_n: XSPEC model number, 1-based
        extr: single ExtractedSpectrum.
            WARNING - breaks convention w/ other model loaders.
        model_name: XSPEC model name, string (no spaces)
    Output:
        None.  Global XSPEC objects configured for instrumental lines.
    """
    # Set responses of <xs.Spectrum> objects
    extr.spec.multiresponse[model_n - 1]     = extr.rmf()
    extr.spec.multiresponse[model_n - 1].arf = extr.arf_fwc()

    fit_dict = extr.fwc_fit()
    instr = xs.Model("constant * (" + fit_dict['expression'] + ")", model_name, model_n)

    # Set parameters all at once
    parlist = [1]  # Set constant factor to 1
    fwc_comps = sorted(fit_dict['comps'].values(), key=lambda x: x['LineE']['value'])
    for i, fwc_comp in enumerate(fwc_comps):
        parlist.extend([fwc_comp['LineE']['value'],
                        fwc_comp['Sigma']['value'],
                        fwc_comp['norm']['value']])
    instr.setPars(*parlist)

    # Freeze everything except constant prefactor
    xs_utils.freeze_model(instr)
    instr.constant.factor.frozen = False


def load_remnant_model(model_n, model_name, extracted_spectra, case='vnei'):
    """Create source model for extracted_spectra
    Set appropriate RMF & ARF files, initialize parameters and parameter
    bounds, apply BACKSCAL ratio scaling.
    Parameter bounds are of course tuned for G309.2-0.6.

    ExtractedSpectrum objects additionally _must_ have an attached
    xs.Spectrum object, referenced via .spec attribute.

    Arguments
        model_n: XSPEC model number, 1-based
        extracted_spectra: list of ExtractedSpectrum objects
        model_name: XSPEC model name, string (no spaces)
        case: remnant type (specifies a canned model setup)
    Output:
        None.  Global XSPEC objects configured for SNR.
    """
    if case is None:
        return

    # Set responses of <xs.Spectrum> objects
    for extr in extracted_spectra:
        extr.spec.multiresponse[model_n - 1]     = extr.rmf()
        extr.spec.multiresponse[model_n - 1].arf = extr.arf()

    # Initialize source model with reasonable "global" parameters

    model_expression = "constant * tbnew_gas * ( {} )".format(case)
    src = xs.Model(model_expression, model_name, model_n)

    if case == 'vnei':
        # Apply fitting bounds
        src.setPars({src.tbnew_gas.nH.index : "1, , 1e-2, 0.1, 10, 10",  # generally well-constrained already
                     src.vnei.kT.index : "1, , , , 10, 10",  # upper bound only
                     src.vnei.S.index : "1, , , , 10, 10",  # upper bound only
                     src.vnei.Si.index : "1, , , , 10, 10"} )  # upper bound only
        src.tbnew_gas.nH.frozen = True
        src.vnei.kT.frozen = True
        src.vnei.Tau.frozen = True
        src.vnei.S.frozen = True
        src.vnei.Si.frozen = True
    elif case == 'vnei+powerlaw':
        # Apply fitting bounds
        src.setPars({src.tbnew_gas.nH.index : "1, , 1e-2, 0.1, 10, 10",  # generally well-constrained already
                     src.vnei.kT.index : "1, , , , 10, 10",  # upper bound only
                     src.vnei.S.index : "1, , , , 10, 10",  # upper bound only
                     src.vnei.Si.index : "1, , , , 10, 10"} )  # upper bound only
        # TODO Appropriate bounds for powerlaw component TBD
        src.tbnew_gas.nH.frozen = True
        src.vnei.kT.frozen = True
        src.vnei.Tau.frozen = True
        src.vnei.S.frozen = True
        src.vnei.Si.frozen = True
    elif case == 'vnei+srcutlog':
        # Apply fitting bounds
        src.setPars({src.tbnew_gas.nH.index : "1, , 1e-2, 0.1, 10, 10",  # generally well-constrained already
                     src.vnei.kT.index : "1, , , , 10, 10",  # upper bound only
                     src.vnei.S.index : "1, , , , 10, 10",  # upper bound only
                     src.vnei.Si.index : "1, , , , 10, 10",  # upper bound only
                     src.srcutlog.alpha.index : "0.53",  # Gaensler+ 1998
                     src.srcutlog.norm.index : 6  # 1 GHz flux density (Jy), interpolated from Gaensler+ data fit
                     } )  # upper bound only
        src.tbnew_gas.nH.frozen = True
        src.vnei.kT.frozen = True
        src.vnei.Tau.frozen = True
        src.vnei.S.frozen = True
        src.vnei.Si.frozen = True
        src.srcutlog.alpha.frozen = True
        src.srcutlog.norm.frozen = True
        src.srcutlog.__getattribute__('break').frozen = False  # break reserved in Python...
    elif case == 'vpshock':
        src.tbnew_gas.nH = 1
        src.vpshock.kT = 1
        src.vpshock.Tau_l = 1e9
        src.vpshock.Tau_u = 1e11
    elif case == 'vsedov':
        raise Exception("Need to test vsedov further, doesn't work")
        #src = xs.Model("constant * tbnew_gas * vsedov", model_name, model_n)
        #snr.vsedov.kT = 2
        #snr.vsedov.kT_i = 1
    else:
        print "Warning: case {} not pre-configured, please freeze and set parameters manually"

    # Set individal spectrum parameters
    for extr in extracted_spectra:
        src_curr = xs.AllModels(extr.spec.index, model_name)
        # Apply backscal ratio scalings
        src_curr.constant.factor = extr.backscal() / ExtractedSpectrum.FIDUCIAL_BACKSCAL
        src_curr.constant.factor.frozen = True
        # Save model for this spectrum


def load_soft_proton(model_n, model_name, extracted_spectra):
    """Set soft proton contamination power laws for each spectrum in
    extracted_spectra.
    Set appropriate RMF & ARF files, initialize parameters and parameter
    bounds, apply BACKSCAL ratio scaling.

    Ties power-law indices between MOS1 and MOS2 exposures in same obsid.
    Requires that each obsid has only one MOS1 and one MOS2 exposure.

    ExtractedSpectrum objects additionally _must_ have an attached
    xs.Spectrum object, referenced via .spec attribute.

    Arguments
        model_n: XSPEC model number, 1-based
        model_name: XSPEC model name, string (no spaces)
        extracted_spectra: list of ExtractedSpectrum objects
    Output:
        None.  Global XSPEC objects configured for soft proton model.
    """

    # Set responses of <xs.Spectrum> objects
    for extr in extracted_spectra:
        extr.spec.multiresponse[model_n - 1]     = extr.rmf_diag()
        extr.spec.multiresponse[model_n - 1].arf = "none"

    # Initialize sp model
    sp = xs.Model("constant * powerlaw", model_name, model_n)

    # Set individal spectrum parameters
    for extr in extracted_spectra:
        sp_curr = xs.AllModels(extr.spec.index, model_name)
        # Let power law indices, norms vary independently
        # Must set index limits for each model; parameter limits do not
        # propagate through links
        sp_curr.powerlaw.PhoIndex.link = ""
        sp_curr.powerlaw.PhoIndex.values = "0.4, , 0, 0.1, 1, 2" # Set hard/soft limits
        sp_curr.powerlaw.PhoIndex.frozen = False
        sp_curr.powerlaw.norm.link = ""
        sp_curr.powerlaw.norm.frozen = False
        # Apply backscal ratio scalings to make comparing norms easier
        sp_curr.constant.factor = extr.backscal() / ExtractedSpectrum.FIDUCIAL_BACKSCAL
        sp_curr.constant.factor.frozen = True

    # Tie MOS1/MOS2 photon indices together
    for x in extracted_spectra:
        if x.instr != 'mos1':
            continue
        sp_mos1 = xs.AllModels(x.spec.index, model_name)
        sp_mos2 = None
        # Find matching MOS2 observation
        for y in extracted_spectra:
            if y.instr == 'mos2' and y.reg == x.reg and y.obsid == x.obsid:
                if sp_mos2:  # May occur in complex XMM pointings
                    raise Exception("Extra mos2 spectrum!")
                sp_mos2 = xs.AllModels(y.spec.index, model_name)
        # Tie photon indices
        sp_mos2.powerlaw.PhoIndex.link = xs_utils.link_name(sp_mos1, sp_mos1.powerlaw.PhoIndex)


def load_cxrb(model_n, model_name, extracted_spectra):
    """Load cosmic X-ray background for each spectrum in
    extracted_spectra.
    Set appropriate RMF & ARF files, initialize XRB model and parameter
    values, apply BACKSCAL ratio scaling.

    ExtractedSpectrum objects additionally _must_ have an attached
    xs.Spectrum object, referenced via .spec attribute.

    Arguments
        model_n: XSPEC model number, 1-based
        model_name: XSPEC model name, string (no spaces)
        extracted_spectra: list of ExtractedSpectrum objects
    Output:
        None.  Global XSPEC objects configured for XRB model.
    """

    # Set responses of <xs.Spectrum> objects
    for extr in extracted_spectra:
        extr.spec.multiresponse[model_n - 1]     = extr.rmf()
        extr.spec.multiresponse[model_n - 1].arf = extr.arf()

    # Initialize XRB model with reasonable "global" parameters
    xrb = xs.Model("constant * (apec + tbnew_gas*(powerlaw + apec))", model_name, model_n)

    # Hickox and Markevitch (2006) norm
    # convert 10.9 photons cm^-2 s^-1 sr^-1 keV^-1 to photons cm^-2 s^-1 keV^-1
    # sr^-1 --> XMM detector pixels (backscal unit, 0.05 arcsec^2)
    exrb_norm = 10.9 * (180/pi)**-2 * 60**-4 * (1/0.05)**-2 * ExtractedSpectrum.FIDUCIAL_BACKSCAL

    # NOTE HARDCODED -- best fit values from src/bkg combined fit
    # after error runs on some parameters of interest
    # Corresponds to: 20160624_src_bkg_nohack_rerun.log outputs
    xrb.setPars({xrb.powerlaw.PhoIndex.index : 1.4,
                 xrb.powerlaw.norm.index : exrb_norm,
                 xrb.apec.kT.index : 0.262,  # Unabsorped apec (local bubble)
                 xrb.tbnew_gas.nH.index : 1.321,  # Galactic absorption
                 xrb.apec_5.kT.index : 0.744,  # Absorbed apec (galactic halo)
                 xrb.apec.norm.index : 2.98e-4,
                 xrb.apec_5.norm.index : 2.19e-3})

    xs_utils.freeze_model(xrb)

    # Set individal spectrum parameters
    for extr in extracted_spectra:
        xrb_curr = xs.AllModels(extr.spec.index, model_name)
        # Apply backscal ratio scalings
        # Re-freeze because changing value from link thaws by default
        xrb_curr.constant.factor = extr.backscal() / ExtractedSpectrum.FIDUCIAL_BACKSCAL
        xrb_curr.constant.factor.frozen = True



if __name__ == '__main__':
    pass

