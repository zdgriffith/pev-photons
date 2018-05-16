#!/usr/bin/env python

########################################################################
# Plots the sensitivity and discovery potential
# as a function of declination, with HESS source fluxes extrapolated
########################################################################

import argparse
import scipy
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate
from glob import glob

from pev_photons.utils.support import prefix, resource_dir
from pev_photons.utils.support import fig_dir, plot_setter, plot_style

def plot_sens(label, color):
    arrs = []
    for fname in files:
        a = np.load(fname)
        arrs.append([item for item in a[0]])
    arrs = np.array(sorted(arrs))

    kind_labels = ['Sensitivity', 'Discovery Potential']
    linestyle = ['-', '--']
    for j, sens_label in enumerate(kind_labels):
        if j == 0:
            ax0.plot(arrs.T[0], arrs.T[j+1]*1e3,
                     color=color, ls=linestyle[j],
                     label='%s' % label)
        else:
            ax0.plot(arrs.T[0], arrs.T[j+1]*1e3,
                     color=color, ls=linestyle[j])
    dec_list, sens, disc = arrs.T
            
    return dec_list, sens, disc

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Plot the sensitivity as a function of declination.',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--systematic', default='hadronic')
    p.add_argument('--year', default='2012')
    p.add_argument('--alpha', default=2.0, type=float)
    args = p.parse_args()

    plt.style.use(plot_style)
    colors = plt.rcParams['axes.color_cycle']
    plt.rcParams['axes.labelsize'] = 16
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10

    fig, (ax0, ax1) = plt.subplots(2, 1, gridspec_kw={'height_ratios':[3, 1]})

    models = {'hadronic': ['qgs', 'sybll'],
              'lambda': ['LaputopLambdaUp', 'LaputopLambdaDown', 'Laputop'],
              'LaputopS125': ['LaputopS125Up', 'LaputopS125Down', 'Laputop'],
              'charges': ['charges_0.90', 'charges_1.10', 's125_1.00'],
              's125': ['s125_0.98', 's125_1.02', 's125_1.00']}

    labels = {'hadronic': ['QGSJet II-04', 'SYBLL 2.1'],
              'lambda': ['$\lambda$ + 0.2', '$\lambda$ - 0.2', '$\lambda$'],
              'LaputopS125': [r'1.03$\times$S$_{125}$', r'0.97$\times$S$_{125}$', r'1.00$\times$S$_{125}$'],
              'charges': [r'0.90$\times$(InIce Charge)', r'1.10$\times$(InIce Charge)', r'1.00$\times$(InIce Charge)'],
              's125': [r'1.02$\times$S$_{125}$', r'0.98$\times$S$_{125}$', r'1.00$\times$S$_{125}$']}

    f = []
    for i, model in enumerate(models[args.systematic]):
        if args.systematic in ['lambda', 'LaputopS125']:
            files = glob(prefix+'systematics/sens_jobs/%s/index_%s/%s_*' % (args.year, args.alpha, model))
        else:
            files = glob(prefix+'systematics/sens_jobs/index_%s/%s_*' % (args.alpha, model))
        dec_list, sens, disc = plot_sens(labels[args.systematic][i], colors[i])
        f.append(sens)
        
    for i, sens in enumerate(f):
        ax1.plot(dec_list, sens/f[-1], color=colors[i], ls='-')

    ax0.set_xticklabels([])
    ax0.set_xlim([-81, -54])
    if args.systematic in ['lambda', 'LaputopS125']:
        #ax0.set_title('%s E$^{-%s}$ Point Source Sensitivity' % (args.year, args.alpha))
        ax0.set_title('E$^{-%s}$ Point Source Sensitivity' % (args.alpha))
        ax0.set_ylim([1e-20, 5e-17])
    elif args.systematic == 'hadronic':
        ax0.set_title('%s E$^{-%s}$ Point Source Sensitivity' % (args.year, args.alpha))
        ax0.set_ylim([1e-21, 5e-18])
    else:
        ax0.set_title('E$^{-%s}$ Point Source Sensitivity' % (args.alpha))
        ax0.set_ylim([1e-21, 5e-18])
    ax0.set_ylabel('Flux [cm$^{-2}$s$^{-1}$TeV$^{-1}$]')
    ax0.set_yscale('log')
    l = ax0.legend(loc='upper left')
    plot_setter(plt.gca(),l)

    ax1.set_xlabel(r'Declination [$^{\circ}$]')
    ax1.set_xlim([-81, -54])
    ax1.set_ylim([0.65, 1.35])
    ax1.set_ylabel('Ratio', fontsize=12)
    ax1.set_yticks([0.7,0.8,0.9,1.0,1.1,1.2,1.3])
    ax1.set_yticklabels([0.7,0.8,0.9,1.0,1.1,1.2,1.3], fontsize=8)
    ax1.grid(alpha=0.2)
    fig.tight_layout()
    plt.savefig(fig_dir+'systematics/{}_{}_{}_sensitivity.png'.format(args.systematic, args.alpha, args.year))
    plt.close()

    fig, ax = plt.subplots()

    bins=np.arange(0.1,1.5,0.01)
    for i, sens in enumerate(f):
        if i != len(f)-1:
            ratio = sens/f[-1]
            median = np.median(ratio)
            ax.axvline(x=median, color=colors[i])
            ax.hist(ratio, bins=bins,
                    histtype='stepfilled', color=colors[i], alpha=0.4,
                    label='{}\nmedian={:.3f}'.format(labels[args.systematic][i], median))
        else:
            ax.axvline(x=1, color=colors[i])
    #ax.set_xlim([0.80, 1.35])
    ax.set_xlim([0.80, 1.20])

    ax.set_xlabel('Ratio to Standard')
    ax.legend(loc='upper left')
    fig.tight_layout()
    plt.savefig(fig_dir+'systematics/{}_{}_{}_sens_ratio_bins.png'.format(args.systematic, args.alpha, args.year))
    plt.close()
