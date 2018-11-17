#!/usr/bin/env python

########################################################################
# Plot the HESS flux extrapolations and IceCube sensitivites
# as a function of energy cut off
########################################################################

import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
from itertools import product
import scipy
from scipy import interpolate

from pev_photons import utils

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Plot HESS source energy cut off sensitivities.',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    args = p.parse_args()

    plt.style.use(utils.plot_style)
    colors = plt.rcParams['axes.color_cycle']

    row_n = 5
    col_n = 3
    fig, ax = plt.subplots(row_n, col_n, sharex='col', figsize=(12, 9))
    hess = np.load(utils.resource_dir+'hess_sources.npz')
    hess_sens = np.load(utils.prefix+'TeVCat/hess_sens_2pev_old.npz')

    E = np.arange(100, 50000, 0.1)
    cut_offs = np.load(utils.prefix+'TeVCat/hess_cut_offs.npy')
    for i, (j, k) in enumerate(product(range(row_n), range(col_n))):
        if i in [5]:
            Ecut = np.array(range(100, 30100, 100))
        else:
            Ecut = np.array(range(100, 20100, 100))
        ax[j, k].set_title(hess['name'][i], fontsize=12)
        if i in [2,7]:
            ax[j, k].text(25, 0.5, 'N/A', fontsize=25)
            continue
        flux = hess['flux'][i]*(2e3)**(-hess['alpha'][i])
        flux *= np.exp(-2e3 / E)*1e-12
        flux *= utils.apply_source_absorption(2e3, i)

        sens = []
        disc = []
        for E_i in Ecut:
            try:
                flux_i = np.load(utils.prefix+'TeVCat/cut_off_abs/{}_Ecut_{}_sens.npy'.format(i, E_i))
            except:
                flux_i = np.load(utils.prefix+'TeVCat/cut_off_abs/{}_Ecut_{}_sens.npy'.format(i, E_i-100))
            flux_i *= np.exp(-2e3 / E_i)
            flux_i *= utils.apply_source_absorption(2e3, i)
            sens.append(flux_i*1e3)
 
        ax[j, k].plot(E*1e-3, flux, label='$\Phi_{HESS}$(2 PeV)')
        ax[j, k].plot(Ecut*1e-3, sens, label='$\Phi_{90\%}$(2 PeV)')
        if cut_offs[i]:
            ax[j, k].axvline(x=cut_offs[i]*1e-3, ls=':', color='k')
        if k == 1 and j == 3:
            ax[j, k].legend(fontsize=16, loc='lower right')

        if j == (row_n-1):
            ax[j, k].set_xlabel('Energy Cut Off [PeV]', fontsize=14)
        if k == 0:
            ax[j, k].set_ylabel('Flux at 2 PeV', fontsize=14)
        ax[j, k].set_xscale('log')
        ax[j, k].set_yscale('log')
        ax[j, k].set_xlim([0.1, 50])
        ax[j, k].set_ylim([3e-23, 5e-19])

    plt.tight_layout()
    plt.savefig(utils.fig_dir+'TeVCat/cut_offs_2pev_abs.png', dpi=300)
    plt.close()
