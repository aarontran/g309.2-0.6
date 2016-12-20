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


def load_data_and_models(regs, snr_model='vnei', suffix='grp01',
                         mosmerge=True, marfrmf=True, sp_bknpower=False):
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
      suffix = grp01, grp50

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
        if mosmerge:
            extrs = [ ExtractedSpectrum("0087940201", "mosmerge", reg, suffix=suffix, marfrmf=marfrmf),
                      ExtractedSpectrum("0087940201", "pnS003",   reg, suffix=suffix, marfrmf=marfrmf),
                      ExtractedSpectrum("0551000201", "mosmerge", reg, suffix=suffix, marfrmf=marfrmf) ]
        else:
            extrs = [ ExtractedSpectrum("0087940201", "mos1S001", reg, suffix=suffix),
                      ExtractedSpectrum("0087940201", "mos2S002", reg, suffix=suffix),
                      ExtractedSpectrum("0087940201", "pnS003",   reg, suffix=suffix),
                      ExtractedSpectrum("0551000201", "mos1S001", reg, suffix=suffix),
                      ExtractedSpectrum("0551000201", "mos2S002", reg, suffix=suffix) ]
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

    load_soft_proton(2, 'sp', all_extrs, broken=sp_bknpower)
    for extr in all_extrs:
        extr.models['sp'] = xs.AllModels(extr.spec.index, 'sp')
        extr.models['xrb'] = xs.AllModels(extr.spec.index, 'xrb')

    # SNR model -- distinct source model for each region
    # if "bkg" in regs, source numbering will be discontinuous
    for n_reg, reg in enumerate(regs):
        if reg == "bkg" or snr_model is None:
            continue
        model_n = 3 + n_reg
        load_remnant_model(model_n, "snr_" + reg, extrs_from[reg], case=snr_model)
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
    extr.spec.multiresponse[model_n - 1]     = extr.rmf_instr()
    extr.spec.multiresponse[model_n - 1].arf = extr.arf_instr()

    fit_dict = extr.fwc_fit()
    instr = xs.Model("constant * (" + fit_dict['1']['instr']['expression'] + ")",
                     model_name, model_n)

    # Set parameters all at once
    parlist = ["1, , 0.1, 0.1, 10, 10"]  # Set constant factor to 1 (range: 0.1-10)
    for cname in fit_dict['1']['instr']['componentNames']:
        parlist.extend([fit_dict['1']['instr'][cname]['LineE']['value'],
                        fit_dict['1']['instr'][cname]['Sigma']['value'],
                        fit_dict['1']['instr'][cname]['norm']['value']])
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
        case: remnant type (specifies a canned model setup), one of:
                'vnei', 'vnei+powerlaw', 'vnei+srcutlog', 'vnei+nei',
                'vpshock'
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
                     src.vnei.S.index : "1, , , , 100, 100",  # upper bound only
                     src.vnei.Si.index : "1, , , , 100, 100"} )  # upper bound only
        src.tbnew_gas.nH.frozen = True
        src.vnei.kT.frozen = True
        src.vnei.Tau.frozen = True
        src.vnei.S.frozen = True
        src.vnei.Si.frozen = True
    elif case == 'vnei+powerlaw':
        # Apply fitting bounds
        src.setPars({src.tbnew_gas.nH.index : "1, , 1e-2, 0.1, 10, 10",  # generally well-constrained
                     src.vnei.kT.index : "1, , , , 10, 10",  # upper bound only
                     src.vnei.S.index : "1, , , , 100, 100",  # upper bound only
                     src.vnei.Si.index : "1, , , , 100, 100"} )  # upper bound only
        # TODO Appropriate bounds for powerlaw component TBD
        src.tbnew_gas.nH.frozen = True
        src.vnei.kT.frozen = True
        src.vnei.Tau.frozen = True
        src.vnei.S.frozen = True
        src.vnei.Si.frozen = True
    elif case == 'vnei+srcutlog':
        # Apply fitting bounds
        src.setPars({src.tbnew_gas.nH.index : "1, , 1e-2, 0.1, 10, 10",  # generally well-constrained
                     src.vnei.kT.index : "1, , , , 10, 10",  # upper bound only
                     src.vnei.S.index : "1, , , , 100, 100",  # upper bound only
                     src.vnei.Si.index : "1, , , , 100, 100",  # upper bound only
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
    elif case == 'vnei+nei':
        # Apply fitting bounds
        src.setPars({src.tbnew_gas.nH.index : "1, , 1e-2, 0.1, 10, 10",  # generally well-constrained
                     src.vnei.kT.index : "1, , , , 10, 10",  # upper bounds only
                     src.vnei.S.index : "1, , , , 100, 100",
                     src.vnei.Si.index : "1, , , , 100, 100",
                     src.nei.kT.index : "1, , , , 10, 10"})
        src.tbnew_gas.nH.frozen = True
        src.vnei.kT.frozen = True
        src.vnei.Tau.frozen = True
        src.vnei.S.frozen = True
        src.vnei.Si.frozen = True
        src.nei.kT.frozen = True
        src.nei.Tau.frozen = True
    elif case == 'vpshock':
        src.setPars({src.tbnew_gas.nH.index : "1, , 1e-2, 0.1, 10, 10",  # generally well-constrained
                     src.vpshock.kT.index : "1, , , , 10, 10",  # upper bound only
                     src.vpshock.S.index : "1, , , , 100, 100",
                     src.vpshock.Si.index : "1, , , , 100, 100",
                     src.vpshock.Tau_l.index : 1e8,     # no bounds, set reasonable initial value
                     src.vpshock.Tau_u.index : 1e10})  # no bounds, set reasonable initial value
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


def load_soft_proton(model_n, model_name, extracted_spectra, broken=True):
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
        broken: use broken power law?
    Output:
        None.  Global XSPEC objects configured for soft proton model.
    """

    # Set responses of <xs.Spectrum> objects
    for extr in extracted_spectra:
        extr.spec.multiresponse[model_n - 1]     = extr.rmf_diag()
        extr.spec.multiresponse[model_n - 1].arf = "none"

    # Initialize sp model
    if broken:
        sp = xs.Model("constant * bknpower", model_name, model_n)
    else:
        sp = xs.Model("constant * powerlaw", model_name, model_n)

    # Set individal spectrum parameters
    for extr in extracted_spectra:
        sp_curr = xs.AllModels(extr.spec.index, model_name)
        # Let power law indices, norms vary independently
        # Must set index limits for each model; parameter limits do not
        # propagate through links
        if broken:
            if extr.obsid == '0551000201':
                sp_curr.bknpower.PhoIndx1.link = ""
                sp_curr.bknpower.PhoIndx1.values = "0.3, , 0, 0.1, 1, 2"
                sp_curr.bknpower.PhoIndx1.frozen = False
                sp_curr.bknpower.PhoIndx2.link = ""
                sp_curr.bknpower.PhoIndx2.values = "0.6, , 0, 0.1, 2, 3"
                sp_curr.bknpower.PhoIndx2.frozen = False
                sp_curr.bknpower.BreakE.link = ""
                sp_curr.bknpower.BreakE.values = "2.0, , 0, 0.5, 10, 20"
                sp_curr.bknpower.BreakE.frozen = False
                sp_curr.bknpower.norm.link = ""
                sp_curr.bknpower.norm.frozen = False
            elif extr.obsid == '0087940201':
                sp_curr.bknpower.PhoIndx1.link = ""
                sp_curr.bknpower.PhoIndx1.values = "0.4, , 0, 0.1, 1, 2"
                sp_curr.bknpower.PhoIndx1.frozen = False
                sp_curr.bknpower.PhoIndx2.link = xs_utils.link_name(sp_curr,
                                                    sp_curr.bknpower.PhoIndx1)
                sp_curr.bknpower.PhoIndx2.frozen = False
                sp_curr.bknpower.BreakE.link = ""
                sp_curr.bknpower.BreakE.values = 20
                sp_curr.bknpower.BreakE.frozen = True
                sp_curr.bknpower.norm.link = ""
                sp_curr.bknpower.norm.frozen = False
            else:
                raise Exception("sp model not set for {:s}".format(extr.obsid))
        else:
            sp_curr.powerlaw.PhoIndex.link = ""
            sp_curr.powerlaw.PhoIndex.values = "0.4, , 0, 0.1, 1, 2" # Hard/soft limits
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
        if broken:
            sp_mos2.bknpower.PhoIndx1.link = xs_utils.link_name(sp_mos1,
                                                    sp_mos1.bknpower.PhoIndx1)
            sp_mos2.bknpower.PhoIndx2.link = xs_utils.link_name(sp_mos1,
                                                    sp_mos1.bknpower.PhoIndx2)
        else:
            sp_mos2.powerlaw.PhoIndex.link = xs_utils.link_name(sp_mos1,
                                                    sp_mos1.powerlaw.PhoIndex)


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
        extr.spec.multiresponse[model_n - 1]     = extr.rmf_flat()
        extr.spec.multiresponse[model_n - 1].arf = extr.arf_flat()

    # Initialize XRB model with reasonable "global" parameters
    xrb = xs.Model("constant * (apec + tbnew_gas*powerlaw + tbnew_gas*apec)",
                   model_name, model_n)

    # Hickox and Markevitch (2006) norm
    # convert 10.9 photons cm^-2 s^-1 sr^-1 keV^-1 to photons cm^-2 s^-1 keV^-1
    # sr^-1 --> XMM detector pixels (backscal unit, 0.05 arcsec^2)
    #
    # The prefactor 0.61 comes from removing point sources brighter than
    # 1e-14 erg cm^-2 s^-1 in 0.4-7.2 keV band.  After accounting for
    # absorption + rescaling to 2-10 keV band, the point source threshold is
    # ~1.46e-14 erg cm^-2 sec^-1 in 2-10 keV band.
    # I integrate the distribution of Moretti+ (2003) to get the excluded
    # surface brightness, which is 39% of the total EXRB surf. brightness
    # in 2-10 keV, based on Hickox/Markevitch (2006) model.
    # Therefore, scale down EXRB normalization from 10.9 --> (1-0.39)*10.9
    exrb_norm = 0.61 * 10.9 * (180/pi)**-2 * 60**-4 * (1/0.05)**-2 * ExtractedSpectrum.FIDUCIAL_BACKSCAL

    # NOTE HARDCODED -- best fit values from src/bkg combined fit
    # after error runs on some parameters of interest
    # Corresponds to: 20161015_src_bkg_mg.log outputs
    xrb.setPars({xrb.powerlaw.PhoIndex.index : 1.4,
                 xrb.powerlaw.norm.index : exrb_norm,
                 xrb.apec.kT.index : 0.265,  # Unabsorped apec (local bubble)
                 xrb.apec.norm.index : 2.36e-4,
                 xrb.tbnew_gas.nH.index : 1.12,  # Galactic absorption (for extragal background)
                 xrb.tbnew_gas_5.nH.index : 1.39,  # Halo absorption
                 xrb.apec_6.kT.index : 0.744,  # Absorbed apec (galactic halo)
                 xrb.apec_6.norm.index : 1.94e-3}
                )

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

