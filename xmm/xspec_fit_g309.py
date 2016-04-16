#!/usr/local/bin/python
"""
PyXSPEC port of combined SNR and background fit...

Run in top-level namespace to enable subsequent interactive work
(e.g. in ipython shell)

Using /usr/local/bin/python for HEAD network use
"""

from __future__ import division

import argparse
from datetime import datetime
#import json
#import matplotlib.pyplot as plt
#import numpy as np
from math import pi
import os
import sys
from subprocess import call

from astropy.io import fits
import xspec as xs

import xspec_utils as xs_utils

# In Python 2.x, *args must go after specific kwargs...
# makes sense -- it becomes ambiguous whether first input arg is meant for
# *args, or for first specified keyword arg...
def load_data(*regs, **kwargs):
    """
    Input config parameters and run hopefully reasonably customizable fit
    with minimal abstraction leakage from prior data pipeline

    Output: user is left with XSPEC session
    having all spectra loaded for simultaneous fitting with:
      cosmic x-ray background
      source (except for 'bkg' region specially)
      soft proton power laws
      instrumental lines fixed from FWC data fits
    and is ready for further customization or fitting
    """

    if len(set(regs)) != len(regs):
        raise Exception("Duplicate regions not allowed")

    if not kwargs['snr_model']:
        raise Exception("snr_model is a required kwarg to load_data(...)")

    # Assign in blocks of 5, currently
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

    # NOTE: we may not need to assign datagroup numbers
    # Just save the XSPEC spectrum object, which allows us to get the index?

    # Spectrum and response assignment
    # --------------------------------

    # 0: x-ray background
    # 1: instrumental lines
    # 2: SNR plasma model
    # 3: soft proton background
    # (maps to 1,2,3,4 in PyXSPEC methods)

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

    # Current approach -- keep ALL model-specific settings
    # * choice of rmf/arf
    # * global settings
    # * "standard" parameter links, etc
    # inside loader methods
    #
    # Loader methods require all_extrs = list of ExtractedSpectrum objects
    # that ADDITIONALLY comes with a .spec attribute, pointing to the
    # associated xs.Spectrum object......
    #
    # so maybe that should be part of the ExtractedSpectrum "spec"...

    for extr in all_extrs:
        extr.models = {}

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



def load_instr(model_n, extr, model_name):
    """Load instrumental lines.

    Import previously fitted gaussian instrumental lines.
    Fix instr line energies and norms, but allow overall norm to vary
    (i.e., all line ratios pinned to FWC line ratios)

    Currently expect 2 lines (MOS) and 7 lines (PN) modeled in FWC spectrum
    MOS lines: Al, Si
    PN lines: Al, Ti, Cr, Ni, Cu, Zn, Cu(K-beta)

    WARNING -- input argument is a single spectrum, not a list

    Input: ...
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
    elif case == 'xrb':
        src = None
    else:
        raise Exception("Invalid snr model: {} not recognized".format(case))

    # Set individal spectrum parameters
    for extr in extracted_spectra:
        src_curr = xs.AllModels(extr.spec.index, model_name)
        # Apply backscal ratio scalings
        #src_curr.constant.factor = extr.backscal() / ExtractedSpectrum.FIDUCIAL_BACKSCAL
        src_curr.constant.factor = 1  # TODO temporary for validation of OLD results... _MAYBE WRONG_
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
    sp.powerlaw.PhoIndex = 0.4
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



class ExtractedSpectrum:
    """Contains all parameters needed to uniquely address
    a G309.2-0.6 spectrum, as created by my data pipeline

    NOTE: as defined, this class should not contain information
    about XSPEC data loading, etc.
    Other tools may tack on that information, but it's not part of the "basic"
    specification.
    """

    XMMPATH = os.environ['XMM_PATH']

    temp = fits.open(XMMPATH + "/0087940201/odf/repro/mos1S001-src-grp50.pi",
                  memmap=True)
    temp.close()
    FIDUCIAL_BACKSCAL = temp[1].header['backscal']
    del temp  # This is kind of stupid, but leads to the desired effect

    def __init__(self, obsid, exp, reg):
        """Create ExtractedSpectrum"""
        self.obsid = obsid
        self.exp = exp
        self.reg = reg
        self.instr = exp.split('S')[0]  # mos1, mos2, pn
        self.spec = None

    # It may be simpler to write the following methods as object attributes
    # since parameters should not be changed (not enforced though)

    def repro_dir(self):
        return self.XMMPATH + "/{obs}/odf/repro".format(obs=self.obsid)

    # Spectrum

    def pha(self):
        fpha = self.repro_dir()
        if self.instr == "mos1" or self.instr == "mos2":
            fpha += "/{exp}-{reg}-grp50.pi".format(exp=self.exp, reg=self.reg)
        elif self.instr == "pn":  # Use OOT substracted spectrum for PN
            fpha += "/{exp}-{reg}-os-grp50.pi".format(exp=self.exp, reg=self.reg)
        return fpha

    def qpb(self):
        return self.repro_dir() + "/{exp}-{reg}-qpb.pi".format(exp=self.exp, reg=self.reg)

    def backscal(self):
        # Repeated calls are inefficient, but this isn't the bottleneck
        pha_fits = fits.open(self.pha(), memmap=True)
        backscal = pha_fits[1].header['backscal']
        pha_fits.close()
        return backscal

    # Response files

    def rmf(self):
        return self.repro_dir() + "/{exp}-{reg}.rmf".format(exp=self.exp, reg=self.reg)

    def arf(self):
        return self.repro_dir() + "/{exp}-{reg}.arf".format(exp=self.exp, reg=self.reg)

    def arf_fwc(self):
        return self.repro_dir() + "/{exp}-{reg}-ff.arf".format(exp=self.exp, reg=self.reg)

    def rmf_diag(self):
        return self.XMMPATH + "/caldb/{}-diag.rsp".format(self.instr)

    # FWC instrumental line handling

    def fwc_fit(self):
        fjson = self.repro_dir() + "/{exp}-{reg}-ff-key-fit.json".format(exp=self.exp, reg=self.reg)
        return xs_utils.load_fit_dict(fjson)


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


