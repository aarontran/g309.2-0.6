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


def load_data(*regs, **kwargs):
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
    if not kwargs['snr_model']:
        raise Exception("snr_model is a required kwarg")

    # ExtractedSpectrum objects allow script to easily resolve pipeline outputs
    # regs sets the ordering for XSPEC datagroup assignment
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
    # a possibly nicer solution is a dataframe that allows quick filtering /
    # selection by region, obsid, etc

    # Spectrum and response assignment
    # --------------------------------

    old_wd = os.getcwd()

    for i, extr in enumerate(all_extrs, start=1):
        # Load spectrum into XSPEC
        os.chdir(extr.repro_dir())  # chdir so XSPEC can resolve header arf/rmf/bkg, avoid awful errors
        xs.AllData("{n}:{n} {file}".format(n=i, file=extr.pha()))
        spec = xs.AllData(i)
        spec.background = extr.qpb()
        # Attach xs.Spectrum to ExtractedSpectrum
        extr.spec = spec

    os.chdir(old_wd)

    # Load models
    # -----------

    # Keep ALL model-specific settings -- rmf/arf assignment,
    # globally fixed parameter values, "standard" parameter links, etc. inside
    # loader methods.  Loader methods require all_extrs = list of
    # ExtractedSpectrum objects that ADDITIONALLY comes with a .spec attribute,
    # pointing to the associated xs.Spectrum object.
    for extr in all_extrs:
        extr.models = {}

    # 0: x-ray background
    # 1: instrumental lines
    # 2: SNR plasma model
    # 3: soft proton background
    # (maps to 1,2,3,4 in PyXSPEC methods)

    load_cxrb(1, all_extrs)

    load_soft_proton(2, all_extrs)

    # SNR model -- distinct source model for each region
    # if "bkg" in regs, source numbering will be discontinuous; that's OK
    for n_reg, reg in enumerate(regs):
        if reg == "bkg":
            continue
        load_source_model(3 + n_reg, extrs_from[reg], model_name="snr_{}".format(reg), case=kwargs['snr_model'])
        # TODO note code variable snr_model here

    # One instrumental line model per spectrum
    for n_extr, extr in enumerate(all_extrs):
        load_instr(3 + len(regs) + n_extr, extr, model_name="instr_{:d}".format(n_extr))

    return extrs_from



def load_instr(model_n, extr, model_name=None):
    """Load instrumental lines.

    Import previously fitted gaussian instrumental lines.
    Fix instr line energies and norms, but allow overall norm to vary
    (i.e., all line ratios pinned to FWC line ratios)

    Currently expect 2 lines (MOS) and 7 lines (PN) modeled in FWC spectrum
    MOS lines: Al, Si
    PN lines: Al, Ti, Cr, Ni, Cu, Zn, Cu(K-beta)

    WARNING -- input argument is a single spectrum, not a list

    Input: ...
        kwarg model_name is _required_
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

    # Save model for this spectrum
    # no need to address by: xs.AllModels(extr.spec.index, model_name)
    extr.models[model_name] = instr


def load_source_model(model_n, extracted_spectra, model_name, case='vnei'):
    """Set source (typically SNR) model"""
    # Set responses of <xs.Spectrum> objects
    for extr in extracted_spectra:
        extr.spec.multiresponse[model_n - 1]     = extr.rmf()
        extr.spec.multiresponse[model_n - 1].arf = extr.arf()

    # Initialize source model with reasonable "global" parameters
    if case == 'vnei':
        src = xs.Model("constant * TBabs * vnei", model_name, model_n)
        # Default values are fine
        src.TBabs.nH.frozen = True
        src.vnei.kT.frozen = True
        src.vnei.Tau.frozen = True
    elif case == 'vpshock':
        src = xs.Model("constant * TBabs * vpshock", model_name, model_n)
        src.TBabs.nH = 1
        src.vpshock.kT = 1
        src.vpshock.Tau_l = 1e9
        src.vpshock.Tau_u = 1e11
    elif case == 'vsedov':
        raise Exception("Need to test vsedov further, doesn't work")
        #src = xs.Model("constant * TBabs * vsedov", model_name, model_n)
        #snr.vsedov.kT = 2
        #snr.vsedov.kT_i = 1
    elif case is None:
        src = None
    else:
        raise Exception("Invalid snr model: {} not recognized".format(case))

    # Set individal spectrum parameters
    for extr in extracted_spectra:
        src_curr = xs.AllModels(extr.spec.index, model_name)
        # Apply backscal ratio scalings
        src_curr.constant.factor = extr.backscal() / ExtractedSpectrum.FIDUCIAL_BACKSCAL
        src_curr.constant.factor.frozen = True
        # Save model for this spectrum
        extr.models[model_name] = src_curr


def load_soft_proton(model_n, extracted_spectra):
    """Set soft proton contamination power laws
    Warning -- requires each obsid to have <=1 MOS1, <=1 MOS2 spectrum
    Will not work otherwise.  Easy to fix, though.
    """

    # Set responses of <xs.Spectrum> objects
    for extr in extracted_spectra:
        extr.spec.multiresponse[model_n - 1]     = extr.rmf_diag()
        extr.spec.multiresponse[model_n - 1].arf = "none"

    # Initialize sp model with reasonable "global" parameters
    sp = xs.Model("constant * powerlaw", 'sp', model_n)
    sp.powerlaw.PhoIndex.values = "0.4, , -0.1, 0, 1, 2" # Set hard/soft limits
    sp.powerlaw.norm = 1e-2

    # Set individal spectrum parameters
    for extr in extracted_spectra:
        sp_curr = xs.AllModels(extr.spec.index, 'sp')
        # Let power law indices, norms vary independently
        sp_curr.powerlaw.PhoIndex.link = ""
        sp_curr.powerlaw.PhoIndex.frozen = False
        sp_curr.powerlaw.norm.link = ""
        sp_curr.powerlaw.norm.frozen = False
        # Apply backscal ratio scalings to make comparing norms easier
        sp_curr.constant.factor = extr.backscal() / ExtractedSpectrum.FIDUCIAL_BACKSCAL
        sp_curr.constant.factor.frozen = True
        # Save model for this spectrum
        extr.models['sp'] = sp_curr

    # Tie MOS1/MOS2 photon indices together
    for x in extracted_spectra:
        if x.instr != 'mos1':
            continue
        sp_mos1 = x.models['sp']
        sp_mos2 = None
        # Find matching MOS2 observation
        for y in extracted_spectra:
            if y.instr == 'mos2' and y.reg == x.reg and y.obsid == x.obsid:
                if sp_mos2:  # May occur in complex XMM pointings
                    raise Exception("Extra mos2 spectrum!")
                sp_mos2 = y.models['sp']
        # Tie photon indices
        sp_mos2.powerlaw.PhoIndex.link = xs_utils.link_name(sp_mos1, sp_mos1.powerlaw.PhoIndex)


def load_cxrb(model_n, extracted_spectra):
    """Set CXRB"""

    # Set responses of <xs.Spectrum> objects
    for extr in extracted_spectra:
        extr.spec.multiresponse[model_n - 1]     = extr.rmf()
        extr.spec.multiresponse[model_n - 1].arf = extr.arf()

    # Initialize XRB model with reasonable "global" parameters
    xrb = xs.Model("constant * (apec + TBabs*(powerlaw + apec))", 'xrb', model_n)

    # Hickox and Markevitch (2006) norm
    # convert 10.9 photons cm^-2 s^-1 sr^-1 keV^-1 to photons cm^-2 s^-1 keV^-1
    # sr^-1 --> XMM detector pixels (backscal unit, 0.05 arcsec^2)
    exrb_norm = 10.9 * (180/pi)**-2 * 60**-4 * (1/0.05)**-2 * ExtractedSpectrum.FIDUCIAL_BACKSCAL

    # NOTE HARDCODED -- best fit values from src/bkg combined fit
    xrb.setPars({xrb.powerlaw.PhoIndex.index : 1.4},
                {xrb.powerlaw.norm.index : exrb_norm},
                {xrb.apec.kT.index : 0.261},  # Unabsorped apec (local bubble)
                {xrb.TBabs.nH.index : 1.372},  # Galactic absorption
                {xrb.apec_5.kT.index : 0.755},  # Absorbed apec (galactic halo)
                {xrb.apec.norm.index : 3.06e-4},
                {xrb.apec_5.norm.index : 2.33e-3} )

    xs_utils.freeze_model(xrb)

    # Set individal spectrum parameters
    for extr in extracted_spectra:
        xrb_curr = xs.AllModels(extr.spec.index, 'xrb')
        # Apply backscal ratio scalings
        # Re-freeze because changing value from link thaws by default
        xrb_curr.constant.factor = extr.backscal() / ExtractedSpectrum.FIDUCIAL_BACKSCAL
        xrb_curr.constant.factor.frozen = True
        # Save model for this spectrum
        extr.models['xrb'] = xrb_curr





if __name__ == '__main__':
    pass

#    parser = argparse.ArgumentParser(description="Execute interactive G309 region fits in XSPEC")
#    parser.add_argument('reg', default='src',
#        help="Region to fit to SNR/plasma model")
#    parser.add_argument('--snr_model', default='vnei',
#        help="Choose SNR model")
#    parser.add_argument('--n_H', type=float, default=None,
#        help="Fix SNR absorption nH in fits (units 10e22), else free to vary")
#    parser.add_argument('--no_fit', action='store_true',
#        help="Don't start any fits; drop user straight into interactive mode")
#    parser.add_argument('--with_bkg', action='store_true',
#        help=("Load bkg spectra for simultaneous fitting instead of using"
#              " canned values from integrated SNR/bkg fit"))
#
#    # Set a number of global variables from CL args
#    # Interface in scripts tbd...
#    args = parser.parse_args()
#    REG = args.reg
#    SNR_MODEL = args.snr_model
#    N_H = args.n_H
#    WITH_BKG = args.with_bkg
#    NO_FIT = args.no_fit
#
#    if SNR_MODEL not in ['vnei', 'vpshock', 'vsedov', 'xrb']:
#        raise Exception("Invalid SNR model")
#
#    load_data()
#
#    print "Finished at:", datetime.now()


