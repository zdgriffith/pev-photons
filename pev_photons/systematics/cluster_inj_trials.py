#!/usr/bin/env python

########################################################################
## Submit a dagman to the cluster for
## systematic template sensitivity trials
########################################################################

import argparse
import os

from pev_photons.utils.support import prefix, resource_dir, dag_dir
from pev_photons.utils.cluster_support import DagMaker

if __name__ == "__main__":

    p = argparse.ArgumentParser(description='Submit trials to the cluster.',
                   formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--test', action='store_true', default=False,
                   help='Option for running test off cluster.')
    p.add_argument('--rm_old', action='store_true', default=False,
                   help='Remove old dag files?')
    p.add_argument('--nJobs', type=int, default=50,
                   help='The number of jobs to submit.')
    p.add_argument('--nTrials', type=int, default=200,
                   help='The number of trials run per job.')
    p.add_argument("--alpha", type=float, default=3.0,
                   help='Spectral index of signal.')
    p.add_argument('--name', type=str, default='fermi_pi0',
                   help='Name of the template.')
    p.add_argument("--systematic", help='Systematic to test.')
    p.add_argument("--year", help='Data year.', default='2012')
    args = p.parse_args()

    if 'Laputop' in args.systematic:
        inj_list = range(0,171,17)
    else:
        inj_list = range(0,551,50)

    dag_maker = DagMaker(name='gp_sens_trials_{}'.format(args.systematic),
                         temp_dir=dag_dir)
    if args.rm_old:
        dag_maker.remove_old(prefix=prefix)

    static_args = {'n_trials': args.nTrials, 'name': args.name,
                   'alpha': args.alpha, 'systematic': args.systematic}
    iters = {'job': range(args.nJobs), 'n_inj': inj_list}
    ex = dag_maker.submit(script=os.path.join(os.getcwd(), 'inj_trials.py'),
                          static_args=static_args, iters=iters,
                          submit_file=os.path.join(resource_dir,
                                                   'extra_memory.submit'),
                          test=args.test, prefix=prefix, random_seed=True)
    os.system(ex)
