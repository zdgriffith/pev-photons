#!/usr/bin/env python

########################################################################
# Get the position of the hottest spot in a map 
########################################################################

import argparse
import numpy as np
import healpy as hp

def test_hotspot(ra, dec, args):
    from load_datasets import load_ps_dataset

    ps_llh = load_ps_dataset(args)

    hotspot = np.empty((1,),
                       dtype=[('ra', np.float), ('dec', np.float),
                              ('TS', np.float), ('nsources', np.float),
                              ('gamma', np.float)])

    fit = ps_llh.fit_source(ra, dec, scramble = False)

    hotspot['ra'] = np.degrees(ra)
    hotspot['dec'] = np.degrees(dec)
    hotspot['TS'] = fit[0]
    hotspot['nsources'] = fit[1]['nsources']
    hotspot['gamma'] = fit[1]['gamma']

    print(hotspot)
    np.save(args.prefix+'all_sky/hotspot.npy', hotspot)

def get_hotspot_direction(args):
    m = np.load(args.prefix+'all_sky/skymap.npy')
    npix = len(m)
    nside = hp.npix2nside(npix)
    theta, ra = hp.pix2ang(nside, range(npix))
    dec = np.pi/2. - theta
    mask = np.greater(np.degrees(dec), -85.0)&np.less(np.sin(dec), -0.8)

    max_ts = np.flip(np.sort(m[mask]), axis=0)[0]
    index = np.isclose(m[mask],max_ts)

    return (ra[mask][index][0], dec[mask][index][0])

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Test hotspot',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', dest='prefix', type = str,
                   default = '/data/user/zgriffith/pev_photons/',
                   help    = 'base directory for file storing')
    p.add_argument("--ncpu", type=int, default=1,
                    help="Number of cores to run on.")
    p.add_argument("--seed", type=int, default=1,
                   help='rng seed')
    args = p.parse_args()

    ra, dec = get_hotspot_direction(args)
    test_hotspot(ra, dec, args)
