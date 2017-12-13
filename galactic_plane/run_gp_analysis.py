#!/usr/bin/env python

########################################################################
# Run the galactic plane correlation analysis
########################################################################

import argparse
import numpy as np

from load_datasets import load_gp_dataset

def run_bg_trials(template_llh, args):
    trials = template_llh.do_trials(args.bg_trials)
    np.save(args.prefix+'galactic_plane/trials/%s_job_%s.npy' % (args.name, args.job),
            trials['TS'])

def run_template_test(template_llh, args):
    out = template_llh.fit_template_source(scramble=False)

    fit_arr = np.empty((1,), dtype=[('TS', np.float), ('nsources', np.float)])
    fit_arr['TS'][0] = out[0]
    fit_arr['nsources'][0] = out[1]['nsources']
    np.save(args.prefix+'galactic_plane/'+args.name+'_fit_result.npy', fit_arr)

if __name__ == "__main__":

    p = argparse.ArgumentParser(
            description='galactic plane test',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', type=str,
                   default='/data/user/zgriffith/pev_photons/',
                   help='Base directory for file storing.')
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
    args = p.parse_args()

    template_llh, exp, mc, livetime = load_gp_dataset(args)

    if args.bg_trials:
        run_bg_trials(template_llh, args)
    else:
        run_template_test(template_llh, args)
