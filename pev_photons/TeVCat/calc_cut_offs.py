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

def absorption(fname):
    surv = np.loadtxt(os.path.join(utils.resource_dir,
                                   'gamma_survival_vs_distance.txt'))
    surv = surv.T
    spline = scipy.interpolate.InterpolatedUnivariateSpline(surv[0],
                                                            surv[1], k=2)
    return spline

def calc_flux(flux_0, alpha, E, E_0, Ecut=None, ratio=None):
        flux = flux_0*(E/E_0)**(-alpha)
        if Ecut is not None:
            flux *= np.exp(-E / Ecut)
        if ratio is not None:
            flux *= ratio
        return flux

def crossing_point(E, flux_a, flux_b):
    sens_zone = E[np.greater(flux_a, flux_b)]
    if len(sens_zone) == 0:
        return np.nan
    else:
        return sens_zone[0]

if __name__ == "__main__":

    hess = np.load(os.path.join(utils.resource_dir, 'hgps_sources.npz'))

    absorp_spline = absorption(utils.resource_dir+'gamma_survival_vs_distance.txt')
    ratio = absorp_spline(hess['distance'])

    Ecut = np.append(range(10, 1010, 10), range(1100, 10100, 100))
    cut_offs= np.zeros(len(hess['flux']))
    for i in range(len(hess['flux'])):
        flux = calc_flux(hess['flux'][i]*1e-12, hess['alpha'][i],
                         E=1e3, E_0=1,
                         Ecut=Ecut, ratio=ratio[i])

        sens = np.zeros(Ecut.shape[0])
        for j, E_i in enumerate(Ecut):
            flux_i = np.load(utils.prefix+'TeVCat/cut_off/{}_Ecut_{}.npy'.format(i, E_i))
            sens[j] = calc_flux(flux_i*1e3, hess['alpha'][i], E=1e3, E_0=1e3)

        cut_offs[i] = crossing_point(Ecut, flux, sens)
    print(hess['name'])
    print(cut_offs)
    print(hess['distance'])
