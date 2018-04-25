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

def plot_sens(args, model, color, value=None):
    indices = [2.0]
    kind_labels = ['Sensitivity', 'Discovery Potential']
    linestyle = ['-', '--']

    if args.coarse:
        kinds = ['sens', 'disc']
        dec_list = np.linspace(-84.,-54.,10)
        for i, index in enumerate(indices):
            for j, kind in enumerate(kinds):
                flux = np.load(prefix+'systematics/{}_{}_index_{}.npy'.format(model, kind, index))
                ax0.plot(dec_list, flux*(1e3),
                         color=color, ls=linestyle[j],
                         label='%s E$^{-%s}$ %s' % (model, index, kind_labels[j]))
                if kind == 'sens':
                    sens = flux
                else:
                    disc = flux
    else:
        for i, index in enumerate(indices):
            arrs = []
            if value is not None:
                files = glob(prefix+'systematics/sens_jobs/index_%s/%s_%.2f_*' % (index, model, value))
            else:
                files = glob(prefix+'systematics/sens_jobs/index_%s/%s_*' % (index, model))
            for fname in files:
                a = np.load(fname)
                arrs.append([item for item in a[0]])

            arrs = np.array(sorted(arrs))
            for j, label in enumerate(kind_labels):
                ax0.plot(arrs.T[0], arrs.T[j+1]*1e3,
                         color=color, ls=linestyle[j],
                         label='%s E$^{-%s}$ %s' % (model, index, kind_labels[j]))
            dec_list, sens, disc = arrs.T
                
    return dec_list, sens, disc

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Plot the sensitivity as a function of declination.',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--systematic', default='hadronic')
    p.add_argument('--coarse', action='store_true',
                   default=False,
                   help='if True, plot coarse sens. result from test run.')
    p.add_argument('--plot_hess_sens', action='store_true',
                   default=False,
                   help='if True, plot HESS 90% limits.')
    args = p.parse_args()

    plt.style.use(plot_style)
    colors = plt.rcParams['axes.color_cycle']
    plt.rcParams['axes.labelsize'] = 16
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10

    fig, (ax0, ax1) = plt.subplots(2, 1, gridspec_kw={'height_ratios':[3, 1]})

    f = []
    if systematic == 'hadronic':
        for i, model in enumerate(['sybll', 'qgs']):
            dec_list, sens, disc = plot_sens(args, model, colors[i])
            f.append(sens)
    else:
        for i, value in enumerate([0.90, 1.10]):
            dec_list, sens, disc = plot_sens(args, args.systematic, colors[i],
                                             value=value)
            f.append(sens)
        
    ax1.plot(dec_list, f[0]/f[1], color=colors[0], ls='-')
    ax1.plot(dec_list, f[1]/f[1], color=colors[1], ls='-')

    ax0.set_xticklabels([])
    ax0.set_xlim([-81, -54])
    ax0.set_ylim([1e-21, 5e-17])
    ax0.set_ylabel('Flux [cm$^{-2}$s$^{-1}$TeV$^{-1}$]')
    ax0.set_yscale('log')
    l = ax0.legend(loc='upper left')
    plot_setter(plt.gca(),l)

    ax1.set_xlabel(r'Declination [$^{\circ}$]')
    ax1.set_xlim([-81, -54])
    ax1.set_ylim([0.6, 1.4])
    ax1.set_ylabel('Ratio', fontsize=12)
    ax1.set_yticks([0.7,0.8,0.9,1.0,1.1,1.2,1.3])
    ax1.set_yticklabels([0.7,0.8,0.9,1.0,1.1,1.2,1.3], fontsize=8)
    ax1.grid(alpha=0.2)
    fig.tight_layout()
    plt.savefig(fig_dir+'systematics/%s_sensitivity.png' args.systematic)
    plt.close()

    fig, ax = plt.subplots()
    ratio = f[0]/f[1]
    ax.hist(ratio, bins=np.arange(0.5,1.5,0.01), histtype='step')
    
    median = np.median(ratio)
    r_min = np.min(ratio)
    r_max = np.max(ratio)
    ax.axvline(x=median, label='Median')
    textstr = 'median = %.2f\nmax = %.2f\nmin = %.2f' % (median, r_max, r_min)
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=20,
        verticalalignment='top')

    ax.set_xlim([0.5, 1.5])
    ax.set_ylim([0, 50])
    ax.set_xlabel('(SBYLL Sens.)/(QGS Sens.)')
    ax.legend()
    fig.tight_layout()
    plt.savefig(fig_dir+'systematics/%s_sens_ratio_bins.png' % args.systematic)
    plt.close()
