#!/usr/bin/env python

########################################################################
# Run signal-injected trials for tempalte sensitivity calculation
########################################################################

import argparse
import numpy as np

from skylab.template_injector import TemplateInjector
from skylab.sensitivity_utils import estimate_sensitivity

from pev_photons import utils

def fit_ts(template_llh, alpha=3.0, E0=2e6, job=0,
           n_trials=100, n_inj=0, name='fermi_pi0'):
    """ Calculate TS trials with an injected gamma-ray signal
        conforming to the given template """

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

    np.save(utils.prefix+'template/sens_trials/'+args.name+'/'+args.name+'_job_'+str(args.job)+'.npy',
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

    template_llh = load_dataset('galactic_plane', ncpu=args.ncpu, seed=args.seed,
                                alpha=args.alpha, template_name=args.name)
    fit_ts(template_llh, alpha=args.alpha, E0=args.E0,
           job=args.job, n_trials=args.n_trials,
           n_inj=args.n_inj, name=args.name)
