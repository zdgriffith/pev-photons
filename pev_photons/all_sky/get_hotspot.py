#!/usr/bin/env python

########################################################################
# Get the position of the hottest spot in a map 
########################################################################

import argparse
import numpy as np
import healpy as hp

from pev_photons.utils.load_datasets import load_dataset
from pev_photons.utils.support import prefix

def test_hotspot(ps_llh, ra, dec):
    """ fit for a point source at the location of the all-sky-scan hotspot """

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

    pairs = [hotspot.dtype.names[i]+': %0.2f' % val for i, val in enumerate(hotspot[0])]
    for pair in pairs:
        print(pair)
    np.save(prefix+'all_sky/hotspot.npy', hotspot)


def get_hotspot_direction():
    """ returns the direction in right ascension and declination. """
    m = np.load(prefix+'all_sky/skymap.npy')
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
    p.add_argument("--ncpu", type=int, default=1,
                    help="Number of cores to run on.")
    p.add_argument("--seed", type=int, default=1,
                   help='rng seed')
    args = p.parse_args()

    ps_llh = load_dataset('point_source', ncpu=args.ncpu, seed=args.seed)
    ra, dec = get_hotspot_direction()
    test_hotspot(ps_llh, ra, dec)
