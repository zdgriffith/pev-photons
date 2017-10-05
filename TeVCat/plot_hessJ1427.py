#!/usr/bin/env python

##############################
## Plot the energy spectrum ##
## of HESS J1427-608 and    ##
## our upper limit          ##
##############################

import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import scipy
from support_functions import get_fig_dir, plot_setter
fig_dir = get_fig_dir()
plt.style.use('stefan')
colors = mpl.rcParams['axes.color_cycle']

#Plot data points
def plot_data(data, label, args):
    if 'Fermi' in label:
        color     = 'k'
    else:
        color     = colors[3]

    #Convert data from ergs to eV and from E^2*Flux to Flux
    data.T[1:] *= 0.624

    #Plot in flux with just HESS, E^2*Flux with Fermi data 
    if not args.addFermi:
        data.T[1:] /= data.T[0]**2

    plt.errorbar(data.T[0], data.T[1], yerr = [data.T[1] - data.T[2], data.T[3] - data.T[2]],
                 color = color, fmt='o', capthick = 0, mec=color, label = label)
    return

#Plot fits
def plot_fit(label, args):

    E0    = 1

    if 'Fermi' in label:
        #HESS+Fermi fit information
        phi0      = 0.624*1.515*10**-12
        phi_unc   = 0.2*10**-12
        gamma     = 2.02
        gamma_unc = 0.03
        phi_sys   = 0
        gamma_sys = 0
        E         = 10**(np.arange(-3.01, 4.01, 0.001))
        mask      = (E<100000)
        color     = 'r'
        cfill     = [1, 0, 0, 0.5] #red
    else:
        #HESS fit information
        phi0      = 1.3*10**-12
        phi_unc   = 0.4*10**-12
        gamma     = 2.2
        gamma_unc = 0.1
        phi_sys   = 0.2*1.3*10**-12
        gamma_sys = 0.2
        E         = 10**(np.arange(-0.01, 4.01, 0.0001))
        mask      = (E>=1)
        color     = colors[3]
        cfill     = [253/256., 174/256., 97/256., 0.5] #burnt orange

    if args.addFermi:
        phi_high = np.zeros(len(E))
        phi_low  = np.zeros(len(E))
        phi_sys_high = np.zeros(len(E))
        phi_sys_low  = np.zeros(len(E))
        phi = phi0*(E0**(-gamma))*(E/E0)**(2-gamma)
        for i, Ei in enumerate(E):
            if Ei < E0:
                phi_high[i] += (phi0+phi_unc)*(Ei/E0)**(2-(gamma+gamma_unc))
                phi_low[i]  += (phi0-phi_unc)*(Ei/E0)**(2-(gamma-gamma_unc))
                phi_sys_high[i] += (phi0+phi_sys)*(Ei/E0)**(2-(gamma+gamma_sys))
                phi_sys_low[i]  += (phi0-phi_sys)*(Ei/E0)**(2-(gamma-gamma_sys))
            else:
                phi_high[i] += (phi0+phi_unc)*(Ei/E0)**(2-(gamma-gamma_unc))
                phi_low[i]  += (phi0-phi_unc)*(Ei/E0)**(2-(gamma+gamma_unc))
                phi_sys_high[i] += (phi0+phi_sys)*(Ei/E0)**(2-(gamma-gamma_sys))
                phi_sys_low[i]  += (phi0-phi_sys)*(Ei/E0)**(2-(gamma+gamma_sys))
    else:
        phi = phi0*(E0**(-gamma))*(E/E0)**(-gamma)
        phi_high  = (phi0+phi_unc)*(E0**(-(gamma-gamma_unc))*(E/E0)**-(gamma-gamma_unc))
        phi_low   = (phi0-phi_unc)*(E0**(-(gamma+gamma_unc))*(E/E0)**-(gamma+gamma_unc))
        phi_sys_high  = (phi0+phi_sys)*(E0**(-(gamma-gamma_sys))*(E/E0)**-(gamma-gamma_sys))
        phi_sys_low   = (phi0-phi_sys)*(E0**(-(gamma+gamma_sys))*(E/E0)**-(gamma+gamma_sys))

    if args.Ecut is not None:
        phi      *= np.exp(-E/args.Ecut)
        phi_high *= np.exp(-E/args.Ecut)
        phi_low  *= np.exp(-E/args.Ecut)

    if args.no_absorption:
        ratio  = [1]*len(E)
    else:
        surv   = np.loadtxt(args.prefix+'TeVCat/gamma_survival_vs_energy.txt')
        surv   = surv.T
        spline = scipy.interpolate.InterpolatedUnivariateSpline(surv[0]*10**-12, surv[1], k=2)
        ratio  = spline(E)

    plt.plot(E[mask],ratio[mask]*phi[mask], label = label, color = color, linestyle='-') #center line

    #Shade statistical uncertainty
    plt.fill_between(E[mask], ratio[mask]*phi_low[mask],ratio[mask]*phi_high[mask],
                     color = cfill, edgecolor = 'none')

    #Shade with lighter color for systematic error
    if 'Fermi' not in label:
        cfill[3] = 0.15
        plt.fill_between(E[mask], ratio[mask]*phi_sys_low[mask],ratio[mask]*phi_sys_high[mask],
                         color = cfill, edgecolor = 'none')
    return gamma

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Plot a skymap',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', dest='prefix', type = str,
                   default = '/data/user/zgriffith/pev_photons/',
                   help    = 'base directory for file storing')
    p.add_argument('--addFermi', dest='addFermi', action = 'store_true',
            default = False, help='if True, plot Fermi data and fit as well')
    p.add_argument('--no_absorption', dest='no_absorption', action = 'store_true',
            default = False, help='if True, flux extrapolations have no absorption')
    p.add_argument('--Ecut', dest='Ecut', type = float, default = None,
            help='Option for an exponential cut-off in the flux predictions')
    args = p.parse_args()

    fig,ax = plt.subplots(1)

    #Data points
    hess_data = np.loadtxt(args.prefix+'TeVCat/hessJ1427_data.txt') 
    plot_data(hess_data, 'H.E.S.S. Data', args)
    gamma     = plot_fit('H.E.S.S. Best Fit', args)
    if args.addFermi:
        fermi_data = np.loadtxt(args.prefix+'TeVCat/hessJ1427_fermi_data.txt') 
        plot_data(fermi_data, 'Fermi Data', args)
        combined_gamma = plot_fit('H.E.S.S.+Fermi Best Fit', args)

    #IceCube Upper limit
    b  = np.array([0.712*10**3,3.84*10**3]) #5% and 95% containment values in energy
    x  = 10**np.mean(np.log10(b)) #Center point in log space to put the arrow
    y0 = 4.7e-20 
    if args.addFermi:
        y0 *= 10**6
        y  = y0*((x/(10**3))**(2-gamma))
        plt.plot(b, y0*((b/(10**3))**(2-gamma)), color = colors[4],label="IceCube 5 year 90$\%$ U.L.")
    else:
        y  = y0*(x/(10**3))**-gamma
        plt.plot(b, y0*((b/(10**3))**(-gamma)), color = colors[4],label="IceCube 5 year 90$\%$ U.L.")


    #Arrow
    plt.plot([x,x], [y,0.6*y],linewidth=2.,color=colors[4])
    plt.scatter(x,0.6*y,marker="v",color=colors[4],s=10)

    #Reorder legend and make the lines thicker
    handles,labels = ax.get_legend_handles_labels()
    #handles = [handles[3], handles[0], handles[1], handles[2]]
    #labels  = [labels[3], labels[0], labels[1], labels[2]]

    if args.addFermi:
        plt.xlim([10**-3, 10**4])
        plt.ylim([10**-14, 10**-11])
        plt.ylabel(r'E$^2$dN/dE [cm$^{-2}$s$^{-1}$TeV]', fontweight='bold')
        outFile = 'hessJ1427_with_fermi_and_abs.pdf'
        l       = ax.legend(handles,labels, loc='lower left', fontsize = 16, prop={'weight':'bold'})
    else:
        plt.xlim([5*10**-1, 10**4])
        plt.ylim([10**-21, 0.5*10**-11])
        plt.ylabel(r'dN/dE [cm$^{-2}$s$^{-1}$TeV$^{-1}$]', fontweight='bold')
        outFile = 'hessJ1427.pdf'
        l       = ax.legend(handles,labels, loc='upper right', fontsize = 16, prop={'weight':'bold'})

    plot_setter(plt.gca(),l)
    plt.xlabel('Energy [TeV]', fontweight='bold')
    plt.text(1,10**-20, 'IceCube Preliminary', color = 'r', fontsize=14) # unpublished disclaimer
    plt.xscale('log')
    plt.yscale('log')
    plt.tight_layout()
    plt.savefig(fig_dir+outFile)
    plt.close()
