#!/usr/bin/env python

########################################################################
# Perform a scan over the entire FOV, evaluating the TS at each pixel.
########################################################################

import argparse
import numpy as np
import logging

import healpy as hp

from load_datasets import load_ps_dataset

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Create an all sky TS map.',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', type=str,
                   default='/data/user/zgriffith/pev_photons/',
                   help='The base directory for file storing.')
    p.add_argument('--outFile', type=str,
                   default='all_sky/skymap.npy',
                   help='The output file name.')
    p.add_argument("--ncpu", type=int, default=1,
                    help="Number of cores to run on.")
    p.add_argument("--seed", type=int, default=1,
                   help='rng seed')
    p.add_argument('--extension', type=float, default=0,
                   help='Spatial extension to source hypothesis in degrees.')
    args = p.parse_args()

    ps_llh = load_ps_dataset(args)
    logging.getLogger("skylab.ps_llh.PointSourceLLH").setLevel(logging.INFO)

    nside = 512
    npix = hp.nside2npix(nside)
    m = np.zeros(npix)
    theta, ra = hp.pix2ang(nside, range(npix))
    dec = np.pi/2. - theta
    mask = np.less(np.sin(dec), -0.8)

    ts = np.zeros(npix, dtype=np.float)
    xmin = np.zeros_like(ts, dtype=[(p, np.float) for p in ps_llh.params])
    if args.extension:
        ts, xmin = ps_llh._scan(ra[mask], dec[mask], ts,
                               xmin, mask, src_extension=np.radians(args.extension))
        np.save(args.prefix+'/all_sky/ext/skymap_ext_%s.npy' % args.extension, ts)
    else:
        ts, xmin = ps_llh._scan(ra[mask], dec[mask], ts, xmin, mask)
        np.save(args.prefix+'/all_sky/skymap.npy', ts)
