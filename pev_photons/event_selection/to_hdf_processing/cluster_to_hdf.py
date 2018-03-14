#!/usr/bin/env python 
import argparse
import os
import sys
import re
import glob

from pev_photons.utils.support import prefix

def write_dag_MC(batches, GCD, out_dir):
    for k, batch in enumerate(batches):

        # Name outfile
        out = '{}/{}_{}.hdf5'.format(out_dir, args.MC_dataset, k)

        arg  = '{} '.format(' '.join(batch))
        arg += '-g {} --year {} -o {} --isMC'.format(GCD, args.year, out)
        arg += ' --run_lambdas'

        if args.test:
            cmd = 'python '+script
            ex  = ' '.join([cmd, arg])
            if k == 5:
                break
        else:
            arg  = script+' '+arg
            dag.write("JOB " + str(k) + " /data/user/zgriffith/dagman/new_icerec.submit\n")
            dag.write("VARS " + str(k) + " ARGS=\"" + arg + "\"\n")

    ex = 'condor_submit_dag -f -maxjobs {} {}'.format(args.maxjobs, dag_name)
    os.system(ex)
    return

def write_dag_data(batches, GCD_files, out_dir):
    count = 0
    for k, key in enumerate(batches.keys()):
        for j, batch in enumerate(batches[key]):
            count += 1

            # Name outfile
            run = re.split('\_', os.path.basename(batch[0]))[3]
            out = '{}/{}_{}.hdf5'.format(out_dir, run, j)

            arg = '{} '.format(' '.join(batch))

            GCD = [GCD for GCD in GCD_files if run in GCD_files][0]
            arg += '-g {} --year {} -o {}'.format(GCD, args.year, out)

            if args.test:
                cmd = 'python '+script
                ex  = ' '.join([cmd, arg])
                if j == 5:
                    break
            else:
                arg  = script+' '+arg
                dag.write("JOB " + str(count) + " /data/user/zgriffith/dagman/new_icerec.submit\n")
                dag.write("VARS " + str(count) + " ARGS=\"" + arg + "\"\n")

    ex = 'condor_submit_dag -f -maxjobs {} {}'.format(args.maxjobs, dag_name)
    os.system(ex)
    return

def get_data_batches(files):
    batches = {}
    for fname in files:
        run = re.split('\_', os.path.basename(fname))[3]
        if run in batches:
            new_batch = 0
            for i in range(len(batches[run])):
                if len(batches[run][i]) < args.n:
                    batches[run][i].append(fname)
                    new_batch += 1
            if new_batch == 0:
                batches[run].append([fname])
        else:
            batches[run] = [[fname]]
    return batches

def get_data_files():
    if args.year == '2011':
        file_list   = glob.glob('/data/ana/CosmicRay/IceTop_level3/exp/IC86.%s/*/*/*/*.i3.bz2' % args.year)
    else:
        file_list   = glob.glob('/data/ana/CosmicRay/IceTop_level3/exp/test_data/IC86.%s/*/*/*/*.i3.bz2' % args.year)
    file_list.sort()

    goodRunList = prefix+'run_files/non_burn_runs_%s.txt' % args.year
    return fileCleaner(goodRunList, file_list)

if __name__ == "__main__":

    p = argparse.ArgumentParser(description='analysis level processing of files',
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--year', help='Detector year.')
    p.add_argument('--MC_dataset', default=None,
                   help='If simulation, the dataset to run over.')
    p.add_argument('--n', type=int, default=10,
                   help='Number of files to run per batch')
    p.add_argument('--test', action='store_true', default=False,
                   help='Option for running test off cluster')
    p.add_argument('--maxjobs', default='1200',
                   help='max jobs running on cluster')
    p.add_argument('--rm_old', action='store_true', default=False,
                   help='Remove old dag files?')
    args = p.parse_args()

    script = os.path.join(os.getcwd(), 'to_hdf_processing.py')
    isMC = args.MC_dataset is not None

    #-------------------------------------------------------------------------
    # Set up Dag info

    if args.test:
        args.n = 2
    else:
        if isMC:
            dag_name = os.path.join(prefix, 'dagman', args.MC_dataset+'_to_hdf.dag')
        else:
            dag_name = os.path.join(prefix, 'dagman', args.year+'_to_hdf.dag')

        if args.rm_old:
            print('Deleting '+dag_name[:-4]+' files...')
            os.system('rm '+dag_name[:-4]+'*')
        dag = open(dag_name, "w+")

    #-------------------------------------------------------------------------
    # Get the list of files to be processed

    if isMC:
        if args.MC_dataset in ['12622', '12533', '12612', '12613', '12614']:
            files = glob.glob('/data/user/zgriffith/Level3/IT81_sim/%s/*.i3.gz' % args.MC_dataset)
            GCD = '/data/user/zgriffith/Level3/GCDs/IT_'+args.year+'_GCD.i3.gz' 
        elif args.MC_dataset in ['12360']:
            files = glob.glob('/data/user/zgriffith/Level3/IT81_sim/%s/*.i3.gz' % args.MC_dataset)
            path = '/data/ana/CosmicRay/IceTop_level3/sim/IC86.2012/'
            files = glob.glob(os.path.join(path, '{}/*.i3.gz'.format(args.MC_dataset)))
            GCD = os.path.join(path, 'GCD/Level3_{}_GCD.i3.gz'.format(args.dataset))
        else:
            files = glob.glob(prefix+'datasets/level3/%s/*.i3.gz' % args.MC_dataset)
            GCD = '/data/user/zgriffith/Level3/GCDs/IT_'+args.year+'_GCD.i3.gz' 
        batches = [files[i:i+args.n] for i in range(0, len(files), args.n)]
        out_dir = prefix+'datasets/%s/' % args.MC_dataset

        write_dag_MC(batches, GCD, out_dir)
    else:
        files = get_data_files()
        batches = make_data_batches(files)
        GCD_files = glob.glob('/data/ana/CosmicRay/IceTop_level3/exp/test_data/IC86.%s/*/*/*/*_GCD.i3.gz' % args.year)
        out_dir = prefix+'/datasets/data/'+args.year
        write_dag_data(batches, GCD_files, out_dir)
