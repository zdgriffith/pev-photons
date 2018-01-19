#!/usr/bin/env python

########################################################################
# Submit a dagman to the cluster evaluating the sensitivity for a fine
# grid (0.1 degrees) in declination.
########################################################################

import argparse
import os
import sys

from utils.support import prefix, resource_dir

if __name__ == "__main__":

    p = argparse.ArgumentParser(description='Runs sensitivity evaluation on cluster',
                          formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--test', action='store_true', default=False,
                   help='Option for running test off cluster')
    p.add_argument('--maxjobs', type=str, default='1200',
                   help='Max jobs running on the cluster.')
    p.add_argument('--rm_old', action='store_true', default=False,
                   help='Remove old dag files?')
    args = p.parse_args()

    script = os.getcwd() + '/sens_on_cluster.py'

    if args.test:
        cmd = 'python '+script 
    else:
        dag_name = prefix+'dagman/ps_sens.dag'
        ex = ('condor_submit_dag -f -maxjobs ' + args.maxjobs
              + ' ' + dag_name)

        if args.rm_old:
            print('Deleting '+dag_name[:-3]+' files...')
            os.system('rm '+dag_name[:-3]+'*')

        dag = open(dag_name, "w+")

    #dec_0 = -85
    #dec_1 = -53.4
    dec_0 = -70
    dec_1 = -69

    job_num = 0
    for index in [2.0,2.7]:
        for i in range(int((dec_1-dec_0)*10)):
            dec = dec_0+i/10.
            arg  = ' --dec %s' % dec
            arg += ' --index %s' % index
            arg += ' --index %s' % index
            if args.test:
                ex  = ' '.join([cmd, arg])
            else:
                dag.write('JOB ' + str(job_num) + ' ' + resource_dir+'basic.submit\n')
                dag.write('VARS ' + str(job_num) + ' script=\"' + script + '\"\n')
                dag.write('VARS ' + str(job_num) + ' ARGS=\"' + arg + '\"\n')
                dag.write('VARS ' + str(job_num) + ' log_dir=\"' + prefix+'dagman/logs/' + '\"\n')
            job_num += 1

    os.system(ex)
