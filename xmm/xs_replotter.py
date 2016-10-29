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

import yaml

def main():
    """ Make plots """
    parser = argparse.ArgumentParser(description=("Plot XSPEC QDP dumps"
                                     " of data and fitted model components."))
    parser.add_argument('config', help=("YAML configuration file for plot"))
    parser.add_argument('--residuals', action='store_true')
    parser.add_argument('--out', action='store_true')
    args = parser.parse_args()

    config_file = args.config
    opt_residuals = args.residuals
    opt_out = args.out

    with open(config_file, 'r') as fh:
        for config in yaml.load_all(fh):

            # Set some defaults
            if 'legend' not in config:  # TODO this behavior may change
                config['legend'] = True
            if 'ms-single-column-plot' not in config:
                config['ms-single-column-plot'] = False
            if 'height' not in config:
                config['height'] = 1.75

            if 'width' not in config:
                if config['ms-single-column-plot']:
                    config['width'] = 3.54
                else:
                    config['width'] = 7.0

            # Apply global defaults (cascading styles) for some parameters
            # but not all (e.g., 'name' and 'file' don't make sense to cascade)
            # TODO a more consistent behavior would be useful
            for par in ['cols', 'colors', 'labels', 'linestyles',
                        'ylim', 'delchi-ylim']:
                for pane in config['subplots']:
                    if par in config and par not in pane:
                        pane[par] = config[par]

            main_plots(config)
            if opt_out:
                print "Writing: {}".format(config['out'] + '.pdf')
                plt.savefig(config['out'] + '.pdf')
                plt.clf()
            else:
                plt.show()

            if opt_residuals:
                residual_plots(config)
                if opt_out:
                    print "Writing: {}".format(config['out'] + '-delchi.pdf')
                    plt.savefig(config['out'] + '-delchi.pdf')
                    plt.clf()
                else:
                    plt.show()

            print "---"


def main_plots(config):
    """Make main plots"""

    n_panes = len(config['subplots'])

    # Plot data and models
    fig, axes = plt.subplots(n_panes, sharex=True,
                             figsize=(config['width'], n_panes * config['height']))
    if n_panes == 1:
        axes = [axes]  # plt.subplots collapses unneeded dimensions

    # Make each subplot, using individual configurations
    for n, ax in enumerate(axes):

        # Load configuration for individual panel
        pane = config['subplots'][n]

        # Load XSPEC dumped data
        dat = np.loadtxt(pane['file'])
        x       = dat[:,0]
        x_err   = dat[:,1]
        y       = dat[:,2]
        y_err   = dat[:,3]
        model_sum   = dat[:,4]
        n_models = dat.shape[1] - 5

        # Set default configuration as needed
        if 'ylim' not in pane:
            pane['ylim'] = (1e-4, 1.0)  # Good for small G309 regions

        if 'cols' not in pane:
            pane['cols'] = range(5, n_models + 5)
        if 'colors' not in pane:
            pane['colors'] = [None] * len(pane['cols'])
        if 'labels' not in pane:
            pane['labels'] = [None] * len(pane['cols'])
        if 'linestyles' not in pane:
            pane['linestyles'] = ['-'] * len(pane['cols'])

        pane['ylim'] = map(float, pane['ylim'])

        assert len(pane['colors']) == len(pane['cols'])
        assert len(pane['labels']) == len(pane['cols'])
        assert len(pane['linestyles']) == len(pane['cols'])

        # Plot selected model components
        for col_idx, col in enumerate(pane['cols']):
            # e.g. cols = [5,6,7] has col_idx values 0,1,2
            # to index into colors, labels, linestyles
            plot_step(x, x_err, dat[:,col], ax=ax,
                      color=pane['colors'][col_idx],
                      label=pane['labels'][col_idx],
                      linestyle=pane['linestyles'][col_idx])

        # Plot summed model
        plot_step(x, x_err, model_sum, ax=ax,
                  color='k', alpha=1, zorder=10)

        # Plot actual data
        # TODO ensure elinewidth=0.6 is still readable in two-column format
        plot_err(x, y, x_err, y_err, ax=ax,
                 capsize=0, ls='none', elinewidth=0.6,
                 color='#377eb8', alpha=1, zorder=9)

        # Axis ticks, limits, labels
        prep_xaxis(ax)
        ax.set_yscale("log")
        ax.set_ylim(*pane['ylim'])

        if ax is axes[-1]:
            ax.set_xlabel("Energy (keV)")
        ax.set_ylabel(r'Counts\hspace{1pt} s$^{-1}$ keV$^{-1}$')

        # Annotation text
        if 'name' in pane:
            if config['ms-single-column-plot']:
                ax.text(0.05, 0.93, pane['name'], ha='left', va='top',
                        transform=ax.transAxes, fontsize=9)
            else:
                ax.text(0.02, 0.93, pane['name'], ha='left', va='top',
                        transform=ax.transAxes, fontsize=10)

        # Legend on top plot
        if ax is axes[0] and config['legend'] and pane['labels']:
            if config['ms-single-column-plot']:
                ax.legend(loc='best', prop={'size':8},
                          labelspacing=0.15, frameon=False)
            else:
                ax.legend(loc='best', prop={'size':8},
                          labelspacing=0.3, framealpha=0.5)


        # Check if data are hidden by plotting limits
        print "{} data range: [{:.2g}, {:.2g}]".format(
                basename(pane['file']), np.amin(y), np.amax(y))
        if np.amin(y) < ax.get_ylim()[0] or np.amax(y) > ax.get_ylim()[1]:
            print "    Warning: data point(s) hidden by plot y limits"

    plt.tight_layout(pad=0.5)

    return fig


def residual_plots(config):
    """Make residual plots"""

    # Nearly identical to "main_plots", but not cleanly refactorable.
    # The bulk of these methods is devoted to plot setup and configuration
    # little things like setting ticks, x/y axes

    n_panes = len(config['subplots'])

    # Almost copy-pasted code, but not cleanly refactorable
    fig, axes = plt.subplots(n_panes, sharex=True, figsize=(6.5, n_panes*1.5))
    if n_panes == 1:
        axes = [axes]  # plt.subplots collapses unneeded dimensions

    for n, ax in enumerate(axes):

        # Load configuration for individual panel
        pane = config['subplots'][n]

        # Set default configuration as needed
        if 'delchi-ylim' not in pane:
            pane['delchi-ylim'] = (-4, 4)
        pane['delchi-ylim'] = map(float, pane['delchi-ylim'])

        # Load XSPEC dumped data
        dat = np.loadtxt(pane['file'])
        x       = dat[:,0]
        x_err   = dat[:,1]
        y       = dat[:,2]
        y_err   = dat[:,3]
        model_sum   = dat[:,4]

        delchi = (y - model_sum)/y_err

        ax.errorbar(x, (y - model_sum)/y_err,
                    xerr=x_err, yerr=(y_err / y_err),
                    capsize=0, ls='none', elinewidth=0.6,
                    color='#377eb8', alpha=1, zorder=9)
        # TODO ensure elinewidth=0.5 is still readable in manuscript fmt

        ax.axhline(y=0, color='k')

        # Axis ticks, limits, labels
        prep_xaxis(ax)
        ax.set_ylim(*pane['delchi-ylim'])

        if ax is axes[-1]:
            ax.set_xlabel("Energy (keV)")
        ax.set_ylabel(r'$\Delta\chi$')

        # Annotation text
        if 'name' in pane:
            ax.text(0.015, 0.92, pane['name'], ha='left', va='top',
                    transform=ax.transAxes)

        # Check if data are hidden by plotting limits
        print "{} delchi range: [{:.2g}, {:.2g}]".format(
                basename(pane['file']), np.amin(delchi), np.amax(delchi))
        if np.amin(delchi) < ax.get_ylim()[0] or np.amax(delchi) > ax.get_ylim()[1]:
            print "    Warning: data point(s) hidden by plot y limits"

    plt.tight_layout(pad=0.5)

    return fig


def prep_xaxis(ax):
    """Set up x-axis range and ticks"""
    ax.set_xscale("log")
    ax.set_xlim(0.3, 11.0)  # WARNING: hard-coded X-axis limits and ticks
    ax.set_xticks([0.5, 1, 2, 5, 10])
    ax.xaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:g}'))
    #ax.set_xticks([0.1, 1, 10])
    #ax.set_xticklabels(['0.1', '1', '10'])
    #ax.xaxis.set_minor_locator(plt.FixedLocator([0.2, 0.5, 2, 5]))


def plot_err(x, y, xerr, yerr, ax=None, **kwargs):
    """Plot x and y error bars, with custom tweak to force lower y-errors > 0
    Based on: stackoverflow.com/a/13492914/
    """
    if ax is None:
        ax = plt.gca()

    yerr_low = np.array(yerr)  # Don't modify external yerr
    yerr_low[yerr >= y] = 0.9999999999 * y[yerr >= y]  # Force lower error bound to 1e-10 above zero
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
