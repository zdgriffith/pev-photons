#!/usr/bin/env python

########################################################################
# Submit a dagman to the cluster for calculating all sky trials
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
    p.add_argument('--nJobs', type=int, default=200,
                   help='The number of jobs to submit at each point.')
    p.add_argument('--nTrials', type=int, default=5,
                   help='The number of trials run per job.')
    args = p.parse_args()

    dag_maker = DagMaker(name='all_sky_trials', temp_dir=dag_dir)
    if args.rm_old:
        dag_maker.remove_old(prefix=prefix)

    static_args = {'bg_trials': args.nTrials}
    iters = {'job': range(args.nJobs)}
    ex = dag_maker.submit(script=os.path.join(os.getcwd(), 'all_sky_scan.py'),
                          static_args=static_args, iters=iters,
                          submit_file=os.path.join(resource_dir, 'basic.submit'),
                          test=args.test, prefix=prefix)
    os.system(ex)
