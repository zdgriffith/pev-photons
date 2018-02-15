#!/usr/bin/env python

import re
import os
import sys
import argparse
import glob

from utils.support import prefix

def make_batches(files):
    j = 0
    batches = []
    for f in files:
        if j == 0:
            batch = []
        batch.append(f)
        j += 1
        if j == args.n:
            batches.append(batch)
            j = 0
        
    return batches

if __name__ == "__main__":

    p = argparse.ArgumentParser(
            description='Run on i3 files, write to hdf5',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--dataset', dest='dataset',
            help='Simulation dataset to process')
    p.add_argument('-n', '--n', dest='n', type=int, default=200,
            help='Number of files to run per batch')
    p.add_argument('--test', dest='test', action='store_true',
            default=False,
            help='Option for running test off cluster')
    p.add_argument('--maxjobs', dest='maxjobs',
            default='1200',
            help='max jobs running on cluster')
    p.add_argument('--rm_old', dest='rm_old', action='store_true',
            default=False,
            help='Remove old dag files?')
    args = p.parse_args()

    #------------------------------------------------------------------------
    # Set up DAG

    dag_name = os.path.join(prefix, 'dagman/{}_processing.dag'.format(args.dataset))

    if args.test:
        args.n = 10
    else:
        ex = 'condor_submit_dag -f -maxjobs {} {}'.format(args.maxjobs, dag_name)

        if args.rm_old:
            print('Deleting {} files...'.format(dag_name[:-4]))
            os.system('rm {}*'.format(dag_name[:-4]))
        dag = open(dag_name, "w+")

    path = '/data/ana/CosmicRay/IceTop_level3/sim/IC86.2012/'
    gcd = os.path.join(path, 'GCD/Level3_{}_GCD.i3.gz'.format(args.dataset))
    files = glob.glob(os.path.join(path, '{}/*.i3.gz'.format(args.dataset)))

    #------------------------------------------------------------------------

    batches = make_batches(files)

    script = "/home/zgriffith/pev_photons/event_selection/sim_processing.py"
    outDir = os.path.join(prefix, 'datasets', args.dataset)

    for j, batch in enumerate(batches):
    
        first = re.split('\_', os.path.basename(batch[0]))[3][:-6]
        last = re.split('\_', os.path.basename(batch[-1]))[3][:-6]
        out = os.path.join(outDir, '{}_{}.hdf5'.format(first, last))

        arg  = ' {} {} -g {} -o {} '.format(script, ' '.join(batch), gcd, out)

        if args.test:
            ex = 'python ' + arg
            break
        else:
            dag.write("JOB " + str(j) + " /data/user/zgriffith/dagman/new_icerec.submit\n")
            dag.write("VARS " + str(j) + " ARGS=\"" + arg + "\"\n")

    os.system(ex)
