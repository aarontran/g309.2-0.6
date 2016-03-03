"""
Utility methods for PyXSPEC usage
"""

import json

import xspec as xs


def load_fit_dict(f_in):
    """Load fit info from filename f_in"""
    with open(f_in, 'r') as fh:
        fdict = json.load(fh)
    return fdict


def dump_fit_dict(f_out, *args, **kwargs):
    """Dump fit info to filename f_out; see fit_dict for *args, **kwargs"""
    with open(f_out, 'w') as fh:
        ret = json.dump(fit_dict(*args), fh)
    return ret


def fit_dict(model, want_err=False):
    """
    Form dictionary of fit parameters.
    Mostly useful for simple fits: one or two models, one spectrum.
    For more complex fits, dict will not encode/store enough information
    to retrace fit.

    Warning: want_err runs XSPEC error command.  This is time consuming and
    may find new local chi-squared minima in the process.
    Don't use this unless your fit is really simple.

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

        # Component object, e.g. m.gaussian1
        comp = eval('model.'+cname)  # E.g., model.
        fdict['comps'][cname] = {}

        for pname in comp.parameterNames:

            # Parameter object, e.g. p = m.srcutlog.break
            if "srcutlog" in cname and pname == 'break':
                # Hacky workaround for local model
                p = comp.__getattribute__('break')
            else:
                p = eval('model.'+cname+'.'+pname)

            fdict['comps'][cname][pname] = {}
            fdict['comps'][cname][pname]['value'] = p.values[0]
            if want_err:
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
