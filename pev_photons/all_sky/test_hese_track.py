#!/usr/bin/env python

########################################################################
# Test the position of the HESE track
########################################################################

import argparse
import numpy as np
import healpy as hp
import pandas as pd

from pev_photons import utils

def bg_trials(ps_llh, ra, dec, n_trials=10):
    """ Produce background TS trials for the HESE track event.
    Parameters
    ----------
    ra: float
        The right ascension value in radians.
    dec: float
        The declination value in radians.
    n_trials: int
        The number of trials to run.
    """
    ps_llh.capscramble = True

    trials = ps_llh.do_trials(n_trials, src_ra=ra,
                              src_dec=dec)

    np.save(utils.prefix+'all_sky/hese_track_trials.npy',
             trials['TS'])

def test_source(ps_llh, ra, dec):
    """ Fit for a source at the HESE track event location.
    Parameters
    ----------
    ra: float
        The right ascension value in radians.
    dec: float
        The declination value in radians.
    """
    source = np.empty((1,),
                      dtype=[('ra', np.float), ('dec', np.float),
                             ('TS', np.float), ('nsources', np.float),
                             ('gamma', np.float)])

    fit = ps_llh.fit_source(ra, dec, scramble=False)

    source['ra'] = np.degrees(ra)
    source['dec'] = np.degrees(dec)
    source['TS'] = fit[0]
    source['nsources'] = fit[1]['nsources']
    source['gamma'] = fit[1]['gamma']

    np.save(utils.prefix+'all_sky/hese_track.npy', source)

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Test source',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ncpu", type=int, default=1,
                    help="Number of cores to run on.")
    p.add_argument("--seed", type=int, default=1,
                   help='rng seed')
    p.add_argument("--n_trials", type=int, default=100,
                   help='Number of trials')
    args = p.parse_args()

    events = pd.read_hdf(utils.resource_dir+'HESE.hdf5')
    events = events[~events['is_cascade']]
    ra = np.radians(events['ra'].values[0])
    dec = np.radians(events['dec'].values[0])

    ps_llh = utils.load_dataset('point_source', ncpu=args.ncpu, seed=args.seed)
    if args.n_trials is not None:
        test_source(ps_llh, ra, dec, n_trials=args.n_trials)
    else:
        bg_trials(ps_llh, ra, dec)
