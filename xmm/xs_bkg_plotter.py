"""
Make nicer plots to see what's going on
"""

import argparse
import matplotlib.pyplot as plt
import numpy as np

def main():
    """ Make plots """

    parser = argparse.ArgumentParser(description="Make nice separated plots")
    parser.add_argument('--stem', default='snr', help="prefix stem for 5 dat files")
    parser.add_argument('--reg', default='snr', help="region (bkg or snr)")
    args = parser.parse_args()
    stem, reg = args.stem, args.reg
    stem = args.stem

    if (reg != "bkg" and reg != "snr"):
        raise Exception("bad reg")

    #fnames=["bkg_m1.dat",
    #        "bkg_m2.dat",
    #        "bkg_pn.dat",
    #        "bkg_m1motch.dat",
    #        "bkg_m2motch.dat"]

    fnames = [stem + x for x in
        ["_m1.dat", "_m2.dat", "_pn.dat", "_m1motch.dat", "_m2motch.dat"]]

    fig, axes = plt.subplots(5, sharex=True, figsize=(18, 18))
    for fname, ax in zip(fnames, axes):

        a = np.loadtxt(fname)
        x = a[:,0]
        x_err = a[:,1]

        plot_err(x, a[:,2], x_err, a[:,3], ax=ax, capsize=0, ls='none', elinewidth=1)
        plot_step(x, x_err, a[:,4], ax=ax, color='k')  # Summed model
        if (reg == "bkg"):
            plot_step(x, x_err, a[:,5], ax=ax, color='r')  # X-ray background
            plot_step(x, x_err, a[:,6], ax=ax, color='y')  # Instrumental lines
            plot_step(x, x_err, a[:,7], ax=ax, color='c')  # SP power law
        elif (reg == "snr"):
            plot_step(x, x_err, a[:,5], ax=ax, color='r')  # X-ray background
            plot_step(x, x_err, a[:,6], ax=ax, color='y')  # Instrumental lines
            plot_step(x, x_err, a[:,7], ax=ax, color='g')  # SNR model
            plot_step(x, x_err, a[:,8], ax=ax, color='c')  # SP power law

        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlim(0.3, 11.0)
        ax.set_ylim(1e-4, 1.0)

    plt.tight_layout()

    # AD HOC copy-pasta to plot residuals.
    fig2, axes2 = plt.subplots(5, sharex=True, figsize=(18, 18))
    for fname, ax in zip(fnames, axes2):

        a = np.loadtxt(fname)
        x = a[:,0]
        x_err = a[:,1]

        # Residual ratio
        ax.errorbar(x, (a[:,2] - a[:,4])/a[:,4],
                xerr=x_err, yerr=(a[:,3] / a[:,4]),
                capsize=0, ls='none', elinewidth=1)

        ax.axhline(y=0, color='k')
        ax.set_xscale("log")
        ax.set_xlim(0.3, 11.0)
        ax.set_ylim(-1.5, 1.5)  # Appropriate for residual ratio plot

    plt.tight_layout()


    plt.show()


def plot_err(x, y, xerr, yerr, ax=None, **kwargs):
    """Plot x and y error bars, with custom tweak to force lower y-errors > 0
    Based on: stackoverflow.com/a/13492914/
    """
    if ax is None:
        ax = plt.gca()

    yerr_low = np.array(yerr)  # Don't modify external yerr
    yerr_low[yerr >= y] = 0.99999999 * y[yerr >= y]  # Push errorbar to 1e-8 above zero
    ax.errorbar(x, y, xerr=xerr, yerr=(yerr_low, yerr), **kwargs)


def plot_step(xmid, xerr, y, ax=None, **kwargs):
    """Plot with XSPEC-style steps based on x errorbars"""
    if ax is None:
        ax = plt.gca()
    ax.plot(np.append(xmid - xerr, (xmid[-1] + xerr[-1])),
            np.append(y, y[-1]),
            drawstyle='steps-post', **kwargs)


if __name__ == '__main__':
    main()
