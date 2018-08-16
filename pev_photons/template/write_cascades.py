#!/usr/bin/env python

########################################################################
# Create the source template for the HESE cascade correlation search
########################################################################

import numpy as np
import healpy as hp
import pandas as pd

from pev_photons.utils.support import prefix, resource_dir

if __name__ == "__main__":

    hese = np.load('/data/user/wgiang/yr4HESE/unblindedandsmoothedmaps.pickle')
    indices = [49, 32, 37, 24, 25, 28, 15, 1, 5, 8]
    cascades = np.take(hese, indices, axis=0)

    cascades = (10**cascades)/np.sum(10**cascades, axis=1)[:,np.newaxis]
    cascades = np.sum(cascades, axis=0)
    cascades = cascades/np.sum(cascades)

    npix = len(cascades)
    nside = hp.npix2nside(npix)
    dec, ra = hp.pix2ang(nside, range(npix))

    # Convert from equatorial to galactic coordinates
    theta_gal, phi_gal = hp.Rotator(coord = ['G','C'], rot = [180,180])(dec, ra)
    pix = hp.ang2pix(nside, theta_gal, phi_gal)
    cascades = np.take(cascades, pix)
    np.save(prefix+'resources/cascade_template.npy', cascades)
