"""
Utility methods for PyXSPEC usage
"""

import json
import os

import xspec as xs


# --------------------------------------
# Methods for manipulating XSPEC objects
# --------------------------------------

def get_models_for_spec(spectrum):
    """Get all active XSPEC models for a given spectrum object's data group

    In practice, my spectra usually have data group == index (i.e., ignore data
    group entirely because each spectrum has some independent parameter...
    different XMM instrumental lines, SP contamination model)

    WARNING: not tested on models with no names (i.e. really simple fit cases).
    This should be an easy fix (TODO).

    Input: XSPEC spectrum object
    Output: list of `xspec.Model` objects, ordered by source number
    """
    # Suppress "Spectrum X has no response for source Y" console warnings
    # that appear at chattiness >= 10
    old_chatter = xs.Xset.chatter
    old_logChatter = xs.Xset.logChatter
    xs.Xset.chatter = 9
    xs.Xset.logChatter = 9

    models = []
    for idx in sorted(xs.AllModels.sources):
        # Hack: if spectrum has no response for source number idx,
        # XSPEC throws a generic Exception (hence the generic "except")
        # This is the only way I know of to get a spectrum's source #s
        try:
            spectrum.multiresponse[idx-1]  # convert to 0-based index
        except:
            continue
        model_name = xs.AllModels.sources[idx]
        models.append(xs.AllModels(spectrum.dataGroup, model_name))

    xs.Xset.chatter = old_chatter
    xs.Xset.logChatter = old_logChatter

    return models


def load_spec(spec_number, spec_path, background=None, default_dir=None):
    """
    More robust spectrum load (wrapper for PyXSPEC methods)

    Args:
        number: XSPEC spectrum number (1-based)
        spec_path: filename of spectrum
        background: (optional) filename of background spectrum, to be subtracted
        default_dir: (optional) if spectrum PHA arf/rmf/bkg are not found,
            XSPEC will hang, so provide correct directory if needed
    Returns:
        newly created xspec.Spectrum instance
    """
    old_wd = os.getcwd()
    if default_dir is not None:
        os.chdir(default_dir)

    xs.AllData("{n}:{n} {fname}".format(n=spec_number, fname=spec_path))
    spec = xs.AllData(spec_number)
    if background is not None:
        spec.background = background
    os.chdir(old_wd)

    return spec


def freeze_model(model):
    """Freeze all parameters in a given model"""
    for cname in model.componentNames:
        comp = model.__getattribute__(cname)
        freeze_component(comp)

def freeze_component(comp):
    """Freeze all parameters in a given component"""
    for pname in comp.parameterNames:
        par = comp.__getattribute__(pname)
        par.frozen=True


def par_num(model, par):
    """Get XSPEC parameter number _within a given model_.
    Used for parameter linking, error runs

    An XSPEC SOURCE comprises distinct models for each datagroup:
    > Model sp:constant<1>*powerlaw<2> Source No.: 2   Active/On
    > ...
    > Model Model Component  Parameter  Unit     Value
    >  par  comp
    >                            Data group: 1
    >    1    1   constant   factor              6.11503E-02  frozen
    >    2    2   powerlaw   PhoIndex            0.672563     +/-  2.64957E-02
    >    3    2   powerlaw   norm                0.174048     +/-  8.98516E-03
    >                            Data group: 2
    >    4    1   constant   factor              5.92835E-02  frozen
    >    5    2   powerlaw   PhoIndex            0.672563     = sp:p2
    >    6    2   powerlaw   norm                0.172186     +/-  8.50475E-03

    To link parameters, you must use XSPEC's "model par", which actually
    depends on the data group; the correct number is:

        [(data group #) - 1] * model.nParameters + par.index

    Input
        model: `xspec.Model`
        par: `xspec.Parameter`
    Output: parameter number (integer) derived from `model.startParIndex`
    """
    if par not in get_all_pars(model):
        raise ValueError("Model {} does not contain {} {:s}".format(
                model.name, par.name, par))

    # model.startParIndex = [(data group #) - 1] * model.nParameters
    return (model.startParIndex - 1) + par.index


def link_name(model, par):
    """Construct link name (string) for a given model parameter.
    (i.e., specific model & data group)

    Link soft proton power laws across MOS1, MOS2 spectra:
    >>> m1 = xs.AllModels(21, 'sp')
    >>> m2 = xs.AllModels(22, 'sp')
    >>> link = link_name(m1, m1.powerlaw.PhoIndex)
    >>> print link
    'sp:62'
    >>> m2.powerlaw.PhoIndex.link = link

    Code checks that par is contained in module:
    >>> link = link_name(m2, m1.powerlaw.PhoIndex)
    Traceback (most recent call last)
    ...
    ValueError: Model sp does not contain PhoIndex <... at 0x29422150>

    Input
        model: `xspec.Model`
        par: `xspec.Parameter`, must be contained in model
    Output: XSPEC link string
    """
    src_index = par_num(model, par)
    return "{:s}:{:d}".format(model.name, src_index)


def get_all_pars(model):
    """(convenience) Generator for xspec `Parameter` objects in model obj"""
    for comp in get_comps(model):
        for par in get_pars(comp):
            yield par

def get_pars(comp):
    """Generator for xspec `Parameter` objects in component obj"""
    for pname in comp.parameterNames:
        yield comp.__getattribute__(pname)

def get_comps(model):
    """Generator for xspec `Component` objects in model obj"""
    for cname in model.componentNames:
        yield model.__getattribute__(cname)


# ---------------------------------
# Methods for saving / dumping fits
# ---------------------------------

# Kind of self-documenting (read the methods and inspect the dicts to see what
# is serialized or not).
# Just JSON dumps, but the actual serialization is an implementation detail
# (can as easily substitute cPickle)

# Convenience wrappers

def load_dict(f_name):
    """Load a {fit,spectrum,model} dict from f_name"""
    with open(f_name, 'r') as fh:
        dict_obj = json.load(fh)
    return dict_obj


def dump_dict(dict_obj, f_name):
    """Dump a {fit,spectrum,model} dict to f_name"""
    with open(f_name, 'w') as fh:
        ret = json.dump(dict_obj, fh, indent=2)
    return ret


def fit_dict():
    """Construct serializable dict of current XSPEC fit information

    Hierarchy: fit -> spectrum -> model
    (yes, there will be considerable redundancy where multiple spectra are
    fitted to a single model)

    Input: none
    Output: dict of fit information
        fitted models
    """
    fdict = {}
    fdict['dof'] = xs.Fit.dof
    fdict['method'] = xs.Fit.method  # fitting algorithm

    # Use my own naming for the fit/test statistic methods & values
    fdict['fitStatMethod'] = xs.Fit.statMethod  # "type of fit statistic in use"
    fdict['testStatMethod'] = xs.Fit.statTest  # "type of test statistic in use"
    fdict['fitStat'] = xs.Fit.statistic  # fit statistic value
    fdict['testStat'] = xs.Fit.testStatistic  # test statistic value

    for x in range(xs.AllData.nSpectra):
        idx = x+1  # Convert to XSPEC's 1-based numbering
        fdict[idx] = spectrum_dict(xs.AllData(idx))

    return fdict


def spectrum_dict(s):
    """Construct serializable dict of spectrum metadata and fitted models
    Input: `xspec.Spectrum` object
    Output: dict of important spectrum information, including dicts of all
        fitted models
    """
    sdict = {}
    sdict['fileName'] = s.fileName
    sdict['index'] = s.index
    sdict['dataGroup'] = s.dataGroup
    try:
        sdict['background'] = s.background.fileName
    except:
        sdict['background'] = None
    sdict['ignoredString'] = s.ignoredString()

    # Arguably can get from FITS or compute yourself, but useful to attach
    sdict['areaScale'] = s.areaScale
    sdict['backScale'] = s.backScale
    sdict['exposure'] = s.exposure
    sdict['rate'] = s.rate

    for m in get_models_for_spec(s):
        sdict[m.name] = model_dict(m)

    return sdict


def model_dict(m):
    """Construct serializable dict of model metadata and parameters

    Not all information stored (e.g., m.energies(...), m.values(...),
    m.folded(...) which require `<xspec.Spectrum>.index` are not saved)

    `componentNames` and `parameterNames` preserve XSPEC's component/parameter
    ordering, and may help reconstruct parameter numbers

    Input: `xspec.Model` object
    Output: dict of important model information (component, parameter names,
        values, errors, etc)
    """
    mdict = {}
    mdict['name'] = m.name
    mdict['expression'] = m.expression
    mdict['componentNames'] = m.componentNames
    mdict['nParameters'] = m.nParameters
    mdict['startParIndex'] = m.startParIndex

    for cname in m.componentNames:
        c = m.__getattribute__(cname)

        mdict[cname] = {}
        mdict[cname]['parameterNames'] = c.parameterNames

        for pname in c.parameterNames:
            p = c.__getattribute__(pname)

            mdict[cname][pname] = {}
            mdict[cname][pname]['value'] = p.values[0]
            mdict[cname][pname]['error'] = p.error
            mdict[cname][pname]['sigma'] = p.sigma
            mdict[cname][pname]['frozen'] = p.frozen
            mdict[cname][pname]['link'] = p.link
            mdict[cname][pname]['unit'] = p.unit

    return mdict


def dump_fit_log(f_name):
    """
    Dump current data, model, fit information to log file
    Input: f_name, file to write log information
    Output: None
    """
    logChatter_orig = xs.Xset.logChatter
    xs.Xset.logChatter = 10
    xs.Xset.openLog(f_name)

    xs.AllData.show()
    xs.AllModels.show()
    xs.Fit.show()

    xs.Xset.logChatter = logChatter_orig
    xs.Xset.closeLog()


if __name__ == '__main__':
    pass
