#!/usr/bin/env python

########################################################################
## Submit a dagman to the cluster for template background trials.
########################################################################

import argparse
import os

from pev_photons import utils

if __name__ == "__main__":

    p = argparse.ArgumentParser(description='Submit trials to the cluster.',
                   formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--test', action='store_true', default=False,
                   help='Option for running test off cluster.')
    p.add_argument('--nJobs', type=int, default=500,
                   help='The number of jobs to submit.')
    p.add_argument('--nTrials', type=int, default=200,
                   help='The number of trials run per job.')
    p.add_argument('--name', type=str, default='fermi_pi0',
                   help='Name of the template.')
    p.add_argument("--alpha", type=float, default=3.0,
                    help="Power law index")
    p.add_argument('--rm_old', action='store_true', default=False,
                   help='Remove old dag files?')
    args = p.parse_args()

    dag_maker = DagMaker(name=args.name+'_bg_trials', temp_dir=utils.dag_dir)
    if args.rm_old:
        dag_maker.remove_old(prefix=utils.prefix)

    static_args = {'bg_trials': args.nTrials, 'name': args.name,
                   'alpha': args.alpha}
    iters = {'job': range(args.nJobs)}
    ex = dag_maker.submit(script=os.path.join(os.getcwd(), 'run_template_analysis.py'),
                          static_args=static_args, iters=iters,
                          submit_file=os.path.join(utils.resource_dir,
                                                   'extra_memory.submit'),
                          test=args.test, prefix=utils.prefix, random_seed=True)
    os.system(ex)
