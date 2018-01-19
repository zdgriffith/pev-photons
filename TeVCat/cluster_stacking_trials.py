#!/usr/bin/env python

import argparse
import os
import sys

from utils.support import prefix, resource_dir

if __name__ == "__main__":

    p = argparse.ArgumentParser(description='Run stacking test trials on cluster',
                   formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--test', action='store_true', default=False,
                   help='Option for running test off cluster')
    p.add_argument('--maxjobs', type=str, default='1200',
                   help='Max jobs running on the cluster.')
    p.add_argument('--rm_old', action='store_true', default=False,
                   help='Remove old dag files?')
    p.add_argument('--nJobs', type=int, default='1000',
                   help='max jobs running on cluster')
    p.add_argument('--nTrials', type=int, default=10,
                   help='max jobs running on cluster')
    args = p.parse_args()

    script = os.getcwd() + '/stacking_test.py'

    if args.test:
        cmd = 'python '+script 
    else:
        dag_name = prefix+'dagman/stacking_trials.dag'
        ex       = 'condor_submit_dag -f -maxjobs ' +args.maxjobs+' '+dag_name

        if args.rm_old:
            print('Deleting '+dag_name[:-3]+' files...')
            os.system('rm '+dag_name[:-3]+'*')

        dag = open(dag_name, "w+")

    job_num = 0
    for job in range(args.nJobs):
        arg  = ' --runTrial --job %s --nTrials %s' % (job, args.nTrials)
        if args.test:
            ex  = ' '.join([cmd, arg])
        else:
            dag.write('JOB ' + str(job_num) + ' ' + resource_dir+'basic.submit\n')
            dag.write('VARS ' + str(job_num) + ' script=\"' + script + '\"\n')
            dag.write('VARS ' + str(job_num) + ' ARGS=\"' + arg + '\"\n')
            dag.write('VARS ' + str(job_num) + ' log_dir=\"' + prefix+'dagman/logs/' + '\"\n')
        job_num += 1

    os.system(ex)
