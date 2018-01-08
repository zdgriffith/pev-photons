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
from pev_photons.support import fig_dir, plot_setter, plot_style
from support_pandas import load_all_folds

def passing_fraction(args, alpha=False, suffix=''):
    if 'all' in args.years:
        args.years = ['2011','2012','2013','2014','2015']

    labels = ['Data', 'Gamma-ray MC']
    set_names = ['data', 'gammas']
    bin_width = 0.1
    bin_vals = np.arange(5.7,8.1,bin_width)

    energies = {'data':[], 'gammas':[]}
    kept_energies = {'data':[], 'gammas':[]}
    weights = {'data':[], 'gammas':[]}
    kept_weights = {'data':[], 'gammas':[]}
    for year in args.years:
        l3_data, l3_sim = load_all_folds(year=year, or_cut=0, alpha=alpha)
        l4_data, l4_sim = load_all_folds(year=year, or_cut=0.7, alpha=alpha)

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

        lines = plt.step(hist.binedges, np.append(percent[0],percent),
                         label=labels[j]+suffix, ls='-')
        lc = lines[0].get_color()
        plt.errorbar(hist.binedges[:-1]+bin_width/2., percent,
                     yerr=error, fmt='none', color=lc,
                     ecolor=lc, ms=0, capthick=2)


if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Create an all sky TS map',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--outFile', type=str,
                   default='passing_vs_energy.png',
                   help='file name')
    p.add_argument('--years', type=str, nargs='+', default=['2012'],
                   help=('Year(s) to plot.  If "all", '
                         'will plot the combination'))
    args = p.parse_args()

    dashi.visual()
    plt.style.use(plot_style)

    labels = [' (point source selection)', ' (galactic plane selection)']
    for i, alpha in enumerate([False,3.0]):
        passing_fraction(args, alpha=alpha, suffix=labels[i])

    l = plt.legend(bbox_to_anchor = (0, 0.65), loc='center left')
    plot_setter(plt.gca(),l)

    plt.xlim([5.7,8])
    plt.ylim([10**-4,1])
    plt.yscale('log')
    plt.xlabel(r'log(E$_{\textrm{reco}}$/GeV)')
    plt.ylabel('Passing Fraction')
    plt.tight_layout()
    plt.savefig(fig_dir+'performance_checks/passing_vs_energy_all_years.pdf')
    plt.savefig(fig_dir+'paper/passing_fraction.pdf')
    plt.close()
