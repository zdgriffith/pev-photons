#!/usr/bin/env python

########################################################################
# Run template correlation analysis
########################################################################

import argparse
import numpy as np

from pev_photons import utils

def run_bg_trials(template_llh, args):
    """ Run background trials for the Fermi-LAT template analysis """
    trials = template_llh.do_trials(args.bg_trials)
    np.save(utils.prefix+'template/trials/%s/%s_job_%s.npy' % (args.name, args.name, args.job),
            trials['TS'])

def run_template_test(template_llh, args):
    """ Run the Fermi-LAT template analysis """
    out = template_llh.fit_template_source(scramble=False)

    fit_arr = np.empty((1,), dtype=[('TS', np.float), ('nsources', np.float)])
    fit_arr['TS'][0] = out[0]
    fit_arr['nsources'][0] = out[1]['nsources']
    np.save(utils.prefix+'template/'+args.name+'_fit_result.npy', fit_arr)

if __name__ == "__main__":

    p = argparse.ArgumentParser(
            description='template likelihood test',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--name', type = str, default='fermi_pi0',
                   help='name of the template')
    p.add_argument("--alpha", type=float, default=3.0,
                    help="Power law index")
    p.add_argument("--ncpu", type=int, default=1,
                    help="Number of cores to run on.")
    p.add_argument('--bg_trials', type=int, default=0,
                   help='if nonzero, run this number of background trials.')
    p.add_argument("--job", type=int, default=0,
                   help='job number if running background trials.')
    p.add_argument("--seed", type=int, default=1,
                   help='rng seed')
    args = p.parse_args()

    if args.name == 'cascades':
        template_llh = utils.load_dataset('HESE', ncpu=args.ncpu, seed=args.seed,
                                          alpha=args.alpha, template_name=args.name)
    else:
        template_llh = utils.load_dataset('galactic_plane', ncpu=args.ncpu, seed=args.seed,
                                          alpha=args.alpha, template_name=args.name)

    if args.bg_trials:
        run_bg_trials(template_llh, args)
    else:
        run_template_test(template_llh, args)
