#!/usr/bin/env python

########################################################################
# Perform a scan over the entire FOV
########################################################################

import argparse
import numpy as np
import logging

import healpy as hp

from pev_photons.utils.load_datasets import load_dataset
from pev_photons.utils.support import prefix

def manual_scan(ps_llh, nside=args.nside, extension=args.extension):
    """Manually test for a point source at each pixel in the sky map.

    Parameters
    ----------
    nside: int
        HEALPIX nside value for skymap.
    extension: float
        radius of source spatial extension in degrees.
    """

    npix = hp.nside2npix(nside)
    m = np.zeros(npix)

    theta, ra = hp.pix2ang(nside, range(npix))
    dec = np.pi/2. - theta
    mask = np.less(np.sin(dec), -0.8)

    ts = np.zeros(npix, dtype=np.float)
    xmin = np.zeros_like(ts, dtype=[(p, np.float) for p in ps_llh.params])
    if extension:
        ts, xmin = ps_llh._scan(ra[mask], dec[mask],
                                ts, xmin, mask,
                                src_extension=np.radians(extension))
        np.save(prefix+'/all_sky/ext/skymap_ext_%s.npy' % extension,
                ts)
    else:
        ts, xmin = ps_llh._scan(ra[mask], dec[mask], ts, xmin, mask)
        np.save(prefix+'/all_sky/skymap.npy', ts)

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Create an all sky TS map.',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--outFile', type=str,
                   default='all_sky/skymap.npy',
                   help='The output file name.')
    p.add_argument("--ncpu", type=int, default=1,
                    help="Number of cores to run on.")
    p.add_argument("--seed", type=int, default=1,
                   help='rng seed')
    p.add_argument("--nside", type=int, default=512,
                   help='The healpix resolution.')
    p.add_argument('--bg_trials', type=int, default=0,
                   help='if nonzero, run this number of background trials.')
    p.add_argument("--job", type=int, default=0,
                   help='job number if running background trials.')
    p.add_argument('--extension', type=float, default=0,
                   help='Spatial extension to source hypothesis in degrees.')
    p.add_argument('--coarse_scan', action='store_true', default=False,
                   help=('Use the all_sky_scan() method, which runs'
                         'a coarser scan first, then a follow up'))
    args = p.parse_args()

    if args.bg_trials:
        ts_list = np.full(args.bg_trials, np.nan)
        for trial in range(args.bg_trials):
            args.seed = np.random.randint(0, 10**6)
            ps_llh = load_dataset('point_source', ncpu=args.ncpu, seed=args.seed,
                                  llh_args={'scramble':True})
            for i, scan in enumerate(ps_llh.all_sky_scan()):
                if i > 0:
                    ts_list[trial] = scan[1]['South']['fit']['TS']
                    break
            np.save(prefix+'all_sky/scan_trials/job_%s.npy' % args.job, ts_list)
    else:
        # Load the dataset.
        ps_llh = load_dataset('point_source', ncpu=args.ncpu, seed=args.seed)

        # Set the logging output file.
        logging.getLogger("skylab.ps_llh.PointSourceLLH").setLevel(logging.INFO)
        logging.basicConfig(filename=prefix+'all_sky/scan.log',
                            filemode='w', level=logging.INFO)
        if args.coarse_scan:
            for i, scan in enumerate(ps_llh.all_sky_scan()):
                if i > 0:
                    m = scan[0]['TS']
                    break
            np.save(prefix+args.outFile, m)
        else:
            manual_scan(ps_llh, nside=args.nside, extension=args.extension)
