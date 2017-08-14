#!/usr/bin/env python

# Converts the TS map to a p-value map

import healpy as hp
import numpy as np

if __name__ == "__main__":

    pre      = np.load('/data/user/zgriffith/pev_photons/all_sky/skymap.npy')
    post     = np.ones_like(pre)
    decPix   = np.load('/data/user/zgriffith/all_sky/dec_vals.npz')
    pixels   = decPix['pix_list']
    njobs    = 342
    for job in range(njobs):
        print(job)
        a      = np.load('/data/user/zgriffith/skylab/dec_TS_job_%s.npz' % float(job))
        trials = a['indv_trials'][0:500000]
        pix    = pixels[job]
        for p in pix:
            post[p] = np.sum(np.greater_equal(trials,pre[p]))/float(len(trials))

    np.save('/data/user/zgriffith/pev_photons/all_sky/p_value_skymap.npy', post)
