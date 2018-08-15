#!/usr/bin/env python

########################################################################
# Get the position of the hottest spot in a map 
########################################################################

import argparse
import numpy as np
import healpy as hp

from pev-photons.utils.load_datasets import load_dataset
from pev-photons.utils.support import prefix
from pev-photons.TeVCat.hess_source_errors import error_profile

def test_hotspot(ps_llh, ra, dec, errors=False):
    """ fit for a point source at the location of the all-sky-scan hotspot """

    hotspot = np.empty((1,),
                       dtype=[('ra', np.float), ('dec', np.float),
                              ('TS', np.float), ('nsources', np.float),
                              ('gamma', np.float)])

    TS, xmin = ps_llh.fit_source(ra, dec, scramble = False)
    fit = dict({'TS':TS}, **xmin) 

    hotspot['ra'] = np.degrees(ra)
    hotspot['dec'] = np.degrees(dec)
    hotspot['TS'] = TS
    hotspot['nsources'] = xmin['nsources']
    hotspot['gamma'] = xmin['gamma']

    if errors:
        n_errors = error_profile(ps_llh, ra, dec, fit,
                                 nsources=np.arange(0, 100, 0.1))
        gamma_errors = error_profile(ps_llh, ra, dec, fit,
                                     gamma=np.arange(0.99, 4.01, 0.01))

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
    test_hotspot(ps_llh, ra, dec, errors=True)
