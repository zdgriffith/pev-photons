#!/usr/bin/env python

########################################################################
# Get the position of the hottest spot in a map 
########################################################################

import numpy as np
import healpy as hp

if __name__ == "__main__":

    m = np.load('/data/user/zgriffith/pev_photons/all_sky/skymap.npy')
    nside = 512
    npix  = hp.nside2npix(nside)
    theta, ra = hp.pix2ang(nside, range(npix))
    dec = np.pi/2. - theta
    mask = np.greater(np.degrees(dec), -85.0)&np.less(np.sin(dec), -0.8)
    max_ts_list = np.flip(np.sort(m[mask]), axis=0)[0:10]
    for ts in max_ts_list:
        index = np.isclose(m[mask],ts)
        print(ts)
        print(np.degrees(dec[mask][index]))
        print(np.degrees(ra[mask][index]))
