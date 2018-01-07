#!/usr/bin/env python

########################################################################
# Runs a stacking test of the HESS source catalog.
########################################################################

import argparse
import numpy as np

from pev_photons.load_datasets import load_ps_dataset
from pev_photons.support import prefix

def run_bg_trials(psllh, sources, args):
    """Run background trials for the H.E.S.S. stacking analysis"""

    trials = psllh.do_trials(args.bg_trials, src_ra=np.radians(sources['ra']),
                             src_dec=np.radians(sources['dec']))
    np.save(prefix+'TeVCat/stacking_trials.npy', trials['TS'])

def run_stacking_test(psllh, sources, args):
    """Run the H.E.S.S. stacking analysis"""

    fit_arr = np.empty((1,),
                       dtype=[('TS', np.float), ('nsources', np.float),
                              ('gamma', np.float)])
    if args.extended:
        out = psllh.fit_source(np.radians(sources['ra']),
                               np.radians(sources['dec']),
                               src_extension=np.radians(sources['extent']),
                               scramble=False)
    else:
        out = psllh.fit_source(np.radians(sources['ra']),
                               np.radians(sources['dec']),
                               scramble=False)
    fit_arr['TS'][0] = out[0]
    fit_arr['gamma'][0] = out[1]['gamma']
    fit_arr['nsources'][0] = out[1]['nsources']
    
    if args.extended:
        np.save(prefix+'TeVCat/extended/stacking_fit_result.npy', fit_arr)
    else:
        np.save(prefix+'TeVCat/stacking_fit_result.npy', fit_arr)

if __name__ == "__main__":

    p = argparse.ArgumentParser(
            description='Runs a stacking test of the HESS source catalog.',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--bg_trials', type=float, default=0,
                   help='if nonzero, run this number of background trials')
    p.add_argument('--extended', action='store_true', default=False,
                   help='If True, use source extension in fit.')
    args = p.parse_args()

    # Load the dataset.
    ps_llh = load_ps_dataset(args)

    sources = np.load(args.prefix+'/TeVCat/hess_sources.npz')
    if args.bg_trials:
        run_bg_trials(psllh, sources, args)
    else:
        run_stacking_test(psllh, sources, args)
