"""
Interface to XMM reduction pipeline products
"""

import os
from astropy.io import fits
import xspec_utils as xs_utils

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
