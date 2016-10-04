"""
Interface to XMM reduction pipeline products
"""

import os
from astropy.io import fits
import xspec_utils as xs_utils

class ExtractedSpectrum:
    """Interface to G309.2-0.6 spectrum and ancillary files from my pipeline"""

    XMMPATH = os.environ['XMM_PATH']

    temp = fits.open(XMMPATH + "/0087940201/repro/mos1S001-src.pi",
                     memmap=True)
    temp.close()
    FIDUCIAL_BACKSCAL = temp[1].header['backscal']
    del temp  # This is kind of roundabout, but leads to the desired effect

    def __init__(self, obsid, exp, reg, suffix="grp01", marfrmf=False):
        """Create ExtractedSpectrum
        suffix: specify desired grouping via filename suffix (grp01 or grp50)
        marfrmf: iff exp="mosmerge", marfrmf=True specifies use of
            merged pre-multiplied arf/rmf files (which should be a more
            "correct" weighting)
        """
        self.obsid = obsid
        self.exp = exp
        self.reg = reg
        self.instr = exp.split('S')[0]  # mos1, mos2, pn; mosmerge (special case)
        self.suffix = suffix
        self.spec = None
        self.marfrmf = marfrmf

        assert obsid in ["0087940201", "0551000201"]
        assert suffix in ["grp01", "grp50"]

    def __repr__(self):
        return "ExtractedSpectrum({}, {:>8s}, {})".format(self.obsid, self.exp,
                self.reg)

    def __str__(self):
        return __repr__()

    # It may be simpler to write the following methods as object attributes
    # since parameters should not be changed (not enforced though)

    def repro_dir(self):
        # Cannot use SAS_REPRO because that precludes use with multiple obsids
        return self.XMMPATH + "/{obs}/repro".format(obs=self.obsid)

    # Spectrum

    def pha(self):
        fpha = self.repro_dir()
        if self.instr in ["mos1", "mos2", "mosmerge"]:
            fpha += "/{exp}-{reg}-{suff}.pi".format(exp=self.exp, reg=self.reg, suff=self.suffix)
        elif self.instr == "pn":  # Use OOT substracted spectrum for PN
            fpha += "/{exp}-{reg}-os-{suff}.pi".format(exp=self.exp, reg=self.reg, suff=self.suffix)
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
        if self.exp == "mosmerge" and self.marfrmf:
            return self.repro_dir() + "/{exp}-{reg}.marfrmf".format(exp=self.exp, reg=self.reg)
        return self.repro_dir() + "/{exp}-{reg}.rmf".format(exp=self.exp, reg=self.reg)

    def arf(self):
        if self.exp == "mosmerge" and self.marfrmf:
            return None
        return self.repro_dir() + "/{exp}-{reg}.arf".format(exp=self.exp, reg=self.reg)

    # RMF/ARF files to fit instrumental lines in observation data
    # mosmerge should use "-ff-instr" (merger weighted by obs exposure times)
    # instead of "-ff" (merger weighted by FWC file exposure times)

    def rmf_instr(self):
        if self.exp == 'mosmerge':
            if self.marfrmf:
                return self.repro_dir() + "/{exp}-{reg}-ff-instr.marfrmf".format(exp=self.exp, reg=self.reg)
            else:
                return self.repro_dir() + "/{exp}-{reg}-ff-instr.rmf".format(exp=self.exp, reg=self.reg)
        return self.repro_dir() + "/{exp}-{reg}-ff.rmf".format(exp=self.exp, reg=self.reg)

    def arf_instr(self):
        if self.exp == 'mosmerge':
            if self.marfrmf:
                return None
            else:
                return self.repro_dir() + "/{exp}-{reg}-ff-instr.arf".format(exp=self.exp, reg=self.reg)
        return self.repro_dir() + "/{exp}-{reg}-ff.arf".format(exp=self.exp, reg=self.reg)

    def rmf_diag(self):
        if self.instr == "mosmerge":
            # mos1/mos2 basically same, ok for merged mos
            return self.XMMPATH + "/caldb/mos1-diag.rsp"
        return self.XMMPATH + "/caldb/{}-diag.rsp".format(self.instr)

    # FWC instrumental line handling

    def fwc_fit(self):
        fjson = self.repro_dir() + "/{exp}-{reg}-ff-fit.json".format(exp=self.exp, reg=self.reg)
        return xs_utils.load_dict(fjson)
