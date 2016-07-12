#!/usr/local/bin/python

from __future__ import division

import xspec as xs

from g309_fits import *
import xspec_utils as xs_utils
from nice_tables import LatexTable

def expanded_tables(output):
    """Dump tables with current elemental abundance variations"""

    rings = [xs.AllModels( 1,'snr_ann_000_100'),
             xs.AllModels( 6,'snr_ann_100_200'),
             xs.AllModels(11,'snr_ann_200_300'),
             xs.AllModels(16,'snr_ann_300_400')]
#             xs.AllModels(21,'snr_ann_400_500')]

    latex_hdr = [['Annulus', ''],
                 [r'$n_\mathrm{H}$', r'($10^{22} \unit{cm^{-2}}$)'],
                 [r'$kT$', r'(keV)'],
                 [r'$\tau$', r'($10^{10} \unit{s\;cm^{-3}}$)'],
                 ['O', '(-)'],
                 ['Ne', '(-)'],
                 ['Mg', '(-)'],
                 ['Si', '(-)'],
                 ['S', '(-)'],
                 ['Fe', '(-)']]
    latex_hdr = np.array(latex_hdr).T

    latex_cols = ['{:s}', 2, 2, 2, 2, 2] + 4 * [2]  # O, Ne, Mg, Fe
    ltab = LatexTable(latex_hdr, latex_cols, "G309.2-0.6 annuli fit with errors", prec=3)

    for ring in rings:
        ltr = [ring.name]
        ltr.extend(val_errs(ring.tbnew_gas.nH))
        ltr.extend(val_errs(ring.vnei.kT))
        ltr.extend([ring.vnei.Tau.values[0] / 1e10,
                    err_pos(ring.vnei.Tau) / 1e10,
                    err_neg(ring.vnei.Tau) / 1e10])
        ltr.extend(val_errs(ring.vnei.O))
        ltr.extend(val_errs(ring.vnei.Ne))
        ltr.extend(val_errs(ring.vnei.Mg))
        ltr.extend(val_errs(ring.vnei.Si))
        ltr.extend(val_errs(ring.vnei.S))
        ltr.extend(val_errs(ring.vnei.Fe))

        ltab.add_row(*ltr)

    with open(output + "_ONeMgFe.tex", 'w') as f_tex:
        f_tex.write(str(ltab))
    with open(output + "_ONeMgFe_row.tex", 'w') as f_tex:
        f_tex.write('\n'.join(ltab.get_rows()))
