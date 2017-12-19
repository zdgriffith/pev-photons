#!/usr/bin/env python

########################################################################
# Plots the sensitivity and discovery potential
# as a function of declination, with HESS source fluxes extrapolated
########################################################################

import argparse
import scipy
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from glob import glob

from support_functions import get_fig_dir, plot_setter

plt.style.use('stefan')
colors = mpl.rcParams['axes.color_cycle']
fig_dir = get_fig_dir()

def plot_hess_sources(args):
    # Load source fluxes and errors
    sources = np.load(args.prefix+'TeVCat/hess_sources.npz')

    # Calculate flux and errors
    middle = sources['flux']*1000**(-sources['alpha'])*1e-12
    stat_upper = ((sources['flux']+sources['flux_stat'])
                 *1000**(-sources['alpha']+sources['alpha_stat'])*1e-12)
    stat_lower = ((sources['flux']-sources['flux_stat'])
                 *1000**(-sources['alpha']-sources['alpha_stat'])*1e-12)
    sys_upper = ((sources['flux']+sources['flux_sys'])
                 *1000**(-sources['alpha']+sources['alpha_sys'])*1e-12)
    sys_lower = ((sources['flux']-sources['flux_sys'])
                 *1000**(-sources['alpha']-sources['alpha_sys'])*1e-12)

    # Apply absorption unless asked not to
    if args.no_absorption:
        ratio = 1
    else:
        surv = np.loadtxt(args.prefix+'TeVCat/gamma_survival_vs_distance.txt')
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

def plot_sens(args):
    indices = [2.0,2.7]
    kind_labels = ['Sensitivity', 'Discovery Potential']
    linestyle = ['-', '--']

    if args.coarse:
        dec_list = np.linspace(-84.,-54.,10)
        kinds = ['sens', 'disc']
        for i, index in enumerate(indices):
            for j, kind in enumerate(kinds):
                flux = np.load(args.prefix+'all_sky/%s_index_%s.npy' % (kind, index))
                plt.plot(dec_list, flux*(1e3),
                         color=colors[i], ls=linestyle[j],
                         label='E$^{-%s}$ %s' % (index, kind_labels[j]))
    else:
        for i, index in enumerate(indices):
            arrs = []
            files = glob(args.prefix+'all_sky/sens_jobs/index_%s/dec*' % index)
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
    p.add_argument('--prefix', default='/data/user/zgriffith/pev_photons/',
                   help='base directory for file storing')
    p.add_argument('--no_absorption', action='store_true',
                   default=False,
                   help='if True, flux extrapolations have no absorption')
    p.add_argument('--coarse', action='store_true',
                   default=False,
                   help='if True, plot coarse sens. result from test run.')
    args = p.parse_args()

    plot_sens(args)
    plot_hess_sources(args)

    plt.xlim([-81, -54])
    plt.ylim([1e-21, 5e-17])
    plt.xlabel(r'Declination [$^{\circ}$]')
    plt.ylabel('Flux at 1 PeV [cm$^{-2}$s$^{-1}$TeV$^{-1}$]')
    plt.yscale('log')
    plt.text(-80, 2e-21, 'IceCube Preliminary', color='r', fontsize=14)
    l = plt.legend(loc='upper left')
    plot_setter(plt.gca(),l)
    plt.savefig(fig_dir+'sensitivity.pdf', bbox_inches='tight')
    plt.savefig('/home/zgriffith/public_html/paper/ps_sensitivity.pdf')
    plt.close()
