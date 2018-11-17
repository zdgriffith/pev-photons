#!/usr/bin/env python

########################################################################
# Plot the energy spectrum of an indivual HESS source.
########################################################################

import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
import scipy
from scipy import interpolate

from pev_photons import utils

def plot_data(index, color, label):
    vals = np.loadtxt(utils.prefix+'/TeVCat/hess_%s_points.txt' % index)
    E = vals.T[0]
    flux = vals.T[1]*E**2
    flux_hi = vals.T[2]*E**2
    flux_lo = vals.T[3]*E**2
    plt.errorbar(E, flux,
                 yerr=[flux - flux_lo, flux_hi - flux],
                 color=color, fmt='o', capthick=0, capsize=0,
                 mec=color, label=label, zorder=5)

#Calculate upper and lower flux bounds
def flux_calc(E, E0, phi0, phi_unc, gamma, gamma_unc):
    flip = np.greater(E, E0)  # Flip the index unc. below normalization.
    return ((phi0 + phi_unc)*(E**(2))
           *(E/E0)**(-(gamma + gamma_unc*(-1)**flip)))

def plot_fit(ax, label, source, color, index, Ecut=None, absorption=None):
    """ Plot the HESS extrapolated flux. """

    E0 = 1
    phi0 = source['flux']*1e-12
    phi_stat = source['flux_stat']*1e-12
    gamma = source['alpha']
    gamma_stat = source['alpha_stat']
    phi_sys = source['flux_sys']*1e-12
    gamma_sys = source['alpha_sys']
    E = 10**(np.arange(-1.00, 4.01, 0.00005))
    cfill = [43/256.,131/256.,186/256., 0.5]

    phi = flux_calc(E, E0,
                    phi0, 0,
                    gamma, 0)
    phi_stat_high = flux_calc(E, E0,
                              phi0, phi_stat,
                              gamma, gamma_stat)
    phi_stat_low = flux_calc(E, E0,
                             phi0, -phi_stat,
                             gamma, -gamma_stat)
    phi_sys_high = flux_calc(E, E0,
                             phi0, phi_sys,
                             gamma, gamma_sys)
    phi_sys_low = flux_calc(E, E0,
                            phi0, -phi_sys,
                            gamma, -gamma_sys)

    for flux in [phi, phi_stat_high, phi_stat_low,
                 phi_sys_high, phi_sys_low]:
            if Ecut is not None:
                flux *= np.exp(-E/Ecut)
            if absorption is not None:
                flux *= utils.apply_source_absorption(E, index)

    # The center line of the flux fit.
    if Ecut is not None:
        ax.plot(E, phi, label='Flux Extrap. '+label, color=color, linestyle='-', zorder=0)
        #The statistical uncertainty bound.
        ax.fill_between(E, phi_stat_low, phi_stat_high,
                        color=cfill, edgecolor='none', zorder=0,
                        rasterized = True)

        #The systematic uncertainty bound.
        cfill[3] = 0.15
        ax.plot(E, phi_sys_low, color=color, linestyle=':', zorder=0)
        ax.plot(E, phi_sys_high, color=color, linestyle=':', zorder=0)
    else:
        ax.plot(E, phi, label='Flux Extrap. '+label, color=color, linestyle='--', zorder=0)

def plot_limit(ax, E0, value, gamma, color, label, source, index, Ecut=None, absorption=None):
    """Plot the IceCube upper limit."""


    #Band
    b = np.linspace(0.712e3, 3.84e3, 50000)  # The 5% to 95% energy range.
    #y_band = value*b**(2-gamma)
    y_band = value*b**(2)
    y_band *= (b/E0)**-gamma
    if absorption is not None:
        y_band *= utils.apply_source_absorption(b, index)
        #y_band *= absorption_distance(source['distance'])/absorption_distance(8.5)
    if Ecut is not None:
        y_band *= np.exp(-b / Ecut)
        #color='orange'
        ax.plot(b, y_band,
                color=color, label='IceCube $\Phi_{90\%}$ '+label)
    else:
        ax.plot(b, y_band, ls='--',
                color=color, label='IceCube $\Phi_{90\%}$ '+label)

    #Arrow
    x = 10**np.mean(np.log10(b))  # Center point for which to put the arrow.
    y = value*x**(2)
    y *= (x/E0)**-gamma
    if absorption is not None:
        y *= utils.apply_source_absorption(x, index)
    if Ecut is not None:
        y *= np.exp(-x / Ecut)
        ax.plot([x, x], [y, 0.7*y], linewidth=2, color=color)
    else:
        ax.plot([x, x], [y, 0.7*y], linewidth=2, color=color, ls='--')
    ax.scatter(x, 0.7*y, marker="v", color=color, s=10)

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Plot the SED of an individual HESS source (HESS J1356-645 by default).',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--Ecut', type=float, default=300.,
                   help='Exponential cut-off value.')
    p.add_argument('--index', type=int, default=5,
                   help='Index of the HESS source.')
    args = p.parse_args()

    plt.style.use(utils.plot_style)
    colors = plt.rcParams['axes.color_cycle']

    fig, ax = plt.subplots()

    sources = np.load(utils.resource_dir + 'hess_sources.npz')
    source = {key:sources[key][args.index] for key in sources.keys()}

    plot_data(args.index, colors[0], label='H.E.S.S. Data')

    label_a = r'($\gamma$=%.2f, No E$_{\small\textrm{cut}}$, Absorp.)' % source['alpha']
    label_b = r'($\gamma$=%.2f, E$_{\small\textrm{cut}}$=%s TeV, Absorp.)' % (source['alpha'], int(args.Ecut))

    plot_fit(ax, label=label_a,
             source=source, color=colors[0], index=args.index,
             absorption=True)

    plot_fit(ax, label=label_b,
             source=source, color=colors[0], index=args.index,
             Ecut=args.Ecut, absorption=True)

    ic_fit = np.load(utils.prefix+'/TeVCat/hess_upper_limits_w_abs.npz')
    plot_limit(ax, E0=2.0e3, value=ic_fit['sensitivity'][args.index]*1e3, gamma=source['alpha'],
               color=colors[1], source=source, index=args.index, label=label_a, absorption=True)

    cut_sens = np.load(utils.prefix+'TeVCat/cut_off_abs/{}_Ecut_{}_sens.npy'.format(args.index, int(args.Ecut)))
    plot_limit(ax, E0=2.0e3, value=cut_sens*1e3, gamma=source['alpha'],
               color=colors[1], source=source, index=args.index, label=label_b, Ecut=args.Ecut, absorption=True)

    handles, labels = ax.get_legend_handles_labels()
    #l = ax.legend(loc='lower left', fontsize=14, handlelength=1.3)
    order = [4, 0,1,2,3]
    #order = [3,0,1,2]
    l = ax.legend([handles[idx] for idx in order], [labels[idx] for idx in order],
                  loc='lower left', fontsize=16, handlelength=1.3)
    utils.plot_setter(ax, l)

    ax.text(1.5, 2e-11, 'HESS J1356-645', fontsize=20)
    ax.set_xlabel('Energy [TeV]', fontweight='bold')
    ax.set_ylabel(r'E$^2$dN/dE [cm$^{-2}$s$^{-1}$TeV]', fontweight='bold')
    ax.set_xlim([1, 10**4])
    ax.set_ylim([10**-16, 10**-10])
    ax.set_xscale('log')
    ax.set_yscale('log')

    plt.savefig(utils.fig_dir+'TeVCat/hess_sed_%s_cutoff.png' % args.index, dpi=300)
    plt.savefig(utils.fig_dir+'paper/hess_J1356.pdf')
    plt.close()
