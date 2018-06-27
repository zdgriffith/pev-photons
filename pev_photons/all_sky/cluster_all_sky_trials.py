#!/usr/bin/env python

########################################################################
# Submit a dagman to the cluster for calculating all sky trials
########################################################################

import argparse
import os
import sys

from pev_photons.utils.support import prefix, resource_dir, dag_dir
from pev_photons.utils.cluster_support import DagMaker

def construct_dag(dag_maker, test=False, nJobs=4, nTrials=25000):
    """ Construct a dag for point source all-sky trials.

    Parameters
    ----------
    dag_maker : DagMaker instance
        Class instance that contains info for creating dag files.
    test : bool
        Denotes whether this is a test on a non-submitter node.
    nJobs : int
        The number of jobs to run for a single declination value.
    nTrials : int
        The number of trials to run per job.

    Returns
    -------
    ex : str
        a bash executable to pass to os.system()
    """
    script = os.path.join(os.getcwd(), 'all_sky_scan.py')
    dag_file = os.path.join(dag_maker.temp_dir, dag_maker.name+'.dag')
    with open(dag_file, 'w+') as dag:
        for i, job in enumerate(range(nJobs)):
            arg = ' --job {} '.format(job)
            arg += ' --bg_trials {} '.format(nTrials)

            if test:
                return ' '.join(['python', cmd, arg])
            else:
                dag_maker.write(dag=dag, index=i, arg=script+arg,
                                submit_file=resource_dir+'basic.submit',
                                prefix=prefix) 
    return 'condor_submit_dag -f {}'.format(dag_file)

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

    ex = construct_dag(dag_maker, test=args.test, nJobs=args.nJobs,
                       nTrials=args.nTrials)
    os.system(ex)
