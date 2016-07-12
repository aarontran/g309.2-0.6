"""
Utility methods for PyXSPEC usage
"""

import json
import os

import xspec as xs


def get_models_for_spec(spectrum):
    """Get all active XSPEC models for a given spectrum object

    Input: XSPEC spectrum
    Output: list of models, ordered by XSPEC source number
    """
    # Suppress "Spectrum X has no response for source Y" console warnings
    # that appear at chattiness >= 10
    old_chatter = xs.Xset.chatter
    old_logChatter = xs.Xset.logChatter
    xs.Xset.chatter = 9  # Threshold for
    xs.Xset.logChatter = 9

    source_numbers = []
    for idx in xs.AllModels.sources:  # source numbers start from 1
        try:
            # If spectrum has no response for source number idx,
            # XSPEC throws a generic Exception (hence the generic "except")
            spectrum.multiresponse[idx-1]  # convert to 0-based index
            source_numbers.append(idx)
        except:
            pass

    models = []
    for idx in sorted(source_numbers):
        model_name = xs.AllModels.sources[idx]
        models.append(xs.AllModels(spectrum.index, model_name))

    xs.Xset.chatter = old_chatter
    xs.Xset.logChatter = old_logChatter

    return models



# --------------------------------
# Methods for manipulating spectra
# --------------------------------

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


# -------------------------------------------------------
# Methods for manipulating models, components, parameters
# -------------------------------------------------------

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


# TODO WARNING
# to set parameters.... only par.index matters
# do NOT use startParIndex, or par_num as given by xs_utils.par_num
def par_num(model, par):
    """Stolen, with modification, from G. Schellenberger slides:
    https://astro.uni-bonn.de/~yyzhang/seminar/pdf/Gerrit.pdf
    """
#    if comp.name not in model.componentNames:
#        return -1
#    if par.name not in comp.parameterNames:
#        return -1
    return model.startParIndex - 1 + par.index


# TODO DOCUMENT AND EXPLAIN
#
# parameters have index, valid within indiv. model (xspec.Model object
# comprised of EXPRESSION + SOURCE NUMBER + MODEL NAME created for a given
# datagroup, that has a matching SOURCE NUMBER).
#
# For a given SOURCE NUMBER, this creates multiple models -- one for each
# datagroup; in general these models are somehow tied together
# because they physically represent the same SOURCE.
# Parameters for linking are ordered then by
# 1. spectrum (datagroup) number,
# 2. within-model number
#
# Then, to link parameters, use MODEL_NAME : SOURCE_INDEX
#
# EXAMPLE: to tie mos1 and mos2 power law indices
#
#    sp_mos2.powerlaw.PhoIndex.link = link_name(sp_mos1, sp_mos1.powerlaw.PhoIndex)
#
# The repetition of "sp_mos1" is required because parameters have no knowledge
# of their containing component or model, and parameter names are non-unique
# within a model (e.g., model with two apec components)
# Thus required to identify both component and parameter --
# may as well just call out the parameter directly
def link_name(model, par):
    """WARNING: assumes par is actually a parameter within model
    AND THAT THEY COME FROM THE SAME DATAGROUP!
    """
    src_index = (model.startParIndex - 1) + par.index
    return "{:s}:{:d}".format(model.name, src_index)


# ---------------------------------
# Methods for saving / dumping fits
# ---------------------------------

def load_fit_dict(f_in):
    """Load fit info from filename f_in"""
    with open(f_in, 'r') as fh:
        fdict = json.load(fh)
    return fdict


def dump_fit_dict(f_out, *args, **kwargs):
    """Dump fit info to filename f_out; see fit_dict for *args, **kwargs"""
    with open(f_out, 'w') as fh:
        ret = json.dump(fit_dict(*args, **kwargs), fh, indent=2)
    return ret


def fit_dict(model):
    """
    Form dictionary of fit parameters.
    Mostly useful for simple fits: one or two models, one spectrum.
    For more complex fits, dict will not encode/store enough information
    to retrace fit.

    Wishlist:
    - generalize to multiple source models for given datagroup
    - print out all dependencies (simultaneously fit spectra, etc.)
    """
    fdict = {}
    fdict['fitstat'] = (xs.Fit.statMethod, xs.Fit.statistic)
    fdict['dof'] = xs.Fit.dof

    fdict['expression'] = model.expression

    # Crappy way to extract component values and errors
    # Dict looks like: fdict['comps']['gaussian']['sigma']['value']
    fdict['comps']={}

    for cname in model.componentNames:
        comp = model.__getattribute__(cname)

        fdict['comps'][cname] = {}

        for pname in comp.parameterNames:
            p = comp.__getattribute__(pname)

            fdict['comps'][cname][pname] = {}
            fdict['comps'][cname][pname]['value'] = p.values[0]
            fdict['comps'][cname][pname]['error'] = p.error
            fdict['comps'][cname][pname]['sigma'] = p.sigma
            fdict['comps'][cname][pname]['frozen'] = p.frozen

    return fdict


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
