#!/usr/bin/env python 
import argparse
import os
import sys
import re
import glob

from pev_photons.utils.support import prefix

if __name__ == "__main__":

    p = argparse.ArgumentParser(description='analysis level processing of files',
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--dataset', help='Simulation dataset to run over')
    p.add_argument('--year', help='Detector year.')
    p.add_argument('--n', type=int, default=10,
                   help='Number of files to run per batch')
    p.add_argument('--test', action='store_true', default=False,
                   help='Option for running test off cluster')
    p.add_argument('--maxjobs', default='1200',
                   help='max jobs running on cluster')
    p.add_argument('--rm_old', action='store_true', default=False,
                   help='Remove old dag files?')
    args = p.parse_args()

    if args.test:
        args.n = 10
    else:
        dag_name = os.path.join(prefix, 'dagman', args.dataset+'_level3_processing.dag')
        ex = 'condor_submit_dag -f -maxjobs {} {}'.format(args.maxjobs, dag_name)

        if args.rm_old:
            print('Deleting '+dag_name[:-4]+' files...')
            os.system('rm '+dag_name[:-4]+'*')
        dag = open(dag_name, "w+")

    script = os.path.join(os.getcwd(), 'to_hdf_processing.py')

    GCD = '/data/user/zgriffith/Level3/GCDs/IT_'+args.year+'_GCD.i3.gz' 
    files = glob.glob(prefix+'datasets/level3/%s/*.i3.gz' % args.dataset)
    outDir = prefix+'datasets/%s/' % args.dataset

    # Split into batches
    batches = [files[i:i+args.n] for i in range(0, len(files), args.n)]

    for k, batch in enumerate(batches):

        # Name outfile
        out = '{}/{}_{}.hdf5'.format(outDir, args.dataset, k)

        arg  = '{} '.format(' '.join(batch))
        arg += '-g {} --year {} -o {}'.format(GCD, args.year, out)

        if args.test:
            cmd = 'python '+script
            ex  = ' '.join([cmd, arg])
            if k == 5:
                break
        else:
            arg  = script+' '+arg
            dag.write("JOB " + str(k) + " /data/user/zgriffith/dagman/new_icerec.submit\n")
            dag.write("VARS " + str(k) + " ARGS=\"" + arg + "\"\n")

    os.system(ex)
