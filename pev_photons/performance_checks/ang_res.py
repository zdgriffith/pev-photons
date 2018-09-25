#!/usr/bin/env python

########################################################################
# Plot the angular resolution of gamma-ray MC for set years.
########################################################################

import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

from pev_photons import utils

def find_nearest(array,value):
    """ Returns the nearest bin value. """
    return  (np.abs(array-value)).argmin()

def sigma(y):
    """ Calculate the 68% containment value. """
    values, base = np.histogram(y, bins=np.arange(0,20,0.01),
                                weights=[1/float(len(y))]*len(y))
    cumulative = np.cumsum(values)

    for i, val in enumerate(cumulative):
        if val >= 0.68:
            return base[i]/1.51

def error(f, label, key, x_bins):
    """ Estimate the angular error for each event. """
    bin_size = x_bins[1]-x_bins[0]

    if key in ['laputop_E', 'primary_E']:
        vals = np.log10(f[key])
    else:
        vals = f[key]

    bin_sigmas, bin_edges, n = stats.binned_statistic(vals,
                                                      f['opening_angle'],
                                                      statistic=sigma,
                                                      bins=x_bins)
    bin_center = bin_edges[:-1] + bin_size/2.

    sigmas = [bin_sigmas[find_nearest(bin_center, val)] for val in vals]

    avg = np.average(sigmas, weights=f['weights']*f['primary_E']**-2.0)
    plt.step(bin_edges, np.append(bin_sigmas[0], bin_sigmas),
             label=label+r', $\langle\sigma\rangle$ = %.2f$^{\circ}$' % avg)

    return np.radians(sigmas)

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Plot the ang. res. weighted to an E^-2 specrum',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--outFile', default='effective_area_years.png',
                   help='file name')
    args = p.parse_args()

    plt.style.use(utils.plot_style)

    # Plot only the first and last years for readibility
    years = ['2011', '2015']

    E_bins = np.arange(5.7, 8.1, 0.1)
    for i, year in enumerate(years):
        f = pd.read_hdf(utils.resource_dir+'datasets/level3/'+year+'_mc_quality.hdf5')
        error(f, year, 'primary_E', E_bins)

    plt.xlabel(r'log(E$_{\textrm{\textsc{mc}}}$/GeV)')
    plt.xlim([5.7,8])
    plt.ylim([0.1,0.6])
    plt.ylabel('Angular Resolution [$^{\circ}$]')
    l = plt.legend()
    utils.plot_setter(plt.gca(), l)
    plt.tight_layout()
    plt.savefig(utils.fig_dir+'performance_checks/ang_res_years.png')
    plt.savefig(utils.fig_dir+'paper/ang_res_years.pdf')
    plt.close()
