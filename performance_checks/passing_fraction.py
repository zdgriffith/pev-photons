#!/usr/bin/env python

########################################################################
# Plots the passing fraction as a function of energy for all years
# of the analysis, for a given spectral assumption of gamma rays.
########################################################################

import argparse
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

import dashi
from support_functions import get_fig_dir, plot_setter
from support_pandas import load_all_folds

dashi.visual()
plt.style.use('stefan')
colors = mpl.rcParams['axes.color_cycle']
fig_dir = get_fig_dir()
       
def passing_fraction(args):
    if 'all' in args.years:
        args.years = ['2011','2012','2013','2014','2015']

    labels = ['Data', 'Gamma Ray MC (E$^{-2.0}$ weighted)']
    set_names = ['data', 'gammas']
    bin_width = 0.1
    bin_vals = np.arange(5.7,8.1,bin_width)

    energies = {'data':[], 'gammas':[]}
    kept_energies = {'data':[], 'gammas':[]}
    weights = {'data':[], 'gammas':[]}
    kept_weights = {'data':[], 'gammas':[]}
    for year in args.years:
        l3_data, l3_sim = load_all_folds(year = year, or_cut = 0)
        l4_data, l4_sim = load_all_folds(year = year, or_cut = 0.7)

        energies['data'].extend(l3_data['laputop_E'])
        kept_energies['data'].extend(l4_data['laputop_E'])
        energies['gammas'].extend(l3_sim['laputop_E'])
        kept_energies['gammas'].extend(l4_sim['laputop_E'])
        weights['data'].extend([1.]*len(l3_data['laputop_E']))
        kept_weights['data'].extend([1.]*len(l4_data['laputop_E']))
        weights['gammas'].extend((l3_sim['primary_E']**-2.0)
                                 *l3_sim['weights'])
        kept_weights['gammas'].extend((l4_sim['primary_E']**-2.0)
                                      *l4_sim['weights'])

    for j, name in enumerate(set_names):
        hist = dashi.factory.hist1d(np.log10(energies[name]),
                                    bin_vals, weights = weights[name])
        kept_hist = dashi.factory.hist1d(np.log10(kept_energies[name]),
                                         bin_vals,
                                         weights = kept_weights[name])
        passed = hist.bincontent-kept_hist.bincontent

        # An error formulation which avoids forbidden space.
        # See Ullrich and Xu 2008:
        # "Treatment of Errors in Efficiency Calculations" eqn 19.
        bin_num = len(passed)
        error = np.zeros(bin_num)
        percent = np.zeros(bin_num)
        for i in range(bin_num):
            k = np.float(passed[i])
            n = np.float(hist.bincontent[i])
            percent[i] = kept_hist.bincontent[i]/float(hist.bincontent[i])
            error[i] = np.sqrt(((k+1)*(k+2)) / ((n+2)*(n+3))
                               - ((k+1)**2) / ((n+2)**2))

        plt.step(hist.binedges, np.append(percent[0],percent),
                 color=colors[j], label=labels[j], ls='-')
        plt.errorbar(hist.binedges[:-1]+bin_width/2., percent,
                     yerr=error, fmt='none', color=colors[j],
                     ecolor=colors[j], ms=0)

    l = plt.legend(loc='lower left')
    plot_setter(plt.gca(),l)

    plt.xlim([5.7,8])
    plt.ylim([10**-4,1])
    plt.yscale('log')
    plt.xlabel('log(E/GeV)')
    plt.ylabel('Passing Fraction')
    plt.tight_layout()
    plt.savefig(fig_dir+'/passing_vs_energy_all_years.png',
                facecolor='none', dpi=300)
    plt.close()

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Create an all sky TS map',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', type=str,
                   default='/data/user/zgriffith/pev_photons/',
                   help='base directory for file storing')
    p.add_argument('--outFile', type=str,
                   default='passing_vs_energy.png',
                   help='file name')
    p.add_argument('--years', type=str, nargs='+', default=['2012'],
                   help=('Year(s) to plot.  If "all", '
                         'will plot the combination'))
    args = p.parse_args()

    passing_fraction(args)
