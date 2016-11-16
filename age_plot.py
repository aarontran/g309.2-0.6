"""
Plot age curves from Sedov vs. plasma fit
"""

from __future__ import division

import numpy as np
import matplotlib.pyplot as plt

def main():
    """Create age plot"""
    d5_domain = np.linspace(0, 2, 100)

    plt.fill_between(d5_domain, sedov_age(d5_domain, 1, 0.1), sedov_age(d5_domain, 1, 1),
                     label='S-T age, $n_0 \in [0.1, 1]$',
                     color='blue', alpha=0.25)

    plt.fill_between(d5_domain, tau_age(d5_domain, 0.1), tau_age(d5_domain, 1),
                     label=r'$\tau$ age, $f \in [0.1,1]$',
                     color='red', alpha=0.25)

    plt.axhspan(st_time_for_arbitrary_density(1, 1.4, 1.0),
                st_time_for_arbitrary_density(1, 1.4, 0.1),
                color='black', alpha=0.1)
    plt.axhline(st_time_for_arbitrary_density(1, 1.4, 1.0),
                color='black', alpha=0.5)

    # Mej = 1.4 M_sun, i.e. use M_chandrasekhar.
    #plt.semilogy(d5_domain, st_time_with_norm_derived_density(d5_domain, 1, 1.4, 1), color='black', ls=':')


    plt.semilogy(d5_domain, sedov_age(d5_domain, 1, 1), color='blue')
    plt.semilogy(d5_domain, tau_age(d5_domain, 1), color='red')

    plt.xlabel(r'Distance $d_{5}$, scaled to 5 kpc')
    plt.ylabel('Remnant age (yr)')
    plt.ylim(10, 50000)
    plt.legend(loc='lower right', frameon=False)
    plt.tight_layout()
    plt.savefig('ms/fig_age_plot.pdf')
    plt.show()

def sedov_age(d5, E51, n0):
    return 4300 * d5**(5/2) * (E51 / n0)**(-1/2)

def tau_age(d5, f):
    # 7000 computed from 2.2e10 s cm^{-3} / (0.1 f^{-1/2} d_5^{-1/2} cm^{-3})
    return 7000 * d5**(1/2) * f**(1/2)

def st_time_with_norm_derived_density(d5, E51, Mej, f):
    """ST time of Truelove & Mckee 1997
    d5: distance scaled to 5 kpc
    E51: energy scaled to 10^51 ergs
    Mej: ejecta mass in units of Msun
    f: filling factor in [0, 1]
    """
    return 1600 * E51**(-1/2) * Mej**(5/6) * (f * d5)**(1/6)

def st_time_for_arbitrary_density(E51, Mej, n0):
    """ST time of Truelove & Mckee 1997
    d5: distance scaled to 5 kpc
    E51: energy scaled to 10^51 ergs
    Mej: ejecta mass in units of Msun
    n0: ambient number density in units 1 cm^{-3}
    """
    # 310 is appropriate for scale factor
    # 0.732 * (10^51 erg)^(-1/2) * (1.99e33 grams)^(5/6) * (1 cm^-3 * 1.4 * 1.67e-24 grams)^(-1/3)
    # which we adopt here
    return 310 * E51**(-1/2) * Mej**(5/6) * n0**(-1/3)

if __name__ == '__main__':
    main()
