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

from pev_photons import utils

def plot_hess_sources(E0=2, no_absorption=None, plot_hess_sens=None):
    # Load source fluxes and errors
    s = np.load(utils.resource_dir+'hess_sources.npz')
    sources = {}
    for key in s.keys():
        sources[key] = s[key]
    sources['alpha_sys'] = [i if i != 0 else 0.2 for i in sources['alpha_sys']]

    # Calculate flux and errors
    middle = sources['flux']*(E0*1e3)**(-sources['alpha'])*1e-12
    stat_upper = ((sources['flux']+sources['flux_stat'])
                 *(E0*1e3)**(-sources['alpha']+sources['alpha_stat'])*1e-12)
    stat_lower = ((sources['flux']-sources['flux_stat'])
                 *(E0*1e3)**(-sources['alpha']-sources['alpha_stat'])*1e-12)
    sys_upper = ((sources['flux']+sources['flux_sys'])
                 *(E0*1e3)**(-sources['alpha']+sources['alpha_sys'])*1e-12)
    sys_lower = ((sources['flux']-sources['flux_sys'])
                 *(E0*1e3)**(-sources['alpha']-sources['alpha_sys'])*1e-12)

    # Apply absorption unless asked not to
    if no_absorption:
        ratio = 1
    else:
        surv = np.loadtxt(utils.resource_dir+'old/gamma_survival_vs_distance.txt')
        surv = surv.T
        spline = scipy.interpolate.InterpolatedUnivariateSpline(surv[0],
                                                                surv[1], k=2)
        ratio = spline(sources['distance'])

    # Plot the source flux and statistical error
    plt.errorbar(sources['dec'], ratio*middle,
                 yerr=ratio*np.array([np.abs(middle-stat_lower),
                                      np.abs(middle-stat_upper)]),
                 fmt='o', color=colors[4],
                 lw=2, capthick=0, capsize=0,
                 ms=5, label='Extrapolated H.E.S.S. Sources')

    # Plot systematic error
    plt.errorbar(sources['dec'], ratio*middle,
                 yerr=ratio*np.array([np.abs(middle-sys_lower),
                                      np.abs(middle-sys_upper)]),
                 fmt='none', color=colors[4], ecolor=colors[4],
                 lw=6, elinewidth=0, capthick=0, capwidth=0, alpha=0.4)

    if plot_hess_sens:
        hess_sens = np.load(utils.prefix+'TeVCat/hess_sens.npz')
        plt.scatter(sources['dec'], hess_sens['sensitivity']*1e3,
                    color=colors[3], marker='*', label='H.E.S.S. 90% limits')

def plot_sens(E0, coarse):
    indices = [2.0, 2.7]
    kind_labels = ['Sensitivity', 'Discovery Potential']
    linestyle = ['-', '--']

    if coarse:
        dec_list = np.linspace(-84., -54., 10)
        kinds = ['sens', 'disc']
        for i, index in enumerate(indices):
            for j, kind in enumerate(kinds):
                flux = np.load(utils.prefix+'all_sky/%s_index_%s.npy' % (kind, index))
                plt.plot(dec_list, flux*(1e3),
                         color=colors[i], ls=linestyle[j],
                         label='E$^{-%s}$ %s' % (index, kind_labels[j]))
    else:
        for i, index in enumerate(indices):
            arrs = []
            if E0 == 1:
                files = glob(utils.prefix+'all_sky/sens_jobs/index_%s/dec*' % index)
            else:
                files = glob(utils.prefix+'all_sky/sens_jobs/2_pev/index_%s/dec*' % index)
            for fname in files:
                a = np.load(fname)
                arrs.append([item for item in a[0]])

            arrs = np.array(sorted(arrs))
            for j, label in enumerate(kind_labels):
                plt.plot(arrs.T[0], arrs.T[j+1]*1e3,
                         color=colors[i], ls=linestyle[j],
                         label='E$^{-%s}$ %s' % (index, label))

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Plot the sensitivity as a function of declination.',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--E0", type=int, default=2,
                   help='Normalization energy in PeV.')
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

    plt.style.use(utils.plot_style)
    colors = plt.rcParams['axes.color_cycle']

    plot_sens(E0=args.E0, coarse=args.coarse)
    plot_hess_sources(E0=args.E0, no_absorption=args.no_absorption,
                      plot_hess_sens=args.plot_hess_sens)

    if args.E0 == 1:
        plt.ylim([1e-22, 5e-17])
    else:
        plt.ylim([1e-23, 5e-18])
    plt.xlim([-85, -54])
    plt.xlabel(r'Declination [$^{\circ}$]')
    plt.ylabel('Flux at 2 PeV [cm$^{-2}$s$^{-1}$TeV$^{-1}$]')
    plt.yscale('log')
    l = plt.legend(loc='upper left')
    utils.plot_setter(plt.gca(),l)
    plt.savefig(utils.fig_dir+'all_sky/sensitivity_{}.png'.format(args.E0), bbox_inches='tight')
    plt.savefig(utils.fig_dir+'paper/sensitivity_{}.pdf'.format(args.E0), bbox_inches='tight')
    plt.close()
