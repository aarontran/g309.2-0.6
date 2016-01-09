"""
Plot behavior of XSPEC TBabs*vnei model for various parameters
"""

#import json
import matplotlib.pyplot as plt
#import numpy as np

import xspec as xs

# Deliberately populate global scope for interactive use (%run in iPython)
# Incredibly ugly code but it's good enough for a one-off job

# "Global" settings
xs.Plot.device = "/xw"
xs.Plot.xAxis = "keV"
xs.Xset.abund = "wilm"
#xs.Plot.yLog = True
#xs.Plot.background = True

s = xs.Spectrum("mos1S001-src.fak")
s.ignore("**-0.4, 10.0-**")

m = xs.Model("tbabs*vnei")

## SET UP SOME METHODS

def m_default():
    m.vnei.kT = 1
    m.vnei.Tau = 1e11
    m.TBabs.nH = 1
    m.vnei.S = 1
    m.vnei.Si = 1
    m.vnei.Fe = 1

def add_curve(lab, col=None):
    xs.Plot("ldata")
    x = xs.Plot.x()
    y = xs.Plot.model()
    if col:
        plt.loglog(x, y, c=col, label=lab)
    else:
        plt.loglog(x, y, label=lab)

def annotate_plot():
    """Add prominent X-ray lines for highly ionized states
    set plot limits, tick labels,
    """

    # He alpha
    plt.axvline(0.57, ls='-', color='k', alpha=0.5)  # O VII
    plt.axvline(0.91, ls='-', color='k', alpha=0.5)  # Ne IX
    plt.axvline(1.34, ls='-', color='k', alpha=0.5)  # Mg XI
    plt.axvline(1.85, ls='-', color='k', alpha=0.5)  # Si XIII
    plt.axvline(2.45, ls='-', color='k', alpha=0.5)  # S XV
    plt.axvline(3.12, ls='-', color='k', alpha=0.5)  # Ar XVII
    plt.axvline(3.88, ls='-', color='k', alpha=0.5)  # Ca XIX, broad
    # Skip Ti, Cr
    plt.axvline(6.68, ls='-', color='k', alpha=0.5)  # Fe XXV, broad line
        # Smeared with Ly alpha -> K alpha, generally

    # He beta
    plt.axvline(0.67, ls=':', color='g', alpha=1)  # O VII
    plt.axvline(1.07, ls=':', color='g', alpha=1)  # Ne IX
    plt.axvline(1.58, ls=':', color='g', alpha=1)  # Mg XI
    plt.axvline(2.18, ls=':', color='g', alpha=1)  # Si XIII
    plt.axvline(2.89, ls=':', color='g', alpha=1)  # S XV
    plt.axvline(3.69, ls=':', color='g', alpha=1)  # Ar XVII

    # Ly alpha
    plt.axvline(2.00, ls=':', color='b', alpha=1)  # Si XIV
    plt.axvline(2.38, ls=':', color='b', alpha=1)  # S XVI
    # Ly beta
    plt.axvline(2.62, ls=':', color='b', alpha=1)  # Si XIV
    plt.axvline(3.11, ls=':', color='b', alpha=1)  # S XVI

    plt.xlim(0.4, 10)
    plt.ylim(1e-3, 1e3)

    tickpos = [0.5, 1, 2, 5, 10]
    plt.xticks(tickpos, map(str, tickpos))
    plt.tick_params(length=2, axis='both', which='minor')
    plt.tick_params(length=4, axis='both', which='major')
    #plt.ticklabel_format(style='plain', axis='x')

    plt.legend(loc='best')
    plt.xlabel("Energy (keV)")
    plt.ylabel("Normalized cts/s/keV")
    plt.tight_layout()

## DO STUFF

# GENERALLY, higher kT and tau
#   --> more He->Ly (2 to 1 e- state)
#   --> more alpha-> beta (n=2->1 to n=3->1)

# First, try varying kT
m_default()
plt.figure(figsize=(10.5,8))
for var in [0.1, 0.3, 1, 3, 10]:
    m.vnei.kT = var
    add_curve("kT = {}".format(var))  # keV
annotate_plot()
plt.savefig('tbabs_vnei_var_kT.png')
plt.show()

# Next, try varying ionization timescale
m_default()
plt.figure(figsize=(10.5,8))
for var in [1e8, 5e9, 1e11, 5e13]:
    m.vnei.Tau = var
    add_curve("Tau = {:g}".format(var))  # s/cm^3
annotate_plot()
plt.savefig('tbabs_vnei_var_tau.png')
plt.show()

# Next, try varying nH absorption
m_default()
plt.figure(figsize=(10.5,8))
for var in [0.1, 0.3, 1, 3, 10]:
    m.TBabs.nH = var
    add_curve("nH = {:g}".format(var))  # 10^22 /cm^2
annotate_plot()
plt.savefig('tbabs_vnei_var_nh.png')
plt.show()

# Finally, try varying abundances (S, Si, Fe)
m_default()
plt.figure(figsize=(10.5,8))
for var in [0.1, 0.3, 1, 3, 10]:
    m.vnei.S = var
    add_curve("S = {:g}x solar".format(var))  # abundance
annotate_plot()
plt.savefig('tbabs_vnei_var_sulfur.png')
plt.show()

m_default()
plt.figure(figsize=(10.5,8))
for var in [0.1, 0.3, 1, 3, 10]:
    m.vnei.Si = var
    add_curve("Si = {:g}x solar".format(var))  # abundance
annotate_plot()
plt.savefig('tbabs_vnei_var_silicon.png')
plt.show()

m_default()
plt.figure(figsize=(10.5,8))
for var in [0.1, 0.3, 1, 3, 10]:
    m.vnei.Fe = var
    add_curve("Fe = {:g}x solar".format(var))  # abundance
annotate_plot()
plt.savefig('tbabs_vnei_var_iron.png')
plt.show()

# This depends on plot state (!)
#x = xs.Plot.x()
#xErr = xs.Plot.xErr()
#m = xs.Plot.model()

#def main():



#if __name__ == '__main__':
#    main()

