#!/usr/local/bin/python
"""
Make nicer plots to see what's going on
"""

import argparse
import matplotlib.pyplot as plt
import numpy as np

def main():
    """ Make plots """

    parser = argparse.ArgumentParser(description="Make nice separated plots")
    parser.add_argument('files', metavar='file', nargs='+',
                        help=("Whitespace delimited data files, "
                              "as output by xs_wdata_split.pl"))
    args = parser.parse_args()

    fnames = args.files
    n = len(fnames)

    # Plot data and models
    fig, axes = plt.subplots(n, sharex=True, figsize=(13, n*3.5))
    for fname, ax in zip(fnames, axes):

        dat = np.loadtxt(fname)
        x       = dat[:,0]
        x_err   = dat[:,1]
        y       = dat[:,2]
        y_err   = dat[:,3]
        model_sum   = dat[:,4]

        n_models = dat.shape[1] - 5  # Hardcoded
        # Note - this should also work for n_models = 1
        # (where XSPEC could only print 5 columns, I don't think it does)
        # but I have not tested this

        plot_err(x, y, x_err, y_err, ax=ax, capsize=0, ls='none', elinewidth=1)
        plot_step(x, x_err, model_sum, ax=ax, color='k')  # Summed model

        # 5 colors from http://colorbrewer2.org/
        # qualitative "5-class Set1" scheme
        colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00']
        if len(colors) <  n_models:
            raise Exception("More models than colors!")

        for model, color in zip(dat[:,5:].T, colors):
            plot_step(x, x_err, model, ax=ax, color=color)

        #ax.set_ylim(1e-3, 10.0)  # Appropriate for (INTEGRATED) source
        ax.set_ylim(1e-4, 1.0)  # Appropriate for smaller regions
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlim(0.3, 11.0)

    plt.tight_layout()

    # Plot residuals (copy-pasted code)
    fig2, axes2 = plt.subplots(n, sharex=True, figsize=(13, n*3.5))
    for fname, ax in zip(fnames, axes2):

        dat = np.loadtxt(fname)
        x       = dat[:,0]
        x_err   = dat[:,1]
        y       = dat[:,2]
        y_err   = dat[:,3]
        model_sum   = dat[:,4]

        # Residual ratio
        ax.errorbar(x, (y - model_sum)/model_sum,
                    xerr=x_err, yerr=(y_err / model_sum),
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
    yerr_low[yerr >= y] = 0.99999999 * y[yerr >= y]  # Force lower error bound to 1e-8 above zero
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
