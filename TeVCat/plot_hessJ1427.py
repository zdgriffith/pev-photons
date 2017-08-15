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
from support_functions import get_fig_dir, plot_setter
fig_dir = get_fig_dir()
plt.style.use('stefan')
colors = mpl.rcParams['axes.color_cycle']

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Plot a skymap',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', dest='prefix', type = str,
                   default = '/data/user/zgriffith/pev_photons/TeVCat/',
                   help    = 'base directory for file storing')
    p.add_argument('--inFile', dest='inFile', type = str,
                   default = 'hessJ1427_data.txt',
                   help    = 'input file with source data')
    p.add_argument('--outFile', dest='outFile', type = str,
                   default = 'hessJ1427.pdf',
                   help    = 'plot file name')
    p.add_argument('--addFermi', dest='addFermi', action = 'store_true',
            default = False, help='if True, plot Fermi data and fit as well')
    args = p.parse_args()

    fig,ax = plt.subplots(1)

    #HESS fit information
    phi0      = 1.3*10**-12
    phi_unc   = 0.4*10**-12
    gamma     = 2.2
    gamma_unc = 0.3
    bound     = 50. # Energy in TeV to switch from "known" HESS fit to "extrapolated"

    #HESS data points
    hess_data = np.loadtxt(args.prefix+args.inFile) 

    #Convert data from ergs to eV and from E^2*Flux to Flux
    hess_data.T[1:4] = 0.624*hess_data.T[1:4]/hess_data.T[0]**2
    plt.errorbar(hess_data.T[0], hess_data.T[1], yerr = [hess_data.T[1] - hess_data.T[2], hess_data.T[3] - hess_data.T[2]],
                 color = colors[3], fmt='o', capthick = 0, mec=colors[3], label = 'HESS J1427-608')

    #Plot the HESS best fit line with uncertainty
    E0  = 1
    E   = 10**(np.arange(-0.01, 4.01, 0.01))
    phi = phi0*(E0**(-gamma))*(E/E0)**(-gamma)
    mask = (E>=1)&(E<bound)
    plt.plot(E[mask],phi[mask], label = 'Best Fit', color = colors[3], linestyle='-') #center line
    mask = (E>bound)
    plt.plot(E[mask],phi[mask], color = colors[3], linestyle='-.', label = 'Best Fit (Extrapolated)') #center line in extrap. region

    #Uncertainty bounds
    phi_high  = (phi0+phi_unc)*(E0**(-(gamma-gamma_unc))*(E/E0)**-(gamma-gamma_unc))
    phi_low   = (phi0-phi_unc)*(E0**(-(gamma+gamma_unc))*(E/E0)**-(gamma+gamma_unc))

    #Shade uncertainty region
    cfill = [253/256., 174/256., 97/256., 0.5] #burnt orange color
    mask = E<(bound+0.5)
    plt.fill_between(E[mask], phi_low[mask],phi_high[mask],
                     color = cfill, edgecolor = 'none')

    #Shade with lighter color in extrap. region
    cfill = [253/256., 174/256., 97/256., 0.15] #more transparent burnt orange
    mask = E>bound
    plt.fill_between(E[mask], phi_low[mask],phi_high[mask],
                     color = cfill, edgecolor = 'none')

    #IceCube Upper limit
    b = np.array([0.712*10**3,3.84*10**3]) #5% and 95% containment values in energy
    x = 10**np.mean(np.log10(b)) #Center point in log space to put the arrow
    y0 = 4.28e-20
    y  = y0*((10**3)/x)**gamma

    #Line
    plt.plot(b, y0*((10**3)/b)**gamma, color = colors[4],label="IceCube 5 year 90$\%$ Upper Limit")

    #Arrow
    plt.plot([x,x], [y,0.6*y],linewidth=2.,color=colors[4])
    plt.scatter(x,0.6*y,marker="v",color=colors[4],s=10)

    #Reorder legend and make the lines thicker
    handles,labels = ax.get_legend_handles_labels()
    handles = [handles[3], handles[0], handles[1], handles[2]]
    labels  = [labels[3], labels[0], labels[1], labels[2]]
    l       = ax.legend(handles,labels, loc='upper right', fontsize = 16, prop={'weight':'bold'})
    plot_setter(plt.gca(),l)

    plt.text(1,10**-20, 'IceCube Preliminary', color = 'r', fontsize=14) # unpublished disclaimer

    plt.xlim([5*10**-1, 10**4])
    plt.ylim([10**-21, 0.5*10**-11])
    plt.xlabel('Energy [TeV]', fontweight='bold')
    plt.ylabel(r'dN/dE [cm$^{-2}$s$^{-1}$TeV$^{-1}$]', fontweight='bold')
    plt.xscale('log')
    plt.yscale('log')
    plt.tight_layout()
    plt.savefig(fig_dir+args.outFile)
    plt.close()
