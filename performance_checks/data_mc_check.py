#!/usr/bin/env python

#########################################
###  Plot the gamma ray probability   ###
###  distribution for data and MC     ###
###  from a Random Forest Classifier  ###
#########################################

import argparse, sys, os
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import numpy as n
from pylab import *
from support_functions import get_fig_dir
from support_pandas import livetimes
sys.path.append(os.path.expandvars("$HOME"))
import dashi
dashi.visual()
plt.style.use('stefan')
colors = mpl.rcParams['axes.color_cycle']
fig_dir = get_fig_dir()

#cosmic-ray flux model of "realistic spectrum with a knee" from
#https://wiki.icecube.wisc.edu/index.php/IT73-IC79_Data-MC_Comparison#Weighting
def flux(E):
    phi_0   = 2.95*10**-6
    return phi_0*E**(-2.7)*(1+(E/3.)**100)**(-0.4/100.)*10**-10
    
if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Plot a skymap',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', dest='prefix', type = str,
                   default = '/data/user/zgriffith/pev_photons/',
                   help    = 'base directory for file storing')
    p.add_argument('--outFile', dest='outFile', type = str,
                   default = 'data_mc_verification.png',
                   help    = 'file name')
    args = p.parse_args()

    left  = 0.15
    width = 0.8
    ax0   = plt.axes([left, 0.35, width, 0.6])
    ax1   = plt.axes([left, 0.14, width, 0.19])

    plt.sca(ax0)
    s_min = -0.25 

    bins       = np.arange(0,1.05,0.05)
    prob_dists = np.zeros(((4,5,len(bins)))) 

    key        = 'hard_prediction'
    lt         = livetimes('burn_2012')
    pf         = '/data/user/zgriffith/rf_data/2012/test/'
    set_names  = ['data','sim','protons','iron']
    labels     = ['Data', 'Gammas ($10^{-4.5}$ CR Approx.)', 'CR Flux - All Protons', 'CR Flux - All Iron']
    
    for i, fname in enumerate(set_names):
        for fold in range(5):
            f = pd.read_pickle(pf+'test_%s_fold_%s.pkl' % (fname, fold))
            mask = np.less(f['s125'], 10**10)

            if fname == 'data':
                hist  = dashi.factory.hist1d(f[key][mask], bins, weights = [1/lt]*len(f['laputop_E'][mask]))
                prob_dists[i][fold] += np.append(hist.bincontent[0],hist.bincontent)
            elif fname == 'sim':
                hist = dashi.factory.hist1d(f[key][mask], bins, weights = (10**-4.5)*flux(f['primary_E'][mask]*10**-6)*f['weights'][mask])
                prob_dists[i][fold] += np.append(hist.bincontent[0],hist.bincontent)
            else:
                hist = dashi.factory.hist1d(f[key][mask], bins, weights = flux(f['primary_E'][mask]*10**-6)*(f['weights'][mask]/1.68))
                if fname == 'iron':
                    prob_dists[i][fold] += 0.2*np.append(hist.bincontent[0],hist.bincontent)*199/198.
                else:
                    prob_dists[i][fold] += 0.2*np.append(hist.bincontent[0],hist.bincontent)

        means = np.mean(prob_dists[i], axis=0)
        if i ==0:
            data_means = means
        else:
            ax1.scatter(bins-0.025, data_means/means, color = colors[i], marker = '^')
        stds  = np.std(prob_dists[i], axis=0)
        ax0.step(bins, means, label = labels[i], color = colors[i])
        ax0.errorbar(bins-0.05/2., means, yerr =stds,
                     color = colors[i],
                     lw = 2, capthick = 2, fmt = 'o', marker = 'o', ms = 0)


    ax1.set_xlim([0,1])
    ax1.set_ylim([0,10])
    ax1.axhline(y=1, color = 'k', linestyle='--')
    ax1.set_xlabel('Gamma-Ray Probability')
    ax1.set_ylabel('Data/MC')

    ax0.xaxis.set_visible(False)
    ax0.set_xlim([0,1])
    ax0.set_ylabel('Rate (Hz)')
    ax0.set_ylim([10**-8, 5])
    ax0.set_yscale('log')
    ax0.set_title('Gamma E$^{-2.0}$ Trained')
    ax0.legend(loc='upper right', fontsize = 12)

    plt.savefig(fig_dir + args.outFile, facecolor='none', dpi=300, bbox_inches='tight')
    plt.close()
