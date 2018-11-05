#!/usr/bin/env python

########################################################################
# Plots the survival function(s) for gamma rays
########################################################################

import numpy as np
import scipy
from scipy import interpolate

from pev_photons.utils.support import resource_dir

def apply_absorption(E, distance):
    surv_by_E = np.loadtxt(resource_dir+'cmb_absorption.txt')
    E_spline = scipy.interpolate.InterpolatedUnivariateSpline(surv_by_E.T[0]*10**-12,
                                                              surv_by_E.T[1], k=2)
    surv_by_dist = np.loadtxt(resource_dir+'survival_vs_distance.txt')
    dist_spline = scipy.interpolate.InterpolatedUnivariateSpline(surv_by_dist.T[0],
                                                                 surv_by_dist.T[1].T, k=2)
    if np.isscalar(E):
        return np.min([E_spline(E)*(dist_spline(distance)/dist_spline(8.5)), 1])
    else:
        return np.min([E_spline(E)*(dist_spline(distance)/dist_spline(8.5)), [1]*len(E)], axis=0)
