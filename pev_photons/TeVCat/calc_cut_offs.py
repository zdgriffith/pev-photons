#!/usr/bin/env python

########################################################################
# Calculate the Energy cut-offs for each HESS source.
########################################################################

import os
import argparse
import numpy as np
import scipy
from scipy import interpolate

from pev_photons import utils

def calc_flux(flux_0, alpha, E, E_0, Ecut=None, ratio=None):
        flux = flux_0*(E/E_0)**(-alpha)
        if Ecut is not None:
            flux *= np.exp(-E / Ecut)
        if ratio is not None:
            flux *= ratio
        return flux[0]

def crossing_point(E, flux_a, flux_b):
    sens_zone = E[np.greater(flux_a, flux_b)]
    if len(sens_zone) == 0:
        return np.nan
    else:
        return sens_zone[0]

if __name__ == "__main__":

    hess = np.load(os.path.join(utils.resource_dir, 'hess_sources.npz'))

    cut_offs= np.zeros(len(hess['flux']))
    for i in range(len(hess['flux'])):
        if i in [2, 7]:
            continue
        if i in [5]:
            Ecut = np.array(range(100, 30100, 100))
        else:
            Ecut = np.array(range(100, 20100, 100))
        flux = calc_flux(hess['flux'][i]*1e-12, hess['alpha'][i],
                         E=2e3, E_0=1,
                         Ecut=Ecut, ratio=utils.apply_source_absorption(2e3, i))

        sens = np.zeros(Ecut.shape[0])
        for j, E_i in enumerate(Ecut):
            try:
                flux_i = np.load(utils.prefix+'TeVCat/cut_off_abs/{}_Ecut_{}_sens.npy'.format(i, E_i))
            except:
                flux_i = np.load(utils.prefix+'TeVCat/cut_off_abs/{}_Ecut_{}_sens.npy'.format(i, E_i-100))
            sens[j] = calc_flux(flux_i*1e3, hess['alpha'][i], E=2e3,
                                E_0=2e3, Ecut=Ecut,
                                ratio=utils.apply_source_absorption(2e3, i))

        cut_offs[i] = crossing_point(Ecut, flux, sens)

    print(hess['name'])
    print(cut_offs)
    print(hess['distance'])
    #np.save(utils.prefix+'TeVCat/hess_cut_offs.npy', cut_offs)
