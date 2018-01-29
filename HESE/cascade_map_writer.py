#!/usr/bin/env python

########################################################################
# Create the source template for the HESE cascade correlation search
########################################################################

import numpy as np
import healpy as hp
import pandas as pd

from utils.support import prefix, resource_dir

def combine_srcs(src_ra, src_dec, ev):
    """ Combine the signal PDFs of each source """
    cos_ev  = np.sqrt(1. - np.sin(ev['dec'].values)**2)
    cosDist = (np.cos(src_ra[:, np.newaxis] - ev['ra'].values)
               * np.cos(src_dec[:, np.newaxis]) * cos_ev
               + np.sin(src_dec[:, np.newaxis]) * np.sin(ev['dec'].values))

    # handle possible floating precision errors
    cosDist[np.isclose(cosDist, 1.) & (cosDist > 1)] = 1.
    dist = np.arccos(cosDist)
    sigma = ev['err'].values/2.

    S = (1./(2.*np.pi*sigma**2) * np.exp(-dist**2 /(2.*sigma**2)))

    return np.sum(S, axis=1)/float(len(ev['dec'].values))

if __name__ == "__main__":

    events = pd.read_hdf(resource_dir+'HESE.hdf5')
    cascades = events[events['is_cascade']]

    nside = 256
    npix = hp.nside2npix(nside)
    dec, ra = hp.pix2ang(nside, range(npix))

    signal_pdf = combine_srcs(ra, np.pi/2.-dec, cascades)

    # Convert from equatorial to galactic coordinates
    """
    theta_gal, phi_gal = hp.Rotator(coord = ['G','C'], rot = [0,0])(dec, ra)
    pix = hp.ang2pix(nside, theta_gal, phi_gal)
    signal_pdf = np.take(signal_pdf, pix)
    """

    np.save(prefix+'HESE/source_templates/cascades.npy', signal_pdf)
