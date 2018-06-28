#!/usr/bin/env python

########################################################################
# Submit a dag to the cluster for calculating background trials
# for each declination value in a healpix map within the FOV.
########################################################################

import argparse
import os

from pev_photons.utils.support import prefix, resource_dir, dag_dir
from pev_photons.utils.cluster_support import DagMaker

if __name__ == "__main__":
    p = argparse.ArgumentParser(description='Submit trials to the cluster.',
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--test', action='store_true', default=False,
                   help='Option for running a job off the cluster.')
    p.add_argument('--rm_old', action='store_true', default=False,
                   help='Remove old dag files?')
    p.add_argument('--nJobs', type=int, default=4,
                   help='The number of jobs to submit at each declination.')
    p.add_argument('--nTrials', type=int, default=25000,
                   help='The number of trials to run per job.')
    p.add_argument('--n_decs', type=int, default=342,
                   help=('The number of unique declination values.',
                         '342 for a HEALPIX Nside of 512.'))
    args = p.parse_args()

    dag_maker = DagMaker(name='ps_dec_trials', temp_dir=dag_dir)
    if args.rm_old:
        dag_maker.remove_old(prefix=prefix)

    static_args = {'n_trials': args.nTrials}
    iters = {'job': range(args.nJobs), 'dec_i': range(args.n_decs)}
    ex = dag_maker.submit(script=os.path.join(os.getcwd(), 'one_dec_ts.py'),
                          static_args=static_args, iters=iters,
                          submit_file=os.path.join(resource_dir, 'basic.submit'),
                          test=args.test, prefix=prefix)
    os.system(ex)
