#!/usr/bin/env python

########################################################################
# Plot the energy spectrum of an indivual HESS source.
########################################################################

import argparse
import numpy as np
import matplotlib.pyplot as plt
import scipy
from scipy import interpolate

from pev_photons import utils
from gamma_ray_survival import absorption_spline

def plot_data(source, color, label):
    E2 = source['Flux_Points_Energy']**2
    plt.errorbar(source['Flux_Points_Energy'], E2*source['Flux_Points_Flux'],
                 yerr=[E2*source['Flux_Points_Flux'] - E2*source['Flux_Points_Flux_Err_Lo'],
                       E2*source['Flux_Points_Flux'] - E2*source['Flux_Points_Flux_Err_Hi']],
                 color=color, fmt='o', capthick=0, capsize=0,
                 mec=color, label=label, zorder=5)

#Calculate upper and lower flux bounds
def flux_calc(E, E0, phi0, phi_unc, gamma, gamma_unc):
    flip = np.greater(E, E0)  # Flip the index unc. below normalization.
    return ((phi0 + phi_unc)*(E**(2))
           *(E/E0)**(-(gamma + gamma_unc*(-1)**flip)))

#Plot the best fits to the source flux.
def plot_fit(label, source, colors, args, index):

    E0 = 1
    # HESS+Fermi fit information
    phi0 = source['flux']*1e-12
    phi_stat = source['flux_stat']*1e-12
    gamma = source['alpha']
    gamma_stat = source['alpha_stat']
    phi_sys = source['flux_sys']*1e-12
    gamma_sys = source['alpha_sys']
    E = 10**(np.arange(-1.00, 4.01, 0.001))
    color = colors[0]
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
            if args.Ecut is not None:
                flux *= np.exp(-E/args.Ecut)
            if not args.no_absorption:
                flux *= absorption_spline(E)

    # The center line of the flux fit.
    plt.plot(E, phi, label=label, color=color, linestyle='-', zorder=index)

    '''
    if args.Ecut is not None:
        phi *= np.exp(-E/args.Ecut)
        plt.plot(E, phi, label='{} TeV cut off'.format(args.Ecut),
                 linestyle='-.', zorder=index)
    '''

    #The statistical uncertainty bound.
    plt.fill_between(E, phi_stat_low, phi_stat_high,
                     color=cfill, edgecolor='none', zorder=index,
                     rasterized = True)

    #The systematic uncertainty bound.
    cfill[3] = 0.15
    plt.plot(E, phi_sys_low, color=color, linestyle='--', zorder=index)
    plt.plot(E, phi_sys_high, color=color, linestyle='--', zorder=index)

    return gamma

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Plot the SED of an individual HESS source (HESS J1356-645 by default).',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--no_absorption', action='store_true', default=False,
                   help='If True, fluxes have no absorption.')
    p.add_argument('--Ecut', type=int, default=None,
                   help='Option for an exponential cut-off.')
    p.add_argument('--index', type=int, default=5,
                   help='Index of the HESS source.')
    args = p.parse_args()

    plt.style.use(utils.plot_style)
    colors = plt.rcParams['axes.color_cycle']

    fig,ax = plt.subplots(1)

    sources = np.load(utils.resource_dir+'hgps_sources.npz')
    source = {key:sources[key][args.index] for key in sources.keys()}
    gamma = plot_fit('Best fit (H.E.S.S. data)', source, colors, args, 0)

    plot_data(source, colors[0], label='H.E.S.S. data')

    #IceCube Upper limit
    b = np.array([0.712*10**3,3.84*10**3])  # The 5% to 95% energy range.
    x = 10**np.mean(np.log10(b))  # Center point for which to put the arrow.

    '''
    sens = np.load(utils.prefix+'/TeVCat/hess_sens.npz')
    y0 = sens['sensitivity'][args.index]*1e9
    y = y0*(x**(2-gamma))

    plt.plot(b, y0*b**(2 - gamma),
             color=colors[1],label="IceCube 5-year 90$\%$ upper limit")
    #Arrow
    plt.plot([x, x], [y, 0.6*y], linewidth=2, color=colors[1])
    plt.scatter(x, 0.6*y, marker="v", color=colors[1], s=10)
    '''

    if args.Ecut:
        flux_i = np.load(utils.prefix+'TeVCat/cut_off/{}_Ecut_{}.npy'.format(args.index, args.Ecut))
        y0 = flux_i*1e3
        y0 *= (1e3)**gamma
        y = y0*(x**(2-gamma))

        plt.plot(b, y0*b**(2 - gamma),
                 #color=colors[1], ls='-.',
                 color=colors[1], ls='-',
                 label="IceCube UL ({} TeV cut off)".format(args.Ecut))
        #Arrow
        plt.plot([x, x], [y, 0.6*y], linewidth=2, color=colors[1])
        plt.scatter(x, 0.6*y, marker="v", color=colors[1], s=10)

    plt.xlim([3*10**-1, 10**4])
    plt.ylim([10**-16, 10**-10])
    plt.ylabel(r'E$^2$dN/dE [cm$^{-2}$s$^{-1}$TeV]', fontweight='bold')
    l = ax.legend(loc='lower left')

    utils.plot_setter(plt.gca(),l)
    plt.xlabel('Energy [TeV]', fontweight='bold')
    plt.xscale('log')
    plt.yscale('log')
    plt.savefig(utils.fig_dir+'TeVCat/hess_source_%s.png' % args.index, dpi=300)
    if args.index==5:
        plt.savefig(utils.fig_dir+'paper/hess_J1356.pdf')
    plt.close()
