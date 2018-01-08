#!/usr/bin/env python

########################################################################
# For each HESS source, calculate the
# minimum cut-off energy matching a sensitivity
########################################################################

import argparse
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import InterpolatedUnivariateSpline

import dashi
from pev_photons.support import prefix, fig_dir, plot_style

def cutoff_calculator():
    sources = np.load(prefix+'TeVCat/hess_sources.npz')

    surv = np.loadtxt(prefix+'TeVCat/gamma_survival_vs_distance.txt')
    surv = surv.T
    spline = InterpolatedUnivariateSpline(surv[0], surv[1], k=2)
    ratio = spline(sources['distance'])

    medians = ratio*(sources['flux']*1e-12)
    medians *= 1000**(2-sources['alpha'])

    kind = ['sensitivity', 'discovery_potential']
    cutoff = [[],[]] 

    for j, k in enumerate(kind):
        for i, flux in enumerate(medians):
            if np.isnan(sources[k][i]):
                continue
            E = 2000.
            if flux < (sources[k][i]):
                cutoff[j].append(np.nan)
            else:
                while flux*np.exp(-1000/E) > (sources[k][i]):
                    E -= 10.
                cutoff[j].append(E)

    return cutoff

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Calculate minimum cut-off energies for sources.',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--outFile', type=str,
                   default='cutoff_energies.png',
                   help='The output file name.')
    args = p.parse_args()

    dashi.visual()
    plt.style.use(plot_style)

    cutoff = cutoff_calculator()
    kind = ['Sensitivity', 'Discovery Potential']
    
    for i, k in enumerate(kind):
        hist = dashi.factory.hist1d(cutoff[i], np.arange(0,3025,25))
        hist.line(label=k) 

    plt.xlabel('Minimum Cut-Off Energy [TeV]')
    plt.legend()
    plt.savefig(fig_dir+'TeVCat/'+args.outFile, facecolor='none', dpi=300)
    plt.close()
