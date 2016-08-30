"""
Attempt to clarify fitting code and restructure library functions
using pandas dataframe to help address spectra.

The goal is to get around PyXSPEC's habit of referring to everything
using spectrum #s, source #s, parameter #s, etc...
End up needing to construct methods to map spectra files to PyXSPEC numbers.

So we need a mapping:
    obsid, exposure, region --> (ExtractedSpectrum, PyXSPEC Spectrum object) --> PyXSPEC number

And further need mappings for model numbers etc (responses); model number
assignment is arbitrary and depends on the order in which you load RMF/ARF
files.

Aborted or put on hold (May/June 2016).  Ends up being a lot of trouble.
"""

import os
import pandas as pd

# HIGHEST LEVEL:
# ------------------------
# address spectra by region name alone.
bkgs = g309_spectra('bkg')
srcs = g309_spectra('src')

# now we still want access to ExtractedSpectrum
# to e.g. be able to select on instrument, exposure#, etc...
# I think the safest is to simply mandate that ExtractedSpectrum comes with a
# "spec" object

# This cries out for a structured/record array format

set_energy_range('0.4', '11', [x.spec for x in bkgs])

# NEXT LEVEL DOWN - TBD...
# ------------------------

for reg in regs:
    extrs = [ ExtractedSpectrum("0087940201", "mos1S001", reg),
              ExtractedSpectrum("0087940201", "mos2S002", reg),
              ExtractedSpectrum("0087940201", "pnS003",   reg),
              ExtractedSpectrum("0551000201", "mos1S001", reg),
              ExtractedSpectrum("0551000201", "mos2S002", reg) ]

a = pd.DataFrame([ExtractedSpectrum("0087940201", "mos1S001", 'src'),
                  ExtractedSpectrum("0087940201", "mos2S002", 'src'),
                  ExtractedSpectrum("0087940201", "pnS003",   'src'),
                  ExtractedSpectrum("0551000201", "mos1S001", 'src'),
                  ExtractedSpectrum("0551000201", "mos2S002", 'src'),
                  ExtractedSpectrum("0087940201", "mos1S001", 'bkg'),
                  ExtractedSpectrum("0087940201", "mos2S002", 'bkg'),
                  ExtractedSpectrum("0087940201", "pnS003",   'bkg'),
                  ExtractedSpectrum("0551000201", "mos1S001", 'bkg'),
                  ExtractedSpectrum("0551000201", "mos2S002", 'bkg') ],
                 columns=['extr'])

# Clumsy: this duplicates information.  But, useful for filtering.
a['obsid'] = a.extr.map(lambda x: x.obsid)
a['reg'] = a.extr.map(lambda x: x.reg)
a['exp'] = a.extr.map(lambda x: x.exp)

# Even worse.
a['pha'] = a.extr.map(lambda x: x.pha())
a['qpb'] = a.extr.map(lambda x: x.qpb())
a['rmf'] = a.extr.map(lambda x: x.rmf())
a['arf'] = a.extr.map(lambda x: x.arf())
a['arf_fwc'] = a.extr.map(lambda x: x.arf_fwc())
a['rmf_diag'] = a.extr.map(lambda x: x.rmf_diag())

def load_g309_spec(extr):
    """Load ExtractedSpectrum object for G309 XMM data into XSPEC"""
    # Load each spectrum into individual datagroups because each spectrum has
    # different instrumental lines and PN contamination
    spec = spectrum_datagroup(extr.pha(), fdir=extr.repro_dir())
    spec.response = extr.rmf()
    spec.response.arf = extr.arf()
    spec.background = extr.qpb()
    return spec

a['spec'] = a.extr.map(load_g309_spec)



# Set up XRB model
# ================

# Hickox and Markevitch (2006) norm
# convert 10.9 photons cm^-2 s^-1 sr^-1 keV^-1 to photons cm^-2 s^-1 keV^-1
# sr^-1 --> XMM detector pixels (backscal unit, 0.05 arcsec^2)
exrb_norm = 10.9 * (180/pi)**-2 * 60**-4 * (1/0.05)**-2 * ExtractedSpectrum.FIDUCIAL_BACKSCAL

xrb = load_model("xrb", "constant * (apec + tbnew_gas*(powerlaw + apec))",
           set_pars={'powerlaw.PhoIndex' : 1.4,
                     'powerlaw.norm' : exrb_norm,
                     'apec.kT' : 0.256,  # Unabsorped apec (local bubble)
                     'tbnew_gas.nH' : 1.318,  # Galactic absorption
                     'apec_5.kT' : 0.648,  # Absorbed apec (galactic halo)
                     'apec.norm' : 2.89e-4,
                     'apec_5.norm' : 2.50e-3},
           spectra=a['spec'],
           rmfs=a['rmf'],
           arfs=a['arf'])

xs_utils.freeze_model(xrb)

# OPTION ONE
# ----------
def set_xrb_backscal(row):
    m = xs.AllModels(row['spec'].index, "xrb")
    m.constant.factor = row['backscal'] / ExtractedSpectrum.FIDUCIAL_BACKSCAL
    m.constant.factor.frozen = True

a.apply(set_xrb_backscal, axis=1)

# OPTION TWO
# ----------
for extr, spec in zip(a['extr'], a['spec']):
    xrb_curr = xs.AllModels(spec.index, "xrb")
    xrb_curr.constant.factor = extr.backscal() / ExtractedSpectrum.FIDUCIAL_BACKSCAL
    xrb_curr.constant.factor.frozen = True




# Set up SP model
# ===============

load_model("sp", "constant * powerlaw",
           spectra=a['spec'],
           rmfs=a['rmf_diag'],
           arfs=None)

for spec in a['spec']:

    sp_curr = xs.AllModels(spec.index, "sp")

    # Let power law indices, norms vary independently.
    # We must set index limits separately for each model; cannot initialize
    # model with bounds and then unlink because parameter limits do not
    # propagate through links
    sp_curr.powerlaw.PhoIndex.link = ""
    sp_curr.powerlaw.PhoIndex.values = "0.4, , 0, 0.1, 1, 2" # Set hard/soft limits
    sp_curr.powerlaw.PhoIndex.frozen = False
    sp_curr.powerlaw.norm.link = ""
    sp_curr.powerlaw.norm.frozen = False
    # Apply backscal ratio scalings to make comparing norms easier
    sp_curr.constant.factor = extr.backscal() / ExtractedSpectrum.FIDUCIAL_BACKSCAL
    sp_curr.constant.factor.frozen = True

           set_pars={'powerlaw.PhoIndex' : "0.4, , 0, 0.1, 1, 2"}, # Set hard/soft limits





def load_model(model_name, expression, spectra=None, rmfs=None,
        arfs=None, set_pars=None):
    """
    Add a new model.
    Increments XSPEC model number in the process.

    WARNING: do not use in insecure code... subject to injection attack
    due to eval use.

    spectra: required keyword argument, takes a list
    setpars: keys are "comp_name.param_name"

    Special cases: rmfs = None and arfs = None are OK
    if rmfs = None, arfs must be None
    """
    if rmfs is None:
        assert arfs is None:
        rmfs = ["none"] * len(spectra)
    else:
        assert len(rmfs) == len(spectra)

    if arfs is None:
        arfs = ["none"] * len(spectra)
    else:
        assert len(arfs) == len(spectra)

    for spec, rmf, arf in zip(spectra, rmfs, arfs):
        spec.multiresponse[model_n - 1] = rmf
        spec.multiresponse[model_n - 1].arf = arf

    model_n = len(xs.AllModels.sources) + 1  # XSPEC 1-based model numbering

    m = xs.Model(expression, model_name, model_n)

    if set_pars is not None:
        # Convert named parameters into XSPEC model indices
        set_pars_trans = {}
        for comp_par, value in set_pars.items():
            idx = eval("m." + comp_par + ".index")
            set_pars_trans[idx] = value
        m.setPars(set_pars_trans)

    return m


def spectrum_datagroup(fname, fdir='.'):
    """Load a spectrum into a new XSPEC data group.
    XSPEC spectrum and data group numbers both increase by one.
    Input:
        fname: spectrum file name (OGIP PHA)
        fdir (optional): spectrum's directory (avoid pyXSPEC blocking behavior)
            defaults to cwd
    Returns:
        xspec.Spectrum object
    """
    old_wd = os.getcwd()
    os.chdir(fdir)

    # PyXSPEC manual: this is the only way to specify a new data group
    xs.AllData("{:d}:{:d} {:s}".format(xs.AllData.nGroups + 1,
                                       xs.AllData.nSpectra + 1, fname)
    os.chdir(old_wd)

    return xs.AllData(xs.AllData.nSpectra + 1)


