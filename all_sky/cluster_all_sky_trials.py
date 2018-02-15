#!/usr/bin/env python

########################################################################
# Submit a dagman to the cluster for calculating all sky trials
########################################################################

import argparse
import os
import sys

from utils.support import prefix, resource_dir

if __name__ == "__main__":

    p = argparse.ArgumentParser(description='Submit trials to the cluster.',
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--test', action='store_true', default=False,
                   help='Option for running test off cluster.')
    p.add_argument('--maxjobs', type=str, default='1200',
                   help='Max jobs running on the cluster.')
    p.add_argument('--rm_old', action='store_true', default=False,
                   help='Remove old dag files?')
    p.add_argument('--nJobs', type=int, default=200,
                   help='The number of jobs to submit at each point.')
    p.add_argument('--nTrials', type=int, default=5,
                   help='The number of trials run per job.')
    args = p.parse_args()

    script = os.getcwd() + '/all_sky_scan.py'

    if args.test:
        cmd = 'python '+script 
    else:
        dag_name = prefix+'dagman/all_sky_trials.dag'
        ex       = ('condor_submit_dag -f -maxjobs '
                    + args.maxjobs + ' ' + dag_name)

        if args.rm_old:
            print('Deleting '+dag_name[:-3]+' files...')
            os.system('rm '+dag_name[:-3]+'*')

        dag = open(dag_name, "w+")
    
    for job in range(args.nJobs):
        arg  = ' --job %s' % job
        arg += ' --bg_trials %s ' % args.nTrials
        if args.test:
            ex  = ' '.join([cmd, arg])
        else:
            #arg = script+arg
            dag.write('JOB ' + str(job) + ' ' + resource_dir+'basic.submit\n')
            dag.write('VARS ' + str(job) + ' script=\"' + script + '\"\n')
            dag.write('VARS ' + str(job) + ' ARGS=\"' + arg + '\"\n')
            dag.write('VARS ' + str(job) + ' log_dir=\"' + prefix+'dagman/logs/' + '\"\n')
    os.system(ex)
