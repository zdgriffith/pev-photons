#!/usr/bin/env python

########################################################################
# Plots the passing fraction as a function of energy for all years
# of the analysis, for a given spectral assumption of gamma rays.
########################################################################

import argparse
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

import dashi
from pev_photons.utils.support import resource_dir, fig_dir, plot_setter, plot_style

def final_sample(args, year, sel, level, label):
    f = {'level3':{}, 'level4':{}}
    if level == 'level3':
        if label == 'Data':
            f = pd.read_hdf(resource_dir+'datasets/quality_energies/'+year+'.hdf5')
            return np.log10(f['laputop_E']), np.ones(f.shape[0])
        else:
            f = pd.read_hdf(resource_dir+'datasets/level3/'+year+'_mc_quality.hdf5')
            return np.log10(f['laputop_E']), f['weights']
    else:
        if label == 'Data':
            f = np.load(resource_dir+'datasets/'+year+'_exp_'+sel+'.npy')
            return f['logE'], np.ones(f.shape[0])
        else:
            f = np.load(resource_dir+'datasets/'+year+'_mc_'+sel+'.npy')
            return f['logE'], f['ow']

def passing_fraction(args, sel='ps', suffix=''):
    if 'all' in args.years:
        args.years = ['2011', '2012', '2013', '2014', '2015']

    bin_width = 0.1
    bin_vals = np.arange(5.7,8.1,bin_width)

    labels = ['Data', 'Gamma-ray MC']
    cut_levels = ['level3', 'level4']

    energies = {level:{label:[] for label in labels} for level in cut_levels}
    weights = {level:{label:[] for label in labels} for level in cut_levels}

    for year in args.years:
        print(year)
        for level in cut_levels:
            for label in labels:
                energy, weight = final_sample(args, year, sel, level, label)
                energies[level][label].extend(energy)
                weights[level][label].extend(weight)

    for j, label in enumerate(labels):
        hist = {}
        for level in cut_levels:
            hist[level] = dashi.factory.hist1d(energies[level][label], bin_vals,
                                               weights=weights[level][label])

        passed = hist['level3'].bincontent-hist['level4'].bincontent

        # An error formulation which avoids forbidden space.
        # See Ullrich and Xu 2008:
        # "Treatment of Errors in Efficiency Calculations" eqn 19.
        bin_num = len(passed)
        error = np.zeros(bin_num)
        percent = np.zeros(bin_num)
        for i in range(bin_num):
            k = np.float(passed[i])
            n = np.float(hist['level3'].bincontent[i])
            percent[i] = hist['level4'].bincontent[i]/float(hist['level3'].bincontent[i])
            error[i] = np.sqrt(((k+1)*(k+2)) / ((n+2)*(n+3))
                               - ((k+1)**2) / ((n+2)**2))

        lines = plt.step(hist['level3'].binedges, np.append(percent[0],percent),
                         label=labels[j]+suffix, ls='-')
        lc = lines[0].get_color()

        plt.errorbar(hist['level3'].binedges[:-1]+bin_width/2., percent,
                     yerr=error, fmt='none', color=lc,
                     ecolor=lc, ms=0, capthick=2)


if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Plot the passing fraction of data and gamma rays.',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--years', type=str, nargs='+', default=['all'],
                   help=('Year(s) to plot.  If "all", '
                         'will plot the combination'))
    args = p.parse_args()

    dashi.visual()
    plt.style.use(plot_style)

    labels = [' (point source selection)', ' (galactic plane selection)']
    for i, sel in enumerate(['ps','diffuse']):
        passing_fraction(args, sel=sel, suffix=labels[i])

    l = plt.legend(bbox_to_anchor = (0, 0.65), loc='center left')
    plot_setter(plt.gca(),l)

    plt.xlim([5.7,8])
    plt.ylim([10**-5,1])
    plt.yscale('log')
    plt.xlabel(r'log(E$_{\textrm{reco}}$/GeV)')
    plt.ylabel('Passing Fraction')
    plt.tight_layout()
    plt.savefig(fig_dir+'performance_checks/passing_vs_energy.pdf')
    plt.savefig(fig_dir+'paper/passing_vs_energy.pdf')
    plt.close()
