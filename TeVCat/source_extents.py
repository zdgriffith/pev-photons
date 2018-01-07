#!/usr/bin/env python

########################################################################
# Add Source extend to hess sources object
########################################################################

import numpy as np

from pev_photons.support import prefix

if __name__ == "__main__":
    sources = np.load(prefix+'TeVCat/hess_sources.npz')

    extent_major = np.array([0.2, 0.15, 0.05, 0.082, 0.17,
                             0.04, 0.055, 0.31, 0.11, 0,
                             0.15, 0.26, 0.14, 0.18, 0.13])
    extent_minor = np.array([0.2, 0.15, 0.05, 0.055, 0.17,
                             0.08, 0.05, 0.17, 0.04, 0,
                             0.15, 0.26, 0.14, 0.18, 0.13])

    a = {}
    for key in sources.keys():
        a[key] = sources[key]
    a['extent'] = np.sqrt((extent_major**2 + extent_minor**2)/2.)

    np.savez(prefix+'TeVCat/hess_sources.npz', **a)
