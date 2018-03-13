#!/usr/bin/env python

########################################################################
## Submit a dagman to the cluster for template sensitivity trials
########################################################################

import os
import sys
import random
import argparse

from pev_photons.utils.support import prefix, resource_dir

if __name__ == "__main__":

    p = argparse.ArgumentParser(description='Submit trials to the cluster.',
                   formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--test', action='store_true', default=False,
                   help='Option for running test off cluster.')
    p.add_argument('--nJobs', type=int, default=50,
                   help='The number of jobs to submit.')
    p.add_argument('--nTrials', type=int, default=200,
                   help='The number of trials run per job.')
    p.add_argument("--alpha", type=float, default=3.0,
                   help='Spectral index of signal.')
    p.add_argument('--name', type=str, default='sybll',
                   help='Name of the template.')
    p.add_argument('--maxjobs', type=str, default='1200',
                   help='Max jobs running on the cluster.')
    p.add_argument('--rm_old', action='store_true', default=False,
                   help='Remove old dag files?')
    args = p.parse_args()

    script = os.getcwd() + '/inj_trials.py'

    if args.test:
        cmd = 'python '+script 
    else:
        dag_name = prefix+'dagman/'+args.name+'_sens_trials.dag'
        ex       = ('condor_submit_dag -f -maxjobs '
                    + args.maxjobs + ' ' + dag_name)

        if args.rm_old:
            print('Deleting '+dag_name[:-3]+' files...')
            os.system('rm '+dag_name[:-3]+'*')

        dag = open(dag_name, "w+")
    
    # Range, intervals of injected events best found through a course
    # run on sensitivity_test.py first. 
    inj_list = {'sybll':range(0,551,50),
                'qgs':range(0,551,50)}
    job_num = 0 
    for n_inj in inj_list[args.name]:
        for job in range(args.nJobs):
            arg  = ' --job %s --n_inj %s' % (job_num, n_inj)
            arg += ' --alpha %s --seed %s ' % (args.alpha, random.randint(0,10**8))
            arg += ' --n_trials %s --name %s' % (args.nTrials, args.name)
            if args.test:
                ex  = ' '.join([cmd, arg])
            else:
                dag.write('JOB ' + str(job_num) + ' ' + resource_dir+'extra_memory.submit\n')
                dag.write('VARS ' + str(job_num) + ' script=\"' + script + '\"\n')
                dag.write('VARS ' + str(job_num) + ' ARGS=\"' + arg + '\"\n')
                dag.write('VARS ' + str(job_num) + ' log_dir=\"' + prefix+'dagman/logs/' + '\"\n')
            job_num += 1
    os.system(ex)
