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

def plot_sens(args, model, color):
    indices = [2.0]
    kind_labels = ['Sensitivity', 'Discovery Potential']
    linestyle = ['-', '--']
    disc = None

    if args.coarse:
        dec_list = np.linspace(-84.,-54.,100)
        #kinds = ['sens', 'disc']
        kinds = ['sens']
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
                
    return sens, disc

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Plot the sensitivity as a function of declination.',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--no_absorption', action='store_true',
                   default=False,
                   help='if True, flux extrapolations have no absorption')
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
    d = []
    recos = ['LaputopLambdaUp', 'Laputop', 'LaputopLambdaDown', 'LaputopS125Up', 'LaputopS125Down']
    for i, reco in enumerate(recos):
        sens, disc = plot_sens(args, reco, colors[i])
        f.append(sens)
        d.append(disc)
        
    dec_list = np.linspace(-84.,-54.,100)
    ax1.plot(dec_list, f[0]/f[1], color=colors[0], ls='-')
    ax1.plot(dec_list, f[1]/f[1], color=colors[1], ls='-')
    ax1.plot(dec_list, f[2]/f[1], color=colors[2], ls='-')
    ax1.plot(dec_list, f[3]/f[1], color=colors[3], ls='-')
    ax1.plot(dec_list, f[4]/f[1], color=colors[4], ls='-')
    #ax1.plot(dec_list, disc[1]/disc[0], color=colors[1], ls='--')

    ax0.set_xticklabels([])
    ax0.set_xlim([-81, -54])
    ax0.set_ylim([3e-19, 3e-18])
    ax0.set_ylabel('Flux [cm$^{-2}$s$^{-1}$TeV$^{-1}$]')
    ax0.set_yscale('log')
    l = ax0.legend(loc='upper left', fontsize=10)
    plot_setter(plt.gca(),l)

    ax1.set_xlabel(r'Declination [$^{\circ}$]')
    ax1.set_xlim([-81, -54])
    ax1.set_ylim([0.8, 1.2])
    ax1.set_ylabel('Ratio', fontsize=12)
    #ax1.set_yticks([0.7,0.8,0.9,1.0,1.1,1.2,1.3])
    #ax1.set_yticklabels([0.7,0.8,0.9,1.0,1.1,1.2,1.3], fontsize=8)
    ax1.grid(alpha=0.2)
    fig.tight_layout()
    plt.savefig(fig_dir+'systematics/reco_sens.pdf')
    plt.close()