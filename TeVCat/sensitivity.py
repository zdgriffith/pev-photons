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

from support_functions import get_fig_dir, plot_setter

plt.style.use('stefan')
colors = mpl.rcParams['axes.color_cycle']
fig_dir = get_fig_dir()

def sens_plot(args):
    dec_list = np.arange(-85.0,-53.1,0.3)
    alphas = [2.0,2.7]
    kinds = ['sens', 'disc']
    kind_labels = ['Sensitivity', 'Discovery Potential']
    linestyle = ['-', '--']

    for i, alpha in enumerate(alphas):
        for j, kind in enumerate(kinds):
            decs = []
            fluxes = []
            for dec in dec_list:
                try:
                    flux = np.load((args.prefix+'sensitivity_trials/'+kind+
                                    '_%.4f_dec_alpha_%s.npy' % (dec, alpha)))
                except:
                    continue
                fluxes.append(flux*1e-6)
                decs.append(dec)

            plt.plot(decs, fluxes,
                     color=colors[i], ls=linestyle[j],
                     label='E$^{-%s}$ %s' % (alpha, kind_labels[j]))

    sources = np.load(args.prefix+'TeVCat/hess_sources.npz')
    if args.no_absorption:
        ratio = 1
    else:
        surv = np.loadtxt(args.prefix+'TeVCat/gamma_survival_vs_distance.txt')
        surv = surv.T
        spline = scipy.interpolate.InterpolatedUnivariateSpline(surv[0],
                                                                surv[1], k=2)
        ratio = spline(sources['distance'])

    middle = sources['flux']*1000**(-sources['alpha'])*1e-12
    stat_upper = ((sources['flux']+sources['flux_stat'])
                 *1000**(-sources['alpha']+sources['alpha_stat'])*1e-12)
    stat_lower = ((sources['flux']-sources['flux_stat'])
                 *1000**(-sources['alpha']-sources['alpha_stat'])*1e-12)
    sys_upper = ((sources['flux']+sources['flux_sys'])
                 *1000**(-sources['alpha']+sources['alpha_sys'])*1e-12)
    sys_lower = ((sources['flux']-sources['flux_sys'])
                 *1000**(-sources['alpha']-sources['alpha_sys'])*1e-12)

    plt.errorbar(sources['dec'], ratio*middle,
                 yerr=ratio*np.array([np.abs(middle-stat_lower),
                                      np.abs(middle-stat_upper)]),
                 fmt='o', color=colors[4],
                 lw=2, capthick=0, capsize=0,
                 ms=5, label='Extrapolated H.E.S.S. Sources')

    plt.errorbar(sources['dec'], ratio*middle,
                 yerr=ratio*np.array([np.abs(middle-sys_lower),
                                      np.abs(middle-sys_upper)]),
                 fmt='none', color=colors[4], ecolor=colors[4],
                 lw=6, elinewidth=0, capthick=0, capwidth=0, alpha=0.4)


if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Plot the sensitivity as a function of declination.',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', default='/data/user/zgriffith/pev_photons/',
                   help='base directory for file storing')
    p.add_argument('--no_absorption', action='store_true',
                   default=False,
                   help='if True, flux extrapolations have no absorption')
    args = p.parse_args()

    sens_plot(args)

    plt.xlim([-81, -54])
    plt.ylim([1e-21, 5e-17])
    plt.xlabel(r'Declination [$^{\circ}$]')
    plt.ylabel('Flux at 1 PeV [cm$^{-2}$s$^{-1}$TeV$^{-1}$]')
    plt.yscale('log')
    plt.text(-80, 2e-21, 'IceCube Preliminary', color='r', fontsize=14)
    l = plt.legend(loc='upper left', fontsize=18, prop={'weight':'bold'})
    plot_setter(plt.gca(),l)
    plt.savefig(fig_dir+'sensitivity.pdf', bbox_inches='tight')
    plt.savefig('/home/zgriffith/public_html/paper/ps_sensitivity.pdf')
    plt.close()
