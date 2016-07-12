#!/usr/local/bin/python
"""
Plot XSPEC QDP dumps of data and model components.
Optionally plot residuals (delta chi) as well.

This program is not specific to any particular dataset, but
- x-axis range, ticks are set for XMM EPIC energies (0.3-11 keV)
- y-axis units are XSPEC standard, counts/sec/keV
- delta chi residual y-axis range is [-4,4], good for reasonable-ish fits
- plot size is optimized for about 4-5 subplots (data files)
so, some customization may be needed for your various use cases.
"""

import argparse
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from os.path import basename

def main():
    """ Make plots """

    parser = argparse.ArgumentParser(description=("Plot XSPEC QDP dumps"
                                     " of data and fitted model components."))
    parser.add_argument('files', nargs='+',
                        help=("Whitespace delimited data files"
                              " output by xs_wdata_split.pl"),
                        metavar='FILE')
    parser.add_argument('--components', nargs='*',
                        help=("Model component plot labels"),
                        metavar='COMP')
    parser.add_argument('--colors', nargs='*',
                        help=("Model component plot colors (mpl syntax)"),
                        metavar='COLOR')
    parser.add_argument('--linestyles', nargs='*',
                        help=("Model component plot linestyles (mpl syntax)."
                              " Known error: use 'solid' or 'dashed'"
                              " instead of '-', '--'.  Default: all solid."),
                        metavar='STYLE')
    parser.add_argument('--ylim', nargs=2, type=float,
                        help=("Plot y limits (default 1e-4, 1). Both low/high limits required."),
                        metavar=('LOW', 'HIGH'))
    parser.add_argument('--labels', nargs='*',
                        help=("Subplot labels"),
                        metavar='LABEL')
    parser.add_argument('--out',
                        help=("Outputs to files instead of plotting."
                              " Writes {stem}.pdf, {stem}-delchi.pdf."),
                        metavar='STEM')
    parser.add_argument('--residuals', action='store_true')
    parser.add_argument('--no-x-labels', action='store_true')

    parser.add_argument('--augment', nargs='*',
                        help=("Add model components from other QDP dumps."
                              " Must provide same number of files as ARGV."
                              " Other options: labels, components, ..."
                              " must include augmented columsn."
                              " Must provide --augment-cols."),
                        metavar='FILE')
    parser.add_argument('--augment-cols', nargs='*',
                        help=("Identify which columns (0-based) to add to plot"
                              " from --augment QDP files."),
                        type=int)
    args = parser.parse_args()

    fnames = args.files
    comp_labels= args.components
    colors = args.colors
    linestyles = args.linestyles
    opt_residuals = args.residuals
    plot_labels = args.labels
    opt_ylim = args.ylim
    opt_outstem = args.out
    opt_no_x_labels = args.no_x_labels

    opt_augment_fnames = args.augment
    opt_augment_cols = args.augment_cols

    # Begin validating arguments

    n = len(fnames)

    if not opt_augment_fnames:
        opt_augment_fnames = [None] * n
    else:
        assert len(opt_augment_cols) >= 1
    assert len(opt_augment_fnames) == n

    if not plot_labels:
        plot_labels = [None] * n
    assert len(plot_labels) == n

    if not opt_ylim:
        opt_ylim = (1e-4, 1.0)  # Appropriate for small G309 regions

    # Plot data and models
    fig, axes = plt.subplots(n, sharex=True, figsize=(7.5, n*2))
    if n == 1:
        axes = [axes]  # plt.subplots collapses unneeded dimensions
    for fname, ax, plot_lab, f_augment in zip(fnames, axes, plot_labels, opt_augment_fnames):

        dat = np.loadtxt(fname)
        x       = dat[:,0]
        x_err   = dat[:,1]
        y       = dat[:,2]
        y_err   = dat[:,3]
        model_sum   = dat[:,4]

        if f_augment:  # Stitch it on and proceed like nothing else happened
            # But save the data to plot slightly differently (lower zorder)
            dat_augment = np.loadtxt(f_augment)
            dat = np.concatenate((dat, dat_augment[:, opt_augment_cols]), axis=1)
            n_augment_models = dat_augment[:, opt_augment_cols].shape[1]

        n_models = dat.shape[1] - 5

        # Set up and plot model components
        if not colors:
            colors = [None] * n_models
        if not comp_labels:
            comp_labels = [None] * n_models
        if not linestyles:
            linestyles = ['-'] * n_models

        assert len(colors) == n_models
        assert len(comp_labels) == n_models
        assert len(linestyles) == n_models

        for model, color, lab, ls, n_m in zip(dat[:,5:].T, colors, comp_labels, linestyles, range(n_models)):
            if n_m < (n_models - n_augment_models):  # Normal models
                plot_step(x, x_err, model, ax=ax,
                          color=color, label=lab, linestyle=ls)
            else:  # Augment models
                plot_step(x, x_err, model, ax=ax,
                          color=color, label=lab, linestyle=ls,
                          zorder=0)

        # Plot summed model
        plot_step(x, x_err, model_sum, ax=ax, color='k',
                  alpha=0.8, zorder=10)

        # Plot actual data
        plot_err(x, y, x_err, y_err, ax=ax,
                 capsize=0, ls='none', elinewidth=0.6,
                 color='#377eb8', alpha=1, zorder=9)
        # TODO ensure elinewidth=0.5 is still readable in manuscript fmt

        # Prep subplot display

        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlim(0.3, 11.0)  # WARNING: hard-coded X-axis limits and ticks
        ax.set_xticks([0.5, 1, 2, 5, 10])
        ax.xaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:g}'))

        ax.set_ylim(*opt_ylim)  # Appropriate for smaller regions
        #ax.yaxis.set_major_formatter(mpl.ticker.ScalarFormatter())
        #ax.set_xticks([0.1, 1, 10])
        #ax.set_xticklabels(['0.1', '1', '10'])
        #ax.xaxis.set_minor_locator(plt.FixedLocator([0.2, 0.5, 2, 5]))

        ax.set_ylabel(r'Counts\hspace{1pt} s$^{-1}$ keV$^{-1}$')
        if plot_lab:
            ax.text(0.015, 0.93, plot_lab, ha='left', va='top',
                    transform=ax.transAxes)

        if ax is axes[-1]:
            if args.components is not None:  # do not confuse with args.labels!  TODO change to better names
                ax.legend(loc='best', prop={'size':8})
            ax.set_xlabel("Energy (keV)")

            if opt_no_x_labels:  # Only need to change on bottom plot
                ax.set_xlabel("")
                ax.set_xticklabels([])

        # Check that output plot doesn't obscure information
        print "{} data range: [{:.2g}, {:.2g}]".format(
                basename(fname), np.amin(y), np.amax(y))
        if np.amin(y) < ax.get_ylim()[0] or np.amax(y) > ax.get_ylim()[1]:
            print "    Warning: data point(s) hidden by plot y limits"

    plt.tight_layout()
    if opt_outstem:
        print "Writing: {}".format(opt_outstem + '.pdf')
        plt.savefig(opt_outstem + '.pdf')
        plt.clf()
    else:
        plt.show()

    if opt_residuals:

        print ""

        # Plot residuals (copy-pasted code)
        fig2, axes2 = plt.subplots(n, sharex=True, figsize=(7.5, n*1.5))
        if n == 1:
            axes2 = [axes2]  # plt.subplots collapses unneeded dimensions
        for fname, ax, plot_lab in zip(fnames, axes2, plot_labels):

            dat = np.loadtxt(fname)
            x       = dat[:,0]
            x_err   = dat[:,1]
            y       = dat[:,2]
            y_err   = dat[:,3]
            model_sum   = dat[:,4]

            delchi = (y - model_sum)/y_err

            # Delta chi
            ax.errorbar(x, (y - model_sum)/y_err,
                        xerr=x_err, yerr=(y_err / y_err),
                        capsize=0, ls='none', elinewidth=0.6,
                        color='#377eb8', alpha=1, zorder=9)
            # TODO ensure elinewidth=0.5 is still readable in manuscript fmt

            ax.axhline(y=0, color='k')

            # Prep subplot display

            ax.set_xscale("log")
            ax.set_xlim(0.3, 11.0)  # WARNING: hard-coded X-axis limits and ticks
            ax.set_xticks([0.5, 1, 2, 5, 10])
            ax.xaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:g}'))

            ax.set_ylim(-4, 4)  # Appropriate for residual ratio plot

            ax.set_ylabel(r'$\Delta\chi$')
            if plot_lab:
                ax.text(0.015, 0.92, plot_lab, ha='left', va='top',
                        transform=ax.transAxes)

            if ax is axes2[-1]:
                ax.set_xlabel("Energy (keV)")

            # Check if data are hidden by plotting limits
            print "{} delchi range: [{:.2g}, {:.2g}]".format(
                    basename(fname), np.amin(delchi), np.amax(delchi))
            if np.amin(delchi) < ax.get_ylim()[0] or np.amax(delchi) > ax.get_ylim()[1]:
                print "    Warning: data point(s) hidden by plot y limits"

        plt.tight_layout()

        if opt_outstem:
            print "Writing: {}".format(opt_outstem + '-delchi.pdf')
            plt.savefig(opt_outstem + '-delchi.pdf')
            plt.clf()
        else:
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
