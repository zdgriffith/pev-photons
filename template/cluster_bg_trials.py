#!/usr/bin/env python

########################################################################
## Submit a dagman to the cluster for template background trials.
########################################################################

import os
import sys
import random
import argparse

from utils.support import prefix, resource_dir

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
    p.add_argument('--maxjobs', type=str, default='1200',
                   help='Max jobs running on the cluster.')
    p.add_argument('--rm_old', action='store_true', default=False,
                   help='Remove old dag files?')
    p.add_argument('--rescue', action='store_true', default=False,
                   help='Option for submitting the rescue file.')
    args = p.parse_args()

    script = os.getcwd() + '/run_template_analysis.py'

    if args.test:
        cmd = 'python '+script 
    else:
        dag_name = prefix+'dagman/'+args.name+'_bg_trials.dag'
        ex       = ('condor_submit_dag -f -maxjobs '
                    + args.maxjobs + ' ' + dag_name)

        if args.rm_old:
            print('Deleting '+dag_name[:-3]+' files...')
            os.system('rm '+dag_name[:-3]+'*')

        dag = open(dag_name, "w+")
    
    for job in range(args.nJobs):
        arg  = ' --job %s ' % job
        arg += ' --seed %s ' % random.randint(0,10**8)
        arg += ' --bg_trials %s --name %s' % (args.nTrials, args.name)
        if args.test:
            ex  = ' '.join([cmd, arg])
        else:
            dag.write('JOB ' + str(job) + ' ' + resource_dir+'extra_memory.submit\n')
            dag.write('VARS ' + str(job) + ' script=\"' + script + '\"\n')
            dag.write('VARS ' + str(job) + ' ARGS=\"' + arg + '\"\n')
            dag.write('VARS ' + str(job) + ' log_dir=\"' + prefix+'dagman/logs/' + '\"\n')

    os.system(ex)
