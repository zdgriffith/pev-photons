#!/usr/bin/env python

########################################################################
# Run signal-injected trials for tempalte sensitivity calculation
########################################################################

import argparse
import numpy as np

from skylab.template_injector import TemplateInjector
from skylab.sensitivity_utils import estimate_sensitivity

from utils.load_datasets import load_dataset
from utils.support import prefix

def fit_ts(args):
    template_llh = load_dataset('galactic_plane', args)

    inj = TemplateInjector(template=template_llh.template,
                           gamma=args.alpha,
                           E0=args.E0,
                           Ecut=None,
                           seed=1)
    inj.fill(template_llh.exp, template_llh.mc, template_llh.livetime)

    trials = template_llh.do_trials(args.n_trials, injector=inj,
                                    mean_signal=args.n_inj)

    n = trials['TS'][ trials['TS'] > 0].size
    ntot = trials['TS'].size

    np.save(prefix+'template/sens_trials/'+args.name+'/'+args.name+'_job_'+str(args.job)+'.npy',
            [args.n_inj, n, ntot])

if __name__ == "__main__":
    p = argparse.ArgumentParser(description='Template signal-injected trials.',
                   formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--name', type=str, default='fermi_pi0',
                   help='The name of the template.')
    p.add_argument("--alpha", type=float, default=3.0,
                   help='Spectral index of signal.')
    p.add_argument("--E0", type=float, default=2e6,
                   help='Energy to normalize.')
    p.add_argument("--ncpu", type=int, default=1,
                    help="Number of cores to run on.")
    p.add_argument("--seed", type=int, default=1,
                   help='rng seed')
    p.add_argument("--n_inj", type=float, default=0,
                   help='Number of injected events')
    p.add_argument("--n_trials", type=int, default=100,
                   help='Number of trials')
    p.add_argument("--job", type=int, default=0,
                   help='job number')
    args = p.parse_args()

    fit_ts(args)
