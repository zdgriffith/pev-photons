#!/usr/bin/env python

########################################################################
# Plot the energy spectrum of HESS J1427-608
# with this analysis' upper limit.
########################################################################

import argparse
import numpy as np
import matplotlib.pyplot as plt
import scipy
from scipy import interpolate

from pev_photons.utils.support import resource_dir, fig_dir, plot_setter, plot_style, prefix
from gamma_ray_survival import absorption_spline

def plot_hgps_data(source, color, label):
    E2 = source['Flux_Points_Energy'][0:4]**2
    plt.errorbar(source['Flux_Points_Energy'][0:4], E2*source['Flux_Points_Flux'][0:4],
                 yerr=[E2*source['Flux_Points_Flux'][0:4] - E2*source['Flux_Points_Flux_Err_Lo'][0:4],
                       E2*source['Flux_Points_Flux'][0:4] - E2*source['Flux_Points_Flux_Err_Hi'][0:4]],
                 color=color, fmt='o', capthick=0, capsize=0,
                 mec=color, label=label, zorder=5)
    E2 = source['Flux_Points_Energy'][4:6]**2
    x = source['Flux_Points_Energy'][4:6]
    y = E2*source['Flux_Points_Flux_UL'][4:6]
    
    for index in [4, 5]:
        plt.plot([source['Flux_Points_Energy_Min'][index],
                  source['Flux_Points_Energy_Max'][index]],
                  [y, y], linewidth=2, color=color)
    plt.plot([x, x], [y, 0.6*y], linewidth=2, color=color)
    plt.scatter(x, 0.6*y, marker="v", color=color, s=10)

def plot_new_fit(source, color, args, index):

    E0 = 1
    # HESS+Fermi fit information
    phi0 = source['flux']*1e-12
    phi_stat = source['flux_stat']*1e-12
    gamma = source['alpha']
    gamma_stat = source['alpha_stat']
    phi_sys = source['flux_sys']*1e-12
    gamma_sys = source['alpha_sys']
    E = 10**(np.arange(-1.00, 4.01, 0.001))
    cfill = [1.,0, 0, 0.5]

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
    plt.plot(E, phi, color=color, linestyle='-', zorder=index)

    #The statistical uncertainty bound.
    plt.fill_between(E, phi_stat_low, phi_stat_high,
                     color=cfill, edgecolor='none', zorder=index,
                     rasterized = True)

    #The systematic uncertainty bound.
    cfill[3] = 0.15
    plt.plot(E, phi_sys_low, color=color, linestyle='--', zorder=index)
    plt.plot(E, phi_sys_high, color=color, linestyle='--', zorder=index)

#Plot data points
def plot_data(data, label, colors, args):
    if 'Fermi' in label:
        color = 'k'
    else:
        color = colors[3]

    #Convert data from ergs to eV and from E^2*Flux to Flux
    data.T[1:] *= 0.624

    #Plot in flux with just HESS, E^2*Flux with Fermi data 
    if not args.addFermi:
        data.T[1:] /= data.T[0]**2

    plt.errorbar(data.T[0], data.T[1],
                 yerr=[data.T[1] - data.T[2], data.T[3] - data.T[2]],
                 color=color, fmt='o', capthick=0, capsize=0,
                 mec=color, label=label, zorder=5)
    return

#Calculate upper and lower flux bounds
def flux_calc(E, E0, phi0, phi_unc, gamma, gamma_unc):
    flip = np.greater(E, E0)  # Flip the index unc. below normalization.
    return ((phi0 + phi_unc)*(E0**(-gamma))
           *(E/E0)**(2 - (gamma + gamma_unc*(-1)**flip)))

#Plot the best fits to the source flux.
def plot_fit(label, colors, args, index):

    E0 = 1
    if 'Fermi' in label:
        # HESS+Fermi fit information
        phi0 = 0.624 * 1.515e-12
        phi_stat = 0.2e-12
        gamma = 2.02
        gamma_stat = 0.03
        phi_sys = 0
        gamma_sys = 0
        E = 10**(np.arange(-3.01, 4.01, 0.001))
        color = colors[0]
        cfill = [43/256.,131/256.,186/256., 0.5]
    else:
        # HESS fit information
        phi0 = 1.3e-12
        phi_stat = 0.4e-12
        gamma = 2.2
        gamma_stat = 0.1
        phi_sys = 0.2 * 1.3e-12
        gamma_sys = 0.2
        E = 10**(np.arange(0, 4.01, 0.0001))
        color = colors[3]
        cfill = [253/256., 174/256., 97/256., 0.5] #burnt orange

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
            description='Plot the SED of HESS J1427-608',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--addFermi', action='store_true', default=False,
                   help='If True, plot Fermi data and combined fit.')
    p.add_argument('--no_absorption', action='store_true', default=False,
                   help='If True, fluxes have no absorption.')
    p.add_argument('--Ecut', type=float, default=None,
                   help='Option for an exponential cut-off.')
    args = p.parse_args()

    plt.style.use(plot_style)
    colors = plt.rcParams['axes.color_cycle']

    fig,ax = plt.subplots(1)

    #Data points
    hess_data = np.loadtxt(resource_dir+'/hessJ1427_data.txt') 
    plot_data(hess_data, 'H.E.S.S. data', colors, args)
    gamma = plot_fit('Best fit (H.E.S.S. data)', colors, args, 0)
    if args.addFermi:
        fermi_data = np.loadtxt(resource_dir+'/hessJ1427_fermi_data.txt') 
        plot_data(fermi_data, 'Fermi data', colors, args)
        #combined_gamma = plot_fit('Best fit (combined H.E.S.S. and Fermi data)',
        combined_gamma = plot_fit('Best fit (H.E.S.S. + Fermi)',
                                  colors, args, 1)

    #IceCube Upper limit
    b = np.array([0.712*10**6,3.84*10**6])  # The 5% to 95% energy range.
    x = 10**np.mean(np.log10(b))  # Center point for which to put the arrow.
    y0 = (6.7711930683032905e-10)*(1e-3)
    if args.addFermi:
        y = y0*(x**(2-gamma))
        print(y)
        plt.plot(b*1e-3, y0*b**(2 - gamma),
                 color=colors[4],label="IceCube 5-year 90$\%$ upper limit")
    else:
        y = y0*x**(-gamma)
        plt.plot(b*1e-3, y0*b**(-gamma),
                 color=colors[4],label="IceCube 5-year 90$\%$ upper limit")

    sources = np.load(prefix+'hgps_sources.npz')
    source = {key:sources[key][8] for key in sources.keys()}
    plot_hgps_data(source, 'r', label='New H.E.S.S. data')
    plot_new_fit(source, 'r', args, 0)

    #Arrow
    plt.plot([x*1e-3, x*1e-3], [y, 0.6*y], linewidth=2, color=colors[4])
    plt.scatter(x*1e-3, 0.6*y, marker="v", color=colors[4], s=10)

    #Reorder legend and make the lines thicker
    handles,labels = ax.get_legend_handles_labels()
    #handles = [handles[4], handles[3], handles[0], handles[1], handles[2]]
    #labels  = [labels[4], labels[3], labels[0], labels[1], labels[2]]

    if args.addFermi:
        plt.xlim([10**-3, 10**4])
        #plt.ylim([10**-14, 10**-11])
        #plt.ylim([10**-18, 10**-11])
        plt.ylim([10**-16, 10**-11])
        plt.ylabel(r'E$^2$dN/dE [cm$^{-2}$s$^{-1}$TeV]', fontweight='bold')
        outFile = 'hessJ1427_with_fermi_and_abs.pdf'
        l = ax.legend(handles, labels, loc='lower left',
                      fontsize=16, prop={'weight':'bold'})
        #plt.text(1.5e-3,7*10**-12, 'IceCube Preliminary', color='r', fontsize=14)
        plt.text(1.2e-3,5*10**-12, 'IceCube Preliminary', color='r', fontsize=14)
    else:
        plt.xlim([5*10**-1, 10**4])
        plt.ylim([10**-21, 0.5*10**-11])
        plt.ylabel(r'dN/dE [cm$^{-2}$s$^{-1}$TeV$^{-1}$]', fontweight='bold')
        outFile = 'hessJ1427.pdf'
        l = ax.legend(handles,labels, loc='upper right',
                      fontsize=16, prop={'weight':'bold'})
        plt.text(1,10**-20, 'IceCube Preliminary', color='r', fontsize=14)

    plot_setter(plt.gca(),l)
    plt.xlabel('Energy [TeV]', fontweight='bold')
    plt.xscale('log')
    plt.yscale('log')
    plt.tight_layout()
    plt.savefig(fig_dir+'TeVCat/'+outFile)
    if args.addFermi:
        plt.savefig(fig_dir+'paper/hess_J1427.pdf')
    plt.close()
