#!/usr/bin/env python

########################################################################
## Submit a dagman to the cluster for template sensitivity trials
########################################################################

import os
import sys
import random
import argparse
from itertools import product

from pev_photons.utils.support import prefix, resource_dir, dag_dir

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
    p.add_argument("--systematic", help='Systematic to test.')
    p.add_argument("--year", help='Data year.', default='2012')
    p.add_argument('--maxjobs', type=str, default='1200',
                   help='Max jobs running on the cluster.')
    p.add_argument('--rm_old', action='store_true', default=False,
                   help='Remove old dag files?')
    args = p.parse_args()

    script = os.getcwd() + '/inj_trials.py'
    if args.test:
        cmd = 'python '+script 
        dag_name = ''
    else:
        dag_name = 'gp_sens_{}_{}'.format(args.systematic, args.year)

        if args.rm_old:
            print('Deleting '+dag_name+' files...')
            os.system('rm '+os.path.join(dag_dir, dag_name)+'*')
            os.system('rm '+os.path.join(prefix, 'dagman', dag_name)+'*')
        dag_file = os.path.join(dag_dir, dag_name+'.dag')
        dag = open(dag_file, "w+")

    # Range, intervals of injected events best found through a course
    # run on sensitivity_test.py first. 
    #inj_list = {'sybll':range(0,551,50),
    #            'qgs':range(0,551,50)}
    if 'Laputop' in args.systematic:
        inj_list = range(0,171,17)
    else:
        inj_list = range(0,551,50)
    for i, (n_inj, job) in enumerate(product(inj_list, range(args.nJobs))):
        arg =  '{} '.format(script)
        arg += ' --job %s --n_inj %s' % (i, n_inj)
        arg += ' --alpha %s --seed %s ' % (args.alpha, random.randint(0,10**8))
        arg += ' --n_trials %s --systematic %s' % (args.nTrials, args.systematic)
        if args.test:
            ex  = ' '.join([cmd, arg])
            os.system(ex)
        else:
            dag.write('JOB ' + str(i) + ' ' + resource_dir+'extra_memory.submit\n')
            dag.write('VARS ' + str(i) + ' ARGS=\"' + arg + '\"\n')
            dag.write('VARS {} log_dir=\"{}/logs/{}\"\n'.format(i, dag_dir, dag_name))
            dag.write('VARS {} out_dir=\"{}/dagman/{}\"\n'.format(i, prefix, dag_name))

    if not args.test:
        ex = 'condor_submit_dag -f -maxjobs {} {}'.format(args.maxjobs, dag_file)
        os.system(ex)
