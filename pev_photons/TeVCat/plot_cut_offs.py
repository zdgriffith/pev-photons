#!/usr/bin/env python

########################################################################
# Plot the HESS flux extrapolations and IceCube sensitivites
# as a function of energy cut off
########################################################################

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
    hess = np.load(utils.resource_dir+'hgps_sources.npz')
    hess_sens = np.load(utils.prefix+'TeVCat/hess_sens.npz')

    surv = np.loadtxt(utils.resource_dir+'gamma_survival_vs_distance.txt')
    surv = surv.T
    spline = scipy.interpolate.InterpolatedUnivariateSpline(surv[0],
                                                            surv[1], k=2)
    ratio = spline(hess['distance'])

    E = np.arange(1, 10000, 0.1)
    Ecut = np.append(range(10, 1010, 10), range(1100, 10100, 100))
    for i, (j, k) in enumerate(product(range(row_n), range(col_n))):
        flux = hess['flux'][i]*(1e3)**(-hess['alpha'][i])
        flux *= np.exp(-1e3 / E)*1e-12
        flux *= ratio[i]
        ax[j, k].plot(E, flux, label='H.E.S.S. Extrap.')

        sens = []
        for E_i in Ecut:
            flux_i = np.load(utils.prefix+'TeVCat/cut_off/{}_Ecut_{}.npy'.format(i, E_i))
            sens.append(flux_i*1e3)

        ax[j, k].plot(Ecut, sens, label='Sensitivity')

        if j == (row_n-1):
            ax[j, k].set_xlabel('Energy Cut Off [TeV]', fontsize=14)
        if k == 0:
            ax[j, k].set_ylabel('Flux ', fontsize=14)
        ax[j, k].set_xscale('log')
        ax[j, k].set_yscale('log')
        ax[j, k].set_xlim([50, 10000])
        ax[j, k].set_ylim([1e-22, 1e-15])
        if k == 0 and j == 0:
            ax[j, k].legend(fontsize=12, loc='upper right')

    plt.tight_layout()
    plt.savefig(utils.fig_dir+'TeVCat/cut_offs.png', dpi=300)
    plt.close()
