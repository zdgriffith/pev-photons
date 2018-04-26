#!/usr/bin/env python

########################################################################
# Submit a dagman to the cluster evaluating the sensitivity for a fine
# grid (0.1 degrees) in declination.
########################################################################

import argparse
import os
import sys
from itertools import product

from pev_photons.utils.support import prefix, resource_dir, dag_dir

if __name__ == "__main__":

    p = argparse.ArgumentParser(description='Runs sensitivity evaluation on cluster',
                          formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--test', action='store_true', default=False,
                   help='Option for running test off cluster')
    p.add_argument('--maxjobs', type=str, default='1200',
                   help='Max jobs running on the cluster.')
    p.add_argument('--rm_old', action='store_true', default=False,
                   help='Remove old dag files?')
    p.add_argument("--model", help='hadronic interaction model.')
    p.add_argument("--sim_value")
    args = p.parse_args()

    script = os.getcwd() + '/sens_on_cluster.py'

    if args.test:
        cmd = 'python '+script 
        dag_name = ''
    else:
        if args.sim_value:
            dag_name = 'ps_sens_{}_{}'.format(args.model, args.sim_value)
        else:
            dag_name = 'ps_sens_{}'.format(args.model)

        if args.rm_old:
            print('Deleting '+dag_name[:-3]+' files...')
            os.system('rm '+os.path.join(dag_dir, dag_name)+'*')
        dag_file = os.path.join(dag_dir, dag_name+'.dag')
        dag = open(dag_file, "w+")

    indices = [2.0, 2.7]
    dec_0 = -85
    dec_1 = -53.4
    decs = [dec_0 + i/10. for i in range(int((dec_1-dec_0)*10))]

    for job, (index, dec) in enumerate(product(indices, decs)):
        arg = '--dec {} --index {} --model {}'.format(dec, index, args.model)
        if args.sim_value:
            arg += ' --sim_value {}'.format(args.sim_value)
        if args.test:
            ex  = ' '.join([cmd, arg])
            os.system(ex)
        else:
            dag.write('JOB {} {}/basic.submit\n'.format(job, resource_dir))
            dag.write('VARS {} script=\"{}\"\n'.format(job, script))
            dag.write('VARS {} ARGS=\"{}\"\n'.format(job, arg))
            dag.write('VARS {} log_dir=\"{}/logs/{}\"\n'.format(job, dag_dir, dag_name))
            dag.write('VARS {} out_dir=\"{}/dagman/{}\"\n'.format(job, prefix, dag_name))

    if not args.test:
        ex = 'condor_submit_dag -f -maxjobs {} {}'.format(args.maxjobs, dag_file)
        os.system(ex)
