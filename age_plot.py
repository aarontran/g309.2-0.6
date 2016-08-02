"""
Plot age curves from Sedov vs. plasma fit
"""

from __future__ import division

import numpy as np
import matplotlib.pyplot as plt

def main():
    d5_domain = np.linspace(0, 2, 100)
    plt.fill_between(d5_domain, sedov_age(d5_domain, 1, 0.1), sedov_age(d5_domain, 1, 1),
                     label='Sedov age, $E_{51} = 1$, $n_0 \in [0.1, 1]$',
                     color='blue', alpha=0.25)

    plt.fill_between(d5_domain, tau_age(d5_domain, 0.2), tau_age(d5_domain, 1),
                     label=r'$\tau$-derived age, $f \in [0.2,1]$',
                     color='red', alpha=0.25)

    plt.plot(d5_domain, tau_age(d5_domain, 1), )
    plt.xlabel(r'Distance $d_{5}$, scaled to 5 kpc')
    plt.ylabel('Remnant age (yr)')
    #plt.legend(loc='best')
    plt.tight_layout()
    plt.savefig('fig_age_plot.pdf')
    plt.show()

def sedov_age(d5, E51, n0):
    return 4300 * d5**(5/2) * (E51 / n0)**(-1/2)

def tau_age(d5, f):
    return 5000 * d5**(1/2) * f**(1/2)


if __name__ == '__main__':
    main()
